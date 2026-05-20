# 小说记忆系统

每次写作会话通过文件系统实现持续记忆，不依赖对话上下文。所有状态以文件为真相源。

## 记忆分层

```
docs/YYYY-MM-DD/小说/<中文书名>/
├─ project.md              # 第一层：项目底座（永不丢失）
├─ outline.md              # 第二层：大纲状态（每章完成即更新）
├─ project-state.md        # 第三层：调度快照（每次会话写入）
├─ 伏笔/foreshadow-xxx.md  # 第四层：伏笔追踪（独立文件管理）
├─ 章节/chapter-xxx.md     # 第五层：章节完整记录（目标+正文+审查+技法）
├─ 人物/<角色>.md          # 第六层：角色状态追踪
└─ memory-snapshot.md      # 第七层：快速恢复快照（每次会话结束写入）
```

## 每次会话启动时（novel-draft 和 novel-writing 必须读取）

### 最小恢复读取（6 个文件，缺一不可）

1. `project.md` → 世界观、风格、禁止事项
2. `outline.md` → 当前进度、下一章任务
3. `project-state.md` → 上次会话状态
4. `memory-snapshot.md` → 最近 5 章摘要
5. `人物/` 文件夹 → 所有角色当前状态
6. `伏笔/` 文件夹 → 所有未兑现伏笔的状态

### 恢复流程

```
1. 读取 project-state.md → 确定上次停在哪里
2. 读取 outline.md → 确认当前章的章节号和任务
3. 读取 memory-snapshot.md → 获取最近 5 章摘要
4. 读取人物/所有角色卡 → 获取角色当前状态
5. 读取伏笔/所有文件 → 获取未兑现的伏笔
6. 读取当前章文件 → 确认是否已开始
7. 判定状态 → 路由到对应工序
```

## 每章完成后写入（novel-update）

### 必须写入的 5 项数据

1. **章节摘要**：2-3 句关键事件、角色变化、新增设定 → 追加到 `memory-snapshot.md`
2. **伏笔状态**：有新埋入 → 创建/更新 `伏笔/foreshadow-xxx.md`；有兑现 → 更新对应文件
3. **角色变更**：状态/能力/关系变化 → 追加到 `人物/<角色>.md` 变更记录
4. **大纲状态**：章节状态更新 → 更新 `outline.md`
5. **调度快照**：当前状态、下一步 → 覆盖写入 `project-state.md`

## memory-snapshot.md 格式

```markdown
# 记忆快照 - <书名>

## 最近已完成章节

### chapter-010
- 关键事件：XXX
- 角色变化：XXX
- 新增设定：XXX
- 启用的伏笔：foreshadow-xxx（兑现/未兑现）
- 使用的技法：XXX

### chapter-009
...

## 当前进度
- 已完成：第 X 卷 第 Y 章
- 总字数：XXX
- 下一章：chapter-011 - [任务说明]
- 未兑现伏笔数：N
- 活跃角色列表：XXX

## 最近更新时间
2026-05-17 15:30
```

## project-state.md 格式

```markdown
# 项目调度状态

- 项目：<书名>
- 状态：idea / planned / drafting / reviewing / done / blocked
- 当前章：chapter-XXX
- 当前卷：第 X 卷
- 阻塞原因：（仅 blocked 状态填写）
- 上次会话：2026-05-17 15:30
- 上次操作：完成了 chapter-010 的 draft
```

## 伏笔追踪文件格式

### foreshadow-xxx.md

```markdown
# 伏笔：[名称]

- ID：foreshadow-001
- 名称：XXX
- 层次：大伏线 / 小伏线 / 微伏线
- 状态：planned / planted / reminded / paid_off / abandoned
- 埋入章：chapter-005
- 埋入描述：（在 chapter-005 中如何埋入的）
- 中途提示：
  - chapter-008：[提示方式]
  - chapter-012：[提示方式]
- 兑现章：chapter-015
- 兑现描述：（如何兑现的）
- 关联人物：XXX
- 创建时间：2026-05-15
```

## 角色状态追踪

角色卡 `变更记录` section 追加格式：

```
[chapter-010] 林晚失去左手，身份从"军医"变为"残障幸存者"
[chapter-010] 与赵铁生的关系从"互不信任"变为"共经生死后的战友"
[chapter-012] 发现自己的孢子抗体，能力新增"短时间暴露于孢子中不感染"
```

## 记忆清理规则

- memory-snapshot.md 只保留最近 5 章的详细摘要，更早的合并为 1 句话
- 伏笔文件在 `paid_off` 后保留但标记为已兑现
- 角色卡变更记录不删除，保持完整历史
- project-state.md 每次覆盖，不保留历史
