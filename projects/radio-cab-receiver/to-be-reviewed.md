---

Le récepteur [PE5PVB](https://github.com/PE5PVB/SI4684-DAB-Receiver) (SI4684-DAB-Receiver) sur GitHub : Un projet très populaire qui associe un ESP32 à cette puce Si4684 via le bus SPI avec un écran LCD et des encodeurs rotatifs.

Avantage : Qualité audio et sensibilité de réception maximales.

## 1. Choix des composants et connectique

| Composant | Modèle recommandé | Rôle & Connexion |
| --- | --- | --- |
| **Microcontrôleur** | **ESP32-C5** | Cerveau du système (gestion DAB+, Bluetooth A2DP, commandes). |
| **Récepteur DAB+** | **PE5PVB (Si4684)** ou **DABShield** | Tuner radio. Connexion via **SPI** ou **UART** + I²C pour le contrôle. |
| **Amplificateur** | **TPA3116D2** (Class D, 2x50W), **PAM8403** - https://www.amazon.fr/DollaTek-amplificateur-amplificateurs-alimentation-amplificador/dp/B08HQ5F7RJ/), **MAX98357A** (I²S, 2x3W) | *Dépend de vos enceintes (voir ci-dessous).* |
| **Alimentation** | Transfo 12V ou 24V DC (ex: 12V 5A) | Alimente directement l'ampli et régule le 5V/3.3V pour l'ESP32. |

---

## 2. Choix de l'amplificateur selon vos enceintes (Baffles)

* **Option A : Petit système portable (Petits haut-parleurs 3W à 10W)**
* Utilisez **2 modules MAX98357A** (amplificateurs mono I²S) ou un **PCM5102A** (DAC I²S stéréo) relié à un petit ampli analogique type **PAM8403**.
* **Alimentation :** 5V DC (ou batterie 1S / 2S).


* **Option B : Véritable enceinte stéréo (Haut-parleurs 15W à 50W)**
* Utilisez une carte ampli dédiée type **TPA3116D2 (2x50W)**.
* Récupérez la sortie audio du récepteur DAB+ et la sortie DAC/I²S de l'ESP32 pour les injecter sur l'entrée Line-In (Jack / Borne) de l'ampli.
* **Alimentation :** 12V à 24V DC.

---

## 3. Schéma de câblage et flux audio

```text
                  +-------------------+
                  |  Téléphone (BT)   |
                  +---------+---------+
                            | (Bluetooth Audio A2DP)
                            v
+--------------+   SPI    +---+---+   I²S / DAC    +---------------+   HP   +----------+
| Module DAB+  |--------->| ESP32 |--------------->| Amplificateur |------->| Baffle G |
| (Si4684/etc) |  Control |  C5   |  (Audio Out)   | (TPA3116D2 /  |        +----------+
+------+-------+          +-------+                | MAX98357A)    |   HP   +----------+
       | Analog Audio (OU routé via ESP32)          +-------+-------+------->| Baffle D |
       +----------------------------------------------------+               +----------+

```

### Comment gérer la bascule (DAB+ vs Bluetooth) ?

Il y a deux façons de mixer les sources audio vers l'amplificateur :

1. **Passage tout numérique (Recommandé avec I²S) :**
   L'ESP32-C5 reçoit l'audio du DAB+ (si le module le permet en numérique) ou du Bluetooth, et envoie le flux audio unique sélectionné vers le DAC/Ampli via son bus **I²S**.
2. **Commutation analogique (Plus simple) :**
   Vous utilisez un petit relai / multiplexeur audio (ou un interrupteur double) pour basculer la ligne audio de l'ampli entre la sortie Jack du module DAB+ et la sortie audio du module Bluetooth/ESP32.

---

Pour choisir le bon amplificateur et l'alimentation adaptée à vos deux baffles, il faut analyser **3 caractéristiques clés** de vos enceintes : l'**impédance** ($\Omega$), la **puissance admissible** (Watts RMS), et le **type d'alimentation** requis.

Voici la méthode pas à pas pour faire le bon choix sans risquer de détruire vos haut-parleurs ou votre matériel.

---

## 1. Regardez l'étiquette au dos de vos baffles

Prenez une de vos enceintes et notez deux valeurs fondamentales :

* **L'impédance (en Ohms, $\Omega$) :** En général **4 $\Omega$** ou **8 $\Omega$** (plus rarement 6 $\Omega$).
* **La puissance RMS (en Watts) :** Attention à bien lire la puissance **RMS** (continue) et non la puissance "Peak", "Max" ou "PMPO" qui est souvent gonflée pour le marketing.

---

## 2. Choisir le bon amplificateur

Pour un montage DIY audio avec un ESP32, les cartes d'amplification en **Classe D** sont les plus efficaces (elles chauffent peu et consomment très peu d'énergie).

