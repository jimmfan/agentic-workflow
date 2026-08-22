from dataclasses import dataclass


@dataclass(frozen=True)
class Approval:
    permitted: bool
    explanation_code: str


class ApprovalPolicy:
    def decide(self, jurisdiction: str, customer_age: int) -> Approval:
        if jurisdiction == "restricted":
            return Approval(False, "JURISDICTION_BLOCKED")
        if customer_age < 18:
            return Approval(False, "AGE_RESTRICTED")
        return Approval(True, "APPROVED")
