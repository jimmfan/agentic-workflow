**1. Recommendation**

Keep the current architecture unchanged. The meaningful module here is [`parse_rules`](<../../fixtures/c-testing-trap/campaign/rule_parser.py:35>), with [`CampaignEngine.discount_percent`](<../../fixtures/c-testing-trap/campaign/engine.py:5>) and [`validate_for_authoring`](<../../fixtures/c-testing-trap/campaign/validator.py:4>) as small caller-facing seams for checkout and authoring. The smallest coherent change is to fix the test harness/package layout so tests run without `PYTHONPATH=.` workarounds.

**2. Evidence**

- [`README.md`](<../../fixtures/c-testing-trap/README.md:3>) explicitly says the rule language has user-visible edge behavior and that parser tests protect grammar and validation behavior that would be cumbersome at the checkout layer.
- [`campaign/rule_parser.py`](<../../fixtures/c-testing-trap/campaign/rule_parser.py:14>) contains the concentrated behavior: escaping, duplicate resolution, numeric parsing, bounds checking, and precise `RuleSyntaxError` messages.
- [`campaign/engine.py`](<../../fixtures/c-testing-trap/campaign/engine.py:4>) and [`campaign/validator.py`](<../../fixtures/c-testing-trap/campaign/validator.py:4>) are thin, but they expose different behaviors to different callers, so deleting them would re-spread that knowledge into callers.
- Demonstrated problem: `python3 -m unittest discover ...` fails because `tests/` is not importable, and direct `python3 tests/test_*.py` fails with `ModuleNotFoundError: No module named 'campaign'`. The tests pass only with `PYTHONPATH=.`.

**3. Keep**

- Keep [`tests/test_rule_parser.py`](<../../fixtures/c-testing-trap/tests/test_rule_parser.py:6>). These tests protect the deep module’s grammar, invariants, and diagnostics. Replacing them with only engine tests would reduce diagnostic value and raise refactor cost.
- Keep [`tests/test_campaign_engine.py`](<../../fixtures/c-testing-trap/tests/test_campaign_engine.py:6>) as the checkout seam smoke tests.
- Keep [`tests/test_validator.py`](<../../fixtures/c-testing-trap/tests/test_validator.py:6>) at the authoring seam. It covers exception-to-message-list translation, which is behavior the parser tests do not assert.

**4. Change**

- Change the test packaging/running setup so the suite is runnable without environment-specific import hacks. That is a demonstrated defect in the current test strategy.
- Add one validator success-path test for `validate_for_authoring("loyal:10") == []`; the invalid path is covered, but the empty-error contract is currently inferred.
- Do not merge `engine.py`, `validator.py`, and `rule_parser.py` based on thinness alone. That would be a preference, not an evidence-backed improvement.

**5. Test impact**

- Delete none.
- Move none. The parser tests belong at the parser seam because they protect concentrated parsing behavior, not incidental internals.
- Replace none with higher-level tests; the current split is appropriate.
- Add only the missing harness/package fix and one validator success-path assertion.

**6. Terminology and authority**

Using the candidate method’s terms: this is an in-process design with one deep module, [`parse_rules`](<../../fixtures/c-testing-trap/campaign/rule_parser.py:35>), and two small external seams for distinct callers. No adapter layer is justified. I did not apply “design it twice” because this is not a consequential open interface choice; the current seam placement is already coherent, and the method explicitly allows a direct recommendation in that case.

**7. Confidence and limitations**

Confidence is high on the main recommendation because it is backed by the code, the README, and observed test-run behavior. Limitation: this review is intentionally bounded to the provided fixture, so I did not infer performance requirements or external integration needs that are not present in the repository.