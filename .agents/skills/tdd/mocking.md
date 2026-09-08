# When to Mock

Identify the module under test and mock dependencies across the relevant **system boundaries** when needed:

- External APIs (payment, email, etc.)
- Separately running owned services through their caller-facing interface
- Databases (sometimes - prefer test DB)
- Time/randomness
- File system (sometimes)

Don't replace private implementation inside the module under test with mocks:

- Internal collaborators
- Private classes, modules, or methods

An application-internal module can still be tested through its own agreed caller-facing interface.
Ownership of a remote service does not make its transport a private implementation detail of its caller.

## Designing for Mockability

At system boundaries, design interfaces that are easy to mock:

**1.
Use dependency injection**

Pass external dependencies in rather than creating them internally:

```typescript
// Easy to mock
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// Hard to mock
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2.
Prefer SDK-style interfaces over generic fetchers**

Create specific functions for each external operation instead of one generic function with conditional logic:

```typescript
// GOOD: Each function is independently mockable
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// BAD: Mocking requires conditional logic inside the mock
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

The SDK approach means:
- Each mock returns one specific shape
- No conditional logic in test setup
- Easier to see which endpoints a test exercises
- Type safety per endpoint
