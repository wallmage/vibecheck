# vibecheck

[English](README.md) | [中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Italiano](README.it.md) | [Português](README.pt-BR.md)

**Chaque tour que prend votre IA a un coût.** Sonnet 4.6 : $3/$15 par million de tokens (entrée/sortie). Opus 4.6 : $5/$25 — 1,67x plus cher. Voici ce que ça représente concrètement :

- Votre IA dit « OK, je vais corriger ça » avant de s'exécuter. Ce tour de narration : **$0.031 gaspillé.** Cinq par session : **$0.165 perdus.**
- Votre conversation atteint 40 tours au lieu d'être découpée à 20. Coût supplémentaire lié à la relecture de tout l'historique : **$0.67 gaspillé.**
- `git add`, puis `git commit`, puis `git push` — trois tours au lieu d'une commande chaînée : **$0.098 gaspillé.**

Ce sont 3 des 15 schémas de gaspillage que vibecheck détecte. Chacun est expliqué ci-dessous avec les montants en dollars, ce qui se passe mal et comment y remédier.

Compatible avec Claude, GPT, Gemini, DeepSeek, Qwen, Kimi, GLM, MiniMax. 24+ outils de développement. S'exécute en local — vos données restent sur votre machine.

## Comment installer

Collez ceci dans votre outil de développement IA et appuyez sur Entrée :

> Help me install this skill: https://github.com/wallmage/vibecheck

C'est tout. Votre IA fait le reste.

<details>
<summary>Ou installer manuellement en ligne de commande</summary>

```bash
git clone https://github.com/wallmage/vibecheck.git ~/.claude/skills/vibecheck
```

Puis tapez `/vibecheck scan` dans n'importe quelle session.

Pour mettre à jour : `cd ~/.claude/skills/vibecheck && git pull`
</details>

### Qu'est-ce qu'une skill ?

Une fiche recette pour votre IA. Elle ne modifie rien et n'installe rien. C'est simplement un fichier texte qui explique « voici comment trouver les gaspillages et les corriger ». Supprimez-la quand vous voulez.

### Outils de développement vs outils de chat

**Les outils de développement** (Claude Code, Codex, Cursor, OpenClaw, Copilot, Windsurf, TRAE, Qoder, etc.) s'exécutent sur votre machine — vibecheck détecte automatiquement votre outil et analyse vos journaux de session.

