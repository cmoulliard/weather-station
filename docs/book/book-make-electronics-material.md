# Components for "Make: Electronics" (3rd ed. — Charles Platt)

Here's the complete material list for **"L'électronique en pratique"** (aka *Make: Electronics* by Charles Platt, 3rd edition):

## Metrial available - Freenove 20

![freenove-020.jpg](img/freenove-020.jpg)

## To be integrated

**Optional**

| Product Reference | Key Specifications / Details | Tinytronics Link |
| --- | --- | --- |
| JST-PH 2.0mm 2-Pin Cable | Plug extension/lead for solar panel or custom battery connections. | [TinyTronics](https://tinytronics.nl/shop/en/cables/jst/jst-2.0mm-connector-with-cable-ph2.0-2-pins) |
| Dupont Female-to-Female Jumper Wires | 10cm or 20cm wires to connect the BME280 sensor to the FireBeetle I2C pins (`SDA` / `SCL`). | [TinyTronics](https://www.tinytronics.nl/en/cables-and-connectors/cables-and-adapters/prototyping-wires/dupont-compatible-and-jumper/dupont-jumper-wire-female-female-10cm-10-wires) |
| JST-PH Compatible Crimp Connector and Housing Set | Crimp pins + housings (2.0mm pitch) for making custom JST-PH cables. | [TinyTronics](https://www.tinytronics.nl/en/cables-and-connectors/connectors/jst-compatible/jst-ph-compatible-crimp-connector-and-housing-set) |
| UNI-T UT133B Multimeter |  | [TinyTronics](https://www.tinytronics.nl/en/tools-and-mounting/tools/measuring/lcr-and-multimeters/uni-t-ut133b-multimeter) |
| Pinces alligator |  | [TinyTronics](https://www.tinytronics.nl/en/cables-and-connectors/cables-and-adapters/alligator-clip/goobay-alligator-clip-cable-set-50cm-10-pieces) |


TODO:

- battery with loose wires: https://www.tinytronics.nl/en/power/battery-holders-and-clips/aa/2x-aa-battery-holder-with-loose-wires

| Élément / Composant | Référence / Spécification Tinytronics | Lien Tinytronics | Usage & Remarques |
| --- | --- | --- | --- |
| **Set de résistances CMS 0805** | *1Ω-10MΩ 0805 SMD Resistor Set* | [Résistances CMS 0805](https://www.google.com/search?q=https://www.tinytronics.nl/en/components/resistors/smd-resistors) | Couvre l'ensemble des besoins en résistances CMS 0805 de signal et de polarisation. |
| **Résistances de puissance / Shunts** | Résistances traversantes (1/4W / 1W) ou CMS 1206/2512 | [Toutes les Résistances](https://www.tinytronics.nl/en/components/resistors) | Nécessaires uniquement pour les valeurs < 1 Ω ou les lignes dissipant plus de 125 mW. |
| **Set de condensateurs CMS (Optionnel)** | *0805 SMD Capacitor Set* (ex. 10 pF à 10 µF) | [Condensateurs CMS](https://www.tinytronics.nl/en/components/capacitors) | Complément idéal pour le filtrage et le découplage associés aux résistances. |
| **Accessoires de brasage CMS** | Flux de soudure, tresse à désouder et fil d'étain fin | [Matériel de Soudure](https://www.tinytronics.nl/en/tools-and-mounting/soldering) | Recommandés pour faciliter la manipulation et le brasage des boîtiers 0805. |


## Material defined part of the Annex A

> **Sets / Assortments** — For resistors and capacitors, buying sets is far cheaper than individual parts:
> - Resistors: [set 10Ω–1MΩ ~600pcs (€5.00) — TinyTronics](https://www.tinytronics.nl/en/components/resistors/resistors/10%CF%89-1m%CF%89-resistor-set)
> - Ceramic capacitors: [set 20pF–1µF ~180pcs (€5.00) — TinyTronics](https://www.tinytronics.nl/en/components/capacitors/monolithic-ceramic-capacitor-set-20pf-1uf)
> - Electrolytic capacitors: [set 0.22µF–470µF ~120pcs (€4.00) — TinyTronics](https://www.tinytronics.nl/en/components/capacitors/elektrolytic-capacitor-set-0.22uf-470uf)
> - Trimmer potentiometers: [set Cermet 3362 100Ω–1MΩ 13 values (€3.00) — TinyTronics](https://www.tinytronics.nl/en/components/resistors/potentiometers/cermet-potmeter-type-3362-set-100r-1m)
>
> In the tables below, cells marked **(set)** are covered by these assortments.

### Figure A-1 — Chapter 1 (Experiences 1 - 5)

| Composants | 1 | 2 | 3 | 4 | 5 | Avec | Sans | DigiKey.be | TinyTronics.nl |
|---|---|---|---|---|---|---|---|---|---|
| Pile de 9 V | 1 | 1 | 1 | 1 | | 1 | 4 | [€1.18](https://www.digikey.be/nl/products/detail/keystone-electronics/68/316580) | [€0.50](https://www.tinytronics.nl/en/power/battery-holders-and-clips/9v/9v-battery-clip-with-loose-wires-15cm-hard) |
| LED rouge 5 mm | | 2 | 1 | | 1 | 2 | 4 | [€0.07](https://www.digikey.be/en/products/detail/lumimax-optoelectronic-technology/LEDDC-5RED/26680666) | [€0.10](https://www.tinytronics.nl/en/components/leds/leds/red-led-5mm-diffuse) |
| Fusible cartouche 1 A | | | 1 | | | 1 | 1 | - | [€0.40](https://www.tinytronics.nl/en/components/fuses/fuse-5x20mm-1a) |
| Fusible cartouche 3 A | | | 1 | | | 1 | 1 | - | - |
| Résistance de 15 Ω | 1 | | | 1 | | 1 | 2 | (set) | (set) |
| Résistance de 150 Ω | | 1 | | | | 1 | 1 | (set) | (set) |
| Résistance de 470 Ω | | 1 | 1 | | | 1 | 2 | (set) | (set) |
| Résistance de 1K | | | | 1 | | 1 | 1 | (set) | (set) |
| Résistance de 1,5K | 1 | 1 | | | | 1 | 2 | (set) | (set) |
| Résistance de 2,2K | | 1 | | | | 1 | 1 | (set) | (set) |
| Résistance de 3,3K | | | 1 | | | 1 | 1 | (set) | (set) |

### Figure A-2 — Chapter 2 (Experiences 6 - 11)

| Composants | 6 | 7 | 8 | 9 | 10 | 11 | Avec | Sans | DigiKey.be | TinyTronics.nl |
|---|---|---|---|---|---|---|---|---|---|---|
| Fils de test pinces crocodiles | 5 | 3 | | | | | 5 | 5 | - | [€7.00](https://www.tinytronics.nl/en/cables-and-connectors/cables-and-adapters/alligator-clip) |
| Inter. SPDT glissière 5 mm | 2 | | | | | | 2 | 2 | [€0.65](https://www.digikey.be/en/products/detail/e-switch/EG1206/251333) | [€0.20](https://www.tinytronics.nl/en/switches/manual-switches/slide-switches/small-switch-for-pcb-or-breadboard) |
| Inter. SPDT glissière 2,5 mm | | | | | | 1 | 1 | 1 | [€0.65](https://www.digikey.be/en/products/detail/e-switch/EG1206/251333) | [€0.20](https://www.tinytronics.nl/en/switches/manual-switches/slide-switches/small-switch-for-pcb-or-breadboard) |
| LED générique rouge | 1 | | 2 | 1 | 1 | 2 | 2 | 7 | [€0.07](https://www.digikey.be/en/products/detail/lumimax-optoelectronic-technology/LEDDC-5RED/26680666) | [€0.10](https://www.tinytronics.nl/en/components/leds/leds/red-led-5mm-diffuse) |
| Relais DPDT 9 V CC | | 2 | 1 | | 1 | | 2 | 4 | [€3.42](https://www.digikey.be/en/products/detail/omron-electronics-inc-emc-div/G5V-2-DC9/369045) | - |
| Interrupteur tactile | | 1 | 2 | 2 | 2 | 2 | 2 | 9 | [€0.16](https://www.digikey.be/en/products/detail/te-connectivity-alcoswitch-switches/FSM4JRT/529666) | [€0.15](https://www.tinytronics.nl/en/switches/manual-switches/pcb-switches/breadboard-tactile-pushbutton-switch-momentary-2pin-6*6*5mm) |
| Transistor 2N3904 | | | | | 1 | 6 | 6 | 7 | [€0.12](https://www.digikey.be/en/products/detail/onsemi/2N3904TAR/4213831) | [€0.15](https://www.tinytronics.nl/en/components/transistors/npn-transistor-2n3904) |
| Potentiomètre ajust. 10K | | | | | | 1 | 1 | 1 | [€2.18](https://www.digikey.be/en/products/detail/bourns-inc/3362P-1-104TLF/2536613) | [€0.75](https://www.tinytronics.nl/en/components/resistors/potentiometers/10k%CF%89-potmeter-type-rv09) |
| Haut-parleur de 8 Ω | | | | | | 1 | 1 | 1 | [€2.39](https://www.digikey.be/en/products/detail/raltron-electronics/RSP-1300-000-1341-NS1/22320892) | [€1.00](https://www.tinytronics.nl/en/audio/speakers/speakers/speaker-8%CF%89-1w-40mm) |
| Résistance de 100 Ω | | | | 1 | 2 | 1 | 2 | 5 | (set) | (set) |
| Résistance de 470 Ω | 1 | 1 | 1 | 2 | 1 | | 2 | 6 | (set) | (set) |
| Résistance de 1K | | 2 | 2 | 1 | 1 | | 2 | 6 | (set) | (set) |
| Résistance de 4,7K | | | | | | 4 | 4 | 4 | (set) | (set) |
| Résistance de 10K | | | | 1 | 2 | | 2 | 4 | (set) | (set) |
| Résistance de 33K | | | | | 1 | | 1 | 1 | (set) | (set) |
| Résistance de 47K | | | | | | 2 | 2 | 2 | (set) | (set) |
| Résistance de 100K | | | | | 1 | | 1 | 1 | (set) | (set) |
| Résistance de 330K | | | | 1 | | | 1 | 1 | (set) | (set) |
| Résistance de 470K | | | | | | 2 | 2 | 2 | (set) | (set) |
| Condensateur de 10 nF | | | | | | 3 | 3 | 3 | (set) | (set) |
| Condensateur de 1 µF | | | | 1 | | 2 | 2 | 3 | (set) | (set) |
| Condensateur de 47 µF | | | | | | 1 | 1 | 1 | (set) | (set) |
| Condensateur de 100 µF | 1 | 1 | | | | | 1 | 2 | (set) | (set) |
| Condensateur de 1 000 µF | 1 | 1 | 1 | | | | 1 | 3 | (set) | (set) |

### Figure A-4 — Chapter 3 (Experiences 12 - 14)

| Composants | 12 | 13 | 14 | Avec | Sans | DigiKey.be | TinyTronics.nl |
|---|---|---|---|---|---|---|---|
| LED rouge de 3 mm | | 1 | 2 | 2 | 3 | [€0.15](https://www.digikey.be/en/products/detail/everlight-electronics-co-ltd/HLMP1301-QT264-3ID/2675532) | [€0.10](https://www.tinytronics.nl/en/components/leds/leds/red-led-3mm-diffused) |
| Transistor 2N3904 | | | 2 | 2 | 2 | [€0.12](https://www.digikey.be/en/products/detail/onsemi/2N3904TAR/4213831) | [€0.15](https://www.tinytronics.nl/en/components/transistors/npn-transistor-2n3904) |
| Résistance de 470 Ω | | 1 | | 1 | 1 | (set) | (set) |
| Résistance de 47K | | | 2 | 2 | 2 | (set) | (set) |
| Résistance de 470K | | | 2 | 2 | 2 | (set) | (set) |
| Condensateur de 1 µF | | | 2 | 2 | 2 | (set) | (set) |

### Figure A-5 — Chapter 4 (Experiences 15 - 23)

| Composants | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | Avec | Sans | DigiKey.be | TinyTronics.nl |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Temporisateur 555 | 1 | 2 | 3 | 3 | | 1 | 2 | | 1 | 3 | 13 | [€0.52](https://www.digikey.be/en/products/detail/texas-instruments/NE555P/277057) | [€0.50](https://www.tinytronics.nl/en/components/ics-and-microcontroller-chips/ics/ne555p) |
| Inter. SPDT glissière | 1 | | 1 | | | | 1 | 1 | | 1 | 4 | [€0.65](https://www.digikey.be/en/products/detail/e-switch/EG1206/251333) | [€0.20](https://www.tinytronics.nl/en/switches/manual-switches/slide-switches/small-switch-for-pcb-or-breadboard) |
| Potentiomètre ajust. 500K | 1 | 1 | | | | | | | | 1 | 2 | - | (set pot.) |
| Interrupteur tactile | | 2 | | 1 | 3 | 2 | 9 | 2 | 2 | 9 | 21 | [€0.16](https://www.digikey.be/en/products/detail/te-connectivity-alcoswitch-switches/FSM4JRT/529666) | [€0.15](https://www.tinytronics.nl/en/switches/manual-switches/pcb-switches/breadboard-tactile-pushbutton-switch-momentary-2pin-6*6*5mm) |
| LED rouge de 3 mm | 1 | | 4 | 3 | 1 | 1 | 3 | 2 | 14 | 14 | 29 | [€0.15](https://www.digikey.be/en/products/detail/everlight-electronics-co-ltd/HLMP1301-QT264-3ID/2675532) | [€0.10](https://www.tinytronics.nl/en/components/leds/leds/red-led-3mm-diffused) |
| Haut-parleur de 8 Ω | 1 | | | | | | | | | 1 | 1 | [€2.39](https://www.digikey.be/en/products/detail/raltron-electronics/RSP-1300-000-1341-NS1/22320892) | [€1.00](https://www.tinytronics.nl/en/audio/speakers/speakers/speaker-8%CF%89-1w-40mm) |
| Potentiomètre ajust. 10K | 2 | | 1 | | | | | | | 2 | 3 | [€2.18](https://www.digikey.be/en/products/detail/bourns-inc/3362P-1-104TLF/2536613) | [€0.75](https://www.tinytronics.nl/en/components/resistors/potentiometers/10k%CF%89-potmeter-type-rv09) |
| Diode 1N4148 | 1 | 1 | | | | | | | | 1 | 2 | [€0.09](https://www.digikey.be/en/products/detail/onsemi/1N4148-T50A/978509) | [€0.10](https://www.tinytronics.nl/en/components/diodes/diode-high-speed-1n4148) |
| Compteur 4026B | | 3 | | | | | | | | 3 | 3 | [€1.27](https://www.digikey.be/en/products/detail/texas-instruments/CD4026BE/528411) | - |
| Afficheur LED 7 segments | | 3 | | | | | | | | 3 | 3 | [€2.18](https://www.digikey.be/en/products/detail/kingbright/SC56-11SURKWA/4098569) | - |
| Régulateur LM7805 | | | 1 | 1 | 1 | 1 | | | | 1 | 5 | [€1.63](https://www.digikey.be/en/products/detail/texas-instruments/LM7805CT-NOPB/3901929) | [€0.50](https://www.tinytronics.nl/en/components/voltage-regulators/lm7805c-5v-voltage-regulator) |
| Circuit intégré ET 74HC08 | | 1 | 2 | | | | | | | 1 | 4 | [€0.69](https://www.digikey.be/fr/products/detail/texas-instruments/SN74HC08N/277216) | [€0.60](https://www.tinytronics.nl/en/components/ics-and-microcontroller-chips/ics/74hc08-2-input-and-gate-4-channels-14-pin-dip) |
| Circuit intégré OU 74HC32 | | | | 1 | | 1 | | | | 1 | 3 | [€0.65](https://www.digikey.be/nl/products/detail/texas-instruments/SN74HC32N/277235) | [€1.00](https://www.tinytronics.nl/nl/componenten/ic's-en-microcontrollerchips/ic's/sn74hc32n-2-input-or-poort-4-kanalen-14-pin-dip) |
| Pile de 9 V | | 1 | | | | | | | | 1 | 1 | [€1.18](https://www.digikey.be/nl/products/detail/keystone-electronics/68/316580) | [€0.50](https://www.tinytronics.nl/en/power/battery-holders-and-clips/9v/9v-battery-clip-with-loose-wires-15cm-hard) |
| Relais DPDT 9 V | | | | | 1 | | | | | 1 | 1 | [€3.42](https://www.digikey.be/en/products/detail/omron-electronics-inc-emc-div/G5V-2-DC9/369045) | - |
| Transistor 2N3904 | | | | | 1 | | | | | 1 | 1 | [€0.12](https://www.digikey.be/en/products/detail/onsemi/2N3904TAR/4213831) | [€0.15](https://www.tinytronics.nl/en/components/transistors/npn-transistor-2n3904) |
| CI NON-OU 74HC02 | | | | | | 1 | | | | 1 | 1 | [€0.72](https://www.digikey.be/en/products/detail/texas-instruments/SN74HC02N/277210) | [€0.60](https://www.tinytronics.nl/en/components/ics-and-microcontroller-chips/ics/74hc02n-2-input-nor-gate-4-channels-14-pin-dip) |
| Compteur 74HC393 | | | | | | | 1 | | | 1 | 1 | [€0.61](https://www.digikey.be/en/products/detail/texas-instruments/SN74HC393N/376742) | - |
| CI NON-OU 74HC27 | | | | | | | | | 1 | 1 | 1 | [€0.68](https://www.digikey.be/nl/products/detail/nxp-usa-inc/74HC27N-652/1230262) | - |
| Résistance de 100 Ω | | 1 | | | | | | | | 1 | 1 | (set) | (set) |
| Résistance de 470 Ω | 1 | | 4 | 2 | | 1 | 3 | | | 6 | 17 | (set) | (set) |
| Résistance de 1K | | | 3 | | 3 | 1 | | | | 4 | 13 | (set) | (set) |
| Résistance de 4,7K | | | | 1 | | | | | | 1 | 1 | (set) | (set) |
| Résistance de 10K | 3 | 3 | 5 | 5 | 2 | 9 | 3 | 2 | 2 | 9 | 34 | (set) | (set) |
| Résistance de 47K | | | | 4 | 1 | | | | | 4 | 5 | (set) | (set) |
| Résistance de 100K | | | | | 1 | | 1 | | | 1 | 2 | (set) | (set) |
| Résistance de 470K | 1 | 2 | 2 | | | | | | | 2 | 5 | (set) | (set) |
| Condensateur de 0,01 µF | 1 | 2 | 2 | 2 | | 1 | | | 2 | 2 | 10 | (set) | (set) |
| Condensateur de 0,047 µF | | | | 1 | | | | | | 1 | 1 | (set) | (set) |
| Condensateur de 0,1 µF | | | | 1 | 1 | 3 | 1 | 2 | | 3 | 8 | (set) | (set) |
| Condensateur de 0,47 µF | 1 | 2 | 2 | 1 | 2 | 1 | 1 | 1 | | 2 | 11 | (set) | (set) |
| Condensateur de 10 µF | 1 | 1 | 3 | 1 | | 1 | | | | 3 | 8 | (set) | (set) |
| Condensateur de 100 µF | | | 1 | 2 | 1 | | | | | 2 | 5 | (set) | (set) |

### Figure A-6 — Chapter 5 (Experiences 24 - 30)

| Composants | 24 | 25 | 26 | 27 | 28 | 29 | 30 | Avec | Sans | DigiKey.be | TinyTronics.nl |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Fil de câblage jauge 22 (8 m) | 1 | | 1 | | | | | 1 | 1 | [€4.91](https://www.digikey.be/en/products/detail/sparkfun-electronics/PRT-08022/6833928) | - |
| Aimant néodyme Ø 5 mm | | 1 | | | | | | 1 | 1 | - | [€0.60](https://www.tinytronics.nl/en/mechanics-and-actuators/parts/magnets/neodymium-magnet-6x3mm) |
| Fil de câblage jauge 22-26 (60 m) | | 2 | 1 | 1 | | | | 2 | 4 | [€4.91](https://www.digikey.be/en/products/detail/sparkfun-electronics/PRT-08022/6833928) | - |
| LED rouge de 3 mm | | 1 | 2 | 1 | 1 | 7 | | 7 | 11 | [€0.15](https://www.digikey.be/en/products/detail/everlight-electronics-co-ltd/HLMP1301-QT264-3ID/2675532) | [€0.10](https://www.tinytronics.nl/en/components/leds/leds/red-led-3mm-diffused) |
| Condensateur électro. 1 000 µF | | 1 | 1 | | | | | 1 | 2 | (set) | (set) |
| Diode 1N4148 | | | | | | 1 | | 1 | 1 | [€0.09](https://www.digikey.be/en/products/detail/onsemi/1N4148-T50A/978509) | [€0.10](https://www.tinytronics.nl/en/components/diodes/diode-high-speed-1n4148) |
| Aimant Ø 20 mm (option) | | 1 | | | | | | 1 | 1 | - | [€0.60](https://www.tinytronics.nl/en/mechanics-and-actuators/parts/magnets/neodymium-magnet-6x3mm) |
| Fil émaillé Ø 0,4 mm 120 m (option) | | | 1 | | | | | 1 | 1 | - | [€14.00](https://www.tinytronics.nl/en/cables-and-connectors/cables-and-adapters/prototyping-wires/copper-wire/synflex-v-180-enameled-copper-wire-0.4mm-250g) |
| Haut-parleur Ø 5 cm | | | 1 | | 1 | | | 1 | 2 | [€2.39](https://www.digikey.be/en/products/detail/raltron-electronics/RSP-1300-000-1341-NS1/22320892) | [€1.00](https://www.tinytronics.nl/en/audio/speakers/speakers/speaker-8%CF%89-1w-40mm) |
| Résistance de 47 Ω | | | 2 | | | | | 2 | 2 | (set) | (set) |
| Résistance de 470 Ω | | | 1 | | 1 | 7 | | 7 | 9 | (set) | (set) |
| Interrupteur tactile | | | | 2 | | | | 2 | 2 | [€0.16](https://www.digikey.be/en/products/detail/te-connectivity-alcoswitch-switches/FSM4JRT/529666) | [€0.15](https://www.tinytronics.nl/en/switches/manual-switches/pcb-switches/breadboard-tactile-pushbutton-switch-momentary-2pin-6*6*5mm) |
| Écouteur haute impédance | | | | | 1 | | | 1 | 1 | - | - |
| Fil de jauge 16 (15-30 m) | | | | | 1 | | | 1 | 1 | - | - |
| Diode au germanium | | | | | 1 | | | 1 | 1 | - | - |
| Fils de tests pinces crocodiles | | | | | 4 | | | 4 | 4 | - | [€7.00](https://www.tinytronics.nl/en/cables-and-connectors/cables-and-adapters/alligator-clip) |
| Circuit amplif. LM386 (option) | | | | | | 1 | | 1 | 1 | [€0.14](https://www.digikey.be/nl/products/detail/texas-instruments/LM386N-3/3695210) | - |
| Haut-parleur ou buzzer (option) | | | | | 1 | | | 1 | 1 | [€2.39](https://www.digikey.be/en/products/detail/raltron-electronics/RSP-1300-000-1341-NS1/22320892) | [€1.00](https://www.tinytronics.nl/en/audio/speakers/speakers/speaker-8%CF%89-1w-40mm) |
| Arduino Uno ou Nano | | | | | | 1 | 1 | 1 | 2 | [€23.71](https://www.digikey.be/en/products/detail/arduino/A000066/2784006) | [€7.00](https://www.tinytronics.nl/en/development-boards/microcontroller-boards/arduino-compatible/nano-v3.0-compatible) |
| Câble USB pour Uno ou Nano | | | | | | 1 | 1 | 1 | 2 | - | [€1.50](https://www.tinytronics.nl/en/cables-and-connectors/cables-and-adapters/usb/mini-usb/mini-usb-cable-50cm) |

> *La colonne « Avec » suppose la réutilisation des composants des expériences précédentes du même chapitre. « Sans » = quantité totale si achat neuf pour chaque expérience.*
>
> *Les prix DigiKey.be sont hors TVA. Les prix TinyTronics.nl incluent la TVA.*
>
> *Composants rares (écouteur haute impédance, diode germanium) : chercher sur eBay ou Amazon.*