### A. L'Impédance ($\Omega$)

* L'amplificateur doit supporter l'impédance de vos baffles.
* Si vos baffles font **4 $\Omega$**, choisissez un ampli compatible 4–8 $\Omega$.
* Si vos baffles font **8 $\Omega$**, n'importe quel ampli 4–8 $\Omega$ conviendra parfaitement (l'ampli fournira juste environ 50 % de puissance en moins sous 8 $\Omega$ que sous 4 $\Omega$).

### B. La Puissance (Watts RMS)

* **La règle d'or :** Choisissez un amplificateur capable de fournir entre **75 % et 100 % de la puissance RMS de vos baffles**.
* *Exemple :* Pour 2 baffles de **30W RMS sous 4 $\Omega$**, un module d'ampli stéréo estampillé **2 x 30W** ou **2 x 50W** sous 4 $\Omega$ sera parfait.

### Les cartes d'amplification de référence en DIY :

| Puissance souhaitée | Module d'ampli conseillé | Tension acceptée | Usage type |
| --- | --- | --- | --- |
| **Petite enceinte (2 x 3W à 5W)** | **PAM8403** ou **2x MAX98357A** (I²S) | 5V DC | Enceinte nomade USB / Batterie |
| **Moyenne enceinte (2 x 15W à 25W)** | **TPA3116D2 (version Mini)** ou **TDA7492** | 12V à 19V DC | Écoute de salon / Bureau |
| **Grande enceinte (2 x 30W à 50W)** | **TPA3116D2 (2x50W)** ou **ZK-502MT** | 12V à 24V DC | Caisson Hi-Fi puissant |

---

## 3. Choisir l'alimentation secteur (Le bloc transfo)

La plupart des cartes d'amplificateurs de classe D nécessitent une alimentation en courant continu (**DC**).

Pour déterminer le bloc secteur idéal (type chargeur de PC portable ou alimentation de ruban LED) :

### A. La Tension (Volts - V)

* Consultez la plage de tension acceptée par votre carte ampli (ex: 12V – 24V DC).
* **Plus la tension est haute, plus l'ampli délivrera de la puissance.**
* *Exemple avec un TPA3116D2 :* En 12V, il sortira environ $2 \times 15\text{W}$. En 24V, il sortira jusqu'à $2 \times 50\text{W}$.



### B. L'Intensité / Ampérage (Ampères - A)

Pour éviter que l'alimentation ne s'effondre lors de gros coups de basse :


$$\text{Puissance totale requise (Watts)} = \text{Puissance Audio Totale (W)} \times 1.2\text{ (marge de sécurité)}$$

$$\text{Ampérage nécessaire (A)} = \frac{\text{Puissance totale (W)}}{\text{Tension choisie (V)}}$$

* **Exemple pratique :** Vous alimentez un ampli de $2 \times 30\text{W}$ ($60\text{W}$ au total) en **12V** :

$$\text{Puissance conseillée} = 60\text{W} \times 1.2 = 72\text{W}$$


