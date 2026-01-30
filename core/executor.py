"""Command executor module"""

import os
import subprocess
import time
from typing import Tuple, Optional
from utils.logger import get_logger
import platform


class Executor:

    BLUE = "\033[34m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    RESET = "\033[0m"

    def __init__(self, default_timeout: int = 300, framework_config=None):
        self.default_timeout = default_timeout
        self.framework_config = framework_config
        self.logger = get_logger()

    def _get_executable_name(self, base_name: str) -> str:

        if platform.system() == "Windows":
            return f"{base_name}.exe"
        return base_name

    def _build_command_from_list(self, cmd_list: list) -> list:
        if not cmd_list:
            return cmd_list

        if not self.framework_config or not self.framework_config.build_tools:
            return cmd_list

        bt = self.framework_config.build_tools
        first_arg = cmd_list[0]

        if first_arg == "hvigor":
            # If node_home is not configured, use 'node' from system PATH
            if not bt.node_home:
                node_exe = self._get_executable_name("node")
                hvigorw_js = os.path.normpath(
                    os.path.join(bt.hvigor_home, "bin", "hvigorw.js")
                )
                return [node_exe, hvigorw_js] + cmd_list[1:]

            node_exe = self._get_executable_name("node")
            node_path = os.path.normpath(os.path.join(bt.node_home, node_exe))
            hvigorw_js = os.path.normpath(
                os.path.join(bt.hvigor_home, "bin", "hvigorw.js")
            )
            return [node_path, hvigorw_js] + cmd_list[1:]

        if first_arg == "ohpm":
            ohpm_exe = self._get_executable_name("ohpm")
            ohpm_path = os.path.normpath(os.path.join(bt.ohpm_home, "bin", ohpm_exe))
            return [ohpm_path] + cmd_list[1:]

        return cmd_list

    def execute_command(
        self, command: list, cwd: str, timeout: Optional[int] = None
    ) -> Tuple[bool, str, int, float]:
        timeout = timeout or self.default_timeout

        cmd_list = self._build_command_from_list(command)
        display_cmd = " ".join(cmd_list)

        self.logger.info(f"{self.BLUE}Executing command:{self.RESET} {display_cmd}")
        self.logger.info(f"Working directory: {cwd}")

        if not os.path.exists(cwd):
            error_msg = f"Working directory does not exist: {cwd}"
            self.logger.error(error_msg)
            return False, error_msg, -1, 0.0

        start_time = time.time()

        try:
            env = os.environ.copy()
            if self.framework_config and self.framework_config.build_tools:
                bt = self.framework_config.build_tools

                if bt.ohpm_home:
                    env["OHPM_HOME"] = bt.ohpm_home
                    ohpm_bin = os.path.join(bt.ohpm_home, "bin")
                    if os.path.exists(ohpm_bin):
                        env["PATH"] = f"{ohpm_bin}{os.pathsep}{env.get('PATH', '')}"
                if bt.hvigor_home:
                    env["HVIGOR_HOME"] = bt.hvigor_home
                    hvigor_bin = os.path.join(bt.hvigor_home, "bin")
                    if os.path.exists(hvigor_bin):
                        env["PATH"] = f"{hvigor_bin}{os.pathsep}{env.get('PATH', '')}"
                if bt.deveco_sdk_home:
                    env["DEVECO_SDK_HOME"] = bt.deveco_sdk_home
                if bt.ohos_base_sdk_home:
                    env["OHOS_BASE_SDK_HOME"] = bt.ohos_base_sdk_home
                if bt.java_home:
                    env["JAVA_HOME"] = bt.java_home
                    java_bin = os.path.join(bt.java_home, "bin")
                    if os.path.exists(java_bin):
                        env["PATH"] = f"{java_bin}{os.pathsep}{env.get('PATH', '')}"

            process = subprocess.Popen(
                cmd_list,
                shell=False,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                env=env,
            )

            try:
                output, _ = process.communicate(timeout=timeout)
                exit_code = process.returncode
                duration = time.time() - start_time

                success = exit_code == 0

                if success:
                    self.logger.info(
                        f"Command executed successfully (duration: {duration:.2f}s)"
                    )
                    self.logger.debug(f"Command output:\n{output}")
                else:
                    self.logger.error(
                        f"Command execution failed (exit code: {exit_code}, duration: {duration:.2f}s)"
                    )
                    self.logger.error(f"Command output:\n{output}")

                return success, output, exit_code, duration

            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
                duration = time.time() - start_time
                error_msg = f"Command execution timeout (exceeded {timeout} seconds)"
                self.logger.error(error_msg)
                return False, error_msg, -1, duration

        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Command execution exception: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg, -1, duration

    def execute_testcase(self, testcase) -> bool:
        self.logger.info("=" * 70)
        self.logger.info(f"Starting test case: {self.BLUE}{testcase.name}{self.RESET}")
        self.logger.info("=" * 70)

        testcase.start()

        timeout = testcase.timeout or self.default_timeout

        all_success = True
        for idx, command in enumerate(testcase.commands, 1):
            self.logger.info(f"[{idx}/{len(testcase.commands)}] Executing command...")

            success, output, exit_code, duration = self.execute_command(
                command, testcase.path, timeout
            )

            testcase.add_command_result(command, success, output, exit_code, duration)

            if not success:
                all_success = False
                error_msg = (
                    f"Command execution failed: {command}\nExit code: {exit_code}"
                )
                self.logger.error(error_msg)
                testcase.finish(False, error_msg)
                break

        if all_success:
            testcase.finish(True)
            self.logger.info(
                f"Test case {self.GREEN}succeeded{self.RESET}: {self.BLUE}{testcase.name}{self.RESET} (duration: {testcase.duration:.2f}s)"
            )
        else:
            self.logger.error(f"Test case {self.RED}failed{self.RESET}: {self.BLUE}{testcase.name}{self.RESET}")

        return all_success
