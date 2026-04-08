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

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | Français | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

J'atteignais systématiquement mon quota Claude en début d'après-midi sans comprendre pourquoi. Il s'est avéré que 70 % de mes sessions de coding IA étaient du gaspillage — l'IA décrivait ce qu'elle allait faire, des commandes réparties sur trois tours alors qu'un seul suffisait, du contexte périmé qui s'accumulait et était relu à chaque tour.

vibecheck trouve ce gaspillage. Il lit les logs de vos sessions sur 24+ outils de coding, chiffre 15 patterns spécifiques et les corrige. Tout s'exécute en local. Rien n'est uploadé, pas de télémétrie, pas de serveurs.

Dans mon cas : les dépenses mensuelles sont passées de $2,816 à $422. **85 % de réduction.**

## Installation

Collez ceci dans votre outil de coding IA et appuyez sur Entrée :

> Help me install this skill: https://github.com/wallmage/vibecheck

C'est tout. Votre IA charge le skill et vous êtes prêt à scanner.

<details>
<summary>Ou installez manuellement via la ligne de commande</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Puis tapez `/vibecheck scan` dans n'importe quelle session.

Pour mettre à jour : `cd ~/.claude/skills/vibecheck && git pull`
</details>

### Qu'est-ce qu'un « skill » exactement ?

Un fichier texte brut qui apprend à votre IA quelque chose de nouveau. Pas de binaires, pas de processus en arrière-plan, pas de modifications système. Le fichier skill de vibecheck dit « voici comment trouver le gaspillage et le corriger ». Supprimez le dossier et c'est fini.

### Outils de coding vs. outils de chat

**Les outils de coding** (Claude Code, Codex, Cursor, OpenClaw, Copilot, Windsurf, TRAE, Qoder, etc.) tournent sur votre machine et laissent des logs de session. vibecheck détecte automatiquement ceux que vous avez et scanne directement ces logs.

**Les outils de chat** (Cowork, Claude dans le navigateur) tournent dans un bac à sable sans logs locaux. vibecheck optimise quand même vos fichiers d'instructions — c'est là que provient l'essentiel des économies de toute façon. Vous pouvez aussi coller une commande terminal pour exporter 14 jours de logs et faire un scan complet.

### Permissions

vibecheck lit vos logs de session locaux et inspecte les fichiers d'instructions (`CLAUDE.md`, `AGENTS.md`, `Memory.md`) ainsi que les paramètres globaux de vos outils. Si votre outil possède une configuration globale — un seul fichier pour tous les projets — l'optimiseur commence par là, car une seule correction vous fait économiser partout. Il demande votre accord avant de modifier quoi que ce soit.

## Confidentialité

Tout reste sur votre machine. L'analyse est un ensemble de scripts Python qui parsent vos logs de session locaux. Pas de serveur, pas d'appels API, pas d'analytics. Open source — lisez chaque ligne si vous voulez.

## Commandes

| Commande | Fonction |
|---|---|
| `/vibecheck scan` | Scanne tous les outils détectés sur votre machine. Un rapport unifié avec indicateurs de santé, statistiques classées, principaux patterns de gaspillage et feuille de route d'optimisation |
| `/vibecheck explain` | Vous enseigne les patterns de gaspillage sans rien modifier. Purement éducatif |
| `/vibecheck compress` | Réduit vos fichiers d'instructions de 25-50 % via un compresseur sans perte en 4 passes |
| `/vibecheck monitor` | Comparaison hebdomadaire avec votre référence. Détecte les régressions de coût avant qu'elles ne s'accumulent |

Le scan reste discret : un indicateur de progression compact, puis un résumé propre. `Good` signifie un gaspillage mesuré sous 10 %, `Waste` signifie au-dessus. Les logs bruts et les sorties d'outils restent en coulisses sauf en cas de problème.

### Garder les sessions fraîches

Les longues conversations coûtent plus cher que les courtes — chaque nouveau tour relit tous les anciens, et un contexte surchargé rend l'IA moins précise, ce qui augmente les allers-retours.

