## Electrovanne

https://www.kamody.fr/gardena-regard-pre-montable-v3-1255-20-18732

---

## 📐 1. Architecture du système d'irrigation

Pour une serre, la meilleure solution consiste à utiliser une **vanne à bille motorisée 12V** (ou électrovanne à solénoïde) associée à un **module RTC (Horloge temps réel)** pour que l'ESP32 conserve l'heure exacte même en cas de coupure de courant ou de perte du Wi-Fi.

```text
┌─────────────────────────────────────────────────────────────┐
│                 ALIMENTATION ENTRÉE (12V DC)                │
│             (Bloc secteur 12V ou Panneau Solaire)           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ├──────────────────────────┐
                               ▼                          ▼
               ┌───────────────────────────┐  ┌──────────────────────┐
               │    Convertisseur Buck     │  │ Module Relais /      │
               │   (12V vers 5V Fixe)      │  │ MOSFET 12V           │
               └───────────────┬───────────┘  └──────────┬───────────┘
                               │                         │ (12V Commuté)
                               ▼                         ▼
                         ┌───────────┐          ┌──────────────────┐
                         │  ESP32    │          │  Électrovanne /  │
                         └─────┬─────┘          │  Vanne Motorisée │
                               │                └────────┬─────────┘
                               │                         │ (Eau)
                               ▼                         ▼
                         ┌───────────┐          ┌──────────────────┐
                         │ RTC DS3231│          │  Tuyau Perforé   │
                         │ (Heure)   │          │  (Arrosage Serre)│
                         └───────────┘          └──────────────────┘

```

---

## 🛠️ 2. Liste du matériel recommandé

### Électronique & Commande

* **Microcontrôleur :** **ESP32** (NodeMCU ou DevKit 38 broches).
* **Horloge Temps Réel (RTC) :** **DS3231** (très précise, avec pile bouton de sauvegarde CR2032).
* **Commutation Vanne :**
* *Option A (Silencieux/Efficace) :* Module **MOSFET (AOD4184 / FR120N)** ou transistor TIP120.
* *Option B (Simple) :* Carte **Relais 5V ou 3.3V Optocouplé**.


* **Alimentation :** Bloc secteur **12V DC / 2A** + **Convertisseur Buck DC-DC (LM2596 ou MP1584)** pour descendre le 12V à 5V pour l'ESP32.

### Hydraulique & Serre

* **Électrovanne :**
* **Vanne à bille motorisée 12V (2 fils / inversion automatique ou 3 fils)** : *Recommandée*, car elle s'ouvre complètement sans restreindre la pression (idéale si l'eau provient d'une cuve de récupération par gravité) et ne chauffe pas.
* *Ou* **Électrovanne solénoïde 12V (Normalement Fermée - NC)** : nécessite au moins 0,2 à 0,5 bar de pression (eau du réseau/robinet).


* **Filtre à eau :** Filtre à tamis/disques en amont de la vanne (indispensable pour éviter de boucher les petits trous du tuyau).
* **Réducteur de pression (si eau du réseau) :** 1.5 à 2 bars pour éviter d'éclater le tuyau micro-perforé.
* **Tuyau micro-perforé / Goutte-à-goutte :** Tuyau poreux ou tuyau $16\text{ mm}$ avec goutteurs intégrés.

---

## 🔌 3. Schéma de câblage pas à pas

### A. Connexion du module RTC DS3231 (Bus I2C)

* **VCC** ➔ Broche `3.3V` (ou `5V`) de l'ESP32
* **GND** ➔ Broche `GND` de l'ESP32
* **SDA** ➔ Broche `GPIO 21` de l'ESP32
* **SCL** ➔ Broche `GPIO 22` de l me l'ESP32

### B. Commande de la Vanne via Transistor MOSFET (12V)