$$\text{Courant nécessaire} = \frac{72\text{W}}{12\text{V}} = 6\text{ Ampères}$$



Il vous faudra donc un bloc d'alimentation de **12V / 6A** (ou 12V / 8A).

---

Avec des baffles de **2 x 10 W RMS** (en 4 $\Omega$ ou 8 $\Omega$), vous avez une configuration très facile à alimenter. C'est une puissance idéale pour une radio de chantier, une enceinte de bureau ou un poste d'écoute très efficace sans trop chauffer ni consommer beaucoup d'énergie.

---

## 1. L'amplificateur idéal

Pour cette puissance, deux options en classe D se distinguent :

### Option A : TPA3116D2 (version Mini ou 2x50W bridée) — *Recommandée*

* **Pourquoi :** Même si la carte est vendue pour "2x50W", elle ne délivrera que la puissance envoyée par l'alimentation. En l'alimentant en **12V**, elle fournira exactement autour de **2 x 10W à 15W RMS**, ce qui est parfait pour vos baffles sans risquer de les griller.
* **Format :** Très simple à câbler avec des borniers à vis.

### Option B : PAM8610 (2 x 15W)

* **Pourquoi :** Carte d'amplification compacte et très bon marché spécialement conçue pour les petits systèmes 12V.
* **Puissance :** Délivre environ 2 x 10W sous 13V (avec un son très propre).

---

## 2. L'alimentation secteur (Le transfo)

Pour alimenter votre système (ampli + ESP32-C5 + récepteur DAB+) :

* **Tension :** **12 V DC** (courant continu).
* **Ampérage :** **2 A à 3 A** (soit un bloc secteur d'environ 12V / 2.5A ou 12V / 3A, type chargeur de bande LED ou modem).
* *Calcul :* $2 \times 10\text{W} = 20\text{W} \times 1.2\text{ (marge)} = 24\text{W}$. En 12V, $24\text{W} / 12\text{V} = 2\text{ Ampères}$ minimum.



---

## 3. Schéma d'alimentation global

Comme votre alimentation principale sera en 12V pour l'amplificateur, il faut abaisser cette tension pour l'ESP32-C5 et le module DAB+ qui fonctionnent sous **5V / 3.3V** :

```text
Alimentation 12V / 3A (Prise secteur)
       │
       ├─► (12V) ──► Amplificateur (TPA3116D2 ou PAM8610) ──► Baffles (2x 10W)
       │
       └─► (12V) ──► Module Buck Step-Down (LM2596 / MP1584)
                            │
                            └─► (5V) ──► ESP32-C5 & Module DAB+

```

---

Oui, c'est tout à fait possible et c'est une excellente option pour créer un système audio portable et puissant !

Les cellules Li-ion 18650 ont une tension nominale de **3,7 V** (pleinement chargées à 4,2 V et déchargées autour de 3,0 V). Pour obtenir environ 12 V, il faut les assembler en série ou utiliser un régulateur.

---

### Deux méthodes pour obtenir du 12 V avec des 18650

#### Méthode A : Montage en Série 3S (La méthode directe)

En reliant 3 accus 18650 en série (**3S**) :

* **Tension nominale :** $3 \times 3,7\text{ V} = 11,1\text{ V}$
* **Pleine charge :** $3 \times 4,2\text{ V} = 12,6\text{ V}$
* **Fin de décharge :** $3 \times 3,0\text{ V} = 9,0\text{ V}$

Cette plage de **9 V à 12,6 V** correspond exactement à ce qu'acceptent la plupart des appareils et amplificateurs 12 V (comme les modules TPA3116D2 ou PAM8610).

#### Méthode B : Montage 1S ou 2S + Convertisseur Step-Up (Boost)

Vous pouvez mettre des accus en parallèle (ex: 3.7 V) et utiliser un convertisseur Boost (ex: **XL6009** ou **MT3608**) pour élever la tension à un **12 V fixe et stable**.

* **Avantage :** La tension reste exactement à 12 V du début à la fin.
* **Inconvénient :** Petite perte d'énergie sous forme de chaleur dans le convertisseur (rendement d'environ 85–90 %).

