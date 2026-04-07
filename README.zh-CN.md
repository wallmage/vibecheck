# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**你的 AI 编程工具正在烧你看不到的钱。**

你发的每条消息，AI 都会从头重新读一遍*整个*对话记录。第 50 条消息的成本是第 1 条的 50 倍。AI 说"好的，我现在来修复这个"？花了你的钱，但什么都没做。那 500 行构建日志？之后的每一条消息都会重新读一遍。

大多数 Vibe Coder 在不知不觉中浪费了 **超过 50%** 的 AI Token 预算。

vibecheck 解决这个问题。它扫描你最近 14 天的会话，精确找出浪费在哪里，用大白话解释（不用技术术语——我们会教你什么是 Token），然后在你的配置文件里加一段话就搞定。活照干，钱省一半。

**平均节省：50%+ 的 Token 账单。** 支持所有 LLM 模型（Claude、GPT、Gemini、DeepSeek）。支持 Claude Code、OpenClaw、Codex、OpenCode、Cursor、Windsurf 等 24+ 种 AI 编程工具。100% 本地运行——你的数据永远不会离开你的电脑。

## 立即开始——无需下载任何东西

vibecheck 是一个**技能**——一组你的 AI 编程工具可以学习的指令。你不需要下载或安装任何软件。只需给你的 AI 一个链接，它就会自己学会如何优化你的成本。一条消息搞定。

**把这段话复制粘贴到你的 AI 编程工具里**（Claude Code、Cursor、Codex、Windsurf、Cline——任何一个都行）：

> 从 https://github.com/wallmage/vibecheck 安装 vibecheck 技能，然后运行 /vibecheck scan

就这样。你的 AI 读取技能，扫描最近 14 天，然后一步步教你。

**或者用命令行：**
```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

### 什么是"技能"？

技能就像给你的 AI 一张菜谱。它不会修改你的 AI，也不会在你电脑上安装任何东西。它只是给你的 AI 一组指令——"怎么找浪费模式、怎么解释、怎么修复"。你的 AI 读了菜谱就照着做。随时可以删除。

### 编程工具 vs 聊天工具

**编程工具**（Claude Code CLI、Claude Desktop Builder/Code 模式、Cursor、Codex、Windsurf、Cline）直接运行在你的电脑上。它们能读取你的会话日志，给你完整的个性化扫描。体验最好。

**聊天/沙盒工具**（Claude Cowork、纯聊天模式、浏览器 AI 工具）运行在沙盒里——能看到你的项目文件，但看不到聊天记录。就像客人可以看到你的客厅，但进不了你的卧室。

vibecheck 仍然有两种方式工作：

1. **不扫描（80% 的效果）：** 优化你的配置文件——压缩 CLAUDE.md、添加省 Token 规则、精简提示词。这些修改就能减少 20-40% 的浪费，不需要日志。

2. **扫描（完整效果）：** vibecheck 让你在终端粘贴一条命令，只复制最近 14 天的日志（约 20-50 MB）。5 秒搞定，然后获得完整个性化分析。

### 权限说明

vibecheck 需要访问你的**项目文件夹**来读取和编辑配置文件（CLAUDE.md、AGENTS.md、.cursorrules、SOUL.md 等）。每次修改前都会征求同意，你可以逐条审查。

## 隐私保护

**你的数据永远不会离开你的电脑。** vibecheck 是一组 100% 本地运行的 Python 脚本。没有服务器、没有 API、没有遥测、没有数据分析。作者不可能收集你的数据——技术上做不到。代码完全开源。

## 命令

- `/vibecheck` 或 `/vibecheck scan` — 互动教学 + 完整诊断 + 修复
- `/vibecheck explain` — 仅教学（理解你的账单，不做修改）
- `/vibecheck compress` — 压缩配置文件（缩小 25-50%）
- `/vibecheck monitor` — 周度对比 + 异常告警

## 工作原理

大多数人不知道自己在为什么付费。$20/月的订阅背后可能隐藏着 $200+ 的实际 AI 消耗。

vibecheck 用互动课开始——用你的真实数据——逐步解释：
1. 什么是 Token？（大约一个词）
2. 为什么 AI 每条消息都重新读整个对话？
3. 你的钱去哪了？（50-65% 花在重复阅读旧消息上）

### 即使不扫描

安装技能就会添加优化规则。你的 AI 会学会：不再废话、把编辑合并到一条消息、串联命令、保持对话简短、把输出导入文件。光这些就能节省约 80%。

## 前后对比

```
                              之前           现在           变化
  平均 Turns/会话              36.8           25.9           -10.9 ✅
  平均上下文窗口               128.4K         89.9K          -30% ✅
  浪费的 Turns                36.7%          8.1%           -28.6% ✅
  平均成本/会话                $2.62          $1.35          -$1.27 ✅
  每月支出                     $224           $115           -$109 ✅
```

## 15 种浪费模式

**第一层——三大杀手（70-80%）：** 空转叙述、上下文腐烂、乒乓调试
**第二层——机械浪费（15-20%）：** 冗长输出、未串联命令、代码库漫游、未批量编辑
**第三层——尾部（5-10%）：** 重复读文件、轮询等待、失败重试、Schema 查询、Git 仪式
**第四层——全天候 Agent：** 空闲心跳、工作区膨胀、记忆堆积

## 支持的工具

24+ 种：Claude Code、Cursor、Codex、Windsurf、Cline、OpenClaw、CodeBuddy（腾讯）、通义灵码（阿里）、TRAE（字节）、Kimi Code（月之暗面）、百度 Comate、CodeGeeX（智谱）等。

所有 LLM：Claude (Opus/Sonnet/Haiku)、GPT-4o/4.1/o1/o3、Gemini 2.5/2.0、DeepSeek V3/R1。

## 运行环境

macOS (Apple Silicon + Intel)、Windows、Linux、iPad/手机 via SSH。Python 3.8+，无外部依赖。
