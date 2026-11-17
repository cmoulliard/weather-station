# Plan Électrique - Abri de Jardin

![electricité.drawio.png](../img/electricit%C3%A9.drawio.png)

## 1. Lecture du diagramme

| Repère sur le schéma | Emplacement | Équipement |
| --- | --- | --- |
| **Arrivée** | Sous le sol, côté droit → coffret | Câble 2,5 mm² venant de la maison, protégé par un disjoncteur **Hager MWS 220A – C20** (20A) dans le tableau principal |
| **Coffret** | Paroi OSB droite, intérieur | Coffret divisionnaire de l'abri |
| **Bloc 3 prises** | Paroi droite, intérieur (au-dessus du coffret) | 3 prises |
| **2 prises extérieures droite** | Paroi droite, extérieur (traversée OSB) | 2 prises |
| **2 prises intérieures gauche** | Paroi OSB gauche, intérieur | 2 prises — alimentées par un câble 2,5 mm² passant **sous la chape** |
| **1 prise extérieure gauche** | Paroi gauche, extérieur | 1 prise — repiquée sur les prises intérieures gauches |
| **Interrupteur + Spot** | Paroi droite, intérieur | 1 interrupteur simple commandant 1 spot |

Au total : **8 prises** (réparties en 4 boîtiers) et **1 point lumineux**.

## 2. Points de départ et contraintes

* **Tout l'abri est derrière un seul disjoncteur C20 à la maison.** La puissance totale disponible dans l'abri est donc de **20A ≈ 4 600 W**, quel que soit le nombre de lignes créées dans le coffret.
* **RGIE :** maximum **8 points par circuit**. Une prise simple *ou multiple* (plusieurs prises dans un même boîtier/sous un même cache) compte pour **1 point**. Un point lumineux compte pour 1 point ; l'interrupteur n'est pas un point.
* **Section des câbles :** 2,5 mm² → disjoncteur **≤ 20A** ; 1,5 mm² → disjoncteur **≤ 16A**.
* **Chute de tension de la liaison maison-abri** (20 m, 2,5 mm², 20A) : ≈ 5,7 V soit **2,5 %** → acceptable.

## 3. Combien de lignes ? → 3 lignes

Techniquement, les 4 boîtiers de prises (= 4 points) + le spot (1 point) tiendraient sur une seule ligne, mais le schéma montre déjà des départs séparés depuis le coffret. On retient **3 lignes** :

| Ligne | Disjoncteur | Câble | Points raccordés | Nb points |
| --- | --- | --- | --- | --- |
| **L1 – Prises côté droit** | **16A** courbe C | 3G2,5 mm² | Bloc 3 prises intérieures (paroi droite) + 2 prises extérieures (paroi droite) | 2 (ou 5 si prises individuelles) |
| **L2 – Prises côté gauche** | **16A** courbe C | 3G2,5 mm² (EXVB, sous chape, en gaine) | 2 prises intérieures (paroi gauche) + 1 prise extérieure (paroi gauche) | 2 (ou 3 si prises individuelles) |
| **L3 – Éclairage** | **10A ou 16A** courbe C | 3G1,5 mm² | Interrupteur simple → Spot | 1 |

Pourquoi 3 lignes plutôt que 2 :

* La ligne **L2 passe sous la chape** et dessert une prise extérieure : c'est la plus exposée à l'humidité. Isolée sur son propre disjoncteur, un défaut sur cette ligne n'éteint ni la lumière ni les prises côté droit.
* L'éclairage reste sur une ligne séparée : on garde de la lumière pour intervenir si une ligne prises disjoncte.
* Le coût d'un disjoncteur supplémentaire est faible.

> **Option 2 lignes** (si on veut économiser un disjoncteur) : L1 + L2 sur un seul disjoncteur 16A « Prises » (4 boîtiers = 4 points ≤ 8) + L3 « Éclairage ». Conforme, mais moins pratique en cas de défaut.

### 16A ou 20A ?

→ **16A pour les lignes prises** (même si le câble 2,5 mm² autoriserait 20A).

* En amont, il y a déjà un **C20** à la maison. Mettre des **20A** dans l'abri n'apporte aucune protection supplémentaire : en cas de surcharge, c'est le 20A de la maison ou celui de l'abri qui saute au hasard (aucune sélectivité), et il faudra parfois retourner au tableau de la maison.
* Avec des **16A** dans l'abri, une surcharge sur une ligne fait déclencher le disjoncteur de l'abri en priorité (sélectivité partielle en surcharge ; en court-circuit franc, le C20 de la maison peut aussi déclencher).
* Pour l'éclairage, un **10A** est idéal (meilleure sélectivité) ; un 16A reste conforme sur du 1,5 mm².

## 4. Architecture du Coffret Divisionnaire (dans l'abri)

