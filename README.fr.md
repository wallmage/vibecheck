# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Votre outil de code IA brûle de l'argent que vous ne voyez pas.**

Chaque message que vous envoyez, votre IA relit *toute* la conversation depuis le début. Le message #50 coûte 50x le prix du message #1. Cette narration « OK, je vais corriger ça » ? Ça vous a coûté de l'argent pour rien. Ces 500 lignes de logs ? Relues à chaque futur message.

La plupart des vibe codeurs gaspillent **plus de 50%** de leur budget tokens IA sans le savoir.

vibecheck corrige ça. Il scanne vos 14 derniers jours, trouve exactement où va le gaspillage, l'explique en langage clair, et applique des correctifs d'un paragraphe. Même travail. Moitié prix.

**Économie moyenne : 50%+ de votre facture de tokens.** Supporte tous les modèles LLM (Claude, GPT, Gemini, DeepSeek). Fonctionne avec Claude Code, OpenClaw, Codex, OpenCode, Cursor, Windsurf et 24+ outils. 100% local — vos données ne quittent jamais votre machine.

## Commencer — rien à télécharger

vibecheck est un **skill** — un ensemble d'instructions que votre outil de code IA apprend. Pas de logiciel à télécharger ou installer. Donnez un lien à votre IA, elle apprend à optimiser vos coûts. Un message, c'est fait.

**Copiez ceci dans votre outil de code IA** (Claude Code, Cursor, Codex, Windsurf, Cline) :

> Installe le skill vibecheck depuis https://github.com/wallmage/vibecheck et lance /vibecheck scan

C'est tout. Votre IA lit le skill, scanne 14 jours et vous explique tout.

**Ou en CLI :**
```bash
claude install-skill https://github.com/wallmage/vibecheck
/vibecheck scan
```

**Outils sandbox (Cowork etc.) :**
> Clone https://github.com/wallmage/vibecheck dans /tmp/vibecheck, lis SKILL.md, puis lance /vibecheck scan

### Qu'est-ce qu'un « skill » ?

Un skill, c'est comme une fiche recette pour votre IA. Ça ne modifie pas votre IA et n'installe rien. Ça lui donne des instructions — « comment trouver les patterns de gaspillage, les expliquer, les corriger. » Supprimable à tout moment.

### Outils de code vs outils de chat

**Outils de code** (Claude Code CLI, Cursor, Codex etc.) : accès direct aux logs. Scan complet personnalisé.

**Outils chat/sandbox** (Cowork etc.) : sandbox — fichiers projet visibles, historique non.

1. **Sans scan (80% du bénéfice) :** Optimise le fichier de config. Pas besoin de logs.
2. **Avec scan (100%) :** Une commande dans le terminal — 14 derniers jours (~20-50 Mo).

### Permissions

Accès au **dossier projet** pour lire/éditer le fichier de config. Demande avant chaque modification.

## Confidentialité

**Vos données ne quittent jamais votre machine.** Pas de serveur, pas d'API, pas de télémétrie. Code entièrement open source.

## Commandes

- `/vibecheck scan` — Éducation interactive + diagnostic + corrections
- `/vibecheck explain` — Éducation seule
- `/vibecheck compress` — Compresser le fichier de config (25-50%)
- `/vibecheck monitor` — Comparaison hebdomadaire + alertes

## 15 patterns de gaspillage

**Niveau 1 (70-80%) :** Narration à vide, pourriture de contexte, debugging ping-pong
**Niveau 2 (15-20%) :** Sortie verbeuse, commandes non chaînées, exploration du codebase, éditions non groupées
**Niveau 3 (5-10%) :** Relectures, boucles sleep/poll, retries échoués, recherches de schéma, cérémonie Git
**Niveau 4 — Agents 24/7 :** Heartbeats inactifs, bloat du workspace, accumulation mémoire

## Outils supportés

24+. Tous les LLM : Claude, GPT-4o/4.1/o1/o3, Gemini 2.5/2.0, DeepSeek V3/R1.

macOS, Windows, Linux, iPad/mobile via SSH. Python 3.8+, aucune dépendance externe.
