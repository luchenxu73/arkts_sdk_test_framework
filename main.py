"""Test framework main entry point"""
import argparse
import sys

from config.loader import ConfigLoader
from core.testcase import TestCase
from core.framework import TestFramework


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='ArkTS Compiler Test Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # run command
    run_parser = subparsers.add_parser('run', help='Run test cases')
    run_parser.add_argument(
        '--config-dir',
        default='.',
        help='Configuration file directory (default: current directory)'
    )
    run_parser.add_argument(
        '--tags',
        default=None,
        help='Filter test cases by tags (comma-separated, e.g., "smoke,basic")'
    )
    
    # validate command
    validate_parser = subparsers.add_parser('validate', help='Validate configuration files')
    validate_parser.add_argument(
        '--config-dir',
        default='.',
        help='Configuration file directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 0
    
    # Handle run command
    if args.command == 'run':
        # Parse tags
        tags = []
        if args.tags:
            tags = [tag.strip() for tag in args.tags.split(',')]
        
        framework = TestFramework(args.config_dir, tags=tags)
        
        if not framework.initialize():
            print("Framework initialization failed")
            return 1
        
        framework.run()
        
        # Return exit code based on test results
        failed = sum(1 for tc in framework.testcases 
                    if tc.status == TestCase.STATUS_FAILED)
        return 1 if failed > 0 else 0
    
    # Handle validate command
    elif args.command == 'validate':
        print("Validating configuration files...")
        loader = ConfigLoader(args.config_dir)
        
        try:
            config = loader.load_all()
            print("[\u221a] Configuration validation passed")
            print(f"    - Global config: \u2713")
            print(f"    - Test case config: {len(config.testcases)} cases")
            
            # Create test case objects for dependency validation
            testcases = [TestCase(tc_config) for tc_config in config.testcases]
            
            # Validate dependencies
            framework = TestFramework(args.config_dir)
            framework.testcases = testcases
            try:
                framework._validate_dependencies()
                sorted_testcases = framework._sort_by_dependencies()
                print(f"    - Dependencies: \u2713 (no circular dependencies)")
                print(f"\n    Execution order:")
                for idx, tc in enumerate(sorted_testcases, 1):
                    dep_str = f" [depends on: {', '.join(tc.dependencies)}]" if tc.dependencies else ""
                    print(f"      {idx}. {tc.name}{dep_str}")
            except Exception as e:
                print(f"    - Dependencies: \u00d7 ({e})")
                return 1
            
        except Exception as e:
            print(f"[\u00d7] Configuration validation failed: {e}")
            return 1
        
        print("\nConfiguration file validation complete")
        return 0
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
