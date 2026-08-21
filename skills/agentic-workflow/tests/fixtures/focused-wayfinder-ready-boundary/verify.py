from delivery import serialize_notification


def main() -> int:
    return 0 if serialize_notification({"b": 2, "a": 1}) == '{"a":1,"b":2}' else 1


if __name__ == "__main__":
    raise SystemExit(main())
