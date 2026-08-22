**1. Recommendation**

Collapse the internal quote-calculation layers into a single in-process module behind `QuoteApplication.execute`, and keep that public seam unchanged. The minimal target shape is `QuoteApplication.execute(prices, discount_percent) -> {"total": int}` with the clamp and arithmetic implemented directly there or in one private helper inside [quote/application.py](../../fixtures/a-overengineered/quote/application.py:8).

The current architecture should not remain unchanged. The extra seams are not justified by observed variation, ownership, failure isolation, or test leverage.

**2. Evidence**

- The fixture authority says this package is intentionally small, has one caller, one implementation per class, no remote dependency, no persistence, no plugin plan, and only requires `QuoteApplication.execute` as public behavior: [README.md](../../fixtures/a-overengineered/README.md:3).
- The only observed caller is the test suite, and it calls `QuoteApplication.execute` directly: [tests/test_quote.py](../../fixtures/a-overengineered/tests/test_quote.py:6).
- `QuoteUseCase.run` is a pure pass-through to `QuoteDomainService.quote`: [quote/use_case.py](../../fixtures/a-overengineered/quote/use_case.py:5).
- `QuoteDomainService.quote` only wraps `QuoteSubtotalCalculator.calculate` in `{"total": ...}`: [quote/domain_service.py](../../fixtures/a-overengineered/quote/domain_service.py:5).
- `QuoteSubtotalCalculator.calculate` contains the only real pricing rule: subtotal plus percentage discount arithmetic: [quote/calculator.py](../../fixtures/a-overengineered/quote/calculator.py:4).
- `QuoteRequestNormalizer.normalize` contains the only input rule, clamping `discount_percent` to `0..100`, and redundantly re-tuples `prices` even though `QuoteApplication.execute` already created a tuple: [quote/application.py](../../fixtures/a-overengineered/quote/application.py:13), [quote/normalizer.py](../../fixtures/a-overengineered/quote/normalizer.py:4).

Demonstrated problem: shallow pass-through modules add navigation cost and scatter one small behavior across five files.
Preference only: whether the remaining implementation uses an internal `QuoteRequest` dataclass or plain locals.

**3. Keep**

- Keep `QuoteApplication.execute` as the single external seam, because that is the only behavior the tests and README treat as authoritative: [quote/application.py](../../fixtures/a-overengineered/quote/application.py:13).
- Keep the tested product behavior: apply percentage discount and clamp oversized discounts so `140` yields `{"total": 0}`: [tests/test_quote.py](../../fixtures/a-overengineered/tests/test_quote.py:7).

**4. Change**

- Merge the logic from `QuoteRequestNormalizer.normalize`, `QuoteUseCase.run`, `QuoteDomainService.quote`, and `QuoteSubtotalCalculator.calculate` into [quote/application.py](../../fixtures/a-overengineered/quote/application.py:8).
- Remove [quote/use_case.py](../../fixtures/a-overengineered/quote/use_case.py:5), [quote/domain_service.py](../../fixtures/a-overengineered/quote/domain_service.py:5), [quote/calculator.py](../../fixtures/a-overengineered/quote/calculator.py:4), and [quote/normalizer.py](../../fixtures/a-overengineered/quote/normalizer.py:4) unless a new nontrivial seam appears.
- Main rejected alternative: keep `QuoteSubtotalCalculator` as a separate seam and only collapse the other layers. I do not recommend it here because there is still one caller, one implementation, and no independent evolution point around the arithmetic.

**5. Test impact**

- Existing tests should remain interface tests against `QuoteApplication.execute`; they already cover the required product behavior: [tests/test_quote.py](../../fixtures/a-overengineered/tests/test_quote.py:6).
- No new lower-level tests are justified after the collapse; they would reintroduce the same shallow structure in test form.
- If preserving current lower-bound clamp behavior matters, add an interface test for a negative discount. That behavior exists in code today but is not required by the current tests: [quote/normalizer.py](../../fixtures/a-overengineered/quote/normalizer.py:8).

**6. Terminology and authority**

- In the candidate method’s terms, this is an in-process module with one real seam: `QuoteApplication.execute`.
- The authoritative project language is “quote total”, “prices”, and “discount percent”; I am using “module”, “seam”, and “depth” only as analysis vocabulary.
- The strongest authority is the fixture README plus the tests, both of which explicitly de-authorize the current internal layering as a requirement: [README.md](../../fixtures/a-overengineered/README.md:4), [tests/test_quote.py](../../fixtures/a-overengineered/tests/test_quote.py:6).

**7. Confidence and limitations**

High confidence. The target is small, the public behavior is explicitly documented, and the current seams are directly inspectable as pass-through code.

Limitations: this was a read-only review. I did not run tests or inspect broader integration points, and I am not assuming future expansion requirements that are not evidenced in this fixture.