Règle d'or : 5-10 minutes actives par session, 30-40 tours avant que la taxe de contexte ne se fasse vraiment sentir. Quand vous démarrez une nouvelle session, conservez vos règles permanentes dans les fichiers d'instructions (`CLAUDE.md`, `AGENTS.md`, `Memory.md`) et le contexte projet dans de petits documents locaux. Nouvelle session ne veut pas dire repartir de zéro — juste un contexte propre avec toutes vos connaissances intactes.

---

## Avant / Après

Mesuré sur des sessions réelles :

```
                          BEFORE         NOW            CHANGE
Avg turns/session         73.9           21.1           -52.8
Avg context window        65.6K          33.7K          -49%
Wasteful turns            73.7%          8.0%           -65.7%

Avg cost/session          $3.07          $0.46          -$2.61
Monthly spend             $2,816         $422           -$2,394
```

---

## Comment les tours IA coûtent de l'argent

Introduction rapide pour ceux qui n'ont jamais réfléchi à l'économie des tokens. Aucune connaissance préalable en tarification IA requise.

### Ce qui se passe à chaque tour

Chaque fois que votre IA répond, elle relit l'intégralité de la conversation depuis le début. Prompt système, fichier d'instructions, chaque message que vous avez envoyé, chaque réponse qu'elle a donnée, toutes les sorties d'outils — contenus de fichiers, résultats terminal, logs d'erreur — tout. Puis elle génère une nouvelle réponse.

**Coût du tour = tokens lus x prix d'entrée + tokens générés x prix de sortie**

Les premiers tours sont bon marché. Le tour 1 lit peut-être 5,000 tokens. Au tour 40, il relit 40,000+ tokens de conversation accumulée — chaque message précédent, chaque snippet de code, chaque trace d'erreur. Ce tour tardif coûte 8x le premier.

Le point clé : le gaspillage se **compose**. Un tour gaspillé ne coûte pas seulement ses propres tokens. Il reste dans le contexte pour le reste de la session, relu à chaque tour futur. Un message de narration inutile au tour 10 est relu 30 fois de plus avant la fin.

### Le cache de prompt aide, mais ne résout pas tout

La plupart des fournisseurs cachent désormais le contenu déjà vu et facturent 10x moins. Le coût effectif d'entrée passe de $3.00/million de tokens à $0.30/million.

Ça aide. Mais le nouveau contenu — nouvelles sorties d'outils, nouveaux messages d'erreur, chaque nouvelle réponse IA — entre toujours au plein tarif avant d'être caché. Et le gaspillage se compose même au tarif caché.

### Les abonnements subissent la même douleur

Si vous avez un abonnement, vous pensez peut-être que la tarification API ne vous concerne pas. Si — vous le ressentez simplement différemment. Les abonnements achètent un pool fixe de calcul, et le gaspillage consomme ce pool plus vite. Quand vous atteignez votre quota et êtes limité à 15h, ce n'est pas parce que vous avez trop travaillé — c'est parce qu'une grande partie de ce travail était du gaspillage.

Claude Pro ($20/mois) couvre environ $200 en valeur API équivalente. Claude 20x Max ($200/mois) couvre environ $4,000. Plus de gaspillage = mur atteint plus vite.

<details>
<summary><strong>Analyse approfondie : ce que vaut réellement votre abonnement en tokens</strong></summary>

### Comment j'ai mesuré

J'ai le plan Claude 20x Max à $200/mois et je tombais constamment à court de quota. Assez curieux pour passer à la facturation API et suivre les dépenses réelles sur 100+ points de données — chaque activité de coding enregistrée, consommation vérifiée juste après. Cela m'a permis de calculer la relation entre le prix de l'abonnement et la valeur réelle en tokens.

### Les multiplicateurs

| Plan | Prix | Valeur API | Multiplicateur | Fenêtre 5h | Total hebdo |
|---|---|---|---|---|---|
| Claude Pro | $20/mois | ~$200 | 10x | $6.67 | $46.67 |
| Claude 5x Max | $100/mois | ~$1,000 | 10x | $33.33 | $233.31 |
| Claude 20x Max | $200/mois | ~$4,000 | 20x | $133.33 | $933.31 |