**Les outils de chat** (Cowork, navigateur web) s'exécutent dans un environnement isolé. vibecheck optimise tout de même votre fichier d'instructions (l'essentiel du bénéfice), ou vous pouvez coller une commande de terminal pour copier 14 jours de journaux et effectuer une analyse complète.

### Autorisations

vibecheck lit et modifie votre fichier d'instructions (CLAUDE.md, .cursorrules, etc.). Il demande confirmation avant chaque modification.

## Confidentialité

Vos données ne quittent pas votre machine. Aucun serveur, aucune API, aucune télémétrie. Open source.

## Commandes

- `/vibecheck scan` — vous explique ce que sont les tokens, analyse vos sessions, applique les corrections
- `/vibecheck explain` — uniquement la leçon, sans modification
- `/vibecheck compress` — réduit votre fichier d'instructions de 25 à 50 %
- `/vibecheck monitor` — comparaison hebdomadaire, signale les régressions

## Avant / Après

```
                          AVANT          APRÈS          VARIATION
Nb moy. de tours/session  36.8           25.9           -10.9
Fenêtre de context moy.   128.4K         89.9K          -30%
Tours gaspillés           36.7%          8.1%           -28.6%

Coût moy. par session     $2.62          $1.35          -$1.27
Dépense mensuelle         $224           $115           -$109
```

---

## Comment les tours coûtent de l'argent

À chaque tour, votre IA relit l'intégralité de la conversation — le prompt système, le fichier d'instructions, tous les messages précédents, tous les résultats d'outils — puis génère une réponse.

**Coût d'un tour = tokens d'entrée × tarif entrée + tokens de sortie × tarif sortie**

Les premiers tours sont bon marché (contexte réduit). Les tours tardifs sont coûteux (tout ce qui précède est relu). C'est pourquoi le gaspillage s'amplifie — un tour gaspillé renchérit tous les tours suivants, car le contenu inutile reste dans le context.

La mise en cache des prompts réduit le coût d'entrée de 10x pour le contenu déjà vu. La plupart des outils l'activent automatiquement.

**Utilisateurs avec abonnement :** vous ne voyez pas directement les tarifs API, mais le gaspillage épuise votre quota de messages plus vite. Claude Pro ($20/mois) couvre environ $200 en valeur API. Max ($200/mois) couvre environ $4 000.

<details>
<summary><strong>Recherche : Ce que vaut réellement votre abonnement en tokens</strong></summary>

### Comment j'ai mesuré

J'utilise le plan Claude 20x Max à $200/mois et j'épuisais régulièrement mon quota. J'ai donc voulu savoir : combien d'utilisation API chaque tier achète-t-il réellement ?

Je suis passé à la facturation API et j'ai suivi les dépenses réelles en dollars sur plus de 100 points de données — chaque activité suivie d'un rafraîchissement de la consommation. Assez pour calculer la relation linéaire entre prix d'abonnement et valeur en tokens.

### Les multiplicateurs

| Plan | Prix | Valeur API | Multiplicateur | Fenêtre 5h | Total hebdo |
|---|---|---|---|---|---|
| Claude Pro | $20/mois | ~$200 | 10x | $6.67 | $46.67 |
| Claude 5x Max | $100/mois | ~$1,000 | 10x | $33.33 | $233.31 |
| Claude 20x Max | $200/mois | ~$4,000 | 20x | $133.33 | $933.31 |

Seul le tier 20x Max offre un vrai saut de multiplicateur (20x contre 10x pour les tiers inférieurs).

### Durée d'utilisation réelle

- **$20 Claude Pro** — en travail sérieux (dev, recherche, rédaction), moins d'1 heure et votre quota 5h est épuisé. Total hebdomadaire sous 7 heures. Trop limitant pour tout professionnel.
- **$100 5x Max** — environ 4 heures de travail avant d'atteindre la fenêtre 5h. 30-35 heures/semaine au total. Acceptable pour un usage normal.
- **$200 20x Max** — pour ceux qui travaillent 80-100+ heures/semaine, souvent en multi-threading sur plusieurs sessions.

### Pourquoi Claude a interdit l'utilisation tierce des abonnements

Ces multiplicateurs l'expliquent. À 10-20x la valeur faciale, chaque dollar d'abonnement achète bien plus de calcul que les tarifs API. Les outils tiers consommant les quotas d'abonnement à des taux équivalents API rendaient le modèle économique insoutenable.

### L'alternative Codex

Je n'ai pas encore totalement mesuré la valeur dollar de Codex, mais au tier $20, Codex Plus fournit environ **3x l'utilisation réelle** de Claude Pro.

Pourquoi : les conversations ChatGPT (même avec le modèle o4 extended thinking) ne comptent pas dans votre quota Codex. Vous obtenez le produit chat complet gratuitement en plus du coding. Donc $20 Codex ≈ $60 Claude en utilisation réelle.

**Si vous ne prévoyez pas d'acheter au moins le tier Claude à $100, prenez $20 Codex Plus.** Vous obtenez la recherche approfondie gratuite, le chat extended thinking gratuit, et 3x plus d'utilisation coding que Claude Pro.

</details>

### Scénario de référence

Tous les montants ci-dessous utilisent cette base de calcul (Sonnet 4.6) :

| Paramètre | Valeur |
|---|---|
| Durée de session | 25 tours |
| Context initial | 5 000 tokens |
| Croissance par tour | ~3 000 tokens |
| Taux de cache hit | 90 % |
| Coût d'un tour en milieu de session | $0.038 |
| Total d'une session efficace | $0.96 |

Pour Opus 4.6, multipliez tous les coûts par 1,67x.

---

## Les 15 schémas de gaspillage

### Niveau 1 — Les 3 grands (60-70 % du gaspillage)

#### 1. Narration inutile

**De quoi s'agit-il.** L'IA dit « OK, je vais corriger ça » ou « Laissez-moi d'abord lire le fichier » — puis fait le vrai travail au tour suivant. Le tour de narration n'a rien accompli : aucun appel d'outil, aucun code, aucune lecture de fichier.

**Le gaspillage.** Chaque tour de narration coûte **$0.031** (relecture du context + ~500 tokens de texte de statut). La plupart des sessions en comptent 5 : **$0.165/session gaspillés** — 17 % de la facture ne produisant rien. Sur 10 sessions/jour : **$1.65/jour ($50/mois)** rien que pour la narration.

**La correction.** vibecheck ajoute : *« Pas de tour sans appel d'outil. Pas de narration. Réfléchir et agir dans le même tour. »* Élimine la narration totalement. **Économise $0.15-0.18/session.**

#### 2. Pourrissement du context

**De quoi s'agit-il.** Les longues conversations deviennent progressivement plus coûteuses. Le tour 50 relit les 49 tours précédents. Le coût total de la session croît quadratiquement avec la longueur.

**Le gaspillage.** Une session de 40 tours : **$1.89.** Deux sessions de 20 tours (même travail) : **$1.22.** La différence — **$0.67** — n'achète rien. À 100 tours : une session coûte **$5.62** contre quatre sessions de 25 tours à **$3.84.** Soit **$1.78 gaspillés** faute de découpage.

**La correction.** Enseigne : *« Utiliser /clear ou /compact entre des tâches sans rapport. Démarrer de nouvelles conversations. »* **Économise $0.30-0.70/session pour les utilisateurs aux longues sessions.**

#### 3. Débogage en ping-pong

**De quoi s'agit-il.** Corriger, casser, réessayer, recasser. Chaque tentative échouée ajoute des messages d'erreur dans le context (~4K tokens par cycle), relus à chaque tour suivant.

**Le gaspillage.** Trois cycles d'échec : 6 tours supplémentaires ($0.252) + 12K tokens d'erreurs mortes ($0.036 de taxe de context). **Total : ~$0.29 par épisode.** Se produit dans ~1/3 des sessions. **Pondéré : ~$0.10/session.**

**La correction.** Ajoute : *« Après 2 corrections échouées sur le même fichier : s'arrêter, relire l'erreur en entier, réfléchir, une seule correction ciblée. »* **Économise ~$0.20 par épisode.**

### Niveau 2 — Densité des tours (15-20 % du gaspillage)

#### 4. Sortie d'outil verbeuse

**De quoi s'agit-il.** Une commande build/test déverse 500 lignes (~5K tokens) dans la conversation. Ces tokens sont relus à chaque tour suivant.

**Le gaspillage.** 5K tokens × 12 tours restants × $0.30/1M = **$0.018/occurrence** de taxe de context. Se produit 2-3 fois/session. Sans cache : **$0.180/occurrence** — 10x pire. **Total : $0.04-0.05/session.**

**La correction.** Ajoute : *« Rediriger la sortie build/test vers /tmp/, utiliser les flags --quiet, tail -50 maximum. »* **Économise $0.03-0.05/session.**

#### 5. Commandes non chaînées

**De quoi s'agit-il.** `npm install` dans un tour, `npm run build` dans le suivant. Deux relectures du context là où `&&` les enchaînerait en une seule.

**Le gaspillage.** Chaque séparation : **$0.023.** Les sessions typiques en comptent 3-4. **Total : $0.07-0.09/session.**

**La correction.** Ajoute : *« Chaîner les commandes avec `&&` quand c'est sûr. »* **Économise $0.06-0.08/session.**

#### 6. Errance dans le code

**De quoi s'agit-il.** L'IA ouvre fichier après fichier — README, package.json, configs — avant de faire quoi que ce soit. Cinq lectures consécutives ou plus avant la première modification.

**Le gaspillage.** Cinq lectures inutiles : $0.190 en tours + $0.027 de taxe de context = **$0.217/épisode.** Se produit dans ~25 % des sessions. **Pondéré : ~$0.054/session.**

**La correction.** Encourage la recherche ciblée (grep/glob d'abord), le regroupement de plusieurs lectures par tour. **Économise ~$0.15 par épisode.**

#### 7. Modifications non regroupées

**De quoi s'agit-il.** Modifier le fichier A, puis B, puis C — trois tours là où un seul avec des modifications en parallèle suffirait.

**Le gaspillage.** 2 tours supplémentaires × $0.038 = **$0.076/occurrence.** Se produit dans ~60 % des sessions. **Pondéré : ~$0.046/session.**

**La correction.** Ajoute : *« Regrouper les appels d'outils indépendants (plusieurs Reads/Edits par tour). »* **Économise ~$0.04/session.**

### Niveau 3 — La longue traîne (5-10 % du gaspillage)

#### 8. Relectures de fichiers

**De quoi s'agit-il.** Le même fichier lu deux fois dans une session. Le contenu est déjà dans le context après la première lecture.

**Le gaspillage.** 1 tour gaspillé + contenu dupliqué = **$0.043/relecture.** 1-2 par session. **Pondéré : ~$0.039/session.**

**La correction.** Ajoute : *« Le contenu est dans le context après la première lecture. Ne relire que si le fichier a changé. »* **Économise ~$0.03/session.**

#### 9. Boucles sleep/poll

**De quoi s'agit-il.** `sleep 5 && check_status`, répété 3-5 fois. Chaque vérification relit le context complet.

**Le gaspillage.** 4 vérifications × $0.038 = **$0.152/épisode.** Se produit dans ~20 % des sessions. **Pondéré : ~$0.030/session.**

**La correction.** Ajoute : *« Utiliser les flags --wait ou run_in_background. »* **Économise ~$0.12/épisode.**

#### 10. Nouvelles tentatives après échec

**De quoi s'agit-il.** Une commande échoue, l'IA relance exactement la même commande. Le message d'erreur se retrouve alors deux fois dans le context.

**Le gaspillage.** **$0.042/nouvelle tentative.** Se produit dans ~30 % des sessions. **Pondéré : ~$0.013/session.**

**La correction.** Même règle que le ping-pong : *« S'arrêter, relire l'erreur, réfléchir, une seule correction ciblée. »*

#### 11. Recherches de schéma

**De quoi s'agit-il.** L'IA consulte ses propres définitions d'outils — des informations qu'elle possède déjà. Ajoute 2K+ tokens au context.

**Le gaspillage.** **$0.052/recherche.** Se produit dans ~40 % des sessions. **Pondéré : ~$0.021/session.**

**La correction.** « Pas de tour sans appel d'outil » décourage les tours de découverte. **Économise ~$0.02/session.**

#### 12. Cérémonial Git

**De quoi s'agit-il.** `git add` → `git status` → `git commit` → `git push`, quatre tours. `git add -A && git commit -m "msg" && git push` n'en fait qu'un.

**Le gaspillage.** 3 tours supplémentaires + sortie git = **$0.098/occurrence.** Se produit dans ~70 % des sessions. **Pondéré : ~$0.069/session.**

**La correction.** Ajoute : *« Chaîner les commandes git avec `&&`. »* **Économise ~$0.06/session.**

### Niveau 4 — Agents toujours actifs (OpenClaw, etc.)

Modèle de coût différent : coût par réveil × réveils par jour.

#### 13. Battements de cœur en veille

**De quoi s'agit-il.** L'agent se réveille toutes les 5 minutes, relit l'espace de travail complet, ne trouve rien. 288 réveils/jour, ~97 % en veille.

**Le gaspillage.** 280 réveils inutiles/jour × $0.04 = **$11.20/jour ($336/mois)** pour ne rien faire.

**La correction.** *« Fréquence minimale de 30 min. Ignorer s'il n'y a pas de déclencheur. »* Réduit à ~48 réveils/jour. **Économise $8-10/jour ($240-300/mois).**

#### 14. Surcharge des fichiers de l'espace de travail

**De quoi s'agit-il.** 35K tokens de fichiers de personnalité (SOUL.md, AGENTS.md) relus à chaque réveil. L'IA n'a besoin que des règles comportementales — les tutoriels et les guides sont pour les humains.

**Le gaspillage.** **$5.76/jour ($173/mois)** rien que pour lire les fichiers de configuration.

**La correction.** Compresse les fichiers de l'espace de travail : 35K → 12-15K tokens. **Économise $3-4/jour ($90-120/mois).**

#### 15. Accumulation de mémoire

**De quoi s'agit-il.** L'historique de session grossit sans élagage. 100+ entrées relues à chaque réveil.

**Le gaspillage.** **$3.17/jour ($95/mois)** à lire de la mémoire obsolète.

**La correction.** *« Archiver après 50 tours, résumer, repartir de zéro. »* **Économise $2-3/jour ($60-90/mois).**

---

## En prime : outils d'optimisation

### Compression du fichier d'instructions

Votre fichier d'instructions est lu à chaque tour — une taxe fixe que vous payez quelle que soit la tâche. vibecheck inclut un compresseur sans perte en 4 passes (23 techniques) qui réduit la taille du fichier de 25 à 50 % :

- **Passe 1 (Mécanique) :** Suppression du markdown, conversion des tableaux, fusion des listes à puces. ~10-15 %.
- **Passe 2 (Conservation des faits) :** Déduplication des informations, compression des exemples de code. ~15-25 %.
- **Passe 3 (Haute fidélité) :** Suppression des tutoriels et des textes d'accompagnement utiles aux humains mais pas à l'IA. ~10-15 %.
- **Passe 4 (Télégraphique) :** Réécriture complète en raccourcis pour les fichiers destinés à l'IA uniquement. ~15-25 % (uniquement avec autorisation).

Un fichier de 10K tokens compressé à 6K économise $0.057/session. À 10 sessions/jour : **$0.57/jour ($17/mois).**

### Suppression des sorties

Les tokens de sortie coûtent 5x les tokens d'entrée ($15 vs $3/MTok sur Sonnet). L'IA affichant des blocs de code et des diffs complets que vous n'avez pas demandés gaspille **~$0.047/session.** vibecheck ajoute : *« Pas de code/diffs sauf si demandé. »*

### Suivi des coûts

`/vibecheck monitor` prend un instantané de votre profil de session et le compare à la référence lors des exécutions suivantes. Détecte les régressions avant qu'elles ne coûtent de l'argent.

---

## Récapitulatif des économies

### Outils interactifs (Sonnet 4.6)

| # | Schéma | Gaspillage moy./session | Économie moy. |
|---|---|---|---|
| 1 | Narration inutile | $0.165 | $0.155 |
| 2 | Pourrissement du context | $0.150 | $0.120 |
| 3 | Débogage en ping-pong | $0.097 | $0.067 |
| 4 | Sortie verbeuse | $0.045 | $0.035 |
| 5 | Commandes non chaînées | $0.080 | $0.065 |
| 6 | Errance dans le code | $0.054 | $0.040 |
| 7 | Modifications non regroupées | $0.046 | $0.038 |
| 8 | Relectures de fichiers | $0.039 | $0.030 |
| 9 | Boucles sleep/poll | $0.030 | $0.025 |
| 10 | Nouvelles tentatives après échec | $0.013 | $0.010 |
| 11 | Recherches de schéma | $0.021 | $0.018 |
| 12 | Cérémonial Git | $0.069 | $0.058 |
| + | Compression | $0.057 | $0.057 |
| + | Suppression des sorties | $0.047 | $0.038 |
| | **Total** | **$0.913** | **$0.756** |

**Session typique avec gaspillage : $1.87. Après vibecheck : $1.11. Économies : 41 %.**

- **Faible gaspillage** (sessions courtes, peu de schémas) : 25-35 %
- **Gaspillage modéré** (utilisateur moyen) : 40-50 %
- **Fort gaspillage** (longues sessions, multiples schémas) : 50-65 %

### Agents toujours actifs

| # | Schéma | Gaspillage quotidien | Économies quotidiennes |
|---|---|---|---|
| 13 | Battements de cœur en veille | $11.20 | $9.70 |
| 14 | Surcharge de l'espace de travail | $5.76 | $3.76 |
| 15 | Accumulation de mémoire | $3.17 | $2.37 |
| | **Total** | **$20.13/jour** | **$15.83/jour** |

**Économies mensuelles pour les agents toujours actifs : ~$475.**

---

## Outils compatibles

24+ outils.

- **Analyse complète des sessions :** Claude Code, Codex, Cursor, OpenClaw, GitHub Copilot, Windsurf, TRAE, Qoder, CodeBuddy, WorkBuddy, Google Antigravity
- **Détection + optimisation des instructions :** Cline, Roo Code, Kilo Code, Aider, Gemini CLI, OpenCode, Augment, Kimi Code, MarsCode, Tongyi Lingma, Baidu Comate, CodeGeeX, DevChat, MiniMax

Tous les LLMs : Claude Opus/Sonnet 4.6, GPT-5.4, Gemini 3.1 Pro, DeepSeek V3.2, Qwen 3.6, Kimi K2.5, GLM-5, MiniMax M2.7, et 40+ autres.

macOS, Windows, Linux, iPad via SSH. Python 3.8+, sans dépendances.

<details>
<summary>Méthodologie</summary>

Toutes les estimations de coût utilisent le scénario de référence ci-dessus. Hypothèses principales :

- **Taux de cache hit de 90 %** — typique pour les sessions de développement rapide. Les sessions plus lentes auront des coûts plus élevés.
- **25 tours productifs/session** — les sessions avec gaspillage ajoutent 8-12 tours supplémentaires dus à la narration, aux nouvelles tentatives et aux commandes non chaînées.
- **3 000 tokens/tour de croissance** — les sessions verbeuses peuvent atteindre 4 000-5 000.
- **Taux d'entrée effectif : $0.57/1M** — mélange 90 % avec cache ($0.30) + 10 % sans cache ($3.00).
- **Taux de taxe de context : $0.30/1M** — taux d'entrée avec cache pour les ajouts permanents au context.

Les estimations sont conservatives. Les économies réelles peuvent dépasser les projections pour les utilisateurs ayant de longues sessions, des fichiers d'instructions volumineux, ou un débogage intensif.
</details>
