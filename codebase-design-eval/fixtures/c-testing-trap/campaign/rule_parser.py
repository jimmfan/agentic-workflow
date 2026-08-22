from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    segment: str
    percent: int


class RuleSyntaxError(ValueError):
    pass


def _split_unescaped(text: str, delimiter: str) -> list[str]:
    parts: list[str] = []
    current: list[str] = []
    escaped = False
    for character in text:
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == delimiter:
            parts.append("".join(current))
            current = []
        else:
            current.append(character)
    if escaped:
        raise RuleSyntaxError("dangling escape")
    parts.append("".join(current))
    return parts


def parse_rules(text: str) -> tuple[Rule, ...]:
    if not text.strip():
        return ()
    by_segment: dict[str, Rule] = {}
    for raw_rule in _split_unescaped(text, ";"):
        fields = _split_unescaped(raw_rule, ":")
        if len(fields) != 2 or not fields[0]:
            raise RuleSyntaxError(f"invalid rule: {raw_rule!r}")
        try:
            percent = int(fields[1])
        except ValueError as error:
            raise RuleSyntaxError(f"invalid percentage: {fields[1]!r}") from error
        if not 0 <= percent <= 100:
            raise RuleSyntaxError("percentage must be between 0 and 100")
        by_segment[fields[0]] = Rule(fields[0], percent)
    return tuple(by_segment.values())
