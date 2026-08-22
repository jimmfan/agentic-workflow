**1. Recommendation**

Keep the current production architecture unchanged. The smallest coherent change is in the tests: keep the parser and engine test layers, but replace the validator test with a contract-focused test for `validate_for_authoring`.

The main rejected alternative is merging [engine.py](../../fixtures/c-testing-trap/campaign/engine.py:1), [rule_parser.py](../../fixtures/c-testing-trap/campaign/rule_parser.py:1), and [validator.py](../../fixtures/c-testing-trap/campaign/validator.py:1). I do not see evidence that this would improve leverage or locality.

**2. Evidence**

- The deep module is [`parse_rules`](../../fixtures/c-testing-trap/campaign/rule_parser.py:35). It hides escaping, syntax splitting, percent parsing, bounds checks, and duplicate handling behind one small interface. `_split_unescaped` at [rule_parser.py:14](../../fixtures/c-testing-trap/campaign/rule_parser.py:14) concentrates the grammar hazard.
- [`CampaignEngine.discount_percent`](../../fixtures/c-testing-trap/campaign/engine.py:5) is intentionally thin: parse rules, select matching segment, default to `0`.
- [`validate_for_authoring`](../../fixtures/c-testing-trap/campaign/validator.py:4) is also intentionally thin: convert `RuleSyntaxError` into `list[str]`.
- The README explicitly justifies this split: checkout behavior is protected at the engine layer, while parser tests protect rule-language edge behavior that would be “cumbersome and less diagnostic” through checkout alone [README.md:3](../../fixtures/c-testing-trap/README.md:3).

**3. Keep**

- Keep `campaign.rule_parser.parse_rules` as the authoritative seam for the rule language.
- Keep [`tests/test_rule_parser.py`](../../fixtures/c-testing-trap/tests/test_rule_parser.py:1). These tests cover documented invariants: Unicode, escaped delimiters, duplicate handling, dangling escapes, and percent bounds.
- Keep [`tests/test_campaign_engine.py`](../../fixtures/c-testing-trap/tests/test_campaign_engine.py:1). It protects the checkout-facing behavior of `CampaignEngine`.

**4. Change**

- Demonstrated problem: [`tests/test_validator.py::test_reports_parser_error`](../../fixtures/c-testing-trap/tests/test_validator.py:7) mostly reasserts parser wording already owned by `parse_rules`. That increases refactor cost for parser diagnostics without adding much new behavior coverage.
- Replace it with validator-interface tests:
  - valid input returns `[]`
  - invalid input returns one human-readable error
- If exact authoring error strings are product requirements, document that in [README.md](../../fixtures/c-testing-trap/README.md:1) and then keep exact-string assertions. Right now that requirement is not documented.

**5. Test impact**

- Keep: `tests/test_campaign_engine.py`
- Keep: `tests/test_rule_parser.py`
- Replace: `tests/test_validator.py`
- Do not move parser edge-case tests up into engine tests. That would make failures less diagnostic and would couple checkout tests to parser internals the README deliberately isolates.
- Do not delete validator coverage entirely. `validate_for_authoring` is a caller-facing interface, so it still deserves a small contract test.

**6. Terminology and authority**

- Using the candidate method’s terms: `parse_rules` is the deep module; `CampaignEngine` and `validate_for_authoring` are thin adapters at separate caller seams.
- Canonical project terms should remain the README’s terms: “campaign rules,” “checkout,” and “authoring validator” [README.md:3](../../fixtures/c-testing-trap/README.md:3).
- Authority for this review is limited to the fixture README, source files, and tests named above.

**7. Confidence and limitations**

Moderate-high confidence. I read the requested candidate-method files plus the target README, three source modules, and three test files. I did not run tests or inspect external callers, so I am not making performance, packaging, or public-API recommendations beyond what the source demonstrates.

The practical next step is to leave the production modules alone and narrow the validator tests to the validator’s own contract.