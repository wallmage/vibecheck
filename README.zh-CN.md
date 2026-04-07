# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**你的 AI 编程工具正在烧你看不到的钱。**

你发的每条消息，AI 都会从头重新读一遍*整个*对话记录。第 50 条消息的成本是第 1 条的 50 倍。AI 说"好的，我现在来修复这个"？花了你的钱，但什么都没做。那 500 行构建日志？之后的每一条消息都会重新读一遍。

大多数 Vibe Coder 在不知不觉中浪费了 **超过 50%** 的 AI Token 预算。

vibecheck 解决这个问题。它扫描你最近 14 天的会话，精确找出浪费在哪里，用大白话解释（不用技术术语——我们会教你什么是 Token），然后在你的配置文件里加一段话就搞定。活照干，钱省一半。

**平均节省：50%+ 的 Token 账单。** 支持所有 LLM 模型（Claude、GPT、Gemini、DeepSeek）。支持 Claude Code、OpenClaw、Codex、OpenCode、Cursor、Windsurf 等 24+ 种 AI 编程工具。100% 本地运行——你的数据永远不会离开你的电脑。

```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

## 隐私保护

**你的数据永远不会离开你的电脑。** vibecheck 是一组 100% 本地运行的 Python 脚本。没有服务器，没有 API，没有遥测，没有数据分析，不会回传任何信息。作者不可能收集你的数据——从技术上就做不到。代码完全开源，你可以逐行审查。

扫描只读取你本地的会话日志（硬盘上的 JSONL 文件），在内存中分析，结果显示在你的屏幕上。不上传，不发送，不在你电脑之外存储任何东西——只在 `~/.vibecheck/` 保存一个小快照文件来追踪你的进度。

## 安装

### 方式 A：AI 编程工具（完整体验）

如果你使用 **Claude Code CLI**、**Cursor**、**Windsurf**、**Codex** 等 AI 编程工具——把 vibecheck 安装为技能。这些工具直接运行在你的电脑上，能读取你的会话日志，所以你能获得完整的个性化扫描。

**Claude Code CLI：**
```bash
claude install-skill https://github.com/wallmage/vibecheck
```

**Claude Code 桌面应用（Builder/Code 模式）：**
同样的安装命令。桌面应用的编程模式（Builder、Code）拥有完整的文件访问权限，和 CLI 一样。你能获得同样完整的扫描体验。

**其他 AI 编程工具（Cursor、Codex、Windsurf、Cline 等）：**
告诉你的 AI：
> 从 https://github.com/wallmage/vibecheck 安装 vibecheck 技能，然后运行 `/vibecheck scan`

然后运行：
```
/vibecheck scan
```

**国产 AI 编程工具：**
vibecheck 同样支持 CodeBuddy（腾讯）、通义灵码（阿里）、TRAE/MarsCode（字节跳动）、Kimi Code（月之暗面）、Qoder（阿里）、百度 Comate、CodeGeeX（智谱）、DevChat、MiniMax Code 等工具。告诉你的 AI 安装即可。

### 方式 B：非编程环境（Cowork、聊天模式）

像 **Claude Cowork**、纯聊天模式或浏览器端 AI 工具运行在沙盒环境里——它们能看到你的项目文件，但看不到你的聊天记录。就像客人可以看到你的客厅，但进不了你的卧室——你的对话在私密区域里。

**vibecheck 仍然有两种方式可以工作：**

1. **不扫描（80% 的效果）：** 即使不读取日志，vibecheck 仍然可以优化你的配置文件——压缩 CLAUDE.md、添加省 Token 规则、精简臃肿的提示词。光是这些修改就能减少 20-40% 的浪费，因为它减少了 AI 在每条消息中重复阅读的内容量。直接运行 `/vibecheck compress` 或让 AI 应用优化规则即可。

2. **扫描（完整效果）：** 要获得用你真实数据做的个性化分析，vibecheck 会让你在普通终端里粘贴一条命令。只复制最近 14 天的日志（约 20-50 MB）到一个沙盒能看到的文件夹：

   ```
   python3 vibecheck路径/scripts/export_logs.py
   ```

   vibecheck 会给你准确的命令——粘贴就行。5 秒搞定。然后把工具指向 `~/vibecheck-logs`，就能获得完整扫描。

### 权限说明

vibecheck 需要访问你的**项目文件夹**来读取和编辑你的配置文件（CLAUDE.md、AGENTS.md、.cursorrules、SOUL.md 等）。它会在做任何修改前征求你的同意。你可以逐条审查每个修改建议，单独接受或拒绝。

完整扫描还需要读取你的会话日志（AI 工具保存对话记录的 JSONL 文件）。这些文件始终留在你的电脑上——见[隐私保护](#隐私保护)。

## 命令

- `/vibecheck` 或 `/vibecheck scan` — 互动教学 + 完整诊断 + 修复
- `/vibecheck explain` — 仅教学（理解你的账单，不做修改）
- `/vibecheck compress` — 压缩配置文件（缩小 25-50%）
- `/vibecheck monitor` — 周度对比 + 异常告警

## 工作原理

大多数人不知道自己在为什么付费。$20/月的订阅背后可能隐藏着 $200+ 的实际 AI 消耗。钱都去哪了？

vibecheck 用一堂互动课开始——用你的真实数据——逐步解释：
1. 什么是 Token？（提示：大约一个词）
2. 为什么 AI 每条消息都要重新读一遍整个对话？
3. 你的钱去了哪里？（剧透：50-65% 花在重复阅读旧消息上）

然后它找到你的浪费模式，在配置文件里加一段话就修好了。活照干，消息更少。

### 即使不扫描

如果你不能或不想扫描日志，vibecheck 一样有用。安装技能就会添加优化规则。你的 AI 会学会：
- 不再废话"我现在来做…"（直接做）
- 把多个编辑合并到一条消息里
- 把命令串起来而不是一条一条执行
- 保持对话简短避免上下文膨胀
- 把冗长的输出导入文件而不是刷屏

光这些规则就能节省约 80%。扫描找到剩下的 20%，告诉你钱到底花哪了。

## 前后对比

vibecheck 追踪你的进度。第一次运行显示预测，后续运行显示实际节省：

```
                              之前           现在           变化
  平均 Turns/会话              36.8           25.9           -10.9 ✅
  平均 Sub-Agent/会话          3.2            2.9            -0.3 ✅
  平均上下文窗口               128.4K         89.9K          -30% ✅
  浪费的 Turns                36.7%          8.1%           -28.6% ✅

  平均成本/会话                $2.62          $1.35          -$1.27 ✅
  每月支出                     $224           $115           -$109 ✅