Le tier 20x Max est le seul avec un vrai saut de multiplicateur — 20x la valeur faciale contre 10x pour les tiers inférieurs.

### En pratique

- **$20 Claude Pro** — du travail de développement sérieux (features, recherche, rédaction) consomme votre quota de 5 heures en moins d'une heure. Capacité hebdomadaire sous 7 heures. Serré pour toute utilisation professionnelle.
- **$100 5x Max** — environ 4 heures avant d'atteindre la fenêtre de 5 heures. 30-35 heures/semaine au total. Praticable pour un usage régulier.
- **$200 20x Max** — conçu pour ceux qui travaillent 80-100+ heures/semaine, souvent avec plusieurs sessions en parallèle.

### Pourquoi Anthropic a restreint l'utilisation d'abonnements par des tiers

À 10-20x la valeur faciale, chaque dollar d'abonnement achète bien plus de calcul que le tarif API. Les outils tiers consommant à la vitesse API équivalente rendaient l'équation intenable.

### L'alternative Codex

Au tier $20, Codex Plus offre environ **3x l'utilisation coding** de Claude Pro. Les conversations ChatGPT — même GPT-5.4 Extended Thinking et la recherche approfondie — ne comptent pas dans le quota coding Codex. Vous obtenez donc 3x la capacité coding plus GPT-5.4 gratuit en prime.

**Si votre budget est de $20/mois, Codex Plus vous donne plus de temps de coding que Claude Pro.** Si vous pouvez dépenser plus, les tiers Claude 5x et 20x offrent une proposition de valeur différente.

</details>

### Scénario de référence

Tous les montants de ce document utilisent cette référence (tarification Sonnet 4.6) :

| Paramètre | Valeur |
|---|---|
| Longueur de session | 25 tours |
| Contexte de départ | 21,000 tokens |
| Croissance par tour | ~600 tokens |
| Taux de cache hit | 95 % |
| Coût par tour (milieu de session) | $0.017 |
| Total session efficace | $0.41 |

Pour Opus 4.6, multipliez tous les coûts par 1.67x.

---

## Les 15 patterns de gaspillage

Classés par impact financier. Les trois premiers représentent à eux seuls 60-70 % de tout le gaspillage.

### Tier 1 — Les trois grands (60-70 % du gaspillage)

#### 1. Narration à vide

Votre IA dit « OK, je vais corriger ça » ou « Laissez-moi lire le fichier d'abord » — puis fait le travail au tour suivant. Ce tour de narration n'a rien fait. Pas d'appel d'outil, pas de code, pas de lecture de fichier. Juste une annonce.

Chacun coûte environ **$0.017** — et pire, ces 300-500 tokens de texte de statut restent dans le contexte, relus à chaque tour futur. Sur 428 sessions mesurées : **$1.03/session gaspillés**, 30 % du gaspillage total. À 10 sessions/jour : **$309/mois rien qu'en narration.**

Règle vibecheck : *« Pas de tour sans appel d'outil. Réfléchir et agir dans le même tour. »* **Économie d'environ $0.88/session.**

#### 2. Dégradation du contexte

Le coût de session croît de façon quadratique, pas linéaire. Le tour 50 relit les 49 tours précédents.

Comparaison concrète : une session de 40 tours coûte **$0.70**. Le même travail réparti en deux sessions de 20 tours : **$0.60**. Cet écart de $0.10 est du pur gaspillage dû au maintien d'une conversation gonflée. Les sessions réelles font en moyenne 74 tours — **$0.46/session gaspillés**, 13 % du gaspillage total.

vibecheck enseigne : *« Les travaux non liés vont dans des sessions séparées. Dans les longs fils, rester compact. »* **Économie d'environ $0.37/session.**

#### 3. Débogage en ping-pong