* **Départ Habitation :** disjoncteur **Hager MWS 220A – C20** dédié à la ligne de l'abri (existant).
* **Liaison tranchée (≈ 20 m) :** câble **EXVB 3G2,5 mm²** dans une **gaine annelée rouge (Ø 40 mm)** enterrée à **60 cm**, grillage avertisseur rouge à -40 cm.
* **Coffret IP65 (abri) :**
  1. **Interrupteur différentiel 30 mA, Type A, 40A, bipolaire** — protection des personnes, obligatoire pour les prises extérieures et un local humide. *(Même si la ligne est déjà sous un différentiel à la maison, il permet de couper l'abri seul en cas de défaut d'isolement.)*
  2. **Peigne Phase + Neutre** reliant la sortie du différentiel aux 3 disjoncteurs.
  3. **Disjoncteur 16A** → L1 Prises droite.
  4. **Disjoncteur 16A** → L2 Prises gauche.
  5. **Disjoncteur 10A (ou 16A)** → L3 Éclairage.
  6. **Bornier de terre** (+ bornier de neutre si besoin).

```text
[ARRIVÉE MAISON : EXVB 3G2,5 mm² — protégé par C20 Hager à la maison]
     │          │          │
  Phase      Neutre      Terre
 (Marron)    (Bleu)   (Vert/Jaune)
     ▼          ▼          │
 ┌─────────────────────┐   │
 │ DIFFÉRENTIEL 30 mA  │   │
 │ Type A - 40A - 2P   │   │
 └─────────┬───────────┘   │
           │ Ph + N        │
 ┌─────────▼─────────────────────────┐
 │ PEIGNE Ph + N (4 modules min.)    │
 └────┬───────────┬───────────┬──────┘
      ▼           ▼           ▼        │
 ┌─────────┐ ┌─────────┐ ┌─────────┐   │
 │ DISJ.   │ │ DISJ.   │ │ DISJ.   │   │
 │ 16A  C  │ │ 16A  C  │ │ 10A  C  │   │
 └────┬────┘ └────┬────┘ └────┬────┘   ▼
      │           │           │   ┌───────────┐
      │           │           │   │ BORNIER   │
      │           │           │   │ DE TERRE  │
      │           │           │   └─────┬─────┘
      ▼           ▼           ▼         │ (vers chaque ligne)
     L1          L2          L3
 Prises droite Prises gauche Éclairage
 3 int + 2 ext 2 int + 1 ext Inter. → Spot
 3G2,5 mm²     3G2,5 mm²     3G1,5 mm²
               (sous chape)
```

Encombrement : différentiel (2 modules) + 3 disjoncteurs 1P+N (1 module chacun) = **5 modules** → coffret **8 modules** suffisant, **12 modules** si on veut de la réserve (alimentation ESP32, électrovanne, etc.).

## 5. Câblage fil par fil (Phase, Neutre, Terre)

### A. Câblage interne du coffret

1. **Entrée (EXVB 3G2,5 mm²) :**
   * **Phase (Marron)** → borne supérieure **`L` / `1`** du différentiel 30 mA.
   * **Neutre (Bleu)** → borne supérieure **`N`** du différentiel.
   * **Terre (Vert/Jaune)** → **bornier de terre**. *(La terre ne passe jamais par un disjoncteur ou un différentiel.)*
2. **Pontage vers les disjoncteurs :**
   * **Avec peigne Ph + N (recommandé)** : le peigne se glisse sous les bornes de sortie (bas) du différentiel et dans les bornes d'entrée (haut) des 3 disjoncteurs. Couper le peigne à la bonne longueur.
   * **Sans peigne** : fils 6 mm² (ou 2,5 mm² rigides) en repiquage Phase et Neutre : différentiel → disj. L1 → disj. L2 → disj. L3.

### B. Ligne L1 – Prises côté droit (Disjoncteur 16A – 3G2,5 mm²)

* **Coffret :** Phase → borne `L` (bas) du disj. L1 ; Neutre → borne `N` (bas) du disj. L1 ; Terre → bornier de terre.
* **Coffret → bloc 3 prises intérieures** (au-dessus du coffret) : câblage en repiquage dans le boîtier (Phase sur `L`, Neutre sur `N`, Terre sur la borne centrale ⏚).
* **Coffret (ou bloc 3 prises) → 2 prises extérieures** : traversée de la paroi OSB avec presse-étoupe / passe-câble étanche, prises **IP55** avec clapet.

### C. Ligne L2 – Prises côté gauche (Disjoncteur 16A – EXVB 3G2,5 mm² sous chape)