```

## 15 种浪费模式

**第一层——三大杀手（70-80% 的浪费）**
1. 空转叙述——AI 说"现在我来…"然后才做
2. 上下文腐烂——对话太长不清理，后面的消息越来越贵
3. 乒乓调试——改了坏、坏了改、改了又坏

**第二层——机械浪费（15-20%）**
4. 冗长输出——构建日志淹没对话
5. 未串联命令——命令一条一条跑而不是串起来
6. 代码库漫游——编辑 1 个文件前先读 8 个
7. 未批量编辑——一条消息只改一个文件

**第三层——尾部浪费（5-10%）**
8. 重复读文件——同一个文件读两次
9. 轮询等待——反复问"好了没？"
10. 失败重试——失败的命令留在上下文里
11. Schema 查询——查询 AI 已经知道的工具
12. Git 仪式——Git 命令一条一条跑

**第四层——全天候 Agent（OpenClaw 等）**
13. 空闲心跳——Agent 每 5 分钟醒来，没事做，照样收费
14. 工作区膨胀——每次唤醒重读 35K Token 的人设文件
15. 记忆堆积——会话历史无限增长不清理

## 支持的工具（自动检测）

24+ 种工具：Claude Code、Cursor、Codex、Windsurf、Cline、Roo Code、Aider、Gemini CLI、Copilot、OpenClaw、CodeBuddy（腾讯）、通义灵码（阿里）、TRAE（字节）、Kimi Code（月之暗面）、百度 Comate、CodeGeeX（智谱）等。

## 多语言

自动检测系统语言。用你的语言回复。随时切换。

## 运行环境

- macOS（Apple Silicon + Intel）、Windows、Linux
- iPad/手机通过 SSH 使用

需要 Python 3.8+，无外部依赖。
