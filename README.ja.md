# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**あなたのAIコーディングツールは、見えないところでお金を燃やしています。**

メッセージを送るたびに、AIは会話履歴を*全部*最初から読み直します。50番目のメッセージは1番目の50倍のコストがかかります。AIが「では、修正しますね」と言ったあの発言？お金がかかったのに何もしていません。500行のビルドログ？今後の全メッセージで毎回読み直されます。

ほとんどのバイブコーダーは、知らないうちにAIトークン予算の**50%以上**を無駄にしています。

vibecheckがそれを解決します。過去14日間のセッションをスキャンし、無駄がどこにあるか正確に特定し、わかりやすい言葉で説明し（専門用語なし——トークンとは何かからお教えします）、設定ファイルに1段落追加するだけで修正。同じ作業、半分のコスト。

**平均節約：トークン請求の50%以上。** すべてのLLMモデルに対応。Claude Code、OpenClaw、Codex、OpenCodeなど24以上のAIコーディングツールをサポート。100%ローカル実行——データは一切外部に送信されません。

```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

## プライバシー

**データは一切マシンの外に出ません。** サーバーなし、APIなし、テレメトリなし。作者がデータを収集することは技術的に不可能です。コードは完全オープンソースです。

## インストール

**AIコーディングツール（フル体験）：** `claude install-skill https://github.com/wallmage/vibecheck`、その後 `/vibecheck scan`。

**サンドボックス環境（Coworkなど）：** ログをスキャンしなくても80%の効果——設定ファイルの圧縮、コスト削減ルールの追加。フルスキャンにはターミナルで1行コマンドを貼り付けるだけ（直近14日分のみ、約20-50 MB）。

## コマンド

- `/vibecheck scan` — インタラクティブ教育 + 完全診断 + 修正
- `/vibecheck explain` — 教育のみ
- `/vibecheck compress` — 設定ファイル圧縮（25-50%削減）
- `/vibecheck monitor` — 週次比較 + アラート

## 15の無駄パターン

空回りナレーション、コンテキスト劣化、ピンポンデバッグ、冗長出力、未連結コマンド、コードベース放浪、未バッチ編集、ファイル再読み込み、スリープ/ポーリング、失敗リトライ、スキーマ検索、Git儀式、常時稼働エージェントのアイドルハートビート・ワークスペース肥大化・メモリ蓄積。

## 対応ツール

24種以上：Claude Code、Cursor、Codex、Windsurf、Cline、OpenClaw、CodeBuddy、TRAE、Kimi Codeなど。

全LLM対応：Claude (Opus/Sonnet/Haiku)、GPT-4o/4.1/o1/o3、Gemini 2.5/2.0、DeepSeek V3/R1。
