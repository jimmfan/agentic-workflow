import unittest

from checkout.approval_policy import ApprovalPolicy
from checkout.checkout_plan import CheckoutPlanner
from checkout.stock_ledger import StockLedger


class CheckoutPlannerTests(unittest.TestCase):
    def test_rejects_before_allocating(self) -> None:
        planner = CheckoutPlanner(ApprovalPolicy(), StockLedger())
        plan = planner.plan("restricted", 30, 4, 10, 3)
        self.assertEqual((plan.accepted, plan.explanation_code, plan.allocated), (False, "JURISDICTION_BLOCKED", 0))

    def test_applies_inventory_cap(self) -> None:
        planner = CheckoutPlanner(ApprovalPolicy(), StockLedger())
        plan = planner.plan("open", 30, 5, 9, 2)
        self.assertEqual((plan.allocated, plan.backordered), (2, 3))


if __name__ == "__main__":
    unittest.main()
