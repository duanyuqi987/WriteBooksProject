# 小说任务管理系统

深度融合 task-harness 方法论。解决 AI 写长篇小说的核心问题：多次会话之间的状态丢失。

## 核心洞察

AI 的核心局限是**无状态**——每次会话从零开始。没有结构化系统，AI 的典型失败模式：

| 失败模式 | 症状 |
|---------|------|
| 一次写太多 | 想一次写很多章，写到一半跑偏 |
| 过早声称完成 | 章节其实没写完却说完成了 |
| 上下文污染 | 把新章节写成了前面章节的重复 |
| 重复探索 | 每次会话重新理解项目结构和进度 |

## 真相源设计

### feature_list.json（章节任务列表）

为什么用 JSON 而不是 Markdown？AI 倾向于自由改写 Markdown 文件——调整结构、删除内容、弱化验证。JSON 文件被更谨慎地处理，AI 通常只修改特定字段。

```json
{
  "project": "书名",
  "target_word_count": 500000,
  "current_word_count": 12500,
  "features": [
    {
      "id": "ch-001",
      "category": "第一卷",
      "priority": 1,
      "description": "林晚在废弃医院中独自生存，展示末世日常和她的PTSD",
      "word_count_target": 2200,
      "word_count_actual": 0,
      "techniques": ["白描", "反衬法"],
      "foreshadows": [],
      "passes": false,
      "verification": "读者能感受到林晚的孤独和PTSD症状；末世的残酷日常被具体呈现"
    },
    {
      "id": "ch-002",
      "category": "第一卷",
      "priority": 2,
      "description": "林晚遇到被困的赵铁生和小鹿，决定出手救援",
      "word_count_target": 2200,
      "word_count_actual": 0,
      "techniques": ["一击两鸣"],
      "foreshadows": ["foreshadow-002"],
      "passes": false,
      "verification": "救援场景有紧张感；赵铁生和小鹿的性格通过行动展示"
    }
  ]
}
```

### progress.txt（叙事进度日志）

```text
----------------------------------------
会话 #1 - ch-001: 林晚在废弃医院中独自生存
----------------------------------------
时间：2026-05-17

完成工作：
  [x] 三层写作完成（粗写→细写→技法注入）
  [x] 五层审查通过
  [x] 6项记忆同步完成
  - 字数：2350字（目标2200字）
  - 技法：白描（用动作展现场景）、反衬法（表面冷静，内心PTSD）
  - 关键创造：林晚反复搓洗手这一PTSD表现
  - Canon变更：无

提交：
  - commit: abc1234 docs: 完成 chapter-001 林晚开场章

进度：
  - 已完成：1/240
  - 下一章：ch-002 - 林晚遇到被困的赵铁生和小鹿
  - 未兑现伏笔：0条
```

### init.sh（5秒上下文恢复）

```bash
#!/bin/bash
echo "===== 《书名》写作进度 ====="
echo "当前目录：$(pwd)"
echo ""
echo "--- Git 状态 ---"
git status --short
echo ""
echo "--- 最近提交 ---"
git log --oneline -10
echo ""
echo "--- 章节完成情况 ---"
python3 -c "
import json
with open('feature_list.json') as f:
    data = json.load(f)
completed = sum(1 for f in data['features'] if f['passes'])
total = len(data['features'])
print(f'完成: {completed}/{total} ({completed/total*100:.1f}%)')
print(f'累计字数: {data[\"current_word_count\"]:,} / {data[\"target_word_count\"]:,} ({data[\"current_word_count\"]/data[\"target_word_count\"]*100:.1f}%)')
print()
print('--- 未完成章节 ---')
for f in data['features']:
    if not f['passes']:
        print(f'  [{f[\"id\"]}] {f[\"description\"]} (目标{f[\"word_count_target\"]}字)')
        break
"
echo ""
echo "--- 下一步 ---"
echo "1. 读取 memory-snapshot.md 获取最近章节摘要"
echo "2. 读取 outline.md 获取当前章任务"
echo "3. 开始写下一章"
```

## 智能体工作流（每次会话）

```
1. bash init.sh                          // 5秒恢复上下文
2. 读取 progress.txt                     // 理解上次做了什么和为什么
3. 读取 feature_list.json                // 找到最高优先级的未完成章节
4. 读取 memory-snapshot.md              // 获取最近 5 章摘要
5. 写 1 章                               // 不要贪多，增量才是关键
6. 五层审查                               // 实际验证，不要假设
7. 更新 feature_list.json                // 只改 passes 和 word_count_actual
8. git commit                            // 一章一次提交
9. 追加 progress.txt                     // 记录本次工作
10. 更新 memory-snapshot.md             // 写入新章节摘要
```

## 严格规则

- **只修改 passes 和 word_count_actual**。绝不删除 features、不编辑 descriptions、不改变 priorities、不重组 JSON
- **一次一章**（除非是很短的过渡章）
- **必须 commit 每章**
- **必须在标记完成前验证**
- **必须更新 progress.txt**
- **阻塞时停止**，记录阻塞原因

## 阻塞处理格式

```
BLOCKER: 阻塞问题描述
原因：为什么不能继续
尝试过：已经试过什么方案
建议：可能的方向
```

## 验证最佳实践

- 糟糕："看起来还行"（主观）
- 良好："本章 2350 字，章末不是抒情总结，6 类 AI 检测全部通过"（可执行检查）
- 良好："读者能从林晚反复搓洗手的动作感受到 PTSD，不需要心理描写"（具体）
- 良好："伏笔 foreshadow-002 在第三章自然植入，非突兀"（可验证）
