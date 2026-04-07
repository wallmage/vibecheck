# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Votre outil de code IA brûle de l'argent que vous ne voyez pas.**

Chaque message que vous envoyez, votre IA relit *toute* la conversation depuis le début. Le message #50 coûte 50x le prix du message #1. Cette narration « OK, je vais corriger ça » ? Ça vous a coûté de l'argent pour rien. Ces 500 lignes de logs de build ? Relues à chaque. futur. message.

La plupart des vibe codeurs gaspillent **plus de 50%** de leur budget tokens IA sans le savoir.

vibecheck corrige ça. Il scanne vos 14 derniers jours de sessions, trouve exactement où va le gaspillage, l'explique en langage clair (sans jargon — on vous expliquera ce que sont les tokens), et applique des correctifs d'un paragraphe à votre fichier de configuration. Même travail. Moitié prix.

**Économie moyenne : 50%+ de votre facture de tokens.** Supporte tous les modèles LLM. Fonctionne avec Claude Code, OpenClaw, Codex, OpenCode et 24+ outils de code IA. 100% local — vos données ne quittent jamais votre machine.

```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

## Confidentialité

**Vos données ne quittent jamais votre machine.** Pas de serveur, pas d'API, pas de télémétrie. L'auteur ne peut pas collecter vos données — c'est techniquement impossible. Le code est entièrement open source.

## Installation

**Outils de code IA (expérience complète) :** `claude install-skill https://github.com/wallmage/vibecheck`, puis `/vibecheck scan`.

**Environnements sandbox (Cowork, etc.) :** Même sans scanner les logs, vous obtenez 80% des bénéfices — compression du fichier de config, ajout de règles d'économie. Pour le scan complet, collez une commande dans votre terminal (14 derniers jours seulement, ~20-50 Mo).

## Commandes

- `/vibecheck scan` — Éducation interactive + diagnostic complet + corrections
- `/vibecheck explain` — Éducation seule
- `/vibecheck compress` — Compresser le fichier de config (25-50% plus petit)
- `/vibecheck monitor` — Comparaison hebdomadaire + alertes

## 15 patterns de gaspillage

Narration à vide, pourriture de contexte, débogage ping-pong, sortie verbeuse, commandes non chaînées, exploration du codebase, éditions non groupées, relectures de fichiers, boucles sleep/poll, retries échoués, recherches de schéma, cérémonie Git, et pour les agents 24/7 : heartbeats inactifs, bloat du workspace, accumulation mémoire.

## Outils supportés

24+ outils : Claude Code, Cursor, Codex, Windsurf, Cline, OpenClaw, CodeBuddy, TRAE, Kimi Code, et plus.

Tous les LLM : Claude (Opus/Sonnet/Haiku), GPT-4o/4.1/o1/o3, Gemini 2.5/2.0, DeepSeek V3/R1.
