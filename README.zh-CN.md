# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**你在为 AI 重复读自己说过的话买单。**

你每发一条消息，AI 都会把整个对话从头读一遍。从第一条开始。第 50 条消息发出去之前，AI 先读完了前面 49 条。AI 打了句"好的，我来修"？这句话本身没干任何事——但你花了钱，而且之后每一轮它都会被重新读一遍，继续花钱。

我拿自己的会话跑了一遍。超过一半的 token 花费是浪费。不是个别情况——几乎每个会话都有这些模式。

vibecheck 扫你最近 14 天的 AI 编程会话，告诉你钱花哪了，然后在你的配置文件里加一段话，把大部分浪费堵住。活一样干，账单少一半。

支持所有模型——Claude、GPT、Gemini、DeepSeek、Qwen、Kimi、GLM、MiniMax。支持 Claude Code、Codex、Cursor、OpenClaw、Copilot、Windsurf、TRAE、Qoder 等 24 种工具。本地运行，数据不出你的电脑。

## 不用装任何东西

vibecheck 是个 **skill**——可以理解为一份给 AI 看的攻略。不用下载，不用安装。你贴一条消息，AI 自己就学会了。

把这句话贴到你用的 AI 编程工具里（Claude Code、Cursor、Codex、Windsurf、Cline，都行）：

> 从 https://github.com/wallmage/vibecheck 安装 vibecheck 技能，然后运行 /vibecheck scan

搞定。AI 读完攻略，扫你的会话，然后一步步跟你说哪里在烧钱。

用 Claude Code CLI 的话：
```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

用沙盒工具（Cowork 之类）的话：
> 把 https://github.com/wallmage/vibecheck 克隆到 /tmp/vibecheck，读 SKILL.md，然后运行 /vibecheck scan

### skill 是啥？

一份攻略。不改你的 AI，不装东西。就是一个文本文件，写着"怎么找浪费、怎么解释、怎么修"。AI 读完照做。不想要了随时删。

### 编程工具和聊天工具的区别

**编程工具**（Claude Code、Cursor、Codex、Windsurf、Cline）跑在你电脑上，能读会话日志。扫出来有具体数字——哪个会话最贵、哪个模式烧了多少 token、折合多少钱。

**聊天工具**（Cowork、浏览器里的 AI）跑在沙盒里，看不到你的日志。vibecheck 还是能用：

1. **不扫也行（能拿到 80% 的效果）。** vibecheck 帮你精简 CLAUDE.md，加上规则让 AI 别废话、合并编辑、串联命令。不用碰日志。光这些就能省 20-40%。

2. **把日志拷出来（5 秒的事）。** 在终端贴一条命令，拷 14 天的日志到沙盒能看到的地方，然后跑完整扫描。

### 权限

vibecheck 要读写你的配置文件（CLAUDE.md、AGENTS.md、.cursorrules 之类的）。改之前会问你，你逐条批。

## 隐私

数据不出你的电脑。没有服务器。就几个 Python 脚本，读本地文件，结果打在屏幕上。开源的，不信自己看。

## 命令

- `/vibecheck scan` — 教你 token 是什么、扫你的会话、上修复
- `/vibecheck explain` — 只讲课，不改东西
- `/vibecheck compress` — 把配置文件压缩 25-50%
- `/vibecheck monitor` — 每周对比，有退步会提醒

## 到底干了什么

大部分人不知道自己在为什么付费。Claude $20/月 的订阅背后大概有 $200 的实际 API 消耗。钱花哪了？

vibecheck 用你自己的数据走一遍：
1. Token 是什么（大概一个词一个）
2. 为什么 AI 每条消息都把整个对话重读一遍（钱主要花在这）
3. 你具体哪些模式在烧钱，烧了多少

然后在配置文件里加一段话。AI 读了这些规则就不再干那些浪费的事了。

### 不扫也有用

装上 skill 你的 AI 就会：
- 别说"我现在来修"了直接修（省一轮）
- 三个文件一条消息改完，别分三条
- `git add && git commit` 一条搞定，别分两轮
- 对话长了清一下，别让上下文越来越贵
- 构建输出导到文件里，别在聊天里刷 500 行

大头省在这。扫描找剩下的。

## 前后对比

跑一次看预估，过两周再跑一次看实际变化：

```
                              之前           现在           变化
  平均轮次/会话                 36.8           25.9           -10.9 ✅
  平均上下文大小                128.4K         89.9K          -30% ✅
  浪费的轮次                   36.7%          8.1%           -28.6% ✅
  平均成本/会话                 $2.62          $1.35          -$1.27 ✅
  月花费                       $224           $115           -$109 ✅
```

快照存在 `~/.vibecheck/snapshots/`，重启不丢。

## 15 种浪费模式

**三大杀手（占浪费的 70-80%）**
1. 空话——"我来修一下"→ 直接修
2. 上下文越来越贵——60 轮的对话，最后一轮的成本是第一轮的 60 倍
3. 反复改坏——改了坏、坏了改、改了又坏

**机械浪费（15-20%）**
4. 刷屏——500 行构建日志，之后每轮都重读
5. 命令不串——`git add` 和 `git commit` 分两条发
6. 到处翻——改 1 个文件之前先读了 8 个
7. 编辑不合并——3 个文件分 3 条消息改

**零碎（5-10%）**
8. 重复读文件
9. 轮询——每 5 秒问一次"好了没"
10. 失败重试——报错信息留在上下文里一直被重读
11. 查工具列表——其实 AI 已经知道了
12. Git 仪式——4 条 git 命令分 4 轮发

**全天候 Agent（OpenClaw 之类）**
13. 空转心跳——每 5 分钟醒一次，没事干，照样收费
14. 人设膨胀——每次醒来重读 35K token 的人设文件
15. 历史堆积——会话记录越来越长，从不清理

## 支持的工具

自动检测你用的是哪个，24 种都支持：

Claude Code、Codex、Cursor、Windsurf、Cline、Roo Code、Kilo Code、Aider、Gemini CLI、Copilot、OpenCode、OpenClaw、Augment、CodeBuddy（腾讯）、WorkBuddy（腾讯）、TRAE（字节）、Qoder（阿里）、Kimi Code（月之暗面）、MarsCode（字节）、通义灵码（阿里）、百度 Comate、CodeGeeX（智谱）、DevChat、MiniMax。

所有模型：Claude Opus/Sonnet 4.6、GPT-5.4、Gemini 3.1 Pro、DeepSeek V3.2、Qwen 3.6、Kimi K2.5、GLM-5、MiniMax M2.7 等 40+ 个模型。

## 运行环境

macOS、Windows、Linux、iPad via SSH。Python 3.8+，没有依赖。
