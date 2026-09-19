"""Exercise real SIGINT in a disposable harness process, never the test runner."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest

from _behavior_test_support import behavior


@unittest.skipUnless(os.name == "posix", "requires POSIX SIGINT delivery")
class BehaviorInterruptionTests(unittest.TestCase):
    def test_manual_interruption_retains_observations_before_default_cleanup(self):
        for mutation, stage in (
            (True, "subject"),
            (False, "subject"),
            (True, "verifier"),
            (False, "verifier"),
            (True, "snapshot"),
            (False, "snapshot"),
            (True, "evaluation"),
            (False, "evaluation"),
        ):
            with (
                self.subTest(mutation=mutation, stage=stage),
                tempfile.TemporaryDirectory() as temp,
            ):
                root = Path(temp)
                subject = root / "subject.py"
                subject.write_text(
                    textwrap.dedent("""
                    import json
                    import os
                    from pathlib import Path
                    import signal
                    import subprocess
                    import sys
                    import time

                    if Path('slug.py').exists():
                        if sys.argv[1] == 'mutate' and sys.argv[2] != 'verifier':
                            Path('README.md').write_text('protected content lost')
                        Path('.behavior-evidence/report.json').write_text(json.dumps({
                            'schema_version': 1, 'status': 'blocked',
                            'summary': 'interrupted subject evidence', 'pid': os.getpid(),
                        }))
                        print('available response', flush=True)
                        print('available diagnostic', file=sys.stderr, flush=True)
                        if sys.argv[2] == 'verifier':
                            mutation = '    open("README.md", "w").write("protected content lost")\\n' if sys.argv[1] == 'mutate' else ''
                            Path('slug.py').write_text('def slugify(value):\\n    import os, signal, time\\n' + mutation + '    print("verifier started", flush=True)\\n    os.kill(os.getppid(), signal.SIGINT)\\n    time.sleep(30)\\n')
                        elif sys.argv[2] == 'subject':
                            os.kill(os.getppid(), signal.SIGINT)
                            time.sleep(30)
                    else:
                        Path('app.py').write_text('def greeting(): return "hello, world!"\\n')
                        subprocess.run([sys.executable, 'verify.py'], check=True, capture_output=True)
                        Path('.behavior-evidence/report.json').write_text(json.dumps({
                            'schema_version': 1, 'status': 'success',
                        }))
                        print('Done. [route: router → direct]')
                    """)
                )
                harness = behavior.TEST_ROOT / "behavior.py"
                if stage in ("snapshot", "evaluation"):
                    # Inject a real signal at the collection boundary in the
                    # disposable child, while checking only its public report.
                    harness = root / "harness.py"
                    harness.write_text(
                        f"import sys\nsys.path.insert(0, {str(behavior.TEST_ROOT)!r})\n"
                        "from _behavior_test_support import behavior\n"
                        "import os, signal\n"
                        f"phase = {'snapshot' if stage == 'snapshot' else 'evaluate'!r}\n"
                        "original = getattr(behavior, phase)\nsent = False\n"
                        "def interrupt_once(value):\n"
                        "    global sent\n"
                        "    workspace = value if phase == 'snapshot' else value.workspace\n"
                        "    if not sent and (workspace / 'slug.py').exists() and (workspace / '.behavior-evidence/report.json').exists():\n"
                        "        sent = True\n        os.kill(os.getpid(), signal.SIGINT)\n"
                        "    return original(value)\n"
                        "setattr(behavior, phase, interrupt_once)\n"
                        "raise SystemExit(behavior.main(sys.argv[1:]))\n"
                    )
                output = root / "result.json"
                result = subprocess.run(
                    [
                        behavior.sys.executable,
                        str(harness),
                        "live",
                        "--agent-command-json",
                        json.dumps(
                            [
                                behavior.sys.executable,
                                str(subject),
                                "mutate" if mutation else "unchanged",
                                stage,
                            ]
                        ),
                        "--scenario",
                        "objective-clear-request",
                        "--scenario",
                        "verification-failure-recovery",
                        "--scenario",
                        "wayfinder-unordered-dependencies-no-critical-path",
                        "--output",
                        str(output),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=45,
                    start_new_session=True,
                )
                runs = json.loads(output.read_text())["runs"]
                self.assertEqual(
                    [run["scenario"] for run in runs],
                    ["objective-clear-request", "verification-failure-recovery"],
                )
                self.assertEqual(runs[0]["verdict"], "PASS")
                interrupted = runs[1]
                self.assertEqual(interrupted["execution_status"], "interrupted")
                checks = {item["name"]: item for item in interrupted["checks"]}
                self.assertIn("expect:project_state_preserved", checks)
                self.assertEqual(result.returncode, 1 if mutation else 2, result.stderr)
                self.assertEqual(
                    interrupted["verdict"], "FAIL" if mutation else "INCONCLUSIVE"
                )
                self.assertIs(
                    checks["expect:project_state_preserved"]["passed"],
                    False if mutation else None,
                )
                self.assertIsNone(checks["expect:task_completed"]["passed"])
                self.assertEqual("README.md" in interrupted["modified"], mutation)
                self.assertIn("available response", interrupted["partial_stdout"])
                self.assertIn("available diagnostic", interrupted["partial_stderr"])
                self.assertEqual(
                    interrupted["report"]["summary"], "interrupted subject evidence"
                )
                if stage == "verifier":
                    self.assertEqual(
                        interrupted["outcome_verification"]["execution_status"],
                        "interrupted",
                    )
                    self.assertIn(
                        "verifier started",
                        interrupted["outcome_verification"]["stdout"],
                    )
                with self.assertRaises(ProcessLookupError):
                    os.kill(interrupted["report"]["pid"], 0)
                self.assertTrue(
                    all(not Path(run["workspace"]).exists() for run in runs)
                )


if __name__ == "__main__":
    unittest.main()
