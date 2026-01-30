# ArkTS Compiler Test Framework User Guide

## Table of Contents

- [Quick Start](#quick-start)
- [Environment Configuration](#environment-configuration)
- [Command Usage](#command-usage)
- [Global Configuration](#global-configuration)
- [Test Case Configuration](#test-case-configuration)
- [Hook System](#hook-system)
- [Common Issues](#common-issues)
- [Reference Documentation](#reference-documentation)

---

## Quick Start

If you already have an ArkTS project to test, you can run tests in just three steps:

**Step 1: Create Configuration Directory**
```bash
mkdir my-tests
cd my-tests
```

**Step 2: Create Configuration Files**

Create `config.yaml`:
```yaml
framework:
  build_tools:
    hvigor_home: "C:/DevEco/tools/hvigor"
    ohpm_home: "C:/DevEco/tools/ohpm"
    deveco_sdk_home: "C:/DevEco/sdk"
    ohos_base_sdk_home: "C:/DevEco/sdk"
  default_timeout: 600
  log_level: "INFO"
```

Create `testcases.yaml`:
```yaml
testcases:
  - name: "my_first_test"
    path: "C:/Projects/MyArkTSApp"
    commands:
      - ["hvigor", "assembleHap"]
```

**Step 3: Run Tests**
```bash
python main.py run --config-dir my-tests
```

---

## Environment Configuration

### System Requirements

- Python 3.8+
- Required tools: DevEco Studio, Hvigor, OHPM

### Tool Path Configuration

**Method 1: Explicit Configuration (Recommended)**

Explicitly specify all tool paths in `config.yaml`:
```yaml
framework:
  build_tools:
    hvigor_home: "C:/DevEco/tools/hvigor"           # Required
    ohpm_home: "C:/DevEco/tools/ohpm"               # Required
    deveco_sdk_home: "C:/DevEco/sdk"                # Required
    ohos_base_sdk_home: "C:/DevEco/sdk"             # Required
    node_home: "C:/DevEco/tools/node"               # Optional
    java_home: "C:/DevEco/jbr"                      # Optional
```

**Method 2: Use System Environment Variables**

`node_home` and `java_home` can be omitted, and the framework will automatically find them from system PATH:
```yaml
framework:
  build_tools:
    hvigor_home: "C:/DevEco/tools/hvigor"
    ohpm_home: "C:/DevEco/tools/ohpm"
    deveco_sdk_home: "C:/DevEco/sdk"
    ohos_base_sdk_home: "C:/DevEco/sdk"
    # node_home and java_home omitted, use system PATH
```

---

## Command Usage

### Run Tests

```bash
# Basic usage
python main.py run --config-dir <config-directory>

# Example
python main.py run --config-dir ./examples
```

**Runtime Output:**
```
======================================================================
Test Framework Starting
======================================================================
[√] Configuration loaded successfully
[√] Logger initialized: ./test_results/test_framework_20260124_143022.log

======================================================================
Test Execution Summary
======================================================================
Total: 3, Passed: 2, Failed: 1, Skipped: 0
Pass rate: 66.67%
```

**Tag Filtering**

Use the `--tags` parameter to filter test cases by specific tags:

```bash
# Run test cases with a single tag
python main.py run --config-dir ./config --tags smoke

# Run test cases with multiple tags (OR logic, matches any tag)
python main.py run --config-dir ./config --tags smoke,basic
```

**Automatic Dependency Inclusion:**
- The framework automatically includes all dependencies of selected test cases, even if dependencies don't have matching tags
- Example: Test case B depends on A, only B has "smoke" tag, executing `--tags smoke` will automatically run both A and B
- Logs will show auto-included dependencies: "Auto-included dependencies: xxx"

### Validate Configuration

```bash
python main.py validate --config-dir ./examples
```

Validation includes:
- YAML syntax correctness
- Required fields completeness
- Field type correctness
- File path validity
- Dependency existence check
- Circular dependency detection
- Display final execution order (by topological sort)

---

## Global Configuration

The global configuration file `config.yaml` defines framework-level configuration parameters.

### Configuration Fields

#### build_tools (Required)

Build tool environment configuration. All paths should point to tool installation directories.

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| ohpm_home | Yes | - | OHPM package manager home directory |
| hvigor_home | Yes | - | Hvigor build tool home directory |
| deveco_sdk_home | Yes | - | DevEco Studio SDK path |
| ohos_base_sdk_home | Yes | - | OpenHarmony base SDK path |
| node_home | No | System PATH | Node.js home directory, found from system PATH if not configured |
| java_home | No | System PATH | Java home directory, found from system PATH if not configured |

**Example:**
```yaml
framework:
  build_tools:
    hvigor_home: "C:/DevEco/tools/hvigor"
    ohpm_home: "C:/DevEco/tools/ohpm"
    deveco_sdk_home: "C:/DevEco/sdk"
    ohos_base_sdk_home: "C:/DevEco/sdk"
    node_home: "C:/DevEco/tools/node"  # Optional
    java_home: "C:/DevEco/jbr"          # Optional
```

#### default_timeout (Optional)

Default timeout in seconds. Commands exceeding this time will be forcibly terminated.

- Type: Integer
- Default: 300
- Unit: Seconds

```yaml
framework:
  default_timeout: 600  # 10 minutes
```

#### output_dir (Optional)

Test result output directory, containing log files and test reports.

- Type: String
- Default: `./test_results`

```yaml
framework:
  output_dir: "./test_results"
```

#### log_level (Optional)

Log verbosity level, controlling terminal and log file output levels.

- Type: String
- Default: `INFO`
- Options: `DEBUG`, `INFO`, `WARNING`, `ERROR`

```yaml
framework:
  log_level: "INFO"
```

**Level Descriptions:**
- `DEBUG`: Most detailed, includes all debug information and command output
- `INFO`: Normal information, recommended for daily use
- `WARNING`: Only shows warnings and errors
- `ERROR`: Only shows errors

#### retry_on_failure (Optional, In Development)

Number of automatic retries after test case failure.

- Type: Integer
- Default: 0
- Note: 0 means no retry

```yaml
framework:
  retry_on_failure: 2  # Retry 2 times after failure
```

### Complete Configuration Example

```yaml
framework:
  build_tools:
    hvigor_home: "C:/Program Files/Huawei/DevEco Studio/tools/hvigor"
    ohpm_home: "C:/Program Files/Huawei/DevEco Studio/tools/ohpm"
    deveco_sdk_home: "C:/Program Files/Huawei/DevEco Studio/sdk"
    ohos_base_sdk_home: "C:/Program Files/Huawei/DevEco Studio/sdk"
    node_home: "C:/Program Files/Huawei/DevEco Studio/tools/node"
    java_home: "C:/Program Files/Huawei/DevEco Studio/jbr"
  
  default_timeout: 600
  output_dir: "./test_results"
  log_level: "INFO"
  retry_on_failure: 0
```

---

## Test Case Configuration

The test case configuration file `testcases.yaml` defines all test cases.

### Basic Configuration

Each test case requires only three mandatory fields: `name`, `path`, and `commands`.

#### name (Required)

Unique test case identifier for identification and reference.

- Type: String
- Recommended to use lowercase letters and underscores

#### path (Required)

Project working directory where all commands are executed.

- Type: String
- Supports both absolute and relative paths

#### commands (Required)

List of commands to execute, where each command is a string array.

- Type: Array of arrays
- Format: `[["cmd", "arg1", "arg2"], ...]`
- Supports shorthand commands: `hvigor`, `ohpm`

**Basic Example:**

```yaml
testcases:
  - name: "basic_compile"
    path: "C:/Projects/MyApp"
    commands:
      - ["hvigor", "assembleHap"]

  - name: "clean_build"
    path: "C:/Projects/MyApp"
    commands:
      - ["hvigor", "clean"]
      - ["hvigor", "assembleHap"]

  - name: "install_and_build"
    path: "C:/Projects/MyApp"
    commands:
      - ["ohpm", "install"]
      - ["hvigor", "assembleHap"]
```

### Command Format Description

**Array Format (Required):**
```yaml
commands:
  - ["hvigor", "--mode", "module", "assembleHap"]
  - ["ohpm", "install"]
```

**Shorthand Commands:**
- `hvigor` → Automatically expanded to `node + hvigorw.js`
- `ohpm` → Automatically expanded to `ohpm` full path

**Path Handling:**
The framework automatically handles paths containing spaces, no need to add quotes:
```yaml
testcases:
  - name: "space_path"
    path: "C:/Program Files/My Project"
    commands:
      - ["hvigor", "assembleHap"]
```

### Advanced Configuration

#### timeout (Optional)

Test case-level timeout, overriding the global `default_timeout` setting.

- Type: Integer
- Unit: Seconds

```yaml
testcases:
  - name: "quick_test"
    path: "C:/Projects/Small"
    commands:
      - ["hvigor", "assembleHap"]
    timeout: 300  # 5 minutes

  - name: "long_test"
    path: "C:/Projects/Large"
    commands:
      - ["hvigor", "clean"]
      - ["hvigor", "assembleHap"]
    timeout: 1800  # 30 minutes
```

#### tags (Optional)

Test case tags for grouping and filtering test cases. Use the `--tags` parameter to run only matching test cases.

- Type: String array
- Filter logic: OR (includes if any tag matches)
- Automatically includes dependencies

**Example:**
```yaml
testcases:
  - name: "smoke_test"
    path: "C:/Projects/MyApp"
    tags: ["smoke", "fast"]
    commands:
      - ["hvigor", "assembleHap"]

  - name: "full_regression"
    path: "C:/Projects/MyApp"
    tags: ["regression", "slow"]
    commands:
      - ["hvigor", "clean"]
      - ["hvigor", "assembleHap"]
```

**Usage:**
```bash
# Run only test cases with smoke tag
python main.py run --config-dir ./config --tags smoke

# Run test cases with smoke or fast tag
python main.py run --config-dir ./config --tags smoke,fast

# Run all test cases if tags not specified
python main.py run --config-dir ./config
```

**Dependency Handling:**
```yaml
testcases:
  - name: "setup"       # No tags
    commands: ["setup.sh"]
  
  - name: "test_a"      # Has smoke tag
    tags: ["smoke"]
    dependencies: ["setup"]  # Depends on setup
    commands: ["test.sh"]
```
When executing `--tags smoke`, the `setup` test case will be automatically included and executed first

#### dependencies (Optional)

List of other test case names that must be successfully executed first. The framework automatically handles dependency relationships.

- Type: String array

**Execution Mechanism:**
1. **Initialization Phase**: Framework validates dependency existence, detects circular dependencies, and performs topological sorting
2. **Execution Phase**: Executes in sorted order, checking dependencies at runtime
3. **Failure Handling**: If a dependency test case fails, the current test case will be automatically skipped (SKIPPED)

**Example:**
```yaml
testcases:
  - name: "setup_test"
    path: "C:/Projects/MyApp"
    commands:
      - ["hvigor", "clean"]

  - name: "build_test"
    path: "C:/Projects/MyApp"
    dependencies: ["setup_test"]  # Depends on setup_test
    commands:
      - ["hvigor", "assembleHap"]

  - name: "integration_test"
    path: "C:/Projects/MyApp"
    dependencies: ["build_test"]  # Depends on build_test
    commands:
      - ["hvigor", "test"]
```

**Execution Order:** `setup_test` → `build_test` → `integration_test`

**Notes:**
- Dependent test cases must exist, otherwise validation fails
- Circular dependencies are not allowed (e.g., A→B→A)
- Use the `validate` command to view the final execution order

#### hooks (Optional, In Development)

Hook script configuration for injecting custom logic at specific test execution points. See [Hook System](#hook-system) section for details.

- Type: Object
- Fields: `pre_testcase`, `post_testcase`, `pre_command`, `post_command`, `on_failure`

```yaml
testcases:
  - name: "hooked_test"
    path: "C:/Projects/MyApp"
    commands:
      - ["hvigor", "assembleHap"]
    hooks:
      pre_testcase: "./hooks/setup.py"
      post_testcase: "./hooks/cleanup.py"
      on_failure: "./hooks/collect_logs.py"
```

#### artifacts (Optional, In Development)

Artifact verification and processing configuration. Both fields are optional; you can configure only one or both.

- Type: Object
- Fields:
  - `verify_files`: String array (optional), verify specified files exist
  - `action`: Command array (array of arrays, optional), execute custom scripts for artifact processing

```yaml
testcases:
  # Verify files only
  - name: "verify_only"
    path: "C:/Projects/MyApp"
    commands:
      - ["hvigor", "assembleHap"]
    artifacts:
      verify_files:
        - "build/outputs/entry-signed.hap"
  
  # Execute processing script only
  - name: "action_only"
    path: "C:/Projects/MyApp"
    commands:
      - ["hvigor", "assembleHap"]
    artifacts:
      action:
        - ["python", "scripts/upload.py"]
  
  # Both verify and process
  - name: "verify_and_action"
    path: "C:/Projects/MyApp"
    commands:
      - ["hvigor", "assembleHap"]
    artifacts:
      verify_files:
        - "build/outputs/entry/build/default/outputs/default/entry-default-signed.hap"
        - "build/outputs/library/build/default/outputs/default/library-default-unsigned.har"
      action:
        - ["python", "scripts/check_hap_size.py"]
        - ["python", "scripts/upload_artifacts.py"]
```

---

## Hook System

The hook system allows injecting custom logic at specific test execution points. (In Development)

### Hook Types

| Hook | Trigger Point | Purpose |
|------|---------------|---------|
| pre_testcase | Before test case starts | Setup environment, prepare data |
| post_testcase | After test case ends | Clean environment, collect artifacts |
| pre_command | Before each command execution | Modify environment variables |
| post_command | After each command execution | Check command output |
| on_failure | When test case fails | Collect error logs, failure diagnosis |

### Hook Interface

All hook scripts must implement the `execute(context)` function:

```python
def execute(context):
    """
    Hook execution function
    
    Args:
        context: Context object containing current execution environment information
    
    Returns:
        bool: True to continue execution, False to interrupt flow
    """
    # Hook logic
    return True
```

### Configuration Example

```yaml
testcases:
  - name: "full_test"
    path: "C:/Projects/MyApp"
    commands:
      - ["hvigor", "assembleHap"]
    hooks:
      pre_testcase: "./hooks/setup_env.py"
      post_testcase: "./hooks/collect_artifacts.py"
      on_failure: "./hooks/handle_failure.py"
```

### Hook Examples

**Clean Build Directory (pre_testcase):**
```python
# hooks/clean_build.py
import os
import shutil

def execute(context):
    build_dir = os.path.join(context.testcase_path, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print(f"[Hook] Cleaned build directory: {build_dir}")
    return True
```

**Collect Build Artifacts (post_testcase):**
```python
# hooks/collect_artifacts.py
import os
import shutil

def execute(context):
    source = os.path.join(context.testcase_path, "build/outputs")
    target = os.path.join(context.framework_root, "artifacts", context.testcase_name)
    
    if os.path.exists(source):
        os.makedirs(target, exist_ok=True)
        shutil.copytree(source, target, dirs_exist_ok=True)
        print(f"[Hook] Artifacts collected to: {target}")
    return True
```

**Collect Failure Logs (on_failure):**
```python
# hooks/handle_failure.py
import os

def execute(context):
    log_dir = os.path.join(context.framework_root, "failures", context.testcase_name)
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "failure.log")
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"Test Case: {context.testcase_name}\n")
        f.write(f"Failure Reason: {context.failure_reason}\n")
        f.write(f"Failed Command: {context.failed_command}\n")
        f.write(f"\nError Output:\n{context.error_output}\n")
    
    print(f"[Hook] Failure information saved: {log_file}")
    return True
```

For detailed hook development guide, please refer to [hook_spec.md](hook_spec.md).

---

## Common Issues

### spawn java ENOENT

**Error:** `[ERROR] Error: spawn java ENOENT`

**Solution:** Configure java_home in config.yaml
```yaml
build_tools:
  java_home: "C:/DevEco/jbr"
```

## Reference Documentation

- [Configuration Specification](config_spec.md) - Complete configuration field specifications
- [Hook Script Specification](hook_spec.md) - Detailed hook system development guide (In Development)
- `examples/` directory - Configuration example files
