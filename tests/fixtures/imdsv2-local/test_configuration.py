import json
from pathlib import Path
import unittest


class ConfigurationTests(unittest.TestCase):
    def test_metadata_endpoint_remains_available(self):
        config = json.loads(Path("main.tf.json").read_text())
        template = config["resource"]["aws_launch_template"]["application"]
        self.assertEqual(template["metadata_options"]["http_endpoint"], "enabled")


if __name__ == "__main__":
    unittest.main()
