import os
import yaml
from typing import List
from .models import Config, FrameworkConfig, TestCaseConfig


class ConfigLoader:

    def __init__(self, config_dir: str = "."):

        self.config_dir = config_dir
        self.framework_config: FrameworkConfig = None
        self.testcase_configs: List[TestCaseConfig] = []

    def load_all(self) -> Config:

        self.load_global_config()
        self.load_testcases()

        config = Config(
            framework=self.framework_config, testcases=self.testcase_configs
        )

        config.validate()

        return config

    def load_global_config(self, filename: str = "config.yaml") -> FrameworkConfig:

        config_path = os.path.join(self.config_dir, filename)

        if not os.path.exists(config_path):
            print(
                f"[Warning] Global config file not found: {config_path}, using defaults"
            )
            self.framework_config = FrameworkConfig()
            return self.framework_config

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                framework_data = data.get("framework", {}) if data else {}
                self.framework_config = FrameworkConfig.from_dict(framework_data)
                return self.framework_config
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Config file format error: {config_path}\n{str(e)}")

    def load_testcases(self, filename: str = "testcases.yaml") -> List[TestCaseConfig]:
        config_path = os.path.join(self.config_dir, filename)

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Test case config file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

                if not data:
                    raise ValueError("Test case config file is empty")

                if "testcases" not in data:
                    raise ValueError("Test case config file missing 'testcases' field")

                testcases_data = data["testcases"]

                if not isinstance(testcases_data, list):
                    raise ValueError("testcases must be a list")

                self.testcase_configs = []
                for idx, testcase_dict in enumerate(testcases_data):
                    if not isinstance(testcase_dict, dict):
                        raise ValueError(f"Test case #{idx} must be a dict")

                    required_fields = ["name", "path", "commands"]
                    for field in required_fields:
                        if field not in testcase_dict:
                            raise ValueError(
                                f"Test case #{idx} missing required field: {field}"
                            )

                    testcase_config = TestCaseConfig.from_dict(testcase_dict)
                    testcase_config.validate()
                    self.testcase_configs.append(testcase_config)

                return self.testcase_configs

        except yaml.YAMLError as e:
            raise yaml.YAMLError(
                f"Test case config file format error: {config_path}\n{str(e)}"
            )

    def get_framework_config(self) -> FrameworkConfig:
        return self.framework_config
