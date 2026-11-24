# HiFi and FM/Dab+ radio

## Components

- Radio FM chip
  - [TEA5767](https://www.amazon.com.be/Ausi-Module-TEA5767-Antenne-T%C3%A9lescopique/dp/B0FMR51W2K) Module: single-chip FM Radio IC circuit designed for low-voltage applications
  - [RDA5807M](https://www.electrodragon.com/product/fm-radio-module-rda5807m/)
- Audio amplifier
  - [LM386]( https://www.amazon.com.be/DollaTek-LM386-amplificateur-R%C3%A9sistance-r%C3%A9glable/dp/B07DK55CGL/) 
  - [pam8610](https://www.tinytronics.nl/en/audio/amplifiers/pam8610-2x15w-audio-amplifier-mini-12v-pcb-v2: 2x15W, board only !
  - [pam8610](https://www.tinytronics.nl/en/audio/amplifiers/pam8610-2x15w-audio-amplifier-mini-12v): 2x15W, 3.5mm jack for audio input, DC-jack for power, Screw terminals for speakers. Supply voltage: 7-15V DC. Power at 12V DC: 5W 8Ω --> THD+N=0.1%, 8W 8Ω --> THD+N=1.0%, 10W 8Ω --> THD+N=10%, 15W 4Ω --> THD+N=0.1%
- Power supply:
 - [Mean Well Power Supply](https://www.tinytronics.nl/en/power/power-supplies/12v/mean-well-power-supply-12v-4.2a-switching-power-supply-lrs-50-12) - 12V 4.2A - Switching Power Supply - LRS-50-12. Can be embedded, mounted  

- [SI4686](https://www.hardlabs.io/boards/pe5pvb--si4684-dab-receiver--si4684): DAB receiver

## List of projects:

**FM Radio**
 - https://www.electroniclinic.com/arduino-fm-radio-using-tea5767-and-rda5807m-fm-stereo-radio-modules/
 - https://github.com/turtushig22-blip/ESP32-FM-Radio-Custom-PCB-and-Enclosure

 - https://www.instructables.com/Make-Your-Own-FM-Radio/
 - https://quartzcomponents.com/blogs/electronics-projects/tea5767-fm-radio-module-interfacing-with-arduino

**HiFi**
- Makita 18V battery and wood caisson: https://www.diyaudio.com/community/threads/new-portable-speaker-project.395258/
  - https://www.tinysineaudio.com/products/4-x-50w-bluetooth-dsp-amplifier-board-tsa7804bapt-x

**Dab+ Radio**
- [PE5PVB](https://github.com/PE5PVB/SI4684-DAB-Receiver)
- https://www.hackster.io/mikbigi/digiradio-open-source-dab-fm-receiver-with-aptx-bluetooth-42d2b6
- DABShield (Only for Arduino board !!!): https://www.dabshield.com/

OSS & DIY:
- https://github.com/manvalan/DigiRadio#manufacturing-fabrication-and-assembly-by-pcbway
- https://github.com/hardcoreerik/OrcSDR
- https://github.com/smhgzll/sdr7b