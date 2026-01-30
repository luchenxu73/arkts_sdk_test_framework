"""Configuration data models"""

import os
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class BuildToolsConfig:

    ohpm_home: str
    hvigor_home: str
    deveco_sdk_home: str
    ohos_base_sdk_home: str
    node_home: Optional[str] = None
    java_home: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BuildToolsConfig":
        if not data:
            raise ValueError("build_tools configuration is required")

        required_fields = [
            "ohpm_home",
            "hvigor_home",
            "deveco_sdk_home",
            "ohos_base_sdk_home",
        ]
        missing_fields = [f for f in required_fields if not data.get(f)]
        if missing_fields:
            raise ValueError(
                f"Missing required build_tools fields: {', '.join(missing_fields)}"
            )

        return cls(
            ohpm_home=data["ohpm_home"],
            hvigor_home=data["hvigor_home"],
            deveco_sdk_home=data["deveco_sdk_home"],
            ohos_base_sdk_home=data["ohos_base_sdk_home"],
            node_home=data.get("node_home"),
            java_home=data.get("java_home"),
        )

    def validate(self):
        if not os.path.exists(self.ohpm_home):
            raise ValueError(f"OHPM home directory does not exist: {self.ohpm_home}")

        if not os.path.exists(self.hvigor_home):
            raise ValueError(
                f"Hvigor home directory does not exist: {self.hvigor_home}"
            )

        if not os.path.exists(self.deveco_sdk_home):
            raise ValueError(
                f"DevEco SDK home directory does not exist: {self.deveco_sdk_home}"
            )

        if not os.path.exists(self.ohos_base_sdk_home):
            raise ValueError(
                f"OHOS Base SDK home directory does not exist: {self.ohos_base_sdk_home}"
            )

        if self.node_home and not os.path.exists(self.node_home):
            raise ValueError(f"Node home directory does not exist: {self.node_home}")

        if self.java_home and not os.path.exists(self.java_home):
            raise ValueError(f"Java home directory does not exist: {self.java_home}")


@dataclass
class FrameworkConfig:

    build_tools: BuildToolsConfig
    default_timeout: int = 300
    output_dir: str = "./test_results"
    log_level: str = "INFO"
    retry_on_failure: int = 0

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FrameworkConfig":
        if not data:
            raise ValueError("framework configuration is required")

        build_tools_data = data.get("build_tools")
        if not build_tools_data:
            raise ValueError("build_tools configuration is required")

        build_tools = BuildToolsConfig.from_dict(build_tools_data)

        return cls(
            build_tools=build_tools,
            default_timeout=data.get("default_timeout", 300),
            output_dir=data.get("output_dir", "./test_results"),
            log_level=data.get("log_level", "INFO"),
            retry_on_failure=data.get("retry_on_failure", 0),
        )

    def validate(self):
        self.build_tools.validate()

        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(
                f"Invalid log level: {self.log_level}, "
                f"must be one of: {', '.join(valid_log_levels)}"
            )

        if self.default_timeout <= 0:
            raise ValueError(
                f"default_timeout must be greater than 0, current value: {self.default_timeout}"
            )

        if self.retry_on_failure < 0:
            raise ValueError(
                f"retry_on_failure cannot be negative, current value: {self.retry_on_failure}"
            )


@dataclass
class ArtifactsConfig:
    
    verify_files: List[str] = field(default_factory=list)
    action: List[List[str]] = field(default_factory=list)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArtifactsConfig":
        return cls(
            verify_files=data.get("verify_files", []),
            action=data.get("action", [])
        )
    
    def validate(self, testcase_name: str):
        if self.verify_files:
            if not isinstance(self.verify_files, list):
                raise ValueError(f"Test case '{testcase_name}' artifacts.verify_files must be a list")
            if not all(isinstance(f, str) for f in self.verify_files):
                raise ValueError(f"Test case '{testcase_name}' artifacts.verify_files must contain only strings")
        
        if self.action:
            if not isinstance(self.action, list):
                raise ValueError(f"Test case '{testcase_name}' artifacts.action must be a list")
            for idx, cmd in enumerate(self.action):
                if not isinstance(cmd, list):
                    raise ValueError(
                        f"Test case '{testcase_name}' artifacts.action[{idx}] must be a list (command array)"
                    )
                if not all(isinstance(arg, str) for arg in cmd):
                    raise ValueError(
                        f"Test case '{testcase_name}' artifacts.action[{idx}] must contain only strings"
                    )


@dataclass
class TestCaseConfig:

    name: str
    path: str
    commands: List[List[str]]
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    timeout: Optional[int] = None
    hooks: Optional[Dict[str, str]] = None
    artifacts: Optional[ArtifactsConfig] = None
    validation: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestCaseConfig":
        artifacts = None
        if data.get("artifacts"):
            artifacts = ArtifactsConfig.from_dict(data["artifacts"])
        
        return cls(
            name=data["name"],
            path=data["path"],
            commands=data["commands"],
            tags=data.get("tags", []),
            dependencies=data.get("dependencies", []),
            timeout=data.get("timeout"),
            hooks=data.get("hooks"),
            artifacts=artifacts,
            validation=data.get("validation"),
        )

    def validate(self):
        if not self.name:
            raise ValueError("Test case name cannot be empty")

        if not self.path:
            raise ValueError(f"Test case '{self.name}' path cannot be empty")

        if not self.commands:
            raise ValueError(f"Test case '{self.name}' must have at least one command")

        if not isinstance(self.commands, list):
            raise ValueError(f"Test case '{self.name}' commands must be a list")

        if self.timeout is not None and self.timeout <= 0:
            raise ValueError(f"Test case '{self.name}' timeout must be greater than 0")

        if not isinstance(self.tags, list):
            raise ValueError(f"Test case '{self.name}' tags must be a list")

        if not isinstance(self.dependencies, list):
            raise ValueError(f"Test case '{self.name}' dependencies must be a list")
        
        # Validate artifacts configuration
        if self.artifacts is not None:
            self.artifacts.validate(self.name)


@dataclass
class Config:

    framework: FrameworkConfig
    testcases: List[TestCaseConfig]

    def get_testcase_by_name(self, name: str) -> Optional[TestCaseConfig]:
        """Find test case config by name"""
        for testcase in self.testcases:
            if testcase.name == name:
                return testcase
        return None

    def validate(self):
        self.framework.validate()

        testcase_names = set()
        for testcase in self.testcases:
            testcase.validate()

            if testcase.name in testcase_names:
                raise ValueError(f"Duplicate test case name: {testcase.name}")
            testcase_names.add(testcase.name)

            for dep in testcase.dependencies:
                if dep not in testcase_names:
                    # TBD
                    pass
