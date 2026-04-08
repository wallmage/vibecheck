# handoff

[English](README.md) | [中文](README.zh-CN.md) | 繁體中文 | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

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

**你的對話在衰減，這個工具讓訊號保持鮮活。**

每個 AI 對話都有半衰期。執行緒越長，模型重複閱讀的過時上下文越多，輸出品質越差，浪費在雜訊上的 token 也越多。你知道解決辦法：開個新會話。但你會遺失已經做出的決策、追蹤過的 bug、敲定的架構方案。所以你繼續在舊執行緒裡硬撐，品質持續下降。

`handoff` 打破了這個惡性循環。在任意會話中說 `handoff`，它會產生一個傳輸區塊——無損壓縮，2-4K token——擷取所有重要資訊：決策、發現、失敗、目前狀態、未解決的問題和下一步行動。貼到新對話中，你就能以全速繼續工作，零重複探索。

沒有檔案，沒有外掛，沒有資料庫。只需複製貼上。

## 運作原理

**產生模式** -- 在舊會話中說 `handoff`。技能透過無損壓縮將整個對話壓縮成結構化傳輸區塊。這不是隨意的回顧。它保留具體成果——做了什麼決定、什麼失敗了、什麼做了一半、下一步是什麼——同時去掉問候語、閒聊、重複說明和原始日誌。

**恢復模式** -- 將傳輸區塊貼到新會話中。技能會解析它，給你一個簡潔的目前狀態摘要，然後等待你的下一個指令。

傳輸區塊目標大小為 **2-4K token**。小到可以頻繁使用，密到不會遺失任何重要資訊。

## 自然觸發詞

不需要記住特殊指令。以下任何一個都可以：

- `handoff`
- `hand off`
- `new session`
- `switch session`
- `start fresh`
- `wrap up and hand off`

## 保留的內容

- 決策及其原因
- 技術發現和機制
- 失敗的實驗及失敗原因
- 重要數字、限制、版本、時間、成本
- 目前分支 / 提交 / 未提交狀態
- 未提交或部分完成的工作
- 未解決的問題和阻塞項
- 最佳下一步行動

被丟棄的內容：問候語、鼓勵話、重複的來回討論、原始程式碼傾印、沒有改變任何結果的閒聊、助手關於接下來要做什麼的敘述。訊號留下，雜訊消失。

## 隨處可用

`handoff` 基於純文字運作，適用於：

- 程式開發工具（Claude Code、Cursor、Copilot、Windsurf）
- CLI 工具（基於終端機的 AI 助手）
- GUI 聊天工具（ChatGPT、Claude chat、Gemini）
- 任何可以將文字貼到新對話的產品

無需特殊整合。

## 何時使用

- 目前對話過長，模型開始變遲鈍
- 完成了一部分工作，想要一個乾淨的新會話
- 即將觸達上下文限制
- 想保留決策但不想保留完整的舊執行緒
- 在不同機器或工具之間切換

## 安裝

將以下內容複製到你的 AI 工具中：

```text
Help me install this skill: https://github.com/wallmage/handoff
```

## 使用方法

在舊對話中：

```text
handoff
```

複製產生的傳輸區塊。開啟新會話。貼上。

就這麼簡單。

---

作者：[Wallny](https://github.com/wallmage)
