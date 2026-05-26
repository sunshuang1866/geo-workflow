# Clean Code 设计与评估报告

**状态:** 已发布
**作者:** sunshuang
**日期:** 2026-05-26
**版本:** 1.0

---

## 一、Clean Code 核心原则

本项目遵循 Robert C. Martin《Clean Code》的核心原则，结合 **Skill 脚本型项目**的实际特点，制定以下编码规范。

> 与传统 Python 包不同，geo-workflow 的代码单元是 `.claude/skills/*/scripts/` 下的**独立 CLI 脚本**，每个脚本通过 `argparse` 接收参数，向 `stdout` 输出 JSON，向 `stderr` 输出进度与错误。规范设计以此为核心。

### 1.1 有意义的命名

| 原则 | 说明 | 示例 |
|------|------|------|
| **脚本名用动词短语** | 脚本名应说明它做什么操作 | `score-urls.py` vs `scorer.py` |
| **函数名以动词开头** | 函数名清晰描述行为 | `fetch_from_db()` vs `get_data()` |
| **私有辅助函数加前缀** | 模块内部帮助函数以 `_` 开头 | `_normalize_url()`, `_is_label_error()` |
| **常量全大写** | 模块级配置常量使用大写 | `MIN_VIEWS = 50`, `FORUM_TOP_N = 30` |
| **避免缩写** | 名称应可朗读，语义自明 | `citation_rate` vs `cr`, `platform_records` vs `precs` |

**本项目命名规范：**

```python
# ✅ 好的命名
MIN_VIEWS = 50                          # 全大写常量，含义清晰
FORUM_TOP_N = 30

def fetch_from_discourse(api_url: str, limit: int | None) -> list[dict]:
    pass                                # 动词开头，参数类型明确

def _load_db_config(community: str) -> dict | None:
    pass                                # 下划线表示内部函数

# ❌ 不好的命名
def getData():                          # 做什么数据？哪来的？
    pass

def proc(x, n):                         # 完全不可读
    pass
```

### 1.2 脚本与函数设计

Skill 脚本遵循 **CLI 单元原则**：每个脚本只做一件事，通过 `main()` 函数封装入口逻辑，并附加 `if __name__ == "__main__"` 守卫。

| 原则 | 说明 |
|------|------|
| **单一入口** | 每个脚本必须有 `main()` + `if __name__ == "__main__"` |
| **函数 ≤ 30 行** | 脚本函数建议 ≤ 30 行（比包模块宽松，因逻辑更线性） |
| **单一职责** | 一个函数只做一件事（解析、获取、验证、输出各自独立） |
| **参数传递显式化** | 避免读取全局变量；通过参数传递，保持函数可测试 |

**本项目函数设计示例：**

```python
# ✅ 职责分离：normalize 只做 URL 规范化
def normalize_url(url: str) -> str:
    url = url.strip().lower()
    url = re.sub(r'^https?://', '', url)
    url = re.sub(r'^www\.', '', url)
    url = url.rstrip('/')
    return url


# ✅ 职责分离：is_cited 只做引用判定，不处理输出
def is_cited(response_text: str, official_urls: list[str]) -> tuple[bool, list[str]]:
    """Return (cited, matched_urls). Exact normalized match only."""
    text_lower = response_text.lower()
    matched = [url for url in official_urls if url and normalize_url(url) in text_lower]
    return bool(matched), matched


# ❌ 职责混乱：解析 + 验证 + 打印全混在一起
def handle(data):
    val = data['x']
    if val < 0:
        print("bad")
        sys.exit(1)
    print(json.dumps({"result": val * 2}))
```

### 1.3 stdout / stderr 通信协议

这是 geo-workflow 脚本最核心的设计规范，**所有脚本必须严格遵守**：

| 流 | 用途 | 格式 |
|----|------|------|
| **stdout** | 机器可读输出（供下游脚本解析） | JSON（数组或对象） |
| **stderr** | 人工可读进度、警告、错误 | 自由文本，前缀约定见下表 |

**stderr 前缀约定：**

| 前缀 | 含义 | 对应行为 |
|------|------|----------|
| `ERROR:` | 致命错误，脚本无法继续 | 随后 `sys.exit(1)` |
| `WARNING:` | 非致命异常，脚本可降级继续 | 不退出，记录后继续 |
| （无前缀） | 常规进度信息 | 不退出，仅告知 |

