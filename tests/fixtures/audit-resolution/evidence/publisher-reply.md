# Publisher reply P-204

The Parcel publisher API owner confirms for v2 batch POST: a request key is scoped to an account and remains valid for 24 hours after first acceptance.
Repeating the key within one account returns the first accepted response even when the payload differs.
The same key in a different account creates an independent request.
This guarantee does not apply to v1.
This reply establishes protocol behavior only and makes no deployment decision.
