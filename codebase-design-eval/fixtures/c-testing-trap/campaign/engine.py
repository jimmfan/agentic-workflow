from .rule_parser import parse_rules


class CampaignEngine:
    def discount_percent(self, rules_text: str, customer_segment: str) -> int:
        rules = parse_rules(rules_text)
        return next(
            (rule.percent for rule in rules if rule.segment == customer_segment),
            0,
        )
