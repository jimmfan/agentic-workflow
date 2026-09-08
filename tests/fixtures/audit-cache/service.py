class Store:
    def __init__(self, totals):
        self.totals = dict(totals)
        self.reads = 0

    def total(self, account):
        self.reads += 1
        return self.totals[account]


class Reports:
    def __init__(self, store, ttl=30):
        self.store = store
        self.ttl = ttl
        self.cached = None

    def total(self, account, now):
        if self.cached is not None:
            saved_at, value = self.cached
            if now - saved_at < self.ttl:
                return value
        value = self.store.total(account)
        self.cached = (now, value)
        return value