---

### ⚠️ Sécurité indispensable : Le BMS (Battery Management System)

Pour un montage 3S sécurisé, vous devez obligatoirement ajouter un **BMS 3S** (ex: *BMS 3S 10A* ou *20A*) qui coûtent environ 1 € à 2 € :

1. **Équilibrage :** Il s'assure que les 3 cellules se chargent à la même tension.
2. **Protection décharge :** Il coupe l'alimentation si la tension descend sous 9 V.
3. **Protection surintensité :** Il coupe en cas de court-circuit.

---

1. **Assembler le support d'accus:** Matériel : Support 3S 18650.
   Insérez 3 accus 18650 de même capacité et de même marque dans un support d'accus 3S (boîtier avec bornes).
   *Verification:* Chaque accu affiche environ 3,7 V au multimètre avant l'assemblage.


2. **Câbler la carte BMS 3S:** Soudure.
   Reliez les bornes du support d'accus aux entrées de la carte BMS ($0\text{V}$, $3,7\text{V}$, $7,4\text{V}$, $11,1\text{V}$).
   *Verification:* Le multimètre mesure la tension totale du pack sur les sorties $P+$ et $P-$ du BMS.


3. **Connecter la charge et l'alimentation:** Finition.
   Reliez la sortie $P+$ et $P-$ du BMS à l'entrée 12 V de votre circuit (amplificateur et abaisseur 5 V pour l'ESP32). Pour recharger le pack, utilisez un chargeur dédié 3S (12,6 V DC) connecté sur ces mêmes bornes.


---

