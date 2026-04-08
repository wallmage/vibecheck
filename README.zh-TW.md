# vibecheck

[![GitHub stars](https://img.shields.io/github/stars/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck/network/members)
[![GitHub watchers](https://img.shields.io/github/watchers/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck/watchers)
[![GitHub last commit](https://img.shields.io/github/last-commit/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck/commits/main)
[![GitHub repo size](https://img.shields.io/github/repo-size/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Top language](https://img.shields.io/github/languages/top/wallmage/vibecheck?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Privacy](https://img.shields.io/badge/privacy-local%20only-111827?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Coverage](https://img.shields.io/badge/coverage-24%2B%20tools-0f766e?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Platforms](https://img.shields.io/badge/platforms-macOS%20%7C%20Linux%20%7C%20Windows-4f46e5?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Focus](https://img.shields.io/badge/focus-cost%20optimization-b45309?style=flat-square)](https://github.com/wallmage/vibecheck)
[![Works with](https://img.shields.io/badge/works%20with-Claude%20%7C%20Codex%20%7C%20Gemini-2563eb?style=flat-square)](https://github.com/wallmage/vibecheck)

[English](README.md) | [中文](README.zh-CN.md) | 繁體中文 | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

我一直在下午就把 Claude 額度用完，搞不懂為什麼。後來發現，我大部分的 AI 程式開發過程有 70% 都是浪費——AI 在那邊預告它接下來要做什麼、明明一次就能完成的指令硬拆成三個回合、過時的上下文不斷堆積，每一回合都被重新讀取一遍。

vibecheck 就是專門找出這些浪費的。它讀取你在 24 種以上程式開發工具中的實際對話紀錄，針對 15 種特定模式標上金額，然後修正它們。一切都在本機執行。不上傳、不回報、不連伺服器。

以我自己為例：每月花費從 $2,816 降到 $422。**省了 85%。**

## 安裝方式

把這段貼到你的 AI 程式開發工具裡，按 Enter：

> Help me install this skill: https://github.com/wallmage/vibecheck

就這樣。AI 會自動載入這個 skill，你就可以開始掃描了。

<details>
<summary>或透過命令列手動安裝</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

然後在任何 session 輸入 `/vibecheck scan`。

更新方式：`cd ~/.claude/skills/vibecheck && git pull`
</details>

### 什麼是「skill」？

一個純文字檔，教你的 AI 學會新能力。沒有二進位檔、沒有背景程序、不會改動系統。vibecheck 的 skill 檔案就是告訴 AI「怎麼找出浪費並修正」。把資料夾刪掉就移除了。

### 程式開發工具 vs. 聊天工具

**程式開發工具**（Claude Code、Codex、Cursor、OpenClaw、Copilot、Windsurf、TRAE、Qoder 等）在你的電腦上執行，會留下 session 紀錄。vibecheck 自動偵測你安裝了哪些，直接掃描那些紀錄。

**聊天工具**（Cowork、瀏覽器版 Claude）在沙盒環境執行，沒有本機紀錄。vibecheck 仍然可以最佳化你的指令檔——其實大部分的節省就是從指令檔來的。你也可以貼一行終端指令匯出 14 天的紀錄來做完整掃描。

### 權限

vibecheck 會讀取你的本機 session 紀錄，並檢查指令檔（`CLAUDE.md`、`AGENTS.md`、`Memory.md`）以及全域工具設定。如果你的工具有一個涵蓋所有專案的全域設定檔，最佳化器會先處理那邊，因為改一處就能省全部。它在修改任何東西之前都會先問你。

## 隱私

一切都留在你的電腦上。分析工具是一組 Python 腳本，解析你的本機 session 紀錄。沒有伺服器、沒有 API 呼叫、沒有數據追蹤。完全開源——想看的話每一行都可以看。

## 指令

| 指令 | 功能 |
|---|---|
| `/vibecheck scan` | 掃描你電腦上偵測到的所有工具。產生一份統整報告，包含健康指標、排序統計、主要浪費模式和最佳化路線圖 |
| `/vibecheck explain` | 教你認識各種浪費模式，不做任何修改。純粹學習用 |
| `/vibecheck compress` | 用 4 階段無損壓縮器將你的指令檔縮小 25-50% |
| `/vibecheck monitor` | 每週與基準線比較。在成本回升之前就抓到問題 |

掃描過程很安靜：一個簡潔的進度指示器，然後是清楚的摘要。`Good` 表示測量到的浪費低於 10%，`Waste` 表示高於 10%。原始紀錄和工具細節除非出問題，否則不會顯示。

### 保持 session 精簡

長對話比短對話貴——每一個新回合都會重新讀取所有舊回合，而且過載的上下文會讓 AI 變笨，導致更多來回溝通。

經驗法則：每個 session 5-10 分鐘的有效作業，30-40 回合之後上下文的額外成本就會變得很明顯。開新 session 時，把持久性的規則放在指令檔（`CLAUDE.md`、`AGENTS.md`、`Memory.md`），專案背景放在小型本機文件。開新 session 不代表從頭來過——只是一個乾淨的上下文，你的知識全部還在。

---

## 使用前 / 使用後

根據實際 session 測量：

```
                          使用前         使用後          變化
Avg turns/session         73.9           21.1           -52.8
Avg context window        65.6K          33.7K          -49%
Wasteful turns            73.7%          8.0%           -65.7%

Avg cost/session          $3.07          $0.46          -$2.61
Monthly spend             $2,816         $422           -$2,394
```

---

## AI 回合如何產生費用

如果你從沒想過 token 經濟學，這裡有個簡短入門。不需要 AI 定價背景知識。

### 每個回合發生了什麼

每次 AI 回應時，它都會從頭重新讀取整段對話。系統提示、指令檔、你發送的每條訊息、它給的每個回應、所有工具輸出——檔案內容、終端結果、錯誤紀錄——全部。然後才產生新的回應。

**回合成本 = 讀取的 token 數 x 輸入價格 + 產生的 token 數 x 輸出價格**

早期的回合很便宜。第 1 回合可能讀取 5,000 個 token。到了第 40 回合，它要重新讀取 40,000 多個 token 的累積對話——之前的每條訊息、每段程式碼、每條錯誤追蹤。那個晚期回合的成本是第一回合的 8 倍。

關鍵在於浪費會**複利累積**。一個浪費的回合不只花費它自己的 token 成本，它會留在上下文裡，在 session 剩餘的每個回合都被重新讀取。第 10 回合一條不必要的解說訊息，在你結束前還會被重讀 30 次。

### Prompt cache 有幫助，但解決不了根本問題

大多數供應商現在會快取之前看過的內容，收費降低 10 倍。有效輸入成本從 $3.00/百萬 token 降到 $0.30/百萬。

這有幫助。但新內容——新的工具輸出、新的錯誤訊息、每次新的 AI 回應——剛出現時都是全價，之後才會被快取。而且即使在快取費率下，浪費仍然會複利累積。

### 訂閱制也有同樣的痛點

如果你是訂閱用戶，可能覺得 API 定價跟你無關。其實有關——只是感受方式不同。訂閱買的是固定的運算額度，浪費會更快耗盡那個額度。當你在下午 3 點就被限速，不是因為你工作太多，而是因為很多工作都是浪費。

Claude Pro ($20/月) 大約涵蓋 $200 的 API 等值額度。Claude 20x Max ($200/月) 大約涵蓋 $4,000。浪費越多 = 越快碰壁。

<details>
<summary><strong>深入探討：你的訂閱實際上值多少 token</strong></summary>

### 測量方式

我訂的是 $200/月的 Claude 20x Max 方案，但一直用完額度。好奇之下切換到 API 計費，用超過 100 個數據點追蹤真實花費——記錄每次程式開發活動，完成後立刻查看用量。這讓我能算出訂閱價格與實際 token 價值之間的關係。

### 倍率

| 方案 | 價格 | API 價值 | 倍率 | 5 小時區間 | 每週總額 |
|---|---|---|---|---|---|
| Claude Pro | $20/月 | ~$200 | 10x | $6.67 | $46.67 |
| Claude 5x Max | $100/月 | ~$1,000 | 10x | $33.33 | $233.31 |
| Claude 20x Max | $200/月 | ~$4,000 | 20x | $133.33 | $933.31 |

20x Max 是唯一有真正倍率提升的層級——面值的 20 倍，而低層級只有 10 倍。

### 實際意義

- **$20 Claude Pro** ——認真的開發工作（寫功能、研究、寫文件）不到一小時就會燒完你的 5 小時額度。每週容量不到 7 小時。對專業用途來說很吃緊。
- **$100 5x Max** ——大約 4 小時會碰到 5 小時的限制。每週合計 30-35 小時。日常使用還算夠。
- **$200 20x Max** ——為每週工作 80-100 小時以上、經常同時跑多個 session 的人設計。

### 為什麼 Anthropic 限制了第三方訂閱用量

在 10-20 倍面值的情況下，每一元訂閱都買到遠超 API 費率的運算量。第三方工具以 API 等值速度消耗這些額度，讓這筆帳算不下去。

### Codex 替代方案

在 $20 層級，Codex Plus 提供大約 **3 倍於 Claude Pro 的程式開發用量**。ChatGPT 對話——即使是 GPT-5.4 Extended Thinking 和深度研究——不計入 Codex 程式開發額度。所以你得到 3 倍的程式開發容量，外加免費的 GPT-5.4。

**如果你的預算是 $20/月，Codex Plus 比 Claude Pro 給你更多的程式開發時間。** 如果你願意花更多，Claude 5x 和 20x 層級有不同的價值定位。

</details>

### 參考情境

本文件中所有金額皆使用此基準（Sonnet 4.6 定價）：

| 參數 | 數值 |
|---|---|
| Session 長度 | 25 回合 |
| 起始上下文 | 21,000 tokens |
| 每回合增長 | ~600 tokens |
| Cache 命中率 | 95% |
| Session 中段回合成本 | $0.017 |
| 高效 session 總成本 | $0.41 |

若使用 Opus 4.6，所有成本乘以 1.67 倍。

---

## 15 種浪費模式

依照燒錢程度排列。光是前三名就佔了所有浪費的 60-70%。

### 第一級——三大元兇（佔 60-70% 的浪費）

#### 1. 閒置解說

AI 說「好的，我現在來修」或「讓我先讀一下檔案」——然後在下一回合才真正動手。那個解說回合什麼也沒做。沒有工具呼叫、沒有程式碼、沒有讀檔。只是一個預告。

每次大約花 **$0.017**——更糟的是，那 300-500 個 token 的狀態文字會留在上下文裡，在之後每個回合都被重新讀取。在 428 個 session 的測量中：**每個 session 浪費 $1.03**，佔所有浪費的 30%。以每天 10 個 session 計算，**光是解說就要花 $309/月。**

vibecheck 加了一條規則：*「每個回合都要有工具呼叫。在同一回合思考並行動。」* **每個 session 節省約 $0.88。**

#### 2. 上下文腐化

Session 成本呈二次方增長，不是線性的。第 50 回合要重讀前面所有 49 個回合。

具體比較：一個 40 回合的 session 花 **$0.70**。把同樣的工作拆成兩個 20 回合的 session 則是 **$0.60**。那 $0.10 的差距純粹就是維持臃腫對話的浪費。真實 session 平均有 74 個回合——**每個 session 浪費 $0.46**，佔所有浪費的 13%。

vibecheck 教你：*「不相關的工作放到不同 session。長對話裡保持精簡。」* **每個 session 節省約 $0.37。**

#### 3. 乒乓式除錯

修了、壞了、再試、又壞。每次失敗嘗試會把約 4,000 個 token 的錯誤輸出灌進上下文，而那些無用文字在之後每個回合都會被重讀。三個循環：6 個額外回合 ($0.102) + 12K 個過時錯誤 token ($0.036) = **每次約 $0.14**。出現在約 10% 的 session 中。**加權後：每個 session $0.015。**

vibecheck 加了斷路器：*「同一個檔案修了 2 次還失敗——停下來，重新讀完整的錯誤訊息，思考，一次精準修復。」* **每個 session 節省約 $0.01。**

### 第二級——回合密度（佔 15-20% 的浪費）

把一個回合就能做完的事拆成三個。

#### 4. 冗長的工具輸出

一個 build 或測試指令把 500 行（約 5,000 個 token）灌進對話。這些 token 在 session 剩餘的每個回合都會被重讀。5K token x 12 個剩餘回合，以快取費率計算 = **每次 $0.018**。沒有快取的話：**$0.180**——貴 10 倍。

這其實是測量中單次成本最高的模式。Build 紀錄、npm 輸出、測試結果——幾乎淹沒每個 session。**每個 session $1.05**，佔所有浪費的 31%。

修正：*「把輸出導到 /tmp/。使用 --quiet 旗標。最多 tail -50。」* **每個 session 節省約 $0.89。**

#### 5. 未串接的指令

`npm install` 一個回合。`npm run build` 下一個回合。兩次上下文重讀，而 `npm install && npm run build` 一次就夠了。每次拆分：**$0.010**。在指令密集的 session 中累計 **每個 session $0.14**。

修正：*「安全時用 `&&` 串接指令。」* **每個 session 節省約 $0.11。**

#### 6. 程式碼庫漫遊

AI 先開 README、package.json、三個設定檔、兩個不相關的模組，然後才寫一行程式碼。連續五次讀取，沒有編輯、沒有決策。浪費的回合 $0.085 + 上下文稅 $0.027 = **每次 $0.112。** 平均：**每個 session $0.09。**

修正：先用 grep 或 glob，只讀相關的，每個回合批次處理多個讀取。**每個 session 節省約 $0.07。**

#### 7. 未批次的編輯

編輯檔案 A，然後 B，然後 C——三個回合。一個回合用平行編輯就能完成。兩個額外回合 x $0.017 = **每次 $0.034。** 平均：**每個 session $0.058。**

修正：*「批次處理獨立的工具呼叫。」* **每個 session 節省約 $0.05。**

### 第三級——長尾（佔 5-10% 的浪費）

單獨看很小，但會累積。

#### 8. 重複讀檔

同一個檔案在一個 session 裡被讀了兩次——內容已經在上下文裡了，但 AI 又抓了一次。**每次重讀 $0.019**，檔案平均被重讀 3-4 次。**每個 session $0.066。** 修正：*「已經在上下文裡了。只有檔案有改動才重讀。」* **每個 session 節省約 $0.05。**

#### 9. Sleep/Poll 迴圈

`sleep 5 && check_status`，重複 3-5 次。每次 poll = 完整的上下文重讀，只為了看一個背景程序有沒有完成。4 次 poll x $0.017 = **每次 $0.068**，**每個 session $0.043。** 修正：*「用 --wait 或 run_in_background。」* **每個 session 節省約 $0.034。**

#### 10. 失敗重試

指令失敗，AI 原封不動重跑同一個指令。錯誤輸出現在在上下文裡出現兩次。**每次重試 $0.019**，**每個 session $0.080。** 修正：跟乒乓式除錯一樣——*「停下來，讀錯誤訊息，試不同的方法。」*

#### 11. Schema 查詢

AI 去查自己的工具定義——它本來就有的資訊。白白增加 2K+ 個 token。**每個 session $0.023。**「每個回合都要有工具呼叫」的規則就能解決這個問題。**每個 session 節省約 $0.02。**

#### 12. Git 繁文縟節

`git add` → `git status` → `git commit` → `git push`。四個回合。`git add -A && git commit -m "msg" && git push` 只要一個。**每次 $0.044** 但比你想像的少見——**每個 session $0.003。** 修正：用 `&&` 串接。

### 第四級——全時運作的 Agent

不同的成本模型。像 OpenClaw 這類 agent 會定期喚醒，浪費以每天而非每個 session 計算。

#### 13. 閒置心跳

Agent 每 5 分鐘喚醒一次，重讀整個工作區，發現沒事，繼續睡。每天 288 次喚醒，約 97% 閒置。也就是 280 次閒置喚醒，每次 $0.04 = **每天 $11.20（每月 $336）** 什麼都沒做。

修正：*「最低 30 分鐘心跳。沒有待處理觸發就跳過。」* 降到每天約 48 次喚醒。**每天節省 $8-10（每月 $240-300）。**

#### 14. 工作區檔案膨脹

35,000 個 token 的人格設定檔（SOUL.md、AGENTS.md 等）在每次喚醒時都被重讀。教學、輔導、哲學——都是為人類寫的，不是為了執行任務的 AI。**每天 $5.76（每月 $173）** 光在設定檔上。

vibecheck 壓縮它們：35K → 12-15K token。相同的行為規則，去掉人類導向的填充內容。**每天節省 $3-4（每月 $90-120）。**

#### 15. 記憶累積

Session 歷史無限增長。100 多條記憶項目在每次喚醒時被重讀，包括幾週前已經不重要的東西。**每天 $3.17（每月 $95）** 花在過時的記憶上。

修正：*「超過 50 條就歸檔，摘要，重新開始。」* **每天節省 $2-3（每月 $60-90）。**

---

## 最佳化工具集

vibecheck 不只指出問題，它還修正問題。

### 指令檔壓縮

你的指令檔（`CLAUDE.md`、`AGENTS.md`、`Memory.md`，不管你的工具叫它什麼）在每個回合都會被讀取。它是你做的每件事都要繳的固定稅。臃腫的指令檔就像城裡每條路上都設了收費站。

vibecheck 有一個 4 階段無損壓縮器——23 種技術，「無損」的意思就是不刪除任何事實。相同資訊，更少 token。

| 階段 | 功能 | 節省幅度 |
|---|---|---|
| **第 1 階段——機械式** | 去除 markdown 格式、將表格轉為精簡形式、合併項目符號 | 10-15% |
| **第 2 階段——保留事實** | 去除重複事實、壓縮程式碼範例、摺疊冗長描述 | 15-25% |
| **第 3 階段——高保真** | 移除人類需要但 AI 不需要的教學和輔導文字 | 10-15% |
| **第 4 階段——電報式** | 為純 AI 檔案做完整的簡寫重寫。密集、壓縮，但必須經過你明確同意 | 15-25% |

一個 10,000 token 的指令檔壓縮到 6,000 可以每個 session 省 $0.044。以每天 10 個 session 計算：**光壓縮就省 $0.44/天（$13/月）。**

### 輸出抑制

輸出 token 的成本是輸入的 5 倍（Sonnet 4.6 上 $15 vs. $3/百萬）。AI 印出你沒要求的完整程式碼區塊或 diff？很貴。vibecheck 加了：*「除非被要求，否則不輸出程式碼或 diff。」* **每個 session 節省約 $0.047。**

### 成本監控

`/vibecheck monitor` 對你的 session 概況做快照，並在之後的執行中與基準線比較。新的指令檔引入了冗長內容？不同專案、不同習慣？監控會在成本回升之前抓到問題。

---

## 節省摘要

### 互動式工具（Sonnet 4.6 定價）

| # | 模式 | 平均浪費/session | 平均節省 |
|---|---|---|---|
| 1 | 閒置解說 | $1.03 | $0.88 |
| 2 | 上下文腐化 | $0.46 | $0.37 |
| 3 | 乒乓式除錯 | $0.015 | $0.01 |
| 4 | 冗長輸出 | $1.05 | $0.89 |
| 5 | 未串接指令 | $0.14 | $0.11 |
| 6 | 程式碼庫漫遊 | $0.09 | $0.07 |
| 7 | 未批次編輯 | $0.058 | $0.05 |
| 8 | 重複讀檔 | $0.066 | $0.05 |
| 9 | Sleep/poll 迴圈 | $0.043 | $0.034 |
| 10 | 失敗重試 | $0.08 | $0.06 |
| 11 | Schema 查詢 | $0.023 | $0.02 |
| 12 | Git 繁文縟節 | $0.003 | $0.003 |
| + | 壓縮 | $0.044 | $0.044 |
| + | 輸出抑制 | $0.047 | $0.038 |
| | **合計** | **$3.15*** | **$2.61** |

*個別模式可能在同一回合中同時發生——合計反映的是每個模式各自的測量。實際總計：$3.07 降到 $0.46（見使用前/使用後）。

**典型高浪費 session：$3.07。使用 vibecheck 後：$0.46。節省 85%。**

- **輕度浪費**（短 session、少數模式）：減少 40-55%
- **中度浪費**（一般使用者）：減少 55-70%
- **重度浪費**（長 session、多種模式）：減少 70-85%

### 全時運作的 agent

| # | 模式 | 每日浪費 | 每日節省 |
|---|---|---|---|
| 13 | 閒置心跳 | $11.20 | $9.70 |
| 14 | 工作區膨脹 | $5.76 | $3.76 |
| 15 | 記憶累積 | $3.17 | $2.37 |
| | **合計** | **$20.13/天** | **$15.83/天** |

**全時運作 agent 的每月節省：約 $475。**

---

## 支援的工具

24 種以上工具。不綁定——vibecheck 是純文字檔，任何能讀取指令的 AI 都能用。掃描腳本是純 Python，無需額外套件。

**完整 session 掃描**（讀取你的紀錄，為浪費標上金額）：
Claude Code、Codex、Cursor、OpenClaw、GitHub Copilot、Windsurf、TRAE、Qoder、CodeBuddy、WorkBuddy、Google Antigravity

**偵測 + 指令最佳化**（尚未支援完整紀錄解析，但能偵測工具並最佳化你的設定檔）：
Cline、Roo Code、Kilo Code、Aider、Gemini CLI、OpenCode、Augment、Kimi Code、MarsCode、Tongyi Lingma、Baidu Comate、CodeGeeX、DevChat、MiniMax

**內建定價資料的 LLM：** Claude Opus/Sonnet 4.6、GPT-5.4、Gemini 3.1 Pro、DeepSeek V3.2、Qwen 3.6、Kimi K2.5、GLM-5、MiniMax M2.7，以及 40 種以上。

**平台：** macOS、Windows、Linux、iPad via SSH。Python 3.8+。

---

<details>
<summary><strong>方法論</strong></summary>

所有成本估算使用上述參考情境。主要假設：

- **95% prompt cache 命中率** ——快速程式開發 session 的典型值。回合間隔較長的慢速 session 命中率會較低，成本較高。
- **每個 session 25 個有效回合** ——浪費型 session 因解說、重試和未串接指令會多出 8-12 個額外回合。
- **每回合增長 600 token** ——冗長的 session 每回合可達 1,000-2,000 token。
- **有效輸入費率：$0.435/1M** ——95% 快取 ($0.30/1M) + 5% 未快取 ($3.00/1M) 的混合費率。
- **上下文稅費率：$0.30/1M** ——永久上下文新增項目的快取輸入費率。

保守估計。實際節省通常會超過這些，特別是長 session、大型指令檔或大量除錯的情況。
</details>

## 作者

[Wallny](https://github.com/wallmage)
