# ArkTS编译器测试框架使用教程

## 目录

- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [命令使用](#命令使用)
- [全局配置](#全局配置)
- [用例配置](#用例配置)
- [钩子系统](#钩子系统)
- [常见问题](#常见问题)
- [参考文档](#参考文档)

---

## 快速开始

假设您已经有一个ArkTS项目需要测试，只需三步即可运行：

**第一步：创建配置目录**
```bash
mkdir my-tests
cd my-tests
```

**第二步：创建配置文件**

创建 `config.yaml`：
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

创建 `testcases.yaml`：
```yaml
testcases:
  - name: "my_first_test"
    path: "C:/Projects/MyArkTSApp"
    commands:
      - ["hvigor", "assembleHap"]
```

**第三步：运行测试**
```bash
python main.py run --config-dir my-tests
```

---

## 环境配置

### 系统要求

- Python 3.8+
- 必需工具：DevEco Studio、Hvigor、OHPM

### 工具路径配置

**方式一：显式配置（推荐）**

在 `config.yaml` 中明确指定所有工具路径：
```yaml
framework:
  build_tools:
    hvigor_home: "C:/DevEco/tools/hvigor"           # 必需
    ohpm_home: "C:/DevEco/tools/ohpm"               # 必需
    deveco_sdk_home: "C:/DevEco/sdk"                # 必需
    ohos_base_sdk_home: "C:/DevEco/sdk"             # 必需
    node_home: "C:/DevEco/tools/node"               # 可选
    java_home: "C:/DevEco/jbr"                      # 可选
```

**方式二：使用系统环境变量**

`node_home` 和 `java_home` 可以省略，框架会自动从系统 PATH 中查找：
```yaml
framework:
  build_tools:
    hvigor_home: "C:/DevEco/tools/hvigor"
    ohpm_home: "C:/DevEco/tools/ohpm"
    deveco_sdk_home: "C:/DevEco/sdk"
    ohos_base_sdk_home: "C:/DevEco/sdk"
    # node_home 和 java_home 省略，使用系统PATH
```

---

## 命令使用

### 运行测试

```bash
# 基础用法
python main.py run --config-dir <配置目录>

# 示例
python main.py run --config-dir ./examples
```

**运行时输出：**
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

**标签筛选**

使用 `--tags` 参数筛选特定标签的用例：

```bash
# 运行单个标签的用例
python main.py run --config-dir ./config --tags smoke

# 运行多个标签的用例（OR逻辑，任一标签匹配即可）
python main.py run --config-dir ./config --tags smoke,basic
```

**自动依赖包含：**
- 框架会自动包含被选中用例的所有依赖项，即使依赖项没有匹配的标签
- 例如：用例B依赖A，只有B有"smoke"标签，执行 `--tags smoke` 时会自动运行A和B
- 日志会显示自动包含的依赖项："Auto-included dependencies: xxx"

### 验证配置

```bash
python main.py validate --config-dir ./examples
```

验证内容：
- YAML语法正确性
- 必填字段完整性
- 字段类型正确性
- 文件路径有效性
- 依赖项存在性检查
- 循环依赖检测
- 显示最终执行顺序（按拓扑排序）

---

## 全局配置

全局配置文件 `config.yaml` 定义框架级别的配置参数。

### 配置字段

#### build_tools（必需）

构建工具环境配置，所有路径都是工具的安装目录。

| 字段 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| ohpm_home | 是 | - | OHPM包管理器主目录 |
| hvigor_home | 是 | - | Hvigor构建工具主目录 |
| deveco_sdk_home | 是 | - | DevEco Studio SDK路径 |
| ohos_base_sdk_home | 是 | - | OpenHarmony基础SDK路径 |
| node_home | 否 | 系统PATH | Node.js主目录，未配置时从系统PATH查找 |
| java_home | 否 | 系统PATH | Java主目录，未配置时从系统PATH查找 |

**示例：**
```yaml
framework:
  build_tools:
    hvigor_home: "C:/DevEco/tools/hvigor"
    ohpm_home: "C:/DevEco/tools/ohpm"
    deveco_sdk_home: "C:/DevEco/sdk"
    ohos_base_sdk_home: "C:/DevEco/sdk"
    node_home: "C:/DevEco/tools/node"  # 可选
    java_home: "C:/DevEco/jbr"          # 可选
```

#### default_timeout（可选）

默认超时时间（秒），命令执行超过此时间会被强制终止。

- 类型：整数
- 默认值：300
- 单位：秒

```yaml
framework:
  default_timeout: 600  # 10分钟
```

#### output_dir（可选）

测试结果输出目录，包含日志文件和测试报告。

- 类型：字符串
- 默认值：`./test_results`

```yaml
framework:
  output_dir: "./test_results"
```

#### log_level（可选）

日志详细程度，控制终端和日志文件的输出级别。

- 类型：字符串
- 默认值：`INFO`
- 可选值：`DEBUG`, `INFO`, `WARNING`, `ERROR`

```yaml
framework:
  log_level: "INFO"
```

**级别说明：**
- `DEBUG`：最详细，包含所有调试信息和命令输出
- `INFO`：正常信息，推荐日常使用
- `WARNING`：只显示警告和错误
- `ERROR`：只显示错误

#### retry_on_failure（可选，开发中）

用例失败后的自动重试次数。

- 类型：整数
- 默认值：0
- 说明：0表示不重试

```yaml
framework:
  retry_on_failure: 2  # 失败后重试2次
```

### 完整配置示例

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

## 用例配置

用例配置文件 `testcases.yaml` 定义所有测试用例。

### 基础配置

每个用例只需要三个必需字段：`name`、`path`、`commands`。

#### name（必需）

用例唯一标识符，用于标识和引用用例。

- 类型：字符串
- 建议使用小写字母和下划线

#### path（必需）

项目工作目录，所有命令在此目录下执行。

- 类型：字符串
- 支持绝对路径和相对路径

#### commands（必需）

要执行的命令列表，每个命令是一个字符串数组。

- 类型：数组的数组
- 格式：`[["cmd", "arg1", "arg2"], ...]`
- 支持简化命令：`hvigor`、`ohpm`

**基础示例：**

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

### 命令格式说明

**数组格式（必须使用）：**
```yaml
commands:
  - ["hvigor", "--mode", "module", "assembleHap"]
  - ["ohpm", "install"]
```

**简化命令：**
- `hvigor` → 自动展开为 `node + hvigorw.js`
- `ohpm` → 自动展开为 `ohpm` 完整路径

**路径处理：**
框架自动处理包含空格的路径，无需添加引号：
```yaml
testcases:
  - name: "space_path"
    path: "C:/Program Files/My Project"
    commands:
      - ["hvigor", "assembleHap"]
```

### 进阶配置

#### timeout（可选）

用例级超时时间，覆盖全局 `default_timeout` 设置。

- 类型：整数
- 单位：秒

```yaml
testcases:
  - name: "quick_test"
    path: "C:/Projects/Small"
    commands:
      - ["hvigor", "assembleHap"]
    timeout: 300  # 5分钟

  - name: "long_test"
    path: "C:/Projects/Large"
    commands:
      - ["hvigor", "clean"]
      - ["hvigor", "assembleHap"]
    timeout: 1800  # 30分钟
```

#### tags（可选）

用例标签，用于分组和筛选测试用例。使用 `--tags` 参数可以只运行匹配标签的用例。

- 类型：字符串数组
- 筛选逻辑：OR（任一标签匹配即包含）
- 自动包含依赖项

**示例：**
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

**使用方式：**
```bash
# 只运行smoke标签的用例
python main.py run --config-dir ./config --tags smoke

# 运行smoke或fast标签的用例
python main.py run --config-dir ./config --tags smoke,fast

# 不指定tags则运行所有用例
python main.py run --config-dir ./config
```

**依赖处理：**
```yaml
testcases:
  - name: "setup"       # 无标签
    commands: ["setup.sh"]
  
  - name: "test_a"      # 有smoke标签
    tags: ["smoke"]
    dependencies: ["setup"]  # 依赖setup
    commands: ["test.sh"]
```
执行 `--tags smoke` 时，会自动包含 `setup` 用例并先执行

#### dependencies（可选）

依赖的其他用例名称列表，这些用例必须先成功执行。框架会自动处理依赖关系。

- 类型：字符串数组

**执行机制：**
1. **初始化阶段**：框架验证依赖项存在性，检测循环依赖，并进行拓扑排序
2. **执行阶段**：按排序后的顺序执行，运行时检查依赖是否成功
3. **失败处理**：如果依赖用例失败，当前用例会被自动跳过（SKIPPED）

**示例：**
```yaml
testcases:
  - name: "setup_test"
    path: "C:/Projects/MyApp"
    commands:
      - ["hvigor", "clean"]

  - name: "build_test"
    path: "C:/Projects/MyApp"
    dependencies: ["setup_test"]  # 依赖 setup_test
    commands:
      - ["hvigor", "assembleHap"]

  - name: "integration_test"
    path: "C:/Projects/MyApp"
    dependencies: ["build_test"]  # 依赖 build_test
    commands:
      - ["hvigor", "test"]
```

**执行顺序：** `setup_test` → `build_test` → `integration_test`

**注意事项：**
- 依赖用例必须存在，否则验证失败
- 不允许循环依赖（如 A→B→A）
- 使用 `validate` 命令可以查看最终执行顺序

#### hooks（可选，开发中）

钩子脚本配置，在测试执行的特定时机注入自定义逻辑。详见[钩子系统](#钩子系统)章节。

- 类型：对象
- 字段：`pre_testcase`, `post_testcase`, `pre_command`, `post_command`, `on_failure`

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

#### artifacts（可选，开发中）

产物验证和处理配置。两个字段都是可选的，可以只配置其中一个或两个都配置。

- 类型：对象
- 字段：
  - `verify_files`：字符串数组（可选），验证指定文件是否存在
  - `action`：命令数组（数组的数组，可选），执行自定义脚本进行产物处理

```yaml
testcases:
  # 只验证文件
  - name: "verify_only"
    path: "C:/Projects/MyApp"
    commands:
      - ["hvigor", "assembleHap"]
    artifacts:
      verify_files:
        - "build/outputs/entry-signed.hap"
  
  # 只执行处理脚本
  - name: "action_only"
    path: "C:/Projects/MyApp"
    commands:
      - ["hvigor", "assembleHap"]
    artifacts:
      action:
        - ["python", "scripts/upload.py"]
  
  # 同时验证和处理
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

## 钩子系统

钩子系统允许在测试执行的特定时机注入自定义逻辑。（开发中）

### 钩子类型

| 钩子 | 触发时机 | 用途 |
|------|---------|------|
| pre_testcase | 用例开始前 | 设置环境、准备数据 |
| post_testcase | 用例结束后 | 清理环境、收集产物 |
| pre_command | 每条命令执行前 | 修改环境变量 |
| post_command | 每条命令执行后 | 检查命令输出 |
| on_failure | 用例失败时 | 收集错误日志、故障诊断 |

### 钩子接口

所有钩子脚本必须实现 `execute(context)` 函数：

```python
def execute(context):
    """
    钩子执行函数
    
    Args:
        context: 上下文对象，包含当前执行环境信息
    
    Returns:
        bool: True继续执行，False中断流程
    """
    # 钩子逻辑
    return True
```

### 配置示例

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

### 钩子示例

**清理构建目录（pre_testcase）：**
```python
# hooks/clean_build.py
import os
import shutil

def execute(context):
    build_dir = os.path.join(context.testcase_path, "build")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
        print(f"[钩子] 已清理构建目录: {build_dir}")
    return True
```

**收集构建产物（post_testcase）：**
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
        print(f"[钩子] 产物已收集到: {target}")
    return True
```

**失败日志收集（on_failure）：**
```python
# hooks/handle_failure.py
import os

def execute(context):
    log_dir = os.path.join(context.framework_root, "failures", context.testcase_name)
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "failure.log")
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(f"用例: {context.testcase_name}\n")
        f.write(f"失败原因: {context.failure_reason}\n")
        f.write(f"失败命令: {context.failed_command}\n")
        f.write(f"\n错误输出:\n{context.error_output}\n")
    
    print(f"[钩子] 失败信息已保存: {log_file}")
    return True
```

详细的钩子开发指南请参考 [hook_spec.md](hook_spec.md)。

---

## 常见问题

### spawn java ENOENT

**错误：** `[ERROR] Error: spawn java ENOENT`

**解决：** 在 config.yaml 中配置 java_home
```yaml
build_tools:
  java_home: "C:/DevEco/jbr"
```

## 参考文档

- [配置文件规格说明](config_spec.md) - 完整的配置字段规格
- [钩子脚本规格说明](hook_spec.md) - 钩子系统详细开发指南（开发中）
- `examples/` 目录 - 配置示例文件