Corriger, casser, réessayer, casser encore. Chaque tentative ratée injecte ~4,000 tokens d'erreur dans le contexte, et ce texte mort est relu à chaque tour suivant. Trois cycles : 6 tours supplémentaires ($0.102) + 12K tokens d'erreurs périmées ($0.036) = **environ $0.14 par épisode**. Se produit dans ~10 % des sessions. **Pondéré : $0.015/session.**

Disjoncteur vibecheck : *« Après 2 corrections ratées sur le même fichier — stop, relire l'erreur complète, réfléchir, une correction ciblée. »* **Économie d'environ $0.01/session.**

### Tier 2 — Densité des tours (15-20 % du gaspillage)

Faire en trois tours ce qui devrait en prendre un.

#### 4. Sortie d'outil verbeuse

Une commande de build ou de test déverse 500 lignes (~5,000 tokens) dans la conversation. Ces tokens sont relus à chaque tour restant. 5K tokens x 12 tours restants au tarif caché = **$0.018/instance**. Sans cache : **$0.180** — 10x pire.

C'est en fait le pattern le plus coûteux individuellement. Logs de build, sortie npm, dumps de tests — ils inondent presque chaque session. **$1.05/session**, 31 % du gaspillage total.

Correction : *« Rediriger la sortie vers /tmp/. Utiliser les flags --quiet. tail -50 maximum. »* **Économie d'environ $0.89/session.**

#### 5. Commandes non chaînées

`npm install` dans un tour. `npm run build` dans le suivant. Deux relectures de contexte pour ce que `npm install && npm run build` fait en un seul. Chaque division : **$0.010**. Totalise **$0.14/session** dans les sessions intensives en commandes.

Correction : *« Chaîner les commandes avec `&&` quand c'est sûr. »* **Économie d'environ $0.11/session.**

#### 6. Exploration du codebase

L'IA ouvre README, package.json, trois configs et deux modules sans rapport avant d'écrire une seule ligne de code. Cinq lectures consécutives, pas d'éditions, pas de décisions. $0.085 en tours gaspillés + $0.027 taxe de contexte = **$0.112/épisode.** Moyenne : **$0.09/session.**

Correction : grep ou glob d'abord, ne lire que le pertinent, regrouper plusieurs lectures par tour. **Économie d'environ $0.07/session.**

#### 7. Éditions non groupées

Éditer le fichier A, puis B, puis C — trois tours. Un tour avec des éditions parallèles fait la même chose. Deux tours supplémentaires à $0.017 = **$0.034/instance.** Moyenne : **$0.058/session.**

Correction : *« Grouper les appels d'outils indépendants. »* **Économie d'environ $0.05/session.**

### Tier 3 — La queue (5-10 % du gaspillage)

Petit individuellement. Ça s'accumule.

#### 8. Relectures de fichiers

Le même fichier lu deux fois dans une session — le contenu est déjà en contexte, mais l'IA le récupère à nouveau. **$0.019/relecture**, les fichiers sont relus 3-4 fois en moyenne. **$0.066/session.** Correction : *« Déjà en contexte. Ne relire que si le fichier a changé. »* **Économie d'environ $0.05/session.**

#### 9. Boucles sleep/poll

`sleep 5 && check_status`, répété 3-5 fois. Chaque poll = relecture complète du contexte pour vérifier si un processus en arrière-plan est terminé. 4 polls x $0.017 = **$0.068/épisode**, **$0.043/session.** Correction : *« Utiliser --wait ou run_in_background. »* **Économie d'environ $0.034/session.**

#### 10. Réessais échoués

Commande échoue, l'IA relance la même commande sans modification. La sortie d'erreur est maintenant en double dans le contexte. **$0.019/réessai**, **$0.080/session.** Correction : comme le ping-pong — *« Stop, lire l'erreur, essayer autre chose. »*

#### 11. Consultations de schéma

L'IA consulte ses propres définitions d'outils — des informations qu'elle possède déjà. Ajoute 2K+ tokens pour rien. **$0.023/session.** La règle « pas de tour sans appel d'outil » résout ça. **Économie d'environ $0.02/session.**

#### 12. Cérémonie Git

`git add` → `git status` → `git commit` → `git push`. Quatre tours. `git add -A && git commit -m "msg" && git push` n'en prend qu'un. **$0.044/instance** mais plus rare qu'on ne pense — **$0.003/session.** Correction : chaîner avec `&&`.

### Tier 4 — Agents permanents

Modèle de coût différent. Les agents comme OpenClaw se réveillent périodiquement, et le gaspillage est mesuré par jour, pas par session.

#### 13. Heartbeats à vide

L'agent se réveille toutes les 5 minutes, relit tout le workspace, ne trouve rien, se rendort. 288 réveils/jour, ~97 % à vide. Soit 280 réveils inutiles à $0.04 chacun = **$11.20/jour ($336/mois)** pour rien.

Correction : *« Heartbeat minimum de 30 minutes. Passer si aucun déclencheur en attente. »* Réduit à ~48 réveils/jour. **Économie de $8-10/jour ($240-300/mois).**

#### 14. Gonflement du workspace

35,000 tokens de fichiers de personnalité (SOUL.md, AGENTS.md, etc.) relus à chaque réveil. Tutoriels, coaching, philosophie — écrits pour des humains, pas pour une IA exécutant des tâches. **$5.76/jour ($173/mois)** rien que pour les fichiers de configuration.

vibecheck les compresse : 35K → 12-15K tokens. Mêmes règles comportementales, sans le remplissage destiné aux humains. **Économie de $3-4/jour ($90-120/mois).**

#### 15. Accumulation de mémoire

L'historique de session croît indéfiniment. 100+ entrées mémoire relues à chaque réveil, y compris des choses datant de semaines qui n'ont plus d'importance. **$3.17/jour ($95/mois)** en mémoires périmées.

Correction : *« Archiver après 50 entrées, résumer, repartir à zéro. »* **Économie de $2-3/jour ($60-90/mois).**

---

## La boîte à outils d'optimisation

vibecheck ne se contente pas de pointer les problèmes — il les corrige.

### Compression des fichiers d'instructions

Votre fichier d'instructions (`CLAUDE.md`, `AGENTS.md`, `Memory.md`, quel que soit le nom utilisé par votre outil) est lu à chaque tour. C'est une taxe fixe sur tout ce que vous faites. Un fichier d'instructions gonflé, c'est un péage sur chaque route de la ville.

vibecheck dispose d'un compresseur sans perte en 4 passes — 23 techniques, et « sans perte » signifie littéralement qu'aucun fait n'est supprimé. Même information, moins de tokens.

| Passe | Fonction | Économie |
|---|---|---|
| **Passe 1 — Mécanique** | Supprime le formatage markdown, convertit les tableaux en forme compacte, fusionne les puces | 10-15 % |
| **Passe 2 — Préservation des faits** | Déduplique les faits répétés, compresse les exemples de code, replie les descriptions verbeuses | 15-25 % |
| **Passe 3 — Haute fidélité** | Supprime les tutoriels et textes de coaching dont les humains ont besoin mais pas l'IA | 10-15 % |
| **Passe 4 — Télégramme** | Réécriture complète en sténographie pour les fichiers réservés à l'IA. Dense, compressé — uniquement avec votre autorisation explicite | 15-25 % |

Un fichier d'instructions de 10,000 tokens compressé à 6,000 économise $0.044 par session. À 10 sessions par jour : **$0.44/jour ($13/mois)** rien qu'avec la compression.

### Suppression des sorties

Les tokens de sortie coûtent 5x les tokens d'entrée ($15 vs. $3/million sur Sonnet 4.6). L'IA affiche des blocs de code ou des diffs que vous n'avez pas demandés ? Coûteux. vibecheck ajoute : *« Pas de code ni de diffs sauf demande explicite. »* **Économie d'environ $0.047/session.**

### Suivi des coûts

`/vibecheck monitor` prend un instantané de votre profil de session et compare avec la référence lors des exécutions futures. Un nouveau fichier d'instructions a introduit de la verbosité ? Projet différent, habitudes différentes ? Le moniteur détecte les régressions avant qu'elles ne s'accumulent.