```python
# ✅ 正确的输出分流
print(f"WARNING: DB connection failed: {e}", file=sys.stderr)   # 非致命
print(f"ERROR: questions.json not found: {path}", file=sys.stderr)  # 致命
sys.exit(1)

results = [...]
print(json.dumps(results, ensure_ascii=False, indent=2))        # stdout 输出 JSON

# ❌ 错误的混流
print(f"Fetching {url}...")                                     # 进度信息进了 stdout，破坏 JSON 解析
print(json.dumps(results))
```

### 1.4 错误处理

| 原则 | 说明 |
|------|------|
| **使用具体异常** | 禁止裸 `except:`；至少用 `except Exception` |
| **错误消息含上下文** | 错误消息应包含足够定位问题的信息（URL、文件名、参数值） |
| **区分致命 vs 降级** | 网络超时可降级（WARNING + 继续），文件缺失应致命（ERROR + exit） |
| **exit code 规范** | `0` = 成功，`1` = 失败（兼容 shell 管道和 Claude 脚本编排） |

**本项目错误处理示例：**

```python
# ✅ 具体异常 + 上下文 + 合理降级
try:
    conn = psycopg2.connect(host=cfg["host"], ...)
except Exception as e:
    print(f"WARNING: DB connection failed: {e}", file=sys.stderr)
    return None   # 降级：调用方可切换到 Discourse API 回退路径

# ✅ 致命错误直接退出
try:
    return json.loads(p.read_text(encoding="utf-8"))
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON in {label or filepath}: {e}", file=sys.stderr)
    sys.exit(1)

# ✅ 标签错误单独处理，不中断整体流程
except urllib.error.HTTPError as e:
    if _is_label_error(e):
        print("WARNING: Labels not applied. Retrying without labels.", file=sys.stderr)
        return _post(url, payload_no_labels, headers)
    raise   # 其他 HTTP 错误继续向上抛出

# ❌ 吞掉异常，隐藏问题
try:
    result = call_api(url)
except:
    result = {}
```

### 1.5 文档规范

| 原则 | 说明 |
|------|------|
| **模块文档字符串必须有** | 每个脚本开头的 docstring 说明：用途、Usage 示例、Exit codes |
| **函数文档字符串** | 非私有函数建议有 docstring；Returns、Raises 注明 |
| **注释说明"为什么"** | 代码能说明"是什么"，注释应说明"为什么这样做" |
| **避免冗余注释** | 不注释代码已经清楚表达的内容 |

**本项目文档规范：**

```python
# ✅ 完整的脚本级 docstring
"""Fetch individual forum posts from PostgreSQL hotopic DB or Discourse API.

Primary:  PostgreSQL hotopic DB — queries discussion table (source_type='forum'),
          filters views > MIN_VIEWS, returns top FORUM_TOP_N posts sorted by views DESC.
Fallback: Discourse API — fetches topics from all active forum categories.

Usage:
    python3 fetch-forum-posts.py --community openeuler
    python3 fetch-forum-posts.py --community mindspore --api-url https://discuss.mindspore.cn

Exit codes:
  0 — success (at least one post returned)
  1 — no posts fetched from any source
"""

# ✅ 说明"为什么"的注释（非显而易见的决策）
# No domain-level matching: domain-only checks produce false positives when all
# official URLs share a single domain (e.g. mindspore.cn).

# ❌ 冗余注释（代码已经清楚说明）
# Sort results by views descending
results.sort(key=lambda t: t["views"], reverse=True)
```

### 1.6 格式化规范

| 工具 | 用途 | 配置 |
|------|------|------|
| **black** | 自动代码格式化 | 默认配置（line-length=88） |
| **flake8** | 代码风格检查 | `max-line-length=100`（脚本比包宽松） |
| **isort** | 导入排序 | 默认配置 |

**导入顺序（isort 标准）：**

```python
# 1. 标准库
import argparse
import json
import sys
from pathlib import Path

# 2. 第三方库（如有）
import psycopg2
import playwright

# 3. 本地（_shared）
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _shared.utils import load_json, resolve_platform_token
```

---

## 二、项目 Clean Code 实施现状

### 2.1 检查结果（2026-05-26）

