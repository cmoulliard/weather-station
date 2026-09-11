# ESP32-C3 Super Mini — Breadboard Tutorial

A step-by-step beginner project using the **ESP32-C3 Super Mini** and components from the **Freenove FNK0020 kit**. Each step builds on the previous one.

## What you need

**From the FNK0020 kit:**
- 1× breadboard (830-point)
- 3× LEDs (red, green, blue)
- 3× 220Ω resistors (red-red-brown)
- 1× 10kΩ resistor (brown-black-orange)
- 1× push button (tactile switch)
- 1× active buzzer
- 1× thermistor (NTC 10kΩ) or DHT11 sensor
- Jumper wires (male-to-male)

**Not in the kit (buy separately):**
- 1× ESP32-C3 Super Mini (~€3, AliExpress or Amazon)
- 1× USB-C cable (for programming and power)

## ESP32-C3 Super Mini Pinout

![esp32-c3-super-mini-pin.png](images/esp32-c3-super-mini-pin.png)

**Safe pins for this tutorial:** GPIO0, GPIO1, GPIO3, GPIO4, GPIO5, GPIO10

## Step 0: Set up Arduino IDE

### 0.1 Install Arduino IDE

Download from https://www.arduino.cc/en/software (version 2.x).

### 0.2 Add ESP32 board support

1. Open **File → Preferences**
2. In "Additional Board Manager URLs", paste:
   ```
   https://espressif.github.io/arduino-esp32/package_esp32_index.json
   ```
3. Click OK
4. Open **Tools → Board → Boards Manager**
5. Search `esp32`, install **"esp32 by Espressif Systems"** (version 3.x)

### 0.3 Select the board

1. Plug in the ESP32-C3 Super Mini via USB-C
2. **Tools → Board → esp32 → ESP32C3 Dev Module**
3. **Tools → Port** → select the port that appeared (e.g., `/dev/cu.usbmodem...` on Mac)
4. **Tools → USB CDC On Boot → Enabled** (important for serial output!)

### 0.4 Test the connection

1. Open **Tools → Serial Monitor**, set baud rate to **115200**
2. Press the RST button on the board — you should see boot messages

---

## Step 1: Blink the onboard LED

No wiring needed — just the ESP32-C3 plugged into USB.

### Code

Create a new sketch, paste this, and click Upload (→ button):

```cpp
const int LED_PIN = 8;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(115200);
  Serial.println("Blink started");
}

void loop() {
  digitalWrite(LED_PIN, LOW);   // LED ON (active LOW on this board)
  delay(500);
  digitalWrite(LED_PIN, HIGH);  // LED OFF
  delay(500);
}
```

### What you should see

The blue onboard LED blinks every half second. "Blink started" appears in the Serial Monitor.

### What you learned

- `pinMode()` configures a pin as input or output
- `digitalWrite()` sets a pin HIGH (3.3V) or LOW (0V)
- The onboard LED is **active LOW** — LOW turns it ON, HIGH turns it OFF
- `delay(ms)` pauses execution

---

## Step 2: External LED with resistor

### Wiring

```
Breadboard layout:

  ESP32-C3 Super Mini (plugged into breadboard)
  
  GPIO3 ───── 220Ω resistor ───── LED (long leg = anode) ───── GND
                                       (short leg = cathode)
```

Step by step:
1. Plug the ESP32-C3 Super Mini into the breadboard, straddling the center gap
2. Place a **red LED** on the breadboard — note the legs:
   - **Long leg** = anode (+)
   - **Short leg** = cathode (−)
3. Connect a **220Ω resistor** (red-red-brown) from **GPIO3** to the LED's **long leg**
4. Connect the LED's **short leg** to the **GND** rail
5. Connect a jumper from the ESP32's **GND pin** to the breadboard's **GND rail** (blue line)

### Code

```cpp
const int EXTERNAL_LED = 3;

void setup() {
  pinMode(EXTERNAL_LED, OUTPUT);
}

void loop() {
  digitalWrite(EXTERNAL_LED, HIGH);  // LED ON
  delay(1000);
  digitalWrite(EXTERNAL_LED, LOW);   // LED OFF
  delay(1000);
}
```

### What you learned

- LEDs need a **current-limiting resistor** (220Ω) to avoid burning out
- Without the resistor, the LED draws too much current → burns out instantly
- The resistor value is calculated: R = (3.3V − 2V) / 0.015A ≈ 87Ω (220Ω is safe and standard)