---

## Résumé des économies

### Outils interactifs (tarification Sonnet 4.6)

| # | Pattern | Gaspillage moyen/session | Économie moyenne |
|---|---|---|---|
| 1 | Narration à vide | $1.03 | $0.88 |
| 2 | Dégradation du contexte | $0.46 | $0.37 |
| 3 | Débogage en ping-pong | $0.015 | $0.01 |
| 4 | Sortie verbeuse | $1.05 | $0.89 |
| 5 | Commandes non chaînées | $0.14 | $0.11 |
| 6 | Exploration du codebase | $0.09 | $0.07 |
| 7 | Éditions non groupées | $0.058 | $0.05 |
| 8 | Relectures de fichiers | $0.066 | $0.05 |
| 9 | Boucles sleep/poll | $0.043 | $0.034 |
| 10 | Réessais échoués | $0.08 | $0.06 |
| 11 | Consultations de schéma | $0.023 | $0.02 |
| 12 | Cérémonie Git | $0.003 | $0.003 |
| + | Compression | $0.044 | $0.044 |
| + | Suppression des sorties | $0.047 | $0.038 |
| | **Total** | **$3.15*** | **$2.61** |

*Les patterns individuels peuvent coexister dans le même tour — les totaux reflètent les mesures par pattern. Agrégat réel : $3.07 à $0.46 (voir Avant / Après).

**Session gaspilleuse typique : $3.07. Après vibecheck : $0.46. Économie : 85 %.**

- **Gaspillage léger** (sessions courtes, peu de patterns) : réduction de 40-55 %
- **Gaspillage modéré** (utilisateur moyen) : réduction de 55-70 %
- **Gaspillage élevé** (longues sessions, multiples patterns) : réduction de 70-85 %

### Agents permanents

| # | Pattern | Gaspillage quotidien | Économie quotidienne |
|---|---|---|---|
| 13 | Heartbeats à vide | $11.20 | $9.70 |
| 14 | Gonflement du workspace | $5.76 | $3.76 |
| 15 | Accumulation de mémoire | $3.17 | $2.37 |
| | **Total** | **$20.13/jour** | **$15.83/jour** |

**Économie mensuelle pour les agents permanents : environ $475.**

---

## Outils supportés

24+ outils. Pas de lock-in — vibecheck est un fichier texte, toute IA lisant des instructions peut l'utiliser. Les scripts de scan sont en Python pur, sans dépendances.

**Scan complet de session** (lit vos logs, chiffre le gaspillage) :
Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity

**Détection + optimisation des instructions** (pas encore de parsing complet des logs, mais détecte l'outil et optimise vos fichiers de configuration) :
Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

**LLMs avec données tarifaires :** Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, plus 40+ autres.

**Plateformes :** macOS, Windows, Linux, iPad via SSH. Python 3.8+.

---

<details>
<summary><strong>Méthodologie</strong></summary>

Toutes les estimations de coût utilisent le scénario de référence ci-dessus. Hypothèses clés :

- **95 % de taux de cache hit** — typique pour les sessions de coding rapides. Les sessions plus lentes avec de longues pauses entre les tours auront des taux de cache inférieurs et des coûts plus élevés.
- **25 tours productifs/session** — les sessions gaspilleuses ajoutent 8-12 tours supplémentaires dus à la narration, aux réessais et aux commandes non chaînées.
- **600 tokens/tour de croissance** — les sessions verbeuses peuvent atteindre 1,000-2,000 tokens par tour.
- **Tarif d'entrée effectif : $0.435/1M** — tarif pondéré de 95 % caché ($0.30/1M) + 5 % non caché ($3.00/1M).
- **Taux de taxe de contexte : $0.30/1M** — tarif d'entrée caché pour les ajouts permanents au contexte.

Estimations conservatrices. Les économies réelles dépassent souvent ces chiffres, surtout avec de longues sessions, de gros fichiers d'instructions ou du débogage intensif.
</details>

## Auteur

[Wallny](https://github.com/wallmage)
