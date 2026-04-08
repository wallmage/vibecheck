# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**AI 每一輪操作都在花你的錢。** Sonnet 大約 $0.03/輪，Opus 大約 $0.15/輪。AI 說了句「好，我來修」然後才去修——這就是一輪浪費，白花錢。更慘的是：每一輪都會把整段對話從頭讀一遍，聊得越長，每輪越貴。這就是上下文膨脹。

AI 程式開發工具到處在浪費輪次——先說要幹嘛再幹、一個檔案一個檔案地讀而不是一起讀、`git add` 和 `git commit` 分兩輪跑。vibecheck 兩招砍浪費：減少輪次（合併、平行、砍廢話）和縮小每輪上下文（壓縮設定檔、清理長對話）。這只是 15 種機制中的 2 種，全部加起來能砍掉 50% 以上的帳單。

支援 Claude、GPT、Gemini、DeepSeek、Qwen、Kimi、GLM、MiniMax。24+ 種工具。本機執行，資料不出你電腦。

## 怎麼安裝

把這句話貼到你的 AI 程式開發工具裡，按 Enter：

> Help me install this skill: https://github.com/wallmage/vibecheck

搞定。AI 自己搞定剩下的。

<details>
<summary>或者用命令列手動安裝</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

然後在任意工作階段輸入 `/vibecheck scan`

更新：`cd ~/.claude/skills/vibecheck && git pull`
</details>

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

24+ 種。所有 LLM：Claude Opus/Sonnet 4.6、GPT-5.4、Gemini 3.1 Pro、DeepSeek V3.2、Qwen 3.6、Kimi K2.5、GLM-5、MiniMax M2.7 等 40+ 個模型。

macOS、Windows、Linux、iPad/手機 via SSH。Python 3.8+，無外部依賴。
