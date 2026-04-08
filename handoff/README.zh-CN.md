# handoff

[English](README.md) | 中文 | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

[![GitHub stars](https://img.shields.io/github/stars/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff/watchers)
[![GitHub last commit](https://img.shields.io/github/last-commit/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff)
[![Top language](https://img.shields.io/github/languages/top/wallmage/handoff?style=flat-square)](https://github.com/wallmage/handoff)
[![Workflow](https://img.shields.io/badge/workflow-copy%20%26%20paste-111827?style=flat-square)](https://github.com/wallmage/handoff)
[![Works in](https://img.shields.io/badge/works%20in-CLI%20%7C%20GUI%20%7C%20chat-0f766e?style=flat-square)](https://github.com/wallmage/handoff)
[![Storage](https://img.shields.io/badge/storage-no%20files-4f46e5?style=flat-square)](https://github.com/wallmage/handoff)
[![Focus](https://img.shields.io/badge/focus-context%20transfer-b45309?style=flat-square)](https://github.com/wallmage/handoff)
[![Use case](https://img.shields.io/badge/use%20case-context%20rot%20recovery-2563eb?style=flat-square)](https://github.com/wallmage/handoff)

**你的对话在衰减，这个工具让信号保持鲜活。**

每个 AI 对话都有半衰期。线程越长，模型反复读的旧上下文越多，输出质量就越差，token 也白白烧在噪音上。你知道该怎么办——开个新会话嘛。但你会丢掉之前做过的决策、追踪过的 bug、敲定的架构方案。于是你继续在旧线程里硬撑，质量一路下滑。

`handoff` 打破这个死循环。在任意会话里说 `handoff`，它会生成一个传输块——无损压缩，2-4K token——把决策、发现、失败、当前状态、未解决的问题和下一步行动全部捕获。粘贴到新对话里，直接全速继续，不用重新探索。

没有文件，没有插件，没有数据库。复制粘贴就行。

## 工作原理

**生成模式** -- 在旧会话里说 `handoff`。它会把整段对话无损压缩成一个结构化传输块。不是随便回顾一遍，而是保留具体成果——做了什么决定、什么失败了、什么做了一半、下一步该干嘛——同时扔掉问候语、闲聊、重复说明和原始日志。

**恢复模式** -- 把传输块粘贴到新会话里。它会解析内容，给你一个简洁的状态摘要，然后等你下指令。

传输块目标大小 **2-4K token**。够小，可以经常用；够密，不会丢东西。

## 自然触发词

不用记什么特殊命令，下面这些都能触发：

- `handoff`
- `hand off`
- `new session`
- `switch session`
- `start fresh`
- `wrap up and hand off`

## 保留的内容

- 决策及其原因
- 技术发现和机制
- 失败的实验，以及为什么失败
- 重要数字、限制、版本、时间、成本
- 当前分支 / 提交 / 未提交状态
- 未提交或部分完成的工作
- 未解决的问题和阻塞项
- 最佳下一步行动

丢掉的东西：问候语、鼓励话、反复的来回讨论、原始代码转储、没影响结果的闲聊、助手对下一步的自说自话。信号留下，噪音扔掉。

## 随处可用

`handoff` 就是纯文本，哪儿都能用：

- 编程工具（Claude Code、Cursor、Copilot、Windsurf）
- CLI 工具（基于终端的 AI 助手）
- GUI 聊天工具（ChatGPT、Claude chat、Gemini）
- 任何可以将文本粘贴到新对话的产品

不需要任何集成。

## 何时使用

- 对话太长，模型开始变迟钝了
- 做了一部分工作，想开个干净的新会话
- 快撞上下文限制了
- 想留住决策，但不想拖着整条旧线程
- 在不同机器或工具之间切换

## 安装

把下面这行复制到你的 AI 工具里：

```text
Help me install this skill: https://github.com/wallmage/handoff
```

## 使用方法

在旧对话里：

```text
handoff
```

复制生成的传输块。开新会话。粘贴。

就这样。

---

作者：[Wallny](https://github.com/wallmage)