| 检查项 | 结果 | 状态 |
|--------|------|------|
| **命名规范** | 函数/变量命名清晰，常量大写，私有函数有 `_` 前缀 | ✅ 通过 |
| **stdout/stderr 分离** | 核心脚本（score-urls.py、create-issue.py）严格遵守 | ✅ 通过 |
| **具体异常类型** | urllib.error.HTTPError/URLError, json.JSONDecodeError 等具体类型 | ✅ 通过 |
| **exit code 规范** | 成功 0、失败 1，一致使用 `sys.exit(1)` | ✅ 通过 |
| **硬编码凭证** | 全部通过环境变量注入，无硬编码 token/密码 | ✅ 通过 |
| **脚本 docstring** | 主要脚本已有完整 Usage + Exit codes | ✅ 通过 |
| **black/flake8** | 未配置自动检查，需补充 | ⚠️ 待配置 |
| **函数文档字符串** | 公开函数覆盖率约 60%，部分内部函数缺失 | ⚠️ 待改进 |
| **测试覆盖** | 无测试文件，缺少自动化验证 | ❌ 缺失 |

### 2.2 已遵循的良好实践

| 实践 | 体现位置 |
|------|----------|
| stdout/stderr 严格分流 | `score-urls.py`, `create-issue.py`, `fetch-forum-posts.py` |
| 标签错误单独处理（不中断主流程） | `create-issue.py: create_github/create_gitcode` |
| 多数据源降级策略（DB → Discourse API） | `fetch-forum-posts.py: fetch_from_db → fetch_from_discourse` |
| 通用工具提取到 `_shared/utils.py` | `load_json()`, `resolve_platform_token()` |
| 模块级常量集中定义 | `MIN_VIEWS`, `FORUM_TOP_N`, `GITHUB_API`, `GITCODE_API` |
| URL 规范化逻辑集中管理 | `score-urls.py: normalize_url()` |

### 2.3 待改进项

| 优先级 | 问题 | 建议 |
|--------|------|------|
| **高** | 无测试覆盖 | 为 `_shared/utils.py` 和 `score-urls.py` 核心逻辑添加单元测试 |
| **中** | 未配置 black/flake8 | 添加 `pyproject.toml` 或 `.flake8` 配置，加入提交前检查 |
| **中** | 部分函数缺少 docstring | `fetch_from_db()`、`_fetch_category_topics()` 等补充 Returns/Raises |
| **中** | `fetch_from_db` 函数过长（~90 行） | 拆分 SQL 构建、执行、结果解析三个子函数 |
| **低** | `run-platform-chat.py` 使用裸 `except Exception` | 精确到 `subprocess.CalledProcessError`, `FileNotFoundError` 等 |
| **低** | `load_env()` 缺少返回类型注解 | 补充 `-> dict[str, str]` |

---

## 三、Clean Code 评分

### 3.1 评分维度

| 维度 | 得分 | 说明 |
|------|------|------|
| **命名规范** | ⭐⭐⭐⭐⭐ (5/5) | 函数/变量/常量命名清晰，kebab-case 脚本名语义准确 |
| **通信协议** | ⭐⭐⭐⭐⭐ (5/5) | stdout/stderr 分流严格，exit code 一致 |
| **错误处理** | ⭐⭐⭐⭐☆ (4/5) | 具体异常 + 上下文信息，降级策略清晰；个别使用裸 Exception |
| **代码风格** | ⭐⭐⭐⭐☆ (4/5) | 整体整洁，未配置 black/flake8 自动约束 |
| **文档完整性** | ⭐⭐⭐☆☆ (3/5) | 脚本级 docstring 完善，函数级 docstring 覆盖不足 |
| **测试覆盖** | ⭐☆☆☆☆ (1/5) | 无测试，核心逻辑（URL 匹配、评分算法）无自动验证 |

### 3.2 总体评分

**⭐⭐⭐⭐☆ (3.7/5.0)**

**结论**：命名、通信协议、错误处理等核心规范表现优秀；主要短板在于缺乏测试覆盖和自动格式化约束，建议优先补充核心逻辑单元测试。

---

## 四、Clean Code 检查清单

每次修改脚本前后，请确认以下清单：

### 4.1 通信协议

- [ ] **stdout 只输出 JSON**（数组或对象），不混入进度文本
- [ ] **stderr 用于进度/警告/错误**，前缀规范（`ERROR:` / `WARNING:` / 无前缀）
- [ ] 致命错误后调用 `sys.exit(1)`，正常退出不调用 `sys.exit()`

