from .rule_parser import RuleSyntaxError, parse_rules


def validate_for_authoring(rules_text: str) -> list[str]:
    try:
        parse_rules(rules_text)
    except RuleSyntaxError as error:
        return [str(error)]
    return []