* **ESP32 GPIO 23** ➔ Entrée `SIG` / `GATE` du module MOSFET
* **GND ESP32** ➔ `GND` / `IN-` du module MOSFET
* **Alimentation 12V (+)** ➔ Borne $+$ de l'électrovanne
* **Alimentation 12V (-)** ➔ Entrée `V-` du MOSFET
* **Borne $-$ de l'électrovanne** ➔ Sortie `DRAIN` / `OUT-` du MOSFET

> ⚠️ **Rappel :** Si vous utilisez une électrovanne solénoïde directe, ajoutez une **diode de roue libre 1N4007** en parallèle sur les bornes de la vanne (Cathode avec le trait blanc au $+12\text{V}$, Anode au $-$).

---

## 💻 4. Structure du Code Arduino / C++

Le code ci-dessous utilise la bibliothèque **`RTClib`** pour lire l'heure et déclencher l'arrosage selon 2 plages horaires (ex: matin à 07h00 et soir à 20h00 pendant 15 minutes).

```cpp
#include <Wire.h>
#include "RTClib.h"

RTC_DS3231 rtc;

// Broche de commande de la vanne
const int PIN_VANNE = 23;

// Configuration des plages d'arrosage
const int HEURE_MATIN = 7;     // 07h00
const int MINUTE_MATIN = 0;
const int DUREE_ARROSAGE_MIN = 15; // Durée : 15 minutes

const int HEURE_SOIR = 20;    // 20h00
const int MINUTE_SOIR = 0;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_VANNE, OUTPUT);
  digitalWrite(PIN_VANNE, LOW); // Vanne fermée au démarrage

  if (!rtc.begin()) {
    Serial.println("Erreur : Module RTC non trouvé !");
    while (1);
  }

  // Décommenter la ligne suivante une fois pour régler l'heure du RTC sur l'heure de compilation :
  // rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
}

void loop() {
  DateTime now = rtc.now();

  Serial.print(now.hour(), DEC);
  Serial.print(':');
  Serial.print(now.minute(), DEC);
  Serial.print(':');
  Serial.println(now.second(), DEC);

  // Vérification de la plage du matin
  bool arrosageMatin = (now.hour() == HEURE_MATIN) && 
                       (now.minute() >= MINUTE_MATIN) && 
                       (now.minute() < (MINUTE_MATIN + DUREE_ARROSAGE_MIN));

  // Vérification de la plage du soir
  bool arrosageSoir = (now.hour() == HEURE_SOIR) && 
                      (now.minute() >= MINUTE_SOIR) && 
                      (now.minute() < (MINUTE_SOIR + DUREE_ARROSAGE_MIN));

  if (arrosageMatin || arrosageSoir) {
    digitalWrite(PIN_VANNE, HIGH); // Ouvrir la vanne
    Serial.println("--> ARROSAGE EN COURS");
  } else {
    digitalWrite(PIN_VANNE, LOW);  // Fermer la vanne
    Serial.println("--> Vanne fermée");
  }

  delay(10000); // Vérification toutes les 10 secondes
}

```

---

## 💡 Évolutions futures possibles pour la serre

1. **Interface Web / Wi-Fi :** Grâce au Wi-Fi de l'ESP32, vous pouvez créer un mini-serveur Web pour modifier les heures d'arrosage directement depuis votre smartphone sans re-téléverser de code.
2. **Capteur d'humidité du sol :** Ajouter un capteur d'humidité capacitif (`GPIO 34`) pour annuler l'arrosage si la terre est déjà suffisamment humide.
3. **Capteur de pluie / Niveau de cuve :** Couper la pompe ou bloquer l'ouverture de la vanne si la cuve d'eau de pluie est vide.

---

Pour raccorder votre module relais à l'électrovanne (généralement en **12V DC** pour ce type d'installation DIY sous serre), le choix du câble dépend principalement du **courant (ampérage)** absorbé par votre vanne et de la **distance** d'éloignement.

---

## 1. Quel type et section de câble utiliser ?

### A. La section des conducteurs (en $\text{mm}^2$)

