# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**AIの操作1回ごとにお金がかかります。** Sonnet 4.6の料金は$3/$15/MTok（入力/出力）、Opus 4.6は$5/$25——1.67倍。セッション中盤のSonnet 1ターンは約$0.038。AIが「では修正しますね」と言ってから修正する——その$0.031は無駄です。さらに厄介なのは、毎回会話全体を最初から読み直すこと。会話が長くなるほど1回あたりのコストが上がります。これがコンテキスト膨張です。

AIコーディングツールは常にターンを浪費——実行前にナレーション、ファイルを1つずつ読む、`git add`と`git commit`を別々のターンで実行。vibecheckは4層18種のメカニズムを検出し、設定ファイルルールと圧縮で修正、改善を継続追跡。使用パターンに応じて40-65%の削減が可能です。[詳細仕様 →](SPECSHEET.md)

Claude、GPT、Gemini、DeepSeek、Qwen、Kimi、GLM、MiniMax対応。24+ツール。ローカル実行、データは外部に送信されません。

## インストール方法

AIコーディングツールにこれを貼り付けてEnter：

> Help me install this skill: https://github.com/wallmage/vibecheck

以上です。AIが残りを処理します。

<details>
<summary>またはコマンドラインで手動インストール</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

任意のセッションで `/vibecheck scan` を入力

更新：`cd ~/.claude/skills/vibecheck && git pull`
</details>

### 「スキル」とは？

スキルはAIへのレシピカードのようなものです。AIを変更したり、コンピュータに何かをインストールしたりしません。「無駄パターンの見つけ方、説明の仕方、修正の仕方」という指示を渡すだけ。いつでも削除できます。

### コーディングツール vs チャットツール

**コーディングツール**（Claude Code CLI、Cursor、Codex等）はマシン上で直接実行。セッションログを読めるので、完全なパーソナライズされたスキャンが可能。

**チャット/サンドボックスツール**（Claude Cowork等）はサンドボックス内で実行——プロジェクトファイルは見えるがチャット履歴は見えない。

1. **スキャンなし（80%の効果）：** 設定ファイルの最適化。ログ不要。
2. **スキャンあり（完全な効果）：** ターミナルで1行コマンドを貼り付け、直近14日分のみコピー（約20-50 MB）。

### 権限

**プロジェクトフォルダ**へのアクセスが必要です。変更前に必ず確認を求めます。

## プライバシー

**データは一切マシンの外に出ません。** サーバーなし、APIなし、テレメトリなし。コードは完全オープンソースです。

## コマンド

- `/vibecheck scan` — インタラクティブ教育 + 完全診断 + 修正
- `/vibecheck explain` — 教育のみ
- `/vibecheck compress` — 設定ファイル圧縮（25-50%削減）
- `/vibecheck monitor` — 週次比較 + アラート

## 18のメカニズム

**第1層（70-80%）：** 空回りナレーション、コンテキスト劣化、ピンポンデバッグ
**第2層（15-20%）：** 冗長出力、未連結コマンド、コードベース放浪、未バッチ編集
**第3層（5-10%）：** ファイル再読み、スリープ/ポーリング、失敗リトライ、スキーマ検索、Git儀式
**第4層——常時稼働Agent：** アイドルハートビート、ワークスペース肥大化、メモリ蓄積

## 対応ツール

24種以上。全LLM対応：Claude Opus/Sonnet 4.6、GPT-5.4、Gemini 3.1 Pro、DeepSeek V3.2、Qwen 3.6、Kimi K2.5、GLM-5、MiniMax M2.7 他40+モデル。

macOS、Windows、Linux、iPad/モバイル via SSH。Python 3.8+、外部依存なし。
