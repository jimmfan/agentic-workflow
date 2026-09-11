import json


def normalize_account(value):
    return value.strip().lower()


def summarize(source):
    totals = {}
    for line in source:
        if not line.strip():
            continue
        entry = json.loads(line)
        account = normalize_account(entry["account"])
        totals[account] = totals.get(account, 0) + entry["cents"]
    return totals
