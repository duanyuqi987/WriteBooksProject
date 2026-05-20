---
name: auto-commit-books
description: |
  写书工作完成后自动生成中文 commit message 并提交。
  覆盖 MD/HTML 双轨文件、合并卷文件、构建脚本和配置文件。
  触发条件：写完一章/扩展完内容/重新生成 HTML/合并卷之后。
---

# 写书后自动 Git 提交

## 触发时机

以下任一种工作完成后，执行本 skill：

- ✅ 完成单章或多章内容扩展
- ✅ 重新生成 HTML 阅读版（单章或合并卷）
- ✅ 合并上卷/下卷 MD + HTML
- ✅ 字数统计达标
- ✅ 质量门验证通过

## 提交规则

### 必须提交的文件

- `docs/` 下所有文件（.md、.html、.pdf、.png 等）
- `references/` 规则和模板
- `skills/` 技能定义
- `scripts/` 构建脚本
- `assets/` 静态资源
- `.gitignore` 和项目级 `CLAUDE.md`

### 绝对不能提交

- `.env`、`*.key`、`*.pem`、`*.secret`、`credentials.*`
- `.claude/` 内部状态
- `.superpowers/` 技能缓存
- `node_modules/`、`__pycache__/`、`dist/`、`build/`

## 执行流程

### 1. 先看改动范围

```bash
git status --short
git diff --stat
```

### 2. 生成中文 commit message

根据改动内容自动生成 Conventional Commits 格式的中文提交信息：

```
<type>: <中文简述>

<详细说明（可选）>

Co-Authored-By: Claude <Model> <noreply@anthropic.com>
```

**type 选择**：
- `docs:` — 书稿内容增删改
- `feat:` — 新增技能/脚本/功能
- `fix:` — 修正错误/修复问题
- `chore:` — 配置文件/构建/忽略规则

**示例**：
```
docs: 第三轮深度扩展完成，全16章+5附录达150,028字符

- 上卷9章新增约35,000字符（电磁/拓扑/减速器/编码器/驱动/FOC/PID/通信/实战）
- 下卷7章新增约22,000字符（SDK/三模式/负载PID/ROS2/多电机/机构/最终实战）
- 5个附录新增约7,000字符（产品选型/CAN协议/PID参考/公式速查/术语表）
- 21个HTML同步重新生成
- 合并上卷/下卷阅读版（MD+HTML双轨）

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
```

### 3. 分步提交

大改动分多次提交，每次聚焦一类变更：

```bash
# 第一步：书稿内容
git add docs/
git commit -m "docs: ..."

# 第二步：技能和配置
git add skills/ references/ scripts/
git commit -m "feat: ..."

# 第三步：构建和忽略规则
git add .gitignore CLAUDE.md
git commit -m "chore: ..."
```

### 4. 提交后验证

```bash
git status          # 确认干净
git log --oneline -5  # 确认提交历史
```

## 红线

- ❌ 绝不提交 `.env`、密钥、token、证书
- ❌ 绝不跳 hook（`--no-verify`、`--no-gpg-sign`）
- ❌ 绝不 force push 到 main/master
- ❌ 绝不 amend 已推送的提交
- ❌ 绝不用 `git add -A` 或 `git add .`（防误提交敏感文件）
- ✅ 始终坚持 `git add <具体文件或目录>` 精确控制提交范围

## 快捷命令

写完一轮后，标准提交流程：

```bash
# 1. 查看变更
git status --short && git diff --stat

# 2. 添加书稿（docs/ 全部安全）
git add docs/

# 3. 如有技能/配置变更，单独添加
git add skills/ references/ scripts/ .gitignore CLAUDE.md 2>/dev/null || true

# 4. 提交
git commit -m "$(cat <<'EOF'
docs: <此处写本轮改动的中文简述>

<此处写本轮改动的详细说明（可选）>

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"

# 5. 确认
git status && git log --oneline -3
```
