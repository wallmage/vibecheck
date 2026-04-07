# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**你的 AI 程式開發工具正在燒你看不到的錢。**

你送出的每則訊息，AI 都會從頭重新讀一遍*整段*對話紀錄。第 50 則訊息的成本是第 1 則的 50 倍。AI 說「好的，我現在來修復這個」？花了你的錢但什麼都沒做。那 500 行建置日誌？之後的每一則訊息都會重新讀一遍。

大多數 Vibe Coder 在不知不覺中浪費了**超過 50%** 的 AI Token 預算。

vibecheck 解決這個問題。掃描最近 14 天的工作階段，精確找出浪費在哪裡，用白話解釋（不用術語——我們會教你什麼是 Token），然後在你的設定檔加一段話就搞定。活照做，錢省一半。

**平均節省：50%+ 的 Token 帳單。** 支援所有 LLM 模型。支援 Claude Code、OpenClaw、Codex、OpenCode 等 24+ 種 AI 程式開發工具。100% 本機執行——你的資料永遠不會離開你的電腦。

```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

## 隱私保護

**你的資料永遠不會離開你的電腦。** 沒有伺服器、沒有 API、沒有遙測、沒有資料分析。作者不可能收集你的資料——技術上做不到。程式碼完全開源。

## 安裝

**AI 程式開發工具（完整體驗）：** `claude install-skill https://github.com/wallmage/vibecheck`，然後 `/vibecheck scan`。

**沙盒環境（Cowork 等）：** 即使不掃描日誌也能獲得 80% 的效果——壓縮設定檔、新增省 Token 規則。完整掃描只需在終端機貼上一行指令，複製最近 14 天的日誌（約 20-50 MB）。

## 命令

- `/vibecheck scan` — 互動教學 + 完整診斷 + 修復
- `/vibecheck explain` — 僅教學
- `/vibecheck compress` — 壓縮設定檔（縮小 25-50%）
- `/vibecheck monitor` — 週度對比 + 異常告警

## 15 種浪費模式

找出空轉敘述、上下文腐爛、乒乓除錯、冗長輸出、未串聯命令、程式碼庫漫遊、未批次編輯、重複讀檔、輪詢等待、失敗重試、Schema 查詢、Git 儀式，以及全天候 Agent 的空閒心跳、工作區膨脹、記憶堆積。

## 支援工具

24+ 種：Claude Code、Cursor、Codex、Windsurf、Cline、OpenClaw、CodeBuddy（騰訊）、通義靈碼（阿里）、TRAE（字節）、Kimi Code（月之暗面）等。

支援所有 LLM：Claude (Opus/Sonnet/Haiku)、GPT-4o/4.1/o1/o3、Gemini 2.5/2.0、DeepSeek V3/R1。
