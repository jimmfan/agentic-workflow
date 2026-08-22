# Campaign rule fixture

`CampaignEngine` evaluates campaign rules for checkout. `parse_rules` also
serves an authoring validator, so invalid rule text can be reported before a
campaign is activated.

The compact rule language has user-visible edge behavior: backslash escapes,
Unicode segment names, duplicate segments (last definition wins), percentage
bounds, and precise syntax errors. The high-level tests protect checkout
behavior. The parser tests protect grammar and validation behavior that would
be cumbersome and less diagnostic to express only through checkout.
