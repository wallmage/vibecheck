# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**你的 AI 程式開發工具正在燒你看不到的錢。**

你送出的每則訊息，AI 都會從頭重新讀一遍*整段*對話紀錄。第 50 則訊息的成本是第 1 則的 50 倍。AI 說「好的，我現在來修復這個」？花了你的錢但什麼都沒做。那 500 行建置日誌？之後的每一則訊息都會重新讀一遍。

大多數 Vibe Coder 在不知不覺中浪費了**超過 50%** 的 AI Token 預算。

vibecheck 解決這個問題。掃描最近 14 天的工作階段，精確找出浪費在哪裡，用白話解釋（不用術語——我們會教你什麼是 Token），然後在你的設定檔加一段話就搞定。活照做，錢省一半。

**平均節省：50%+ 的 Token 帳單。** 支援所有 LLM 模型（Claude、GPT、Gemini、DeepSeek）。支援 Claude Code、OpenClaw、Codex、OpenCode 等 24+ 種 AI 程式開發工具。100% 本機執行——你的資料永遠不會離開你的電腦。

## 立即開始——不需要下載任何東西

vibecheck 是一個**技能**——一組你的 AI 程式開發工具可以學習的指令。你不需要下載或安裝任何軟體。只需給你的 AI 一個連結，它就會自己學會如何優化成本。一則訊息搞定。

**把這段話複製貼上到你的 AI 程式開發工具裡**（Claude Code、Cursor、Codex、Windsurf、Cline——任何一個都行）：

> 從 https://github.com/wallmage/vibecheck 安裝 vibecheck 技能，然後執行 /vibecheck scan

就這樣。你的 AI 讀取技能，掃描最近 14 天，然後一步步教你。

**或者用命令列：**
```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

**沙盒工具（Cowork 等）：**
> 把 https://github.com/wallmage/vibecheck 克隆到 /tmp/vibecheck，讀取 SKILL.md，然後執行 /vibecheck scan

### 什麼是「技能」？

技能就像給你的 AI 一張食譜。它不會修改你的 AI，也不會在你電腦上安裝任何東西。它只是給你的 AI 一組指令——「怎麼找浪費模式、怎麼解釋、怎麼修復」。你的 AI 讀了食譜就照著做。隨時可以移除。

### 程式開發工具 vs 聊天工具

**程式開發工具**（Claude Code CLI、Claude Desktop Builder/Code 模式、Cursor、Codex、Windsurf、Cline）直接在你的電腦上執行，能讀取會話日誌，給你完整個性化掃描。

**聊天/沙盒工具**（Claude Cowork 等）執行在沙盒裡——能看到專案檔案但看不到聊天紀錄。

1. **不掃描（80% 效果）：** 優化設定檔——壓縮 CLAUDE.md、新增省 Token 規則。不需要日誌。
2. **掃描（完整效果）：** 在終端機貼上一行指令，複製最近 14 天日誌（約 20-50 MB）。5 秒搞定。

### 權限

vibecheck 需要存取**專案資料夾**來讀取和編輯設定檔。每次修改前徵求同意。

## 隱私保護

**你的資料永遠不會離開你的電腦。** 沒有伺服器、沒有 API、沒有遙測。作者不可能收集你的資料。程式碼完全開源。

## 命令

- `/vibecheck scan` — 互動教學 + 完整診斷 + 修復
- `/vibecheck explain` — 僅教學
- `/vibecheck compress` — 壓縮設定檔（25-50%）
- `/vibecheck monitor` — 週度對比 + 告警

## 15 種浪費模式

**第一層（70-80%）：** 空轉敘述、上下文腐爛、乒乓除錯
**第二層（15-20%）：** 冗長輸出、未串聯命令、程式碼庫漫遊、未批次編輯
**第三層（5-10%）：** 重複讀檔、輪詢等待、失敗重試、Schema 查詢、Git 儀式
**第四層——全天候 Agent：** 空閒心跳、工作區膨脹、記憶堆積

## 支援工具

24+ 種。所有 LLM：Claude、GPT-4o/4.1/o1/o3、Gemini 2.5/2.0、DeepSeek V3/R1。

macOS、Windows、Linux、iPad/手機 via SSH。Python 3.8+，無外部依賴。