### 4.2 命名与结构

- [ ] 脚本文件名为动词短语，kebab-case（如 `fetch-forum-posts.py`）
- [ ] 函数名以动词开头，语义清晰
- [ ] 模块级配置常量全大写（`MIN_VIEWS`, `FORUM_TOP_N`）
- [ ] 内部辅助函数以 `_` 开头（`_normalize_key`, `_fetch_json`）
- [ ] 每个脚本有 `main()` 入口函数 + `if __name__ == "__main__"` 守卫

### 4.3 错误处理

- [ ] 无裸 `except:`；至少明确 `except Exception`
- [ ] 捕获 `urllib.error.HTTPError` / `urllib.error.URLError` / `json.JSONDecodeError` 等具体类型
- [ ] 错误消息包含上下文（URL、文件路径、参数值）
- [ ] 区分致命错误（`sys.exit(1)`）和可降级警告（打印 WARNING，继续运行）

### 4.4 文档与可读性

- [ ] 脚本开头有完整 docstring（用途、Usage 示例、Exit codes）
- [ ] 公开函数有 docstring，标注 Returns（特别是返回 `None` 的场景）
- [ ] 注释说明"为什么"而不是"是什么"
- [ ] 无硬编码 token、密码、URL（全部从环境变量读取）

### 4.5 代码质量

- [ ] `black .claude/skills/` 格式化通过
- [ ] `flake8 .claude/skills/ --max-line-length=100` 无错误
- [ ] 函数 ≤ 30 行（超出考虑拆分）
- [ ] 无未使用的导入

---

## 五、常用命令

```bash
# 代码格式化（在项目根目录执行）
black .claude/skills/

# 代码检查
flake8 .claude/skills/ --max-line-length=100

# 运行单个脚本（示例）
python3 .claude/skills/scoring-engine/scripts/score-urls.py \
  output/openEuler/2026-04-07/responses.json \
  output/openEuler/questions.json \
  output/openEuler/2026-04-07/scoring-results.json

# 验证 JSON 输出格式（检查 stdout 是否为合法 JSON）
python3 .claude/skills/scoring-engine/scripts/score-urls.py \
  responses.json questions.json /dev/stdout 2>/dev/null | python3 -m json.tool

# 完整检查（推荐提交前运行）
black .claude/skills/ && flake8 .claude/skills/ --max-line-length=100
```

---

## 六、Skill 脚本特有规范

### 6.1 _shared 模块使用规范

所有需要复用的工具函数应提取到 `_shared/utils.py`，并在脚本头部通过标准路径注入：

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from _shared.utils import load_json, resolve_platform_token
```

> 不要在脚本中重复实现 JSON 加载、token 解析等已有工具函数。

### 6.2 argparse 规范

```python
# ✅ 推荐写法：description 说明脚本用途
parser = argparse.ArgumentParser(description="Create an Issue on GitHub or GitCode")
parser.add_argument("--owner",    required=True)
parser.add_argument("--repo",     required=True)
parser.add_argument("--dry-run",  action="store_true")
parser.add_argument("--token",    default=None, help="API token (overrides env)")

# 参数有默认值时 help 说明默认值
parser.add_argument("--limit", type=int, default=None,
                    help="Maximum number of posts to return (default: top 30)")
```

### 6.3 环境变量读取规范

```python
# ✅ 推荐：提供明确的默认值，记录缺失时的行为
community = os.environ.get("GEO_COMMUNITY", "")
if not community:
    print("ERROR: GEO_COMMUNITY not set in .env", file=sys.stderr)
    sys.exit(1)

# ✅ 可选变量给合理默认值
dry_run = os.environ.get("GEO_DRY_RUN", "false").lower() == "true"

# ❌ 直接访问不存在的 key（KeyError 无上下文）
community = os.environ["GEO_COMMUNITY"]
```

---

## 七、参考资源

- **书籍**: Robert C. Martin, 《Clean Code: A Handbook of Agile Software Craftsmanship》
- **PEP 8**: https://peps.python.org/pep-0008/
- **black**: https://black.readthedocs.io/
- **flake8**: https://flake8.pycqa.org/
- **argparse 最佳实践**: https://docs.python.org/3/library/argparse.html

---