* **Coffret :** Phase → borne `L` (bas) du disj. L2 ; Neutre → borne `N` ; Terre → bornier de terre.
* **Passage sous la chape :** câble **EXVB 3G2,5 mm²** dans une **gaine (Ø 20-25 mm)** posée avant le coulage, avec remontées en gaine côté coffret et côté paroi gauche.
* **2 prises intérieures (paroi gauche)** : repiquage d'une prise à l'autre.
* **1 prise extérieure (paroi gauche)** : repiquée depuis les prises intérieures, traversée de la paroi étanche, prise **IP55**.

### D. Ligne L3 – Éclairage (Disjoncteur 10A/16A – 3G1,5 mm²)

```text
[COFFRET]                [BOÎTIER INTERRUPTEUR]          [SPOT]
Disj. L3  L ── Marron ──> borne L inter.
                          borne ↑ inter. ── Marron/Noir ──> L spot
Disj. L3  N ── Bleu ────> Wago Neutre ───── Bleu ─────────> N spot
Bornier ⏚ ── Vert/Jaune > Wago Terre ────── Vert/Jaune ───> ⏚ spot
```

* **Coffret → interrupteur** : câble 3G1,5 mm². La Phase arrive sur la borne `L` de l'interrupteur ; Neutre et Terre passent dans des Wago dans le boîtier de l'interrupteur.
* **Interrupteur → Spot** : câble 3G1,5 mm². Le fil « retour » (phase commandée) part de la borne de sortie de l'interrupteur vers la borne `L` du spot ; Neutre et Terre repartent des Wago.
* Pas besoin de boîte de dérivation : le boîtier de l'interrupteur (profond) sert de point de raccordement.

## 6. Liste du matériel

### Coffret

| Composant | Quantité | Spécification technique | Usage |
| --- | --- | --- | --- |
| **Coffret étanche** | 1 | IP65, 8 modules (12 conseillé), avec bornier terre + neutre | Tableau de l'abri |
| **Interrupteur différentiel** | 1 | Bipolaire, **30 mA, Type A, 40A** | Protection des personnes, tout l'abri |
| **Disjoncteur 16A** | 2 | 1P+N, **courbe C**, 3 kA min. | L1 Prises droite, L2 Prises gauche |
| **Disjoncteur 10A** (ou 16A) | 1 | 1P+N, **courbe C** | L3 Éclairage |
| **Peigne Phase + Neutre** | 1 | Peigne d'alimentation Ph+N, à couper à 5 modules (diff. + 3 disj.) — **même marque que le différentiel et les disjoncteurs** (ex. Hager, comme le tableau de la maison) | Pontage différentiel → disjoncteurs |
| **Obturateurs** | selon besoin | Caches modulaires | Fermer les modules libres |
| **Presse-étoupes** | 4-5 | M20/M25 | Entrées de câbles étanches du coffret |

### Prises, interrupteur, éclairage

| Composant | Quantité | Spécification technique | Ligne |
| --- | --- | --- | --- |
| **Bloc 3 prises** (ou 3 prises + cadre triple) | 1 | Avec terre, IP44 min. | L1 – intérieur droit |
| **Prise double étanche** (ou 2 simples) | 1 | **IP55** avec clapet et terre (ex. Niko Hydro) | L1 – extérieur droit |
| **Prise double** (ou 2 simples) | 1 | Avec terre, IP44 min. | L2 – intérieur gauche |
| **Prise simple étanche** | 1 | **IP55** avec clapet et terre | L2 – extérieur gauche |
| **Interrupteur simple allumage** | 1 | IP44/IP55 (ex. Niko Hydro), boîtier profond | L3 |
| **Spot** | 1 | Classe I (avec terre) ou II, IP adapté à l'emplacement | L3 |
| **Bornes Wago** | ~10 | 221-413 / 221-415 | Raccordements interrupteur / prises |

### Câbles et gaines

| Composant | Quantité estimée | Spécification technique | Usage |
| --- | --- | --- | --- |
| **Câble EXVB 3G2,5 mm²** | ≈ 22 m | Câble extérieur rigide | Liaison maison → coffret |
| **Câble EXVB 3G2,5 mm²** | ≈ 10 m (à mesurer) | Câble extérieur rigide | L2 sous chape (coffret → paroi gauche) |
| **Câble XVB 3G2,5 mm²** | ≈ 6 m | Câble rigide | L1 (bloc 3 prises + 2 prises ext. droite) |
| **Câble XVB 3G1,5 mm²** | ≈ 5 m | Câble rigide | L3 (coffret → interrupteur → spot) |
| **Gaine annelée rouge Ø 40 mm** | ≈ 20 m | TPC enterrable | Tranchée maison → abri |
| **Grillage avertisseur rouge** | ≈ 20 m | — | Tranchée à -40 cm |
| **Gaine Ø 20-25 mm** | ≈ 10 m | ICTA / annelée | Passage L2 sous la chape + remontées |