---

## Step 3: Button controls the LED

### Wiring

```
  ESP32-C3 Super Mini

  GPIO3 ──── 220Ω ──── LED(+) ──── GND        (same as Step 2)

  GPIO1 ──── Button pin 1
              Button pin 2 ──── GND             (button pulls to ground)
```

Step by step:
1. Keep the LED wiring from Step 2
2. Place a **push button** on the breadboard (it straddles the center gap)
3. Connect one side of the button to **GPIO1**
4. Connect the other side to **GND**
5. No external pull-up resistor needed — we use the ESP32's internal one

### Code

```cpp
const int LED_PIN = 3;
const int BUTTON_PIN = 1;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  Serial.begin(115200);
}

void loop() {
  int buttonState = digitalRead(BUTTON_PIN);

  if (buttonState == LOW) {
    digitalWrite(LED_PIN, HIGH);
    Serial.println("Button pressed — LED ON");
  } else {
    digitalWrite(LED_PIN, LOW);
  }

  delay(50);
}
```

### What you learned

- `INPUT_PULLUP` enables the ESP32's internal pull-up resistor (~45kΩ)
  - When button is **not pressed**: GPIO reads HIGH (pulled to 3.3V internally)
  - When button is **pressed**: GPIO reads LOW (connected to GND through button)
- This is why pressed = LOW (counterintuitive but standard)
- The 50ms delay is a simple **debounce** — prevents the button from registering multiple presses

---

## Step 4: Add a buzzer

### Wiring

```
  ESP32-C3 Super Mini

  GPIO3 ──── 220Ω ──── LED(+) ──── GND        (same as before)
  GPIO1 ──── Button ──── GND                    (same as before)
  GPIO4 ──── Buzzer (+) ──── GND                (active buzzer)
```

Step by step:
1. Keep all wiring from Step 3
2. Place the **active buzzer** on the breadboard
   - The buzzer has a (+) marking or a longer pin — connect that to **GPIO4**
   - Connect the other pin to **GND**

### Code

```cpp
const int LED_PIN = 3;
const int BUTTON_PIN = 1;
const int BUZZER_PIN = 4;

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(BUZZER_PIN, OUTPUT);
  Serial.begin(115200);
}

void loop() {
  int buttonState = digitalRead(BUTTON_PIN);

  if (buttonState == LOW) {
    // Button pressed: LED on + buzzer beeps
    digitalWrite(LED_PIN, HIGH);
    digitalWrite(BUZZER_PIN, HIGH);
    delay(100);
    digitalWrite(BUZZER_PIN, LOW);
    delay(100);
  } else {
    digitalWrite(LED_PIN, LOW);
    digitalWrite(BUZZER_PIN, LOW);
  }
}
```

### What you learned

