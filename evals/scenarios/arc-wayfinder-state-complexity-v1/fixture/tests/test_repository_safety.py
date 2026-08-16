from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
TERRAFORM = "\n".join(
    path.read_text(encoding="utf-8")
    for path in sorted((ROOT / "terraform").glob("*.tf"))
)


class RepositorySafetyTests(unittest.TestCase):
    def test_externally_managed_cluster_is_not_recreated(self) -> None:
        self.assertIsNone(
            re.search(r'resource\s+"aws_eks_cluster"', TERRAFORM, re.IGNORECASE)
        )

    def test_public_ip_assignment_is_not_enabled(self) -> None:
        self.assertIsNone(
            re.search(
                r"(?:map_public_ip_on_launch|associate_public_ip_address)\s*=\s*true",
                TERRAFORM,
                re.IGNORECASE,
            )
        )

    def test_legacy_security_group_is_not_managed(self) -> None:
        self.assertNotIn("sg-0abc1234def567890", TERRAFORM)

    def test_karpenter_is_not_introduced(self) -> None:
        self.assertIsNone(re.search(r"karpenter\.sh|helm_release.*karpenter", TERRAFORM, re.IGNORECASE | re.DOTALL))

    def test_ami_is_not_hard_coded(self) -> None:
        self.assertIsNone(re.search(r"\bami-[0-9a-f]{8,17}\b", TERRAFORM, re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
