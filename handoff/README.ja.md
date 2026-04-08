# handoff

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | 日本語 | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

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

**会話は劣化する。このツールはシグナルを生かし続ける。**

すべてのAIチャットには半減期がある。スレッドが長くなるほど、モデルは古いコンテキストを繰り返し読み、出力の精度は下がり、ノイズに消費されるトークンは増える。解決策は分かっている：新しいセッションを始めればいい。でもそうすると、これまでの意思決定、追いかけたバグ、固めたアーキテクチャをすべて失う。だから古いスレッドで続けてしまい、品質は下がり続ける。

`handoff` はこの悪循環を断ち切る。任意のセッションで `handoff` と言えば、ロスレス圧縮された2-4Kトークンの転送ブロックが生成される。意思決定、発見、失敗、現在の状態、未解決の問題、次のステップ――重要なものすべてが含まれる。新しいチャットに貼り付ければ、再発見ゼロでフルスピードに戻れる。

ファイルなし。プラグインなし。データベースなし。コピー＆ペーストだけ。

## 仕組み

**生成モード** -- 古いセッションで `handoff` と言う。スキルがロスレス圧縮で会話全体を構造化された転送ブロックに圧縮する。これはカジュアルな要約ではない。具体的な成果を保持する――何を決めたか、何が失敗したか、何が途中か、次に何をすべきか。挨拶、雑談、繰り返しの説明、生ログは除去される。

**再開モード** -- 転送ブロックを新しいセッションに貼り付ける。スキルがそれを解析し、現状の簡潔なサマリーを提示して、次の指示を待つ。

転送ブロックの目標サイズは **2-4Kトークン**。頻繁に使えるほど小さく、重要な情報を失わないほど濃密。

## 自然なトリガー

特別なコマンドを覚える必要はない。以下のどれでも動作する：

- `handoff`
- `hand off`
- `new session`
- `switch session`
- `start fresh`
- `wrap up and hand off`

## 保持される内容

- 意思決定とその理由
- 技術的な発見とメカニズム
- 失敗した実験とその原因
- 重要な数値、制限、バージョン、タイミング、コスト
- 現在のブランチ / コミット / ダーティステート
- 未コミットまたは部分的な作業
- 未解決の問題とブロッカー
- 最善の次のアクション

除去される内容：挨拶、励ましの言葉、繰り返しのやり取り、生のコードダンプ、何も変えなかった雑談、アシスタントの次にやることについての語り。シグナルは残る。ノイズは消える。

## どこでも動作

`handoff` はプレーンテキストで動作する。以下で使える：

- コーディングツール（Claude Code、Cursor、Copilot、Windsurf）
- CLIツール（ターミナルベースのAIアシスタント）
- GUIチャットツール（ChatGPT、Claude chat、Gemini）
- テキストを新しい会話に貼り付けられるあらゆるプロダクト

特別な統合は不要。

## 使うタイミング

- 現在のチャットが長くなり、モデルの反応が鈍くなってきた
- 作業の一区切りがつき、クリーンな新セッションが欲しい
- コンテキストの上限に近づいている
- 意思決定を残したいが、古いスレッド全体は維持したくない
- マシンやツールを切り替える

## インストール

以下をAIツールにコピーしてください：

```text
Help me install this skill: https://github.com/wallmage/handoff
```

## 使い方

古いチャットで：

```text
handoff
```

生成されたブロックをコピー。新しいセッションを開く。貼り付ける。

以上。

---

作者：[Wallny](https://github.com/wallmage)
