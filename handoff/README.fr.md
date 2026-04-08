# handoff

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | Français | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

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

**Vos conversations se degradent. Cet outil garde le signal en vie.**

Chaque chat IA a une demi-vie. Plus un fil est long, plus le modele relit de contexte obsolete, moins ses reponses sont pertinentes, et plus vous brulez de tokens sur du bruit. Vous connaissez la solution : demarrer une nouvelle session. Mais alors vous perdez toutes les decisions prises, les bugs deja traces, l'architecture sur laquelle vous vous etes mis d'accord. Alors vous continuez dans l'ancien fil et la qualite ne fait que baisser.

`handoff` brise ce cercle vicieux. Dites `handoff` dans n'importe quelle session et il genere un bloc de transfert unique -- compression sans perte, 2-4K tokens -- qui capture tout ce qui compte : decisions, decouvertes, echecs, etat actuel, problemes ouverts et prochaines etapes. Collez-le dans un nouveau chat et vous repartez a pleine vitesse sans rien avoir a redecouvrir.

Pas de fichiers. Pas de plugins. Pas de base de donnees. Juste copier-coller.

## Comment ca marche

**Mode generation** -- dans l'ancienne session, dites `handoff`. Le skill compresse toute la conversation en un bloc de transfert structure par compression sans perte. Ce n'est pas un resume superficiel. Il preserve les resultats concrets -- ce qui a ete decide, ce qui a echoue, ce qui est a moitie fait, ce qui vient ensuite -- tout en eliminant les salutations, les apartees, les explications repetees et les transcriptions brutes.

**Mode reprise** -- collez le bloc dans une nouvelle session. Le skill l'analyse, vous donne un resume compact de la situation actuelle et attend votre prochaine instruction.

Le bloc de transfert vise **2-4K tokens**. Assez petit pour etre utilise frequemment. Assez dense pour ne rien perdre d'important.

## Declencheurs naturels

Pas besoin de retenir une commande speciale. N'importe lequel de ces declencheurs fonctionne :

- `handoff`
- `hand off`
- `new session`
- `switch session`
- `start fresh`
- `wrap up and hand off`

## Ce qui est preserve

- Les decisions et leurs justifications
- Les decouvertes techniques et les mecanismes
- Les experiences echouees et leurs causes
- Les chiffres importants, limites, versions, mesures de temps, couts
- La branche / le commit / l'etat dirty actuel
- Le travail non commite ou partiellement termine
- Les problemes ouverts et les bloqueurs
- La meilleure prochaine action

Ce qui est supprime : salutations, encouragements, echanges repetitifs, dumps de code brut, discussions secondaires sans impact, narration de ce que l'assistant allait faire ensuite. Le signal reste. Le bruit disparait.

## Fonctionne partout

`handoff` fonctionne en texte brut. Il est compatible avec :

- Les outils de coding (Claude Code, Cursor, Copilot, Windsurf)
- Les outils CLI (assistants IA en terminal)
- Les outils de chat GUI (ChatGPT, Claude chat, Gemini)
- Tout produit ou vous pouvez coller du texte dans une nouvelle conversation

Aucune integration speciale requise.

## Quand l'utiliser

- Le chat actuel devient long et le modele ralentit
- Vous avez termine une tranche de travail et voulez une session propre
- Vous approchez de la limite de contexte
- Vous voulez conserver les decisions sans garder tout l'ancien fil
- Vous changez de machine ou d'outil

## Installation

Copiez ceci dans votre outil IA :

```text
Help me install this skill: https://github.com/wallmage/handoff
```

## Utilisation

Dans l'ancien chat :

```text
handoff
```

Copiez le bloc genere. Ouvrez une nouvelle session. Collez.

C'est tout.

---

Auteur : [Wallny](https://github.com/wallmage)
