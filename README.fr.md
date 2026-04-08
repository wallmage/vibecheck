# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Chaque tour de votre IA coûte de l'argent.** Sonnet : ~$0.03/tour. Opus : ~$0.15/tour. Quand l'IA dit « OK, je vais corriger ça » avant de corriger — ce tour est du gaspillage pur. Et ça empire : chaque tour relit toute la conversation depuis le début. Plus la conversation est longue, plus chaque tour coûte cher. C'est l'inflation de contexte.

Les outils de code IA gaspillent des tours en permanence — narrer au lieu d'agir, lire 3 fichiers un par un au lieu de tous en même temps, exécuter `git add` et `git commit` séparément. vibecheck élimine le gaspillage de deux façons : moins de tours (regroupement, parallélisation, suppression de la narration) + contexte plus petit par tour (compression du fichier de config, nettoyage des conversations longues). Ce ne sont que 2 des 15 mécanismes. Ensemble, ils réduisent votre facture de 50%+.

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

## 15 patterns de gaspillage

**Niveau 1 (70-80%) :** Narration à vide, pourriture de contexte, debugging ping-pong
**Niveau 2 (15-20%) :** Sortie verbeuse, commandes non chaînées, exploration du codebase, éditions non groupées
**Niveau 3 (5-10%) :** Relectures, boucles sleep/poll, retries échoués, recherches de schéma, cérémonie Git
**Niveau 4 — Agents 24/7 :** Heartbeats inactifs, bloat du workspace, accumulation mémoire

## Outils supportés

24+. Tous les LLM : Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7 et 40+ autres.

macOS, Windows, Linux, iPad/mobile via SSH. Python 3.8+, aucune dépendance externe.
