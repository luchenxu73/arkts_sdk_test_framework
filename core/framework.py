"""Test framework core class"""
from datetime import datetime
from typing import Optional

from config.loader import ConfigLoader
from config.models import Config
from core.testcase import TestCase
from core.executor import Executor
from utils.logger import setup_logger


class TestFramework:
    """Test framework main class"""
    
    # ANSI color codes
    CYAN = '\033[36m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    BLUE = '\033[34m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    def __init__(self, config_dir: str = ".", tags: list = None):
        """
        Initialize test framework
        
        Args:
            config_dir: Configuration file directory
            tags: List of tags to filter test cases (OR logic - any matching tag)
        """
        self.config_dir = config_dir
        self.loader = ConfigLoader(config_dir)
        self.config: Optional[Config] = None
        self.logger = None
        self.executor = None
        self.testcases = []
        self.filter_tags = tags or []
    
    def initialize(self):
        """Initialize framework"""
        print("="*70)
        print("Test Framework Starting")
        print("="*70)
        
        # Load all configurations
        try:
            self.config = self.loader.load_all()
            print("[\u221a] Configuration loaded successfully")
            print(f"    - Framework config: log_level={self.config.framework.log_level}, "
                  f"timeout={self.config.framework.default_timeout}s")
            print(f"    - Test cases: {len(self.config.testcases)}")
        except Exception as e:
            print(f"[\u00d7] Failed to load configuration: {e}")
            return False
        
        # Setup logging
        self.logger = setup_logger(
            name='test_framework',
            log_level=self.config.framework.log_level,
            log_dir=self.config.framework.output_dir,
            console_output=True
        )
        
        # Create test case objects
        self.testcases = [TestCase(tc_config) for tc_config in self.config.testcases]
        self.logger.info(f"Loaded {len(self.testcases)} test cases")
        
        # Filter test cases by tags if specified
        if self.filter_tags:
            self.testcases = self._filter_by_tags(self.testcases, self.filter_tags)
            self.logger.info(f"Filtered to {len(self.testcases)} test cases by tags: {', '.join(self.filter_tags)}")
            print(f"    - Filtered by tags [{', '.join(self.filter_tags)}]: {len(self.testcases)} test cases")
        
        # Validate and sort test cases by dependencies
        try:
            self._validate_dependencies()
            self.testcases = self._sort_by_dependencies()
            self.logger.info("Test case dependencies validated and sorted")
        except Exception as e:
            self.logger.error(f"Dependency validation failed: {e}")
            print(f"[\u00d7] Dependency validation failed: {e}")
            return False
        
        # Create executor with framework config for environment variables
        self.executor = Executor(
            self.config.framework.default_timeout,
            self.config.framework
        )
        
        return True
    
    def _filter_by_tags(self, testcases: list, tags: list) -> list:

        tc_map = {tc.name: tc for tc in testcases}
        
        matched = set()
        for tc in testcases:
            if any(tag in tc.tags for tag in tags):
                matched.add(tc.name)
        
        def add_dependencies(tc_name: str, result: set):
            """Recursively add test case and all its dependencies"""
            if tc_name in result:
                return
            result.add(tc_name)
            
            tc = tc_map.get(tc_name)
            if tc:
                for dep in tc.dependencies:
                    add_dependencies(dep, result)
        
        final_set = set()
        for tc_name in matched:
            add_dependencies(tc_name, final_set)
        
        filtered = [tc for tc in testcases if tc.name in final_set]
        
        auto_included = final_set - matched
        if auto_included:
            self.logger.info(f"Auto-included dependencies: {', '.join(sorted(auto_included))}")
            print(f"    - Auto-included dependencies: {', '.join(sorted(auto_included))}")
        
        return filtered
    
    def _validate_dependencies(self):
        """Validate test case dependencies"""
        testcase_names = {tc.name for tc in self.testcases}
        
        for testcase in self.testcases:
            for dep in testcase.dependencies:
                if dep not in testcase_names:
                    raise ValueError(
                        f"Test case '{testcase.name}' depends on non-existent test case: '{dep}'"
                    )
        
        self._check_circular_dependencies()
    
    def _check_circular_dependencies(self):
        def has_cycle(name, visited, rec_stack, dep_map):
            visited.add(name)
            rec_stack.add(name)
            
            for dep in dep_map.get(name, []):
                if dep not in visited:
                    if has_cycle(dep, visited, rec_stack, dep_map):
                        return True
                elif dep in rec_stack:
                    return True
            
            rec_stack.remove(name)
            return False
        
        # Build dependency map
        dep_map = {tc.name: tc.dependencies for tc in self.testcases}
        
        visited = set()
        for testcase in self.testcases:
            if testcase.name not in visited:
                if has_cycle(testcase.name, visited, set(), dep_map):
                    raise ValueError(
                        f"Circular dependency detected involving test case: '{testcase.name}'"
                    )
    
    def _sort_by_dependencies(self):
        dep_map = {tc.name: tc for tc in self.testcases}
        in_degree = {tc.name: len(tc.dependencies) for tc in self.testcases}
        
        # Find all nodes with no dependencies
        queue = [tc for tc in self.testcases if in_degree[tc.name] == 0]
        sorted_testcases = []
        
        while queue:
            queue.sort(key=lambda x: x.name)
            current = queue.pop(0)
            sorted_testcases.append(current)
            
            for tc in self.testcases:
                if current.name in tc.dependencies:
                    in_degree[tc.name] -= 1
                    if in_degree[tc.name] == 0:
                        queue.append(tc)
        
        if len(sorted_testcases) != len(self.testcases):
            raise ValueError("Failed to sort test cases - possible circular dependency")
        
        return sorted_testcases
    
    def run(self):
        if not self.testcases:
            self.logger.warning("No test cases found")
            return
        
        self.logger.info("Starting test execution...")
        self.logger.info("")
        
        start_time = datetime.now()
        
        completed = {}
        
        for testcase in self.testcases:
            skip_reason = self._check_dependencies(testcase, completed)
            if skip_reason:
                self.logger.error(f"Test case '{testcase.name}' failed: {skip_reason}")
                testcase.finish(False, skip_reason)
                completed[testcase.name] = False
                self.logger.info("")
                continue
            
            success = self.executor.execute_testcase(testcase)
            completed[testcase.name] = success
            self.logger.info("")
        
        total_time = (datetime.now() - start_time).total_seconds()
        self._print_summary(total_time)
    
    def _check_dependencies(self, testcase: TestCase, completed: dict) -> str:
        for dep in testcase.dependencies:
            if dep not in completed:
                return f"dependency '{dep}' not yet executed"
            if not completed[dep]:
                return f"dependency '{dep}' failed"
        return ""
    
    def _print_summary(self, total_time: float):

        passed = sum(1 for tc in self.testcases if tc.status == TestCase.STATUS_PASSED)
        failed = sum(1 for tc in self.testcases if tc.status == TestCase.STATUS_FAILED)
        skipped = sum(1 for tc in self.testcases if tc.status == TestCase.STATUS_SKIPPED)
        total = len(self.testcases)
        
        self.logger.info("="*70)
        self.logger.info(f"{self.BOLD}{self.CYAN}Test Summary{self.RESET}")
        self.logger.info("="*70)
        self.logger.info(f"Total test cases: {self.CYAN}{total}{self.RESET}")
        self.logger.info(f"Passed: {self.GREEN}{passed}{self.RESET}")
        self.logger.info(f"Failed: {self.RED}{failed}{self.RESET}")
        self.logger.info(f"Skipped: {self.YELLOW}{skipped}{self.RESET}")
        
        effective_total = total - skipped
        if effective_total > 0:
            pass_rate = passed/effective_total*100
            rate_color = self.GREEN if pass_rate >= 80 else (self.YELLOW if pass_rate >= 60 else self.RED)
            self.logger.info(f"Pass rate: {rate_color}{pass_rate:.2f}%{self.RESET}")
        else:
            self.logger.info("Pass rate: N/A")
        
        self.logger.info(f"Total time: {self.CYAN}{total_time:.2f}s{self.RESET}")
        self.logger.info("")
        
        self.logger.info("Test case details:")
        for testcase in self.testcases:
            status_symbol = "\u221a" if testcase.status == TestCase.STATUS_PASSED else "\u00d7"
            
            status_colored = testcase.status
            if testcase.status == TestCase.STATUS_PASSED:
                status_colored = f"{self.GREEN}{testcase.status}{self.RESET}"
            elif testcase.status == TestCase.STATUS_FAILED:
                status_colored = f"{self.RED}{testcase.status}{self.RESET}"
            elif testcase.status == TestCase.STATUS_SKIPPED:
                status_colored = f"{self.YELLOW}{testcase.status}{self.RESET}"
            
            self.logger.info(
                f"  [{status_symbol}] {testcase.name} - {status_colored} "
                f"({testcase.duration:.2f}s)"
            )
            if testcase.error_message:
                self.logger.info(f"      Error: {testcase.error_message}")
        
        self.logger.info("="*70)
