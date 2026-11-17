# Plan Électrique - Abri de Jardin (variante coffret de répartition + transfo 12V)

![electricite-abri-bis.drawio.png](../diagrams/electricite-abri-bis.drawio)

## 1. Hypothèse retenue

Pas de disjoncteurs de ligne ni de différentiel dans l'abri : le coffret est équipé en tête d'un **interrupteur-sectionneur général** (coupure de tout l'abri sur place), puis sert de **point de répartition** (bornes sur rail DIN) d'où partent **3 lignes**, et accueille l'**alimentation 12V** avec son propre disjoncteur.

| Ligne / emplacement | Équipement | Câble |
| --- | --- | --- |
| **Coffret** (paroi droite, intérieur) | Interrupteur-sectionneur général + 9 bornes de répartition + disjoncteur transfo + alimentation 12V | Arrivée maison XVB 3G2,5 |
| **Ligne 1 – Porte d'entrée** | **Intérieur** : prise + interrupteur va-et-vient, montage vertical — **Extérieur** : prise **IP55** près de la porte, en repiquage | XVB 5G2,5 **sous la chape**, en gaine annelée (+ XVB 3G2,5 vers la prise extérieure) |
| **Ligne 2 – À côté du coffret** | **Option A** : bloc interrupteur va-et-vient + **double** prise — **ou Option B** : bloc interrupteur va-et-vient + **triple** prise ; **+ Spot / néon** | 5G2,5 (+ 3G2,5 vers le spot / néon) |
| **Ligne 3 – Serre** (paroi extérieure droite) | Double prise verticale **IP55** | XVB 3G2,5 |
| **Dans le coffret** | Alimentation 230V → 12V DC | Coupée par son propre disjoncteur ; 3 câbles 1,5 mm² (usages traités dans un autre document) |

Le **spot / néon** est commandé par les 2 interrupteurs en **va-et-vient** : il s'allume ou s'éteint depuis la porte d'entrée **ou** depuis le coffret.

## 2. Contraintes

* **Un seul circuit** : tout l'abri est derrière le disjoncteur **Hager MWS 220A – C20** du tableau de la maison. Les 3 lignes sont des **départs** de ce circuit, pas des circuits protégés séparément. Puissance totale disponible : **20A ≈ 4 600 W**.
* **Différentiel 30 mA obligatoire en amont** : comme il n'y a pas de différentiel dans l'abri, le C20 de la maison doit être placé **sous un différentiel 30 mA** (à vérifier au tableau, sinon à ajouter).
* **Interrupteur-sectionneur ≠ protection** : il permet de **couper et isoler** l'abri sur place (intervention, absence prolongée), mais ne protège ni contre les surcharges ni contre les défauts ; la protection reste assurée par le C20 et le différentiel 30 mA de la maison.
* **Tout en 2,5 mm²**, y compris les interrupteurs, les navettes et le spot / néon, puisque le circuit est protégé par un 20A. Seule exception : le câblage **en aval** du disjoncteur du transfo peut être en 1,5 mm².
* **RGIE : 8 points maximum** par circuit. Une prise simple ou multiple (même boîtier/même cache) = 1 point ; un point lumineux = 1 point ; un appareil fixe (transfo) = 1 point ; un interrupteur ne compte pas.

## 3. Comptage des points

| Point | Ligne | Option A | Option B |
| --- | --- | --- | --- |
| Porte d'entrée (intérieur) : prise + interrupteur | 1 | 1 | 1 |
| Porte d'entrée (extérieur) : prise IP55 | 1 | 1 | 1 |
| À côté du coffret : bloc interrupteur + double prise | 2 | 1 | — |
| À côté du coffret : bloc interrupteur + triple prise | 2 | — | 1 |
| Spot / néon | 2 | 1 | 1 |
| Serre : double prise verticale | 3 | 1 | 1 |
| Alimentation 12V | coffret | 1 | 1 |
| **Total** | | **6 / 8** ✅ | **6 / 8** ✅ |

Il reste 2 points de réserve pour une extension future.

## 4. Coffret de répartition

### Contenu et encombrement

| Élément | Largeur approx. |
| --- | --- |
| Interrupteur-sectionneur général 2P 40A | 2 modules |
| 9 bornes de répartition 2,5–4 mm² (3 Phase, 3 Neutre, 3 Terre) + butées | ≈ 3 modules |
| Disjoncteur 1P+N pour l'alimentation 12V | 1 module |
| Alimentation 12V rail DIN (60 W) | 2,5 à 3 modules |
| **Total** | **≈ 9 modules → coffret 12 modules** (≈ 3 modules de réserve) |

Les 3 bornes de chaque pôle sont **pontées** entre elles (6 points de serrage par pôle). Les **2 navettes** du va-et-vient (Ligne 1 ↔ Ligne 2) se raccordent entre elles dans le coffret par **2 Wago**, pas sur les bornes de répartition.

### Schéma

```text
[ARRIVÉE MAISON : XVB 3G2,5 mm² — C20 Hager + différentiel 30 mA au tableau de la maison]
        │ Ph (marron)   │ N (bleu)    │ PE (vert/jaune)
 ┌──────▼───────────────▼─────────────┼─────────────────────────────┐
 │  INTERRUPTEUR-SECTIONNEUR 2P 40A   │  (terre jamais coupée)      │
 │  (coupe Ph + N)                    │                             │
 │      │ Ph           │ N            │                             │
 │      ▼ 2,5 mm²      ▼ 2,5 mm²      ▼                             │
 │  BORNES   Ph ■■■ (pontées)   N ■■■ (pontées)   PE ■■■ (pontées)   │
 │                                                                  │
 │  Wago navette noire ●   Wago navette grise ●   (Ligne 1 ↔ Ligne 2)│
 │                                                                  │
 │  Ph + N (2,5 mm²) ──> DISJ. 2A 1P+N ──> (1,5 mm²) ──┐            │
 │  PE (1,5 mm²) ──────────────────────────────────────┤            │
 │                               ALIMENTATION 12V (L / N / ⏚)       │
 └────┬──────────────┬──────────────┬──────────────┬────────────────┘
      ▼              ▼              ▼              ▼
   Ligne 1        Ligne 2        Ligne 3        Sortie 12V DC
   XVB 5G2,5      5G2,5          XVB 3G2,5      3 câbles 2×1,5 mm²
   sous chape     inter + prises serre          (usages : autre document)
   porte entrée   + spot / néon  IP55
   + prise ext.
```

### Borne par borne

| Pôle | Raccordements (sur 6 points de serrage) |
| --- | --- |
| **Phase** | Sortie interrupteur-sectionneur · Ligne 1 · Ligne 2 · Ligne 3 · Entrée disjoncteur transfo · *1 libre* |
| **Neutre** | Sortie interrupteur-sectionneur · Ligne 1 · Ligne 2 · Ligne 3 · Entrée disjoncteur transfo · *1 libre* |
| **Terre** | Arrivée maison · Ligne 1 · Ligne 2 · Ligne 3 · Terre de l'alimentation 12V · *1 libre* |

## 5. Câblage

### A. Arrivée dans le coffret

* **Phase (marron)** → entrée `L` (haut) de l'interrupteur-sectionneur · **Neutre (bleu)** → entrée `N` (haut) de l'interrupteur-sectionneur · **Terre (vert/jaune)** → directement sur la borne Terre (jamais coupée).
* **Sorties de l'interrupteur-sectionneur** (bas) → borne Phase et borne Neutre, en fil rigide **H07V-U 2,5 mm²** (marron, bleu).
* Mettre l'interrupteur-sectionneur sur **OFF** avant toute intervention dans le coffret ou sur une ligne de l'abri ; les bornes d'entrée restent sous tension tant que le C20 de la maison n'est pas coupé.
* Câble **XVB 3G2,5 mm²** (≈ 20 m) en **gaine annelée rouge Ø 40 mm** enterrée à **60 cm**, grillage avertisseur à -40 cm.

### B. Ligne 1 – Porte d'entrée : prise + interrupteur (XVB 5G2,5 mm² sous chape, en gaine annelée) + prise extérieure

| Conducteur | Côté coffret | Côté porte d'entrée (boîtier B, intérieur) |
| --- | --- | --- |
| Marron (Phase) | Borne Phase | Wago Phase → prise `L` **+ borne commune `C` de l'interrupteur B** + repiquage prise extérieure |
| Bleu (Neutre) | Borne Neutre | Wago Neutre → prise `N` + repiquage prise extérieure |
| Vert/Jaune (Terre) | Borne Terre | Wago Terre → prise ⏚ + repiquage prise extérieure |
| Noir (navette 1) | Wago navette noire | Borne `1` de l'interrupteur B |
| Gris (navette 2) | Wago navette grise | Borne `2` de l'interrupteur B |

* Gaine **Ø 20–25 mm** posée avant le coulage de la chape, avec remontées en gaine aux deux extrémités.
* **Boîtier B → prise extérieure IP55** : **XVB 3G2,5 mm²** (marron → `L`, bleu → `N`, vert/jaune → ⏚), traversée de la paroi par **presse-étoupe / passe-câble étanche**. Prise IP55 avec clapet, montée à ≥ 1 m du sol si possible, à l'abri des projections.
* Dans le boîtier B, prévoir un **Wago 221-415** pour la Phase (arrivée, prise, commun interrupteur, repiquage) et deux **Wago 221-413** pour le Neutre et la Terre (arrivée, prise, repiquage). Choisir un **boîtier profond** (≥ 50 mm).

### C. Ligne 2 – À côté du coffret : bloc interrupteur + prises + spot / néon (5G2,5 mm²)

| Conducteur | Côté coffret | Côté boîtier A (à côté du coffret) |
| --- | --- | --- |
| Marron (Phase) | Borne Phase | Prises `L` |
| Bleu (Neutre) | Borne Neutre | Wago Neutre → prises `N` + spot / néon |
| Vert/Jaune (Terre) | Borne Terre | Wago Terre → prises ⏚ + spot / néon |
| Noir (navette 1) | Wago navette noire | Borne `1` de l'interrupteur A |
| Gris (navette 2) | Wago navette grise | Borne `2` de l'interrupteur A |

* **Option A** : bloc interrupteur va-et-vient + double prise. **Option B** : bloc interrupteur va-et-vient + triple prise.
* **Boîtier A → spot / néon** : câble **XVB 3G2,5 mm²** — marron = **retour lampe** (phase commandée, depuis le commun `C` de l'interrupteur A), bleu = Neutre, vert/jaune = Terre.
* Le **commun `C` de l'interrupteur A** n'est **pas** relié à la Phase : il ne reçoit la phase que par les navettes.

### D. Va-et-vient : schéma complet avec codes couleur

```text
 [B — PORTE D'ENTRÉE, intérieur]        [COFFRET]                  [A — PRÈS DU COFFRET]                  [SPOT / NÉON]
  inter. va-et-vient + prise                                        bloc inter. va-et-vient + 2/3 prises
            ◄──────── XVB 5G2,5 ─────────►      ◄──────── 5G2,5 ─────────►                ◄──── 3G2,5 ────►

  Prise L + C inter. B ◄── marron ──── Borne Phase ──── marron ──► Prises L
  Inter. B  1 ◄─────────── noir ────── Wago NOIR ────── noir ────► Inter. A  1
  Inter. B  2 ◄─────────── gris ────── Wago GRIS ────── gris ────► Inter. A  2
                                                                   Inter. A  C ───── marron (retour) ────► L
  Prise N ◄─────────────── bleu ────── Borne Neutre ─── bleu ────► Prises N ── Wago N ─── bleu ─────────► N
  Prise ⏚ ◄─────────────── v/j ─────── Borne Terre ──── v/j ─────► Prises ⏚ ── Wago ⏚ ─── v/j ──────────► ⏚
     │
     │  repiquage XVB 3G2,5 (marron / bleu / vert-jaune) — traversée de paroi par presse-étoupe
     ▼
  [PRISE EXTÉRIEURE IP55 — près de la porte]   L ◄ marron · N ◄ bleu · ⏚ ◄ vert/jaune

  C = borne commune de l'interrupteur va-et-vient · 1 / 2 = bornes des navettes
```

| Couleur | Rôle |
| --- | --- |
| **Marron** | Phase permanente (coffret → prises et `C` de B, coffret → prises de A) ; **retour lampe** commandé (`C` de A → spot / néon) |
| **Bleu** | Neutre (prises, prise extérieure, spot / néon) — ne va **jamais** sur un interrupteur |
| **Noir** | Navette 1 (B ↔ coffret ↔ A) |
| **Gris** | Navette 2 (B ↔ coffret ↔ A) |
| **Vert/Jaune** | Terre, raccordée partout (prises, spot / néon classe I) |

**Fonctionnement** : la Phase arrive sur le commun de B, qui l'envoie sur la navette noire ou grise ; le spot / néon s'allume quand A est positionné sur la même navette. Chaque basculement de l'un ou l'autre interrupteur inverse l'état.

| Position B | Position A | Spot / néon |
| --- | --- | --- |
| noir | noir | allumé |
| noir | gris | éteint |
| gris | noir | éteint |
| gris | gris | allumé |

* Les deux interrupteurs doivent être des **va-et-vient** (inverseurs, 3 bornes : `C`, `1`, `2`).

### E. Ligne 3 – Serre : double prise IP55 (XVB 3G2,5 mm²)

* **Coffret :** Phase → borne Phase ; Neutre → borne Neutre ; Terre → borne Terre.
* Traversée de la paroi OSB droite par **presse-étoupe / passe-câble étanche**, double prise verticale **IP55** avec clapets (Phase sur `L`, Neutre sur `N`, Terre sur ⏚, repiquage entre les 2 prises).

### F. Alimentation 12V

* **Bornes → disjoncteur 2A** : Phase et Neutre en **2,5 mm²** (ce bout n'est protégé que par le C20 de la maison).
* **Disjoncteur 2A → alimentation** : **3 fils 1,5 mm²** souples avec embouts : marron → `L`, bleu → `N` ; vert/jaune depuis la borne Terre → `⏚` de l'alimentation.
  * Prendre une alimentation **avec borne de terre ⏚** (ex. Mean Well **MDR-60-12**). Les modèles **classe II** (ex. Mean Well HDR-60-12) n'ont que `L` et `N` : dans ce cas la terre ne se raccorde pas.
* **Disjoncteur** : 2A courbe C ; passer à **4–6A courbe C** si le 2A déclenche à la mise sous tension (pic d'appel de l'alimentation). Il sert à **couper l'alimentation 12V seule** et protège les fils 1,5 mm².
* **Sortie 12V DC** : **3 câbles 2×1,5 mm²** (+ et −) sortant du coffret par presse-étoupes. Si l'alimentation n'a que 2 paires de bornes de sortie, ajouter un petit répartiteur 12V (2 bornes + et −, ou Wago 221-415). Les équipements raccordés sont décrits dans un autre document.

## 6. Liste du matériel

### Coffret

| Composant | Quantité | Spécification technique |
| --- | --- | --- |
| **Coffret étanche modulaire** | 1 | **IP55**, **12 modules**, 1 rangée, rail DIN, porte |
| **Interrupteur-sectionneur général** | 1 | **2P (Ph + N), 40A** (calibre ≥ C20 de la maison), 230V, 2 modules, rail DIN (ex. Hager SBN240) |
| **Bornes de répartition sur rail DIN** | 9 | 2,5–4 mm² : 3 grises (Phase), 3 bleues (Neutre), 3 vert/jaune (Terre) (ex. Wago série 2002) |
| **Ponts pour bornes** | 3 | Ponts 3 pôles (1 par groupe Phase / Neutre / Terre) |
| **Butées d'arrêt + plaques d'extrémité** | 2 + 3 | Fixation et isolation des bornes |
| **Wago 221-412** | 2 | Jonction des navettes Ligne 1 ↔ Ligne 2 |
| **Alimentation 12V rail DIN** | 1 | 12V DC, 60 W (≈ 5A), **avec borne ⏚** (ex. Mean Well MDR-60-12) |
| **Disjoncteur** | 1 | 1P+N, **2A courbe C** (ou 4–6A), 1 module |
| **Obturateurs** | selon besoin | Caches modulaires |
| **Presse-étoupes** | 9 | M20/M25 : arrivée, Lignes 1-2-3, 3 câbles 12V, 2 en réserve |

### Prises et interrupteurs

| Composant | Quantité | Spécification technique | Ligne |
| --- | --- | --- | --- |
| **Prise + interrupteur va-et-vient, montage vertical** | 1 | Avec terre, IP44/IP55 (ex. Legrand Plexo composable, Niko Hydro) | 1 – Porte d'entrée (intérieur) |
| **Prise extérieure étanche** | 1 | **IP55**, avec clapet et terre | 1 – Porte d'entrée (extérieur) |
| **Presse-étoupe / passe-câble étanche** | 1 | M20 | 1 – Traversée de paroi vers la prise extérieure |
| **Option A** : bloc interrupteur va-et-vient + double prise | 1 | Avec terre, IP44/IP55 | 2 – À côté du coffret |
| **Option B** : bloc interrupteur va-et-vient + triple prise | 1 | Avec terre, IP44/IP55 | 2 – À côté du coffret |
| **Spot / néon** | 1 | Classe I (avec terre) ou classe II, IP adapté (réglette LED de préférence à un tube fluorescent) | 2 |
| **Double prise verticale étanche** | 1 | **IP55**, avec clapets et terre | 3 – Serre |
| **Bornes Wago** | ~12 | 221-413 / 221-415 | Jonctions dans les boîtiers A et B |

### Câbles et gaines

| Composant | Quantité estimée | Spécification technique | Usage |
| --- | --- | --- | --- |
| **Câble XVB 3G2,5 mm²** | ≈ 22 m | Extérieur rigide | Liaison maison → coffret |
| **Câble XVB 5G2,5 mm²** | ≈ 12 m (à mesurer) | Rigide | Ligne 1 sous chape en gaine annelée (≈ 10 m) + Ligne 2 coffret → boîtier A (≈ 2 m), navettes comprises |
| **Câble XVB 3G2,5 mm²** | ≈ 4 m | Rigide | Ligne 2 boîtier A → spot / néon |
| **Câble XVB 3G2,5 mm²** | ≈ 1 m | Rigide | Ligne 1 boîtier B → prise extérieure |
| **Câble XVB 3G2,5 mm²** | ≈ 3 m | Extérieur rigide | Ligne 3 coffret → serre |
| **Fil H07V-U/R 2,5 mm²** (marron, bleu) | ≈ 1 m | Rigide | Interrupteur-sectionneur → bornes ; bornes → disjoncteur transfo |
| **Fil H07V-K 1,5 mm²** (marron, bleu, vert/jaune) | ≈ 0,5 m chacun | Souple + embouts | Disjoncteur / bornes → alimentation 12V |
| **Câble 2×1,5 mm²** | 3 câbles, longueur à définir | Selon usage (autre document) | Sorties 12V DC |
| **Gaine annelée rouge Ø 40 mm** | ≈ 20 m | TPC enterrable | Tranchée maison → abri |
| **Grillage avertisseur rouge** | ≈ 20 m | — | Tranchée à -40 cm |
| **Gaine Ø 20–25 mm** | ≈ 10 m | ICTA / annelée | Ligne 1 sous la chape + remontées |

## 7. Points à confirmer

* **Différentiel 30 mA** en amont du C20 au tableau de la maison : à vérifier.
* **Tracé de la Ligne 1** : longueur de câble et de gaine à mesurer entre le coffret et la porte d'entrée.
* **Emplacement de la serre** : si la double prise est dans la serre elle-même (et non sur la paroi de l'abri), le câble de la Ligne 3 doit être enterré en gaine comme la liaison maison-abri.
* **Option A ou B** à côté du coffret.
