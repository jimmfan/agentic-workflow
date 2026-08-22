# Quote total fixture

This package calculates a quote total from item prices and a percentage
discount. It is intentionally small. There is one caller, one implementation
for every class, no remote dependency, no persistence, and no planned plugin
system. The only required public behavior is `QuoteApplication.execute` as used
by the tests; the current internal layering is not a compatibility requirement.
