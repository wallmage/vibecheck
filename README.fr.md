# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Chaque tour de votre IA coûte de l'argent.** Sonnet 4.6 : $3/$15 par MTok (entrée/sortie). Opus 4.6 : $5/$25 — 1,67x plus cher. Un tour en milieu de session coûte ~$0.038 sur Sonnet. Quand l'IA dit « OK, je vais corriger ça » avant de corriger — ces $0.031 sont du gaspillage pur. Et ça empire : chaque tour relit toute la conversation depuis le début. Plus la conversation est longue, plus chaque tour coûte cher. C'est l'inflation de contexte.

Les outils de code IA gaspillent des tours en permanence — narrer au lieu d'agir, lire les fichiers un par un, exécuter `git add` et `git commit` séparément. vibecheck détecte 18 mécanismes sur 4 niveaux, les corrige via des règles de fichier de config et la compression, et suit les améliorations. Réduit votre facture de 40-65% selon votre utilisation. [Spécifications détaillées →](SPECSHEET.md)

Supporte Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. 24+ outils. Exécution locale, vos données ne quittent jamais votre machine.

## Installation

Collez ceci dans votre outil de code IA et appuyez sur Entrée :

> Help me install this skill: https://github.com/wallmage/vibecheck

C'est tout. Votre IA s'occupe du reste.

<details>
<summary>Ou installation manuelle en ligne de commande</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Puis tapez `/vibecheck scan` dans n'importe quelle session

Mise à jour : `cd ~/.claude/skills/vibecheck && git pull`
</details>

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

## 18 mécanismes

**Niveau 1 (70-80%) :** Narration à vide, pourriture de contexte, debugging ping-pong
**Niveau 2 (15-20%) :** Sortie verbeuse, commandes non chaînées, exploration du codebase, éditions non groupées
**Niveau 3 (5-10%) :** Relectures, boucles sleep/poll, retries échoués, recherches de schéma, cérémonie Git
**Niveau 4 — Agents 24/7 :** Heartbeats inactifs, bloat du workspace, accumulation mémoire

## Outils supportés

24+. Tous les LLM : Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7 et 40+ autres.

macOS, Windows, Linux, iPad/mobile via SSH. Python 3.8+, aucune dépendance externe.