* **Distance courte ($0$ à $10\text{ mètres}$) :**
* Un câble d'une section de **$0,5\text{ mm}^2$ à $0,75\text{ mm}^2$** (souple / multi-brins) est largement suffisant pour une électrovanne standard ($12\text{V}$, consommant entre $0,3\text{A}$ et $1\text{A}$).


* **Distance moyenne à longue ($10$ à $30\text{ mètres}$) :**
* Il est recommandé d'utiliser une section de **$1,0\text{ mm}^2$ à $1,5\text{ mm}^2$** afin de limiter la chute de tension en $12\text{V}$.



### B. Le type de câble (Environnement humide / Serre)

* Pour un usage extérieur ou sous serre (humidité, condensation, arrosage à proximité), privilégiez un **cables 2 conducteurs sous gaine de protection** :
* Câble souple type **H05VV-F** (2x0.75 ou 2x1.5) sous gaine PVC.
* Câble extérieur / enterré type **U-1000 R2V** (2x1.5 $\text{mm}^2$) si le câble doit passer dans la terre ou résister aux UV du soleil.



---

## 2. Jusqu'à quelle distance peut-on aller ?

En courant continu sous basse tension ($12\text{V}$), le principal obstacle sur les longues distances est la **chute de tension** (la résistance interne du câble fait chuter le $12\text{V}$ à $10\text{V}$ ou $9\text{V}$ à l'arrivée). Si la tension baisse trop, la bobine de l'électrovanne manque de force pour s'ouvrir.

### Tableau indicatif des distances max (pour $12\text{V DC}$ / $0,5\text{A}$) :

| Section du câble ($\text{mm}^2$) | Distance max recommandée ($12\text{V}$ DC) | Remarques |
| --- | --- | --- |
| **$0,5\text{ mm}^2$** | **0 à 10 mètres** | Idéal si l'ESP32 est à côté de la serre. |
| **$0,75\text{ mm}^2$** | **10 à 20 mètres** | Très bon compromis souplesse / portée. |
| **$1,5\text{ mm}^2$** | **20 à 50 mètres** | Recommandé si la réserve d'eau ou la vanne est loin. |

> 💡 **Astuce pour les très longues distances ($> 30\text{m}$) :**
> Si vous utilisez une **vanne à bille motorisée**, la distance pose moins de problème qu'avec une électrovanne solénoïde à impulsion, car son moteur consomme très peu d'énergie pendant seulement quelques secondes lors de l'ouverture/fermeture.

---

## 3. Schéma de câblage et précautions

```text
       (Côté ESP32 / Coffret)                                 (Côté Serre)
       
┌────────────────────────────────┐                      ┌──────────────────┐
│  Alimentation 12V DC (+)       ├─────────────────────►│                  │
└────────────────────────────────┘      Câble 2 fils    │                  │
┌────────────────────────────────┐ (ex: 2x0.75 à 2x1.5) │   Électrovanne   │
│  Relais (Bornes COM / NO)      ├─────────────────────►│    (12V DC)      │
└────────────────────────────────┘                      └──────────────────┘

```

1. **Polarité :** Si c'est une électrovanne solénoïde $12\text{V}$ classique, il n'y a en général pas de sens (polarité) pour les 2 fils. Si c'est une vanne motorisée 2 fils avec inversion de polarité, respectez les codes couleurs (Rouge/Noir).
2. **Étanchéité des raccordements :** Côté vanne, effectuez les soudures ou les raccords (type Wago) dans une **boîte de dérivation étanche (IP65/IP68)** ou utilisez des connecteurs étanches avec de la gaine thermo-rétractable pour éviter que la corrosion n'abîme les contacts à cause de l'humidité de la serre.

---

Regard

https://www.amazon.fr/Gardena-1255-20-Regard-pr%C3%A9mont%C3%A9-voies/dp/B0001E3S2W

Pour alimenter **2 zones d'arrosage indépendantes** (ou conserver une sortie manuelle/robinet en plus de votre vanne automatique) tout en faisant passer les câbles électriques, un **regard rectangulaire de taille standard (30 à 45 cm de long)** est idéal.

En effet, il n'existe pas de regards vendus pré-percés avec des empreintes fixes pour 1 entrée / 2 sorties : les fabricants conçoivent les regards d'arrosage avec de **nombreuses encoches prédécoupées tout autour de la base**, ce qui vous permet de découper facilement au cutter ou à la scie les trous exacts dont vous avez besoin pour vos fourreaux et tuyaux.

---

### 🛍️ Modèles de regards adaptés (1 Entrée / 2 Sorties)

Voici 2 références très répandues que vous trouverez facilement en magasin ou en ligne :

1. **Regard Rectangulaire Standard (Rain Bird VB-STD ou Gardena)**
* **Dimensions :** environ $50 \times 38\text{ cm}$ à la base (hauteur $30\text{ cm}$).
* **Pourquoi il convient :** Permet d'installer une nourrisse / collecteur 2 voies, 2 électrovannes (ou 1 vanne + 1 vanne manuelle) et votre boîte étanche électrique sans être à l'étroit.
* **Consulter chez un marchand :**
* [Regard Rain Bird VB-STD sur Leroy Merlin](https://www.google.com/search?q=https://www.leroymerlin.fr/produits/terrasse-jardin/arrosage-pompe-et-recuperateur-eau-de-pluie/arrosage-enterre/regard-electrovanne-rain-bird-vb-std-68694034.html)
* [Regard d'arrosage rectangulaire sur ManoMano](https://www.manomano.fr/cat/regard+electrovanne)




2. **Regard Gardena V3 (Pour 3 vannes max)**
* **Dimensions :** compact et robuste avec fermeture de sécurité pour enfants.
* **Consulter chez un marchand :**
* [Regard pour électrovannes Gardena V3 sur Leroy Merlin](https://www.google.com/search?q=https://www.leroymerlin.fr/produits/terrasse-jardin/arrosage-pompe-et-recuperateur-eau-de-pluie/arrosage-enterre/regard-pour-3-electrovannes-gardena-v3-67010460.html)





---

### 🚰 Montage type "1 Entrée ➔ 2 Sorties" à l'intérieur du regard

Pour diviser votre arrivée d'eau en 2 sorties à l'intérieur du regard, l'accessoire indispensable à ajouter est un **collecteur/nourrice d'arrosage 2 voies en 1" (26x34)** avec raccords union à écrou tournant (très facile à démonter sans tout tourner).

```text
                                           ┌──► Électrovanne 1 ──► Sortie 1 (Serre)
Arrivée d'Eau ──► Collecteur / Nourrice ──┤
                    (2 Voies)              └──► Électrovanne 2 (ou Robinet) ──► Sortie 2
                                                         ▲
Câbles ESP32 ──► Boîte Étanche (Gel IP68) ───────────────┘ (Commande 12V)

```

#### Liste des raccords à placer dans le regard :

* **1x Collecteur 2 voies à écrou tournant 1" (26x34) :** à visser sur l'arrivée d'eau.
* **2x Vannes (motorisées 12V ou solénoïdes) :** vissées sur chaque sortie du collecteur.
* **2x Raccords compression PE (ex: Ø 25mm ou 16mm) :** pour connecter vos 2 tuyaux de départ vers la serre ou le jardin.

---

### 🛠️ Conseils de découpe du regard

1. **Sur le côté latéral court (vers l'abri) :** Découpez l'encoche pour passer le tuyau d'arrivée d'eau + la gaine TPC électrique (20 ou 25 mm).
2. **Sur le côté latéral opposé (vers la serre) :** Découpez 2 encoches côte à côte pour laisser sortir les 2 tuyaux d'arrosage.
3. **Hauteur :** Positionnez les tuyaux à environ 5–10 cm du fond du regard pour garder les vannes bien au-dessus du lit de graviers de drainage.