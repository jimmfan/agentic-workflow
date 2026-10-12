#!/usr/bin/env python3
"""Scripted stand-in for the Responses API; no model and no credentials.

Serves streamed responses from a fixed script so Codex can run a frozen turn
(for example a `search` call followed by a fixed reply) against its real tool,
approval, and session machinery. Every request body is logged so preflights can
inspect exactly what a model would have received.

Script format: a JSON list of steps, one per model request, each either
{"tool_call": {"description": "<tool description>", "arguments": {...}}},
{"custom_tool_call": {"name": "<tool>", "input": "<text>"}}, or
{"message": "<assistant text>"}. A tool call names the tool whose advertised
description matches exactly, so the namespaced model-visible name is resolved
from the request rather than assumed.
"""

import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading


def tool_names(tools, description, prefix=""):
    """Yield model-visible names of tools whose description matches."""
    for tool in tools or []:
        if not isinstance(tool, dict):
            continue
        name = tool.get("name") or tool.get("function", {}).get("name")
        text = tool.get("description") or tool.get("function", {}).get("description")
        if name and text == description:
            yield prefix + name
        nested = tool.get("tools")
        if isinstance(nested, list):
            yield from tool_names(nested, description, prefix)


def item_id(seed, index, prefix, length):
    """Deterministic identifier shaped like the provider's own identifiers."""
    digest = hashlib.sha256(f"{seed}:{index}:{prefix}".encode()).hexdigest()
    return prefix + (digest * 2)[:length]


def sse(event):
    return f"event: {event['type']}\ndata: {json.dumps(event)}\n\n".encode()


class MockProvider:
    def __init__(self, script, log_path, seed="mock"):
        self.script = list(script)
        self.seed = seed
        self.log_path = Path(log_path)
        self.requests = 0
        self.lock = threading.Lock()
        handler = self._handler()
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    @property
    def base_url(self):
        return f"http://127.0.0.1:{self.server.server_address[1]}/v1"

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_exc):
        self.server.shutdown()
        self.server.server_close()

    def log(self, record):
        with self.log_path.open("a") as handle:
            handle.write(json.dumps(record) + "\n")

    def next_step(self, body):
        with self.lock:
            index = self.requests
            self.requests += 1
        if index >= len(self.script):
            return index, None
        return index, self.script[index]

    def _handler(self):
        provider = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_GET(self):
                provider.log({"method": "GET", "path": self.path})
                self.send_response(404)
                self.end_headers()

            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                raw = self.rfile.read(length)
                try:
                    body = json.loads(raw or b"{}")
                except json.JSONDecodeError:
                    body = {"unparsed": raw.decode(errors="replace")}
                if not self.path.rstrip("/").endswith("/responses"):
                    provider.log({"method": "POST", "path": self.path, "body": body})
                    self.send_response(404)
                    self.end_headers()
                    return
                index, step = provider.next_step(body)
                provider.log(
                    {"method": "POST", "path": self.path, "index": index, "body": body}
                )
                if step is None:
                    self.send_response(500)
                    self.end_headers()
                    return
                seed = provider.seed
                response_id = item_id(seed, index, "resp_", 48)
                call_id = item_id(seed, index, "call_", 32)
                if "tool_call" in step:
                    call = step["tool_call"]
                    names = list(tool_names(body.get("tools"), call["description"]))
                    if len(names) != 1:
                        provider.log(
                            {"index": index, "error": "tool not found", "names": names}
                        )
                        self.send_response(500)
                        self.end_headers()
                        return
                    item = {
                        "type": "function_call",
                        "id": item_id(seed, index, "fc_", 48),
                        "call_id": call_id,
                        "name": names[0],
                        "arguments": json.dumps(call["arguments"]),
                        "status": "completed",
                    }
                elif "custom_tool_call" in step:
                    call = step["custom_tool_call"]
                    item = {
                        "type": "custom_tool_call",
                        "id": item_id(seed, index, "ctc_", 50),
                        "call_id": call_id,
                        "name": call["name"],
                        "input": call["input"],
                        "status": "completed",
                    }
                else:
                    item = {
                        "type": "message",
                        "id": item_id(seed, index, "msg_", 48),
                        "role": "assistant",
                        "status": "completed",
                        "content": [
                            {
                                "type": "output_text",
                                "text": step["message"],
                                "annotations": [],
                            }
                        ],
                    }
                events = [
                    {"type": "response.created", "response": {"id": response_id}},
                    {
                        "type": "response.output_item.added",
                        "output_index": 0,
                        "item": item,
                    },
                    {
                        "type": "response.output_item.done",
                        "output_index": 0,
                        "item": item,
                    },
                    {
                        "type": "response.completed",
                        "response": {
                            "id": response_id,
                            "usage": {
                                "input_tokens": 0,
                                "input_tokens_details": {"cached_tokens": 0},
                                "output_tokens": 0,
                                "output_tokens_details": {"reasoning_tokens": 0},
                                "total_tokens": 0,
                            },
                        },
                    },
                ]
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                for event in events:
                    self.wfile.write(sse(event))
                self.wfile.flush()

        return Handler


def provider_settings(base_url, name="mock"):
    """Codex -c settings that route model requests to the mock provider."""
    provider = (
        '{name="' + name + '", base_url="' + base_url + '", wire_api="responses", '
        "requires_openai_auth=false, supports_websockets=false, "
        "request_max_retries=0, stream_max_retries=0}"
    )
    return [f"model_providers.{name}={provider}", f'model_provider="{name}"']
