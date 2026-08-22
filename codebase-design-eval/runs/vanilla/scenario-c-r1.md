**1. Recommendation**

The current architecture should remain unchanged.

The deep module is [`campaign.rule_parser.parse_rules`](<../../fixtures/c-testing-trap/campaign/rule_parser.py:35>). [`CampaignEngine.discount_percent`](<../../fixtures/c-testing-trap/campaign/engine.py:5>) and [`validate_for_authoring`](<../../fixtures/c-testing-trap/campaign/validator.py:4>) are appropriate thin adapters for two different callers.

The smallest coherent change is test-only: keep the parser and checkout tests, and replace the validator test with a single adapter-contract smoke test so the suite stops duplicating parser-owned diagnostics.

**2. Evidence**

[`parse_rules`](<../../fixtures/c-testing-trap/campaign/rule_parser.py:35>) has a small interface but hides substantial behavior: escape handling in [`_split_unescaped`](<../../fixtures/c-testing-trap/campaign/rule_parser.py:14>), Unicode segment preservation, duplicate resolution, integer parsing, bounds checking, and precise `RuleSyntaxError` failures. That is a deep module by the skill’s definition.

[`CampaignEngine.discount_percent`](<../../fixtures/c-testing-trap/campaign/engine.py:5>) is intentionally thin: parse, select matching segment, default to `0`. [`validate_for_authoring`](<../../fixtures/c-testing-trap/campaign/validator.py:4>) is also thin: catch `RuleSyntaxError`, return `list[str]`. Those are shallow adapters, not competing modules.

The README explicitly says the rule language’s edge behavior is user-visible and that parser tests are intentional, not accidental ([`README.md`](<../../fixtures/c-testing-trap/README.md:3>)).

The demonstrated test problem is narrower: [`tests/test_validator.py`](<../../fixtures/c-testing-trap/tests/test_validator.py:7>) reasserts a specific parser error message through the validator adapter, so parser-diagnostic refactors will cause duplicate churn without adding much new coverage.

**3. Keep**

Keep [`campaign.rule_parser.parse_rules`](<../../fixtures/c-testing-trap/campaign/rule_parser.py:35>) as the main seam.

Keep [`tests/test_rule_parser.py`](<../../fixtures/c-testing-trap/tests/test_rule_parser.py:6>). These tests protect interface-level invariants that are directly user-visible: Unicode, escaping, duplicate semantics, and precise syntax failures.

Keep [`tests/test_campaign_engine.py`](<../../fixtures/c-testing-trap/tests/test_campaign_engine.py:6>). It protects the actual checkout contract: matching segment applies, missing segment yields `0`.

Keep the thin adapters themselves. They give two caller-specific interfaces over one deep implementation, which is a reasonable seam placement here.

**4. Change**

Replace [`tests/test_validator.py`](<../../fixtures/c-testing-trap/tests/test_validator.py:6>) with one adapter-level contract test that covers:
- invalid input returns one human-readable error string
- valid input returns `[]`

Reason: the validator’s unique behavior is error translation, not grammar ownership. Grammar edge cases belong in parser tests, not duplicated through the adapter.

Do not move parser edge-case tests into `CampaignEngine` tests. That would test past the wrong interface and raise refactor cost.

No production-code restructuring is demonstrated as necessary. A compiled-rules module or caching layer would be a preference unless repeated parsing becomes a measured problem.

**5. Test impact**

Keep:
- [`tests/test_rule_parser.py`](<../../fixtures/c-testing-trap/tests/test_rule_parser.py:6>)
- [`tests/test_campaign_engine.py`](<../../fixtures/c-testing-trap/tests/test_campaign_engine.py:6>)

Replace:
- [`tests/test_validator.py`](<../../fixtures/c-testing-trap/tests/test_validator.py:6>) with a smaller adapter-contract test

Delete:
- no parser or engine tests should be deleted

Move:
- no tests should be moved across seams

Observed runner note: `python3 -m unittest discover -s tests -v` passed from the fixture root on August 22, 2026. Repo-root discovery with `-t` failed under Python 3.14 because `tests/` is not importable; that is a harness issue, not an architecture issue.

**6. Terminology and authority**

Module: [`campaign.rule_parser.parse_rules`](<../../fixtures/c-testing-trap/campaign/rule_parser.py:35>)

Interface: `parse_rules(text) -> tuple[Rule, ...]` plus its invariants and `RuleSyntaxError` error modes

Seam: the parser function used by both checkout and authoring flows

Adapters: [`CampaignEngine.discount_percent`](<../../fixtures/c-testing-trap/campaign/engine.py:5>) and [`validate_for_authoring`](<../../fixtures/c-testing-trap/campaign/validator.py:4>)

Authority: this review follows the unmodified required skill files and is based only on the observed target README, source, and tests.

**7. Confidence and limitations**

Confidence is high because the target is small and the seam is explicit.

Limitations:
- read-only review; no change was prototyped
- no inspection outside the target beyond the required skill files
- performance concerns around reparsing in `CampaignEngine` are only speculative, not demonstrated by this fixture

The practical next step is to leave the production architecture alone and tighten only the validator test so the suite stays aligned with the real seam.