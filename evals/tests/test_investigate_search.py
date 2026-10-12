"""Deterministic controls for the investigate-before-uncertainty search campaign.

These exercise the frozen corpus ranking, the MCP server protocol, the catalog
and request audits, and the adapter's unchanged default settings. They run no
Codex process and no model.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT / "evals/investigate-before-uncertainty-search"
sys.path.insert(0, str(SUITE))

import campaign  # noqa: E402
import web_server  # noqa: E402


def load_adapter():
    spec = importlib.util.spec_from_file_location(
        "codex_subject", ROOT / "evals/remaining-audit-behavior/codex_subject.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def urls(query):
    return [page["url"] for page in web_server.search(web_server.load_pages(), query)]


class CorpusRankingTests(unittest.TestCase):
    queries = json.loads((SUITE / "queries.json").read_text())

    def test_each_targeted_query_returns_report_b_in_the_top_three(self):
        for query in self.queries["targeted_queries"]:
            with self.subTest(query=query):
                self.assertIn(self.queries["report_b_url"], urls(query))

    def test_bare_race_name_queries_do_not_return_report_b(self):
        for query in self.queries["bare_race_name_queries"]:
            with self.subTest(query=query):
                self.assertNotIn(self.queries["report_b_url"], urls(query))

    def test_fixed_first_turn_query_returns_no_participant_report(self):
        turn1 = json.loads((SUITE / "turn1.json").read_text())
        call = turn1["steps"][0]["custom_tool_call"]["input"]
        query = call.split('query:"', 1)[1].split('"', 1)[0]
        returned = urls(query)
        self.assertTrue(returned[0].endswith("/race-morning"))
        self.assertFalse([url for url in returned if "runnerforum" in url])

    def test_no_page_measures_a_current_gate_d_wave_3_wait(self):
        for page in web_server.load_pages():
            text = page["title"] + page["text"]
            with self.subTest(url=page["url"]):
                self.assertFalse(
                    "Wave 3" in text and "minutes" in text and "2026" in text
                )


class ServerProtocolTests(unittest.TestCase):
    def exchange(self, *messages):
        lines = "".join(json.dumps(message) + "\n" for message in messages)
        completed = subprocess.run(
            [sys.executable, str(campaign.SERVER)],
            input=lines,
            text=True,
            capture_output=True,
            timeout=30,
            check=True,
        )
        return [json.loads(line) for line in completed.stdout.splitlines()]

    def test_lists_only_search_with_the_frozen_description(self):
        replies = self.exchange(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2025-06-18"},
            },
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        )
        self.assertEqual(replies[0]["result"]["protocolVersion"], "2025-06-18")
        tools = replies[1]["result"]["tools"]
        self.assertEqual([tool["name"] for tool in tools], ["search"])
        self.assertEqual(tools[0]["description"], web_server.DESCRIPTION)

    def test_search_returns_full_pages_and_rejects_bad_calls(self):
        replies = self.exchange(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "search",
                    "arguments": {"query": "Gate D security line wait Quillmere"},
                },
            },
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": "other", "arguments": {}},
            },
            {"jsonrpc": "2.0", "id": 3, "method": "resources/list"},
        )
        text = replies[0]["result"]["content"][0]["text"]
        self.assertIn("I waited roughly 35 minutes to get in", text)
        self.assertTrue(replies[1]["result"]["isError"])
        self.assertEqual(replies[2]["error"]["code"], -32601)


class CatalogAndRequestAuditTests(unittest.TestCase):
    shipped = json.dumps(
        {
            "models": [
                {
                    "slug": "gpt-6.1-sol",
                    "supports_search_tool": True,
                    "tool_mode": "code_mode_only",
                },
                {"slug": "other"},
            ]
        }
    )

    def test_override_flips_only_the_frozen_field(self):
        override = campaign.override_catalog(self.shipped)
        self.assertEqual(
            campaign.catalog_audit(self.shipped, override),
            ["/models/0/supports_search_tool"],
        )

    def test_audit_rejects_any_additional_catalog_change(self):
        changed = json.loads(campaign.override_catalog(self.shipped))
        changed["models"][0]["tool_mode"] = "direct"
        with self.assertRaises(ValueError):
            campaign.catalog_audit(self.shipped, json.dumps(changed))

    def body(self, extra_developer="", path="/private/tmp/kx/w/abc/work"):
        description = (
            "Run JavaScript code\n\n### `exec_command`\nRuns a command.\n\n"
            f"### `{campaign.MODEL_VISIBLE_TOOL}`\n{web_server.DESCRIPTION}\n"
        )
        return {
            "input": [
                {
                    "type": "additional_tools",
                    "role": "developer",
                    "tools": [
                        {
                            "type": "namespace",
                            "name": "functions",
                            "tools": [
                                {
                                    "type": "custom",
                                    "name": "exec",
                                    "description": description,
                                }
                            ],
                        }
                    ],
                },
                {
                    "type": "message",
                    "role": "developer",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Skill root " + path + extra_developer,
                        }
                    ],
                },
                {
                    "type": "message",
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "# AGENTS.md instructions\nPolicy text.",
                        }
                    ],
                },
            ]
        }

    def test_clean_request_passes(self):
        self.assertEqual(campaign.audit_request(self.body(), "Policy text."), [])

    def test_notice_leaking_path_and_missing_policy_fail(self):
        self.assertTrue(
            campaign.audit_request(self.body(" Use mcp__web__search."), "Policy text.")
        )
        self.assertTrue(
            campaign.audit_request(
                self.body(path="/Users/x/agentic-workflow/evals/artifacts/run"),
                "Policy text.",
            )
        )
        self.assertTrue(campaign.audit_request(self.body(), "Different policy."))

    def test_exec_item_checker_accepts_model_made_formats_only(self):
        item = {
            "type": "custom_tool_call",
            "id": "ctc_" + "a" * 50,
            "status": "completed",
            "call_id": "call_" + "b" * 32,
            "name": "exec",
            "input": 'text(await tools.mcp__web__search({query:"x"}));\n',
        }
        self.assertEqual(campaign.exec_item_failures(item), [])
        self.assertEqual(
            campaign.exec_item_failures(
                {**item, "call_id": "call_fOelxD596IurZXhv9VQvNtP1"}
            ),
            [],
        )
        self.assertTrue(campaign.exec_item_failures({**item, "id": "ctc_mock_0"}))
        self.assertTrue(campaign.exec_item_failures({**item, "input": "search('x')"}))


class AdapterDefaultTests(unittest.TestCase):
    def test_default_settings_match_the_pre_campaign_adapter(self):
        adapter = load_adapter()
        settings = adapter.subject_settings(
            "gpt-5.6-sol", False, {":root": "deny"}, {"PATH": "/bin"}
        )
        self.assertEqual(
            settings,
            [
                'model="gpt-5.6-sol"',
                'model_reasoning_effort="medium"',
                'approval_policy="never"',
                'default_permissions="audit"',
                'permissions.audit.filesystem={":root"="deny"}',
                "permissions.audit.network.enabled=false",
                'web_search="disabled"',
                "features.apps=false",
                "features.plugins=false",
                "features.memories=false",
                "features.multi_agent=true",
                "agents.max_threads=3",
                "features.shell_snapshot=false",
                'shell_environment_policy.inherit="none"',
                'shell_environment_policy.set={PATH="/bin"}',
                "allow_login_shell=false",
                'model_provider="openai"',
                "project_doc_max_bytes=65536",
            ],
        )
        self.assertIsNone(adapter.campaign)


if __name__ == "__main__":
    unittest.main()