Voici le dossier technique complet (liste du matériel, schéma d'architecture et plan de câblage) pour réaliser votre poste radio/enceinte Bluetooth portable autour de l'**ESP32-C5**.

Ce système permet une **double alimentation** : utilisation nomade sur le pack batterie 3S (18650) ou utilisation fixe via un port USB-C (avec déclencheur Power Delivery 12V).

---

## 1. Liste du matériel requis

### Cartes et Modules

* **Microcontrôleur :** Module ESP32-C5 (DevKit ou carte équivalente).
* **Récepteur DAB+ :** Module tuner DAB+/FM à contrôle SPI/UART (ex: **DABShield** ou module **PE5PVB / Si4684**).
* **Amplificateur Audio :** Carte **TPA3116D2 Mini (2x50W)** ou **PAM8610 (2x15W)** (alimentée en 12V, elle délivrera parfaitement $2 \times 10\text{ W}$ RMS).
* **DAC Audio (si module DAB+ sans sortie analogique) :** Module **PCM5102A** ou **MAX98357A** (I²S).
* **Écran :** Écran **OLED I2C 0.96" SSD1306** (4 broches) ou écran **TFT ST7789 SPI** (pour afficher la station, le volume et le mode BT).
* **Contrôle Volume / Navigation :** **Encodeur rotatif (KY-040)** avec bouton-poussoir intégré.

### Alimentation & Gestion Batterie

* **Accus :** 3 accus **Li-ion 18650** (de même marque/capacité, ex: Samsung 25R ou LG MJ1).
* **Support d'accus :** Boîtier / support 3S 18650.
* **Protection Batterie :** Carte **BMS 3S 10A / 20A** (11.1V – 12.6V).
* **Alimentation USB-C (Option) :** Module **USB-C Trigger PD (Decoy Board)** réglé à **12V** (pour alimenter et charger depuis un bloc USB-C PD).
* **Chargeur 3S :** Module de charge 3S 12.6V DC ou carte de gestion d'alimentation combinée.
* **Régulateur de tension :** Convertisseur **Buck DC-DC (MP1584 ou LM2596)** (pour convertir le 12V principal en **5V fixe** pour l'ESP32, l'écran et le DAB+).

### Composants Passifs et Connectique

* **Interrupteur principal :** Interrupteur à bascule (ON/OFF).
* **Baffles :** 2 haut-parleurs $10\text{ W}$ ($4\ \Omega$ ou $8\ \Omega$).
* **Fils et câblage :** Fils 22 AWG (logique/signal) et fils 18 AWG (lignes d'alimentation 12V).

---

## 2. Schéma d'Architecture Alimentation & Audio

```text
┌─────────────────────────────────────────────────────────────┐
│                 SOURCE D'ALIMENTATION (12V)                 │
│  [Pack 3x 18650 + BMS 3S]  OU  [Module USB-C Trigger 12V]  │
└──────────────────────────────┬──────────────────────────────┘
                               │ (12V DC)
                               ├──────────────────────────┐
                               ▼                          ▼
               ┌───────────────────────────┐  ┌──────────────────────┐
               │    Convertisseur Buck     │  │  Amplificateur 12V   │
               │   (12V vers 5V Fixe)      │  │  (TPA3116 / PAM8610) │
               └───────────────┬───────────┘  └──────────┬───────────┘
                               │ (5V)                    │ (Audio Out)
        ┌──────────────────────┼──────────────────┐      ▼
        ▼                      ▼                  ▼  [Baffles 2x10W]
   ┌─────────┐           ┌──────────┐       ┌──────────┐
   │ ESP32-C5│           │Module DAB│       │Écran OLED│
   └─────────┘           └──────────┘       └──────────┘

```

---

## 3. Plan de Câblage Détaillé

### A. Section Alimentation & Batterie (12V ➔ 5V)

1. **Batteries ➔ BMS 3S :** Reliés aux bornes $0\text{V}$, $3.7\text{V}$, $7.4\text{V}$, et $11.1\text{V}$ du BMS.
2. **Sortie BMS ($P+$ / $P-$) & USB-C Trigger 12V :** Reliés aux deux pôles de l'interrupteur ON/OFF principal.
3. **Sortie de l'interrupteur (Ligne 12V VCC) :**
* Connecter au $+12\text{V}$ (VCC) de l'**Amplificateur Audio**.
* Connecter à l'entrée **IN+** du **Convertisseur Buck**.


4. **Réglage du Convertisseur Buck :** Avant de brancher les cartes logiques, ajuster la potence du Buck pour obtenir **exactement 5.0V** sur les sorties **OUT+** et **OUT-**.
5. **Sortie Buck (5V) :** Alimente les broches `5V` (ou `VIN`) et `GND` de l'**ESP32-C5**, du **module DAB+**, et de l'**Écran OLED**.

---

### B. Connexions Logiques & Audio (ESP32-C5)

#### 1. Module DAB+ (Bus SPI & Audio)

* **VCC / GND :** Connectés au 5V / GND du Buck.
* **SPI Bus :**
* `MOSI` ➔ ESP32-C5 (`GPIO 7`)
* `MISO` ➔ ESP32-C5 (`GPIO 2`)
* `SCK` ➔ ESP32-C5 (`GPIO 6`)
* `CS` ➔ ESP32-C5 (`GPIO 10`)


* **Audio Out (DAB+) :** Relié à l'entrée ligne `L-IN` / `R-IN` / `GND` de l'amplificateur (ou injecté via le DAC I²S pour un traitement par l'ESP32).

#### 2. Écran OLED SSD1306 (Bus I2C)

* `VCC` ➔ 5V (ou 3.3V)
* `GND` ➔ GND
* `SDA` ➔ ESP32-C5 (`GPIO 4`)
* `SCL` ➔ ESP32-C5 (`GPIO 5`)

#### 3. Encodeur Rotatif KY-040 (Volume & Menu)

* `VCC` ➔ 3.3V (ou 5V)
* `GND` ➔ GND
* `CLK` (A) ➔ ESP32-C5 (`GPIO 18`)
* `DT` (B) ➔ ESP32-C5 (`GPIO 19`)
* `SW` (Bouton-poussoir) ➔ ESP32-C5 (`GPIO 20`)

#### 4. Sortie Audio ESP32 (Bluetooth Audio / I²S vers Ampli)

Si vous utilisez un DAC externe type **PCM5102A** pour convertir le flux Bluetooth A2DP de l'ESP32 en signal analogique vers l'amplificateur :

* `BCK` ➔ ESP32-C5 (`GPIO 12`)
* `LRCK` ➔ ESP32-C5 (`GPIO 13`)
* `DOUT` ➔ ESP32-C5 (`GPIO 14`)
* **Sortie RCA/Jack du DAC** ➔ Entrée Audio de l'amplificateur TPA3116.

---

1. **Assemblage et réglage de la ligne d'alimentation:** Étape 1.
   Câblez le pack 3S 18650 sur le BMS, reliez le module USB-C PD 12V, et branchez l'entrée du convertisseur Buck. Ajustez le potentiomètre du Buck avec votre multimètre pour afficher 5,0V.
   *Verification:* Le multimètre mesure $12\text{ V}$ en entrée et $5.0\text{ V}$ stables en sortie du Buck.


2. **Câblage des périphériques logiques:** Étape 2.
   Reliez l'ESP32-C5, l'écran OLED, l'encodeur rotatif et le tuner DAB+ selon la cartographie des broches (GPIO).
   *Verification:* L'écran s'allume et l'ESP32 s'initialise correctement au démarrage.


3. **Raccordement audio et haut-parleurs:** Étape 3.
   Reliez les sorties audio analogiques (DAB+ / DAC) à l'entrée de l'amplificateur TPA3116, puis branchez vos 2 baffles 10W sur les borniers de sortie gauche et droite.
   *Verification:* Aucun souffle excessif ou grésillement n'est émis au repos, et le son sort sur les deux voies en mode DAB+ ou Bluetooth.

---

Voici un schéma explicatif complet et un plan de découpe pour construire votre caisson audio portable sur mesure, optimisé pour intégrer vos 2 haut-parleurs 10W, le tuner DAB+, l'ESP32-C5, l'amplificateur et le pack de batteries.

---

## 📐 1. Visualisation & Modélisation du Caisson

Le caisson est conçu dans un format compact de type **"Radio de chantier / Enceinte Vintage"** (dimensions extérieures d'environ **$26\text{ cm} \times 18\text{ cm} \times 16\text{ cm}$**).

```text
               ╔═════════════════════════════════════════╗
               ║               PANNEAU HAUT              ║
               ║  ┌───────────────┐     ┌─────────────┐  ║
               ║  │ Antenne DAB+  │     │ Poignée Pli │  ║
               ║  └───────────────┘     └─────────────┘  ║
               ╠═════════════════════════════════════════╣
               ║               FACE AVANT                ║
               ║                                         ║
               ║   ┌─────────┐   ┌─────────┐   ┌─────┐   ║
               ║   │ Écran   │   │ Vol/Nav │   │ ON  │   ║
               ║   │ OLED    │   │ (KY040) │   │ OFF │   ║
               ║   └─────────┘   └─────────┘   └─────┘   ║
               ║                                         ║
               ║   ┌───────────┐         ┌───────────┐   ║
               ║   │           │         │           │   ║
               ║   │ Baffle G  │         │ Baffle D  │   ║
               ║   │   (10W)   │         │   (10W)   │   ║
               ║   │           │         │           │   ║
               ║   └───────────┘         └───────────┘   ║
               ║                                         ║
               ╠═════════════════════════════════════════╣
               ║              PANNEAU BAS                ║
               ╚═════════════════════════════════════════╝

```

---

## 🛠️ 2. Fiche de Découpe (Bois : Contreplaqué 12 mm)

Pour obtenir des angles parfaits et un montage simple, voici les dimensions précises des **6 planches** à découper :

| Panneau | Quantité | Largeur | Hauteur | Découpes / Perçages à effectuer |
| --- | --- | --- | --- | --- |
| **Face Avant** | 1 | $26,0\text{ cm}$ | $18,0\text{ cm}$ | 2x trous HP (diamètre selon vos baffles), 1x rectangle OLED ($25 \times 14\text{ mm}$), 1x trou 7mm (Volume), 1x trou rectangulaire (ON/OFF) |
| **Face Arrière** | 1 | $26,0\text{ cm}$ | $18,0\text{ cm}$ | 1x trou rond pour l'évent Bass-Reflex (diamètre ~30mm), 1x trou carré/rond pour le port de charge USB-C Trigger 12V |
| **Haut / Bas** | 2 | $26,0\text{ cm}$ | $13,6\text{ cm}$ | Panneau haut : perçage pour l'embase d'antenne télescopique |
| **Côtés (G/D)** | 2 | $13,6\text{ cm}$ | $15,6\text{ cm}$ | Aucun (panneaux pleins) |

---

## 📦 3. Agencement Interne des Composants

L'espace intérieur est séparé en **deux zones** pour protéger l'électronique des vibrations acoustiques créées par les haut-parleurs :

```text
┌─────────────────────────────────────────────────────────────┐
│                       INTERIEUR CAISSON                     │
│                                                             │
│  [Baffle Gauche]      ┌─────────────────┐   [Baffle Droit]  │
│      (10W)            │ Écran + Encoder │       (10W)       │
│                       └────────┬────────┘                   │
│                                │                            │
│  ══════════════════════════════╧══════════════════════════  │
│              CLOISON / PLATINE SUPPORT INTERNE              │
│                                                             │
│   ┌──────────────┐     ┌─────────────┐    ┌──────────────┐  │
│   │ ESP32-C5 +   │     │ Ampli 12V   │    │ Pack 3S      │  │
│   │ Tuner DAB+   │     │ (TPA3116)   │    │ (18650+BMS)  │  │
│   └──────────────┘     └─────────────┘    └──────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

```

1. **Partie supérieure (Façade) :** Accueille les deux haut-parleurs $10\text{ W}$, l'écran OLED et l'encodeur de volume.
2. **Platine du bas (Au fond du caisson) :** Les cartes électroniques (**ESP32-C5**, **Tuner DAB+**, **Ampli 12V**, **Régulateur Buck 5V**) et le **Pack batterie 3S + BMS** sont vissés à plat sur la planche du bas avec de petites entretoises en plastique.

---

1. **Traçage et perçage de la face avant:** 1 à 2 heures.
   Dessinez au crayon l'emplacement des 2 baffles (espacés d'au moins $3\text{ cm}$ au centre). Percez les trous des haut-parleurs et de l'écran avec votre scie sauteuse (munie de son compas) ou à la scie à guichet.
   *Verification:* Posez vos haut-parleurs et votre écran pour vérifier qu'ils s'encastrent sans forcer.


2. **Assemblage et collage de la caisse:** 45 min.
   Appliquez de la colle à bois sur tous les chants des planches et assemblez le bas, les deux côtés et le haut autour de la face avant. Fixez des petites baguettes de renfort dans les coins intérieurs.
   *Verification:* Vérifiez l'équerrage des panneaux à l'aide d'une équerre de menuisier avant le séchage.


3. **Fixation de l'électronique et câblage:** 1 heure.
   Vissez les cartes électroniques sur la planche de fond avec des entretoises nylon 5mm. Effectuez les liaisons logiques (SPI/I2C) et alimentations selon le plan de câblage.
   *Verification:* Allumez le système via l'interrupteur principal et vérifiez que le son sort sur les deux baffles avant d'imposteur la face arrière.


---