- An **active buzzer** has a built-in oscillator — just give it power (HIGH) and it beeps
- A **passive buzzer** needs a frequency signal (we'd use `tone()`) — check which one your kit has
- Rapid on/off creates an alarm pattern

---

## Step 5: Read temperature (thermistor)

This is where it connects to your weather station project!

### Wiring

```
  ESP32-C3 Super Mini

  3V3 ──── 10kΩ resistor ──┬──── Thermistor ──── GND
                            │
                          GPIO0  (ADC read point = voltage divider midpoint)

  GPIO3 ──── 220Ω ──── LED(+) ──── GND
  GPIO1 ──── Button ──── GND
  GPIO4 ──── Buzzer(+) ──── GND
```

Step by step:
1. Keep all previous wiring
2. Connect a **10kΩ resistor** from the **3V3 pin** to a new breadboard row
3. Connect the **thermistor** from that same row to **GND**
4. Connect **GPIO0** to the junction (the row where resistor meets thermistor)

This creates a **voltage divider**: as temperature changes, the thermistor's resistance changes, which changes the voltage at GPIO0.

### Code

```cpp
#include <math.h>

const int LED_PIN = 3;
const int BUTTON_PIN = 1;
const int BUZZER_PIN = 4;
const int THERM_PIN = 0;

const float SERIES_RESISTOR = 10000.0;
const float NOMINAL_RESISTANCE = 10000.0;
const float NOMINAL_TEMP = 25.0;
const float B_COEFFICIENT = 3950.0;

float readTemperature() {
  int adcValue = analogRead(THERM_PIN);
  float voltage = adcValue / 4095.0;
  float resistance = SERIES_RESISTOR * (1.0 / voltage - 1.0);

  // Steinhart-Hart (simplified B-parameter equation)
  float tempK = 1.0 / (
    1.0 / (NOMINAL_TEMP + 273.15) +
    (1.0 / B_COEFFICIENT) * log(resistance / NOMINAL_RESISTANCE)
  );

  return tempK - 273.15;
}

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(BUZZER_PIN, OUTPUT);
  analogReadResolution(12);
  Serial.begin(115200);
  Serial.println("Mini Weather Station started!");
}

void loop() {
  float tempC = readTemperature();

  Serial.print("Temperature: ");
  Serial.print(tempC, 1);
  Serial.println(" °C");

  // Visual feedback: LED on if temp > 25°C
  if (tempC > 25.0) {
    digitalWrite(LED_PIN, HIGH);
  } else {
    digitalWrite(LED_PIN, LOW);
  }

  // Alarm: buzzer if temp > 30°C
  if (tempC > 30.0) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(200);
    digitalWrite(BUZZER_PIN, LOW);
  }

  // Button: press to get instant reading
  if (digitalRead(BUTTON_PIN) == LOW) {
    Serial.println(">>> MANUAL READ <<<");
    Serial.print("Temperature: ");
    Serial.print(tempC, 1);
    Serial.println(" °C");
    delay(500);
  }

  delay(2000);
}
```

### What you learned

- **Voltage divider**: two resistors in series split the voltage — the midpoint voltage depends on the ratio of resistances
- **Thermistor**: a resistor whose value changes with temperature (NTC = resistance goes DOWN as temperature goes UP)
- **ADC (Analog-to-Digital Converter)**: reads voltage as a number (0–4095 for 12-bit). 0 = 0V, 4095 = 3.3V
- **Steinhart-Hart equation**: converts thermistor resistance to temperature in °C
- This is the same concept your weather station uses, except the BME280 does this internally with much better accuracy

---

## Complete wiring diagram (all steps combined)

```
                        Breadboard
  ┌─────────────────────────────────────────────────────────┐
  │                                                         │
  │   3V3 ────[10kΩ]────┬────[Thermistor]──── GND          │
  │                     │                                   │
  │                   GPIO0                                 │
  │                   (ADC)                                 │
  │                                                         │
  │  GPIO3 ───[220Ω]───[LED +]──── GND                     │
  │                                                         │
  │  GPIO1 ───[Button]──── GND                              │
  │                                                         │
  │  GPIO4 ───[Buzzer +]──── GND                            │
  │                                                         │
  │              ESP32-C3                                    │
  │              Super Mini                                 │
  │              (USB-C up)                                  │
  └─────────────────────────────────────────────────────────┘

  Components used: 4 (LED, button, buzzer, thermistor)
  GPIO pins used:  4 (GPIO0, GPIO1, GPIO3, GPIO4)
  Power:           USB-C (5V from computer)
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Upload fails | Hold **BOOT** button while clicking Upload, release after "Connecting..." |
| No serial output | **Tools → USB CDC On Boot → Enabled**, then re-upload |
| LED doesn't light | Check LED polarity (long leg to resistor side) |
| Wrong temperature | Adjust `B_COEFFICIENT` (common values: 3435, 3950, 4100 — check your thermistor) |
| Button reads wrong | Make sure button straddles the breadboard center gap |
| Port not visible | Try a different USB-C cable (some are charge-only, no data) |

## Next steps

Once this works, you're ready to:
1. Replace the thermistor with a **BME280** (I2C on GPIO4=SDA, GPIO5=SCL) for accurate temperature, humidity, and pressure
2. Add **Wi-Fi** to send readings over MQTT (as in the weather station project)
3. Move from breadboard to **perfboard** for a permanent build

## References

- [ESP32-C3 Super Mini Pinout](https://lastminuteengineers.com/esp32-c3-super-mini-pinout-reference/)
- [ESP32-C3 Super Mini Specs](https://www.espboards.dev/esp32/esp32-c3-super-mini/)
- [Freenove FNK0020 Documentation](https://docs.freenove.com/projects/fnk0020/en/latest/index.html)
- [Getting Started with ESP32-C3 Super Mini](https://randomnerdtutorials.com/getting-started-esp32-c3-super-mini/)
