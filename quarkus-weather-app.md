# Quarkus Weather Station Application

Development guide for building a Quarkus native application that reads sensor data from a Raspberry Pi, publishes it via MQTT, stores it in InfluxDB, uploads to Weather APIs, and exposes a dashboard (built-in Qute/HTMX or external Node-RED).

## Architecture Overview

```
┌──────────────┐      ┌──────────────────────────────────────────────────────────┐
│  BME280      │ I2C  │                  Quarkus Native App                     │
│  Anemometer  │─────►│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐      │
│  Rain Gauge  │ GPIO │  │ Pi4J     │  │ Scheduler│  │ REST Client      │      │
│  Wind Vane   │      │  │ Sensors  │──│ (30s)    │──│ Weather APIs     │      │
└──────────────┘      │  └──────────┘  └──┬───┬───┘  └──────────────────┘      │
                      │                   │   │                                 │
                      │            ┌──────▼┐ ┌▼──────────────────────────┐      │
                      │            │ MQTT  │ │ REST /api/weather         │      │
                      │            │Client │ │ + Carbon Design Dashboard│      │
                      │            │       │ │ (Option B: built-in)     │      │
                      │            └───┬───┘ └──────────────────────────┘      │
                      └────────────────┼───────────────────────────────────────┘
                                       │
                      ┌────────────────▼────────────────────────────────────────┐
                      │              Mosquitto MQTT Broker                      │
                      └──────┬──────────────────────────────┬──────────────────┘
                             │                              │
                      ┌──────▼──────┐               ┌──────▼──────┐
                      │  InfluxDB   │               │  Node-RED   │
                      │  (storage)  │               │  Dashboard  │
                      └──────┬──────┘               │  2.0        │
                             │                      │(Option A:   │
                      ┌──────▼──────┐               │ external)   │
                      │  Grafana    │               └─────────────┘
                      │ (optional)  │
                      └─────────────┘
```

### Dashboard Options

| Option | Stack | Pros | Cons |
|--------|-------|------|------|
| **A: Node-RED Dashboard 2.0** | External Node-RED process subscribes to MQTT | Drag-and-drop gauges/charts, no frontend code | Extra Node.js process (~80 MB RAM) |
| **B: Built-in Carbon Design** | Quarkus serves HTML with Carbon Web Components + Carbon Charts via Web Bundler | Single binary, enterprise-grade UI, no Node.js runtime needed | You write the HTML/JS yourself |
| **C: Grafana** | Grafana queries InfluxDB directly | Best for advanced analytics, alerting | Heaviest footprint (~200 MB RAM) |

## 1. Project Setup

### Create the Quarkus Project

```bash
quarkus create app com.example:quarkus-weather-station \
  --extension='rest-jackson,rest-client-jackson,scheduler,smallrye-reactive-messaging-mqtt,qute,smallrye-health,io.quarkiverse.web-bundler:quarkus-web-bundler' \
  --java=21 \
  --no-code
cd quarkus-weather-station
```

### Add Pi4J and InfluxDB Dependencies

Add to `pom.xml`:

```xml
<!-- Pi4J core and Raspberry Pi plugin -->
<dependency>
    <groupId>com.pi4j</groupId>
    <artifactId>pi4j-core</artifactId>
    <version>2.7.0</version>
</dependency>
<dependency>
    <groupId>com.pi4j</groupId>
    <artifactId>pi4j-plugin-raspberrypi</artifactId>
    <version>2.7.0</version>
</dependency>
<dependency>
    <groupId>com.pi4j</groupId>
    <artifactId>pi4j-plugin-gpiod</artifactId>
    <version>2.7.0</version>
</dependency>

<!-- InfluxDB client -->
<dependency>
    <groupId>com.influxdb</groupId>
    <artifactId>influxdb-client-java</artifactId>
    <version>7.2.0</version>
</dependency>
```

## 2. Data Model

```java
package com.example.weather.model;

import java.time.Instant;

public record WeatherReading(
    double temperature,
    double humidity,
    double pressure,
    double windSpeed,
    double windDirection,
    double rainfall,
    Instant timestamp
) {}
```

## 3. Sensor Service (Pi4J)

```java
package com.example.weather.sensor;

import com.pi4j.Pi4J;
import com.pi4j.context.Context;
import com.pi4j.io.i2c.I2C;
import com.pi4j.io.i2c.I2CConfig;
import com.pi4j.io.gpio.digital.DigitalInput;
import com.pi4j.io.gpio.digital.DigitalInputConfig;
import com.pi4j.io.gpio.digital.PullResistance;
import com.example.weather.model.WeatherReading;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import jakarta.enterprise.context.ApplicationScoped;
import java.time.Instant;

@ApplicationScoped
public class SensorService {

    private static final int BME280_ADDRESS = 0x76;
    private static final int I2C_BUS = 1;
    private static final int RAIN_GPIO = 5;
    private static final int ANEMOMETER_GPIO = 6;

    private Context pi4j;
    private I2C bme280;
    private volatile int rainPulseCount;
    private volatile int windPulseCount;

    @PostConstruct
    void init() {
        pi4j = Pi4J.newAutoContext();

        I2CConfig i2cConfig = I2C.newConfigBuilder(pi4j)
            .bus(I2C_BUS)
            .device(BME280_ADDRESS)
            .id("bme280")
            .build();
        bme280 = pi4j.create(i2cConfig);

        DigitalInputConfig rainConfig = DigitalInput.newConfigBuilder(pi4j)
            .address(RAIN_GPIO)
            .pull(PullResistance.PULL_UP)
            .id("rain-gauge")
            .build();
        DigitalInput rainInput = pi4j.create(rainConfig);
        rainInput.addListener(event -> rainPulseCount++);

        DigitalInputConfig windConfig = DigitalInput.newConfigBuilder(pi4j)
            .address(ANEMOMETER_GPIO)
            .pull(PullResistance.PULL_UP)
            .id("anemometer")
            .build();
        DigitalInput windInput = pi4j.create(windConfig);
        windInput.addListener(event -> windPulseCount++);

        initBme280();
    }

    private void initBme280() {
        // Write configuration registers
        bme280.writeRegister(0xF2, (byte) 0x01); // humidity oversampling x1
        bme280.writeRegister(0xF4, (byte) 0x27); // temp+pressure oversampling x1, normal mode
        bme280.writeRegister(0xF5, (byte) 0xA0); // standby 1000ms, filter off
    }

    public WeatherReading read() {
        byte[] data = new byte[8];
        bme280.readRegister(0xF7, data);

        double temperature = parseTemperature(data);
        double pressure = parsePressure(data);
        double humidity = parseHumidity(data);

        double windSpeed = calculateWindSpeed();
        double rainfall = calculateRainfall();

        return new WeatherReading(
            temperature, humidity, pressure,
            windSpeed, 0.0, rainfall,
            Instant.now()
        );
    }

    private double calculateWindSpeed() {
        int pulses = windPulseCount;
        windPulseCount = 0;
        // 1 pulse/sec = 2.4 km/h (typical anemometer calibration)
        return pulses * 2.4 / 30.0; // averaged over 30s interval
    }

    private double calculateRainfall() {
        int pulses = rainPulseCount;
        rainPulseCount = 0;
        // Each tip = 0.2794 mm of rain (typical tipping bucket)
        return pulses * 0.2794;
    }

    private double parseTemperature(byte[] data) {
        // BME280 temperature compensation (simplified)
        int rawTemp = ((data[3] & 0xFF) << 12) | ((data[4] & 0xFF) << 4) | ((data[5] & 0xFF) >> 4);
        return rawTemp / 100.0; // placeholder: real implementation uses calibration data
    }

    private double parsePressure(byte[] data) {
        int rawPress = ((data[0] & 0xFF) << 12) | ((data[1] & 0xFF) << 4) | ((data[2] & 0xFF) >> 4);
        return rawPress / 256.0; // placeholder: real implementation uses calibration data
    }

    private double parseHumidity(byte[] data) {
        int rawHum = ((data[6] & 0xFF) << 8) | (data[7] & 0xFF);
        return rawHum / 1024.0; // placeholder: real implementation uses calibration data
    }

    @PreDestroy
    void shutdown() {
        if (pi4j != null) {
            pi4j.shutdown();
        }
    }
}
```

## 4. MQTT Publisher

```java
package com.example.weather.mqtt;

import com.example.weather.model.WeatherReading;
import io.smallrye.reactive.messaging.mqtt.MqttMessage;
import jakarta.enterprise.context.ApplicationScoped;
import org.eclipse.microprofile.reactive.messaging.Channel;
import org.eclipse.microprofile.reactive.messaging.Emitter;
import com.fasterxml.jackson.databind.ObjectMapper;

@ApplicationScoped
public class MqttPublisher {

    @Channel("weather-out")
    Emitter<String> emitter;

    private final ObjectMapper mapper = new ObjectMapper();

    public void publish(WeatherReading reading) {
        try {
            String json = mapper.writeValueAsString(reading);
            emitter.send(json);
        } catch (Exception e) {
            throw new RuntimeException("Failed to publish weather reading", e);
        }
    }
}
```

## 5. InfluxDB Writer

```java
package com.example.weather.storage;

import com.example.weather.model.WeatherReading;
import com.influxdb.client.InfluxDBClient;
import com.influxdb.client.InfluxDBClientFactory;
import com.influxdb.client.WriteApiBlocking;
import com.influxdb.client.write.Point;
import com.influxdb.client.domain.WritePrecision;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import jakarta.enterprise.context.ApplicationScoped;
import org.eclipse.microprofile.config.inject.ConfigProperty;

@ApplicationScoped
public class InfluxDbWriter {

    @ConfigProperty(name = "influxdb.url", defaultValue = "http://localhost:8086")
    String url;

    @ConfigProperty(name = "influxdb.token")
    String token;

    @ConfigProperty(name = "influxdb.org", defaultValue = "home")
    String org;

    @ConfigProperty(name = "influxdb.bucket", defaultValue = "weather")
    String bucket;

    private InfluxDBClient client;

    @PostConstruct
    void init() {
        client = InfluxDBClientFactory.create(url, token.toCharArray(), org, bucket);
    }

    public void write(WeatherReading reading) {
        WriteApiBlocking writeApi = client.getWriteApiBlocking();
        Point point = Point.measurement("weather")
            .time(reading.timestamp(), WritePrecision.S)
            .addField("temperature", reading.temperature())
            .addField("humidity", reading.humidity())
            .addField("pressure", reading.pressure())
            .addField("wind_speed", reading.windSpeed())
            .addField("wind_direction", reading.windDirection())
            .addField("rainfall", reading.rainfall());
        writeApi.writePoint(point);
    }

    @PreDestroy
    void shutdown() {
        if (client != null) {
            client.close();
        }
    }
}
```

## 6. Weather API Clients

### Weather Underground

```java
package com.example.weather.api;

import com.example.weather.model.WeatherReading;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.ws.rs.client.Client;
import jakarta.ws.rs.client.ClientBuilder;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;
import java.util.Optional;

@ApplicationScoped
public class WundergroundUploader {

    @ConfigProperty(name = "wunderground.station-id")
    Optional<String> stationId;

    @ConfigProperty(name = "wunderground.station-key")
    Optional<String> stationKey;

    private static final String BASE_URL = "https://weatherstation.wunderground.com/weatherstation/updateweatherstation.php";

    public void upload(WeatherReading reading) {
        if (stationId.isEmpty() || stationKey.isEmpty()) return;

        String dateUtc = DateTimeFormatter.ofPattern("yyyy-MM-dd+HH:mm:ss")
            .withZone(ZoneOffset.UTC)
            .format(reading.timestamp());

        String url = BASE_URL
            + "?ID=" + stationId.get()
            + "&PASSWORD=" + stationKey.get()
            + "&dateutc=" + dateUtc
            + "&tempf=" + celsiusToFahrenheit(reading.temperature())
            + "&humidity=" + reading.humidity()
            + "&baromin=" + hpaToInHg(reading.pressure())
            + "&windspeedmph=" + kmhToMph(reading.windSpeed())
            + "&winddir=" + reading.windDirection()
            + "&rainin=" + mmToInch(reading.rainfall())
            + "&softwaretype=QuarkusWeatherStation"
            + "&action=updateraw";

        try (Client client = ClientBuilder.newClient()) {
            client.target(url).request().get();
        }
    }

    private double celsiusToFahrenheit(double c) { return c * 9.0 / 5.0 + 32.0; }
    private double hpaToInHg(double hpa) { return hpa * 0.02953; }
    private double kmhToMph(double kmh) { return kmh * 0.621371; }
    private double mmToInch(double mm) { return mm * 0.0393701; }
}
```

### OpenWeatherMap

```java
package com.example.weather.api;

import com.example.weather.model.WeatherReading;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.ws.rs.client.Client;
import jakarta.ws.rs.client.ClientBuilder;
import jakarta.ws.rs.client.Entity;
import jakarta.ws.rs.core.MediaType;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import java.util.Optional;

@ApplicationScoped
public class OpenWeatherMapUploader {

    @ConfigProperty(name = "owm.api-key")
    Optional<String> apiKey;

    @ConfigProperty(name = "owm.station-id")
    Optional<String> stationId;

    private static final String BASE_URL = "https://api.openweathermap.org/data/3.0/measurements";

    public void upload(WeatherReading reading) {
        if (apiKey.isEmpty() || stationId.isEmpty()) return;

        String json = """
            [{
              "station_id": "%s",
              "dt": %d,
              "temperature": [{ "average": %.1f }],
              "humidity": [{ "average": %.1f }],
              "pressure": [{ "average": %.1f }],
              "wind": [{ "speed": %.1f, "deg": %.0f }],
              "precipitation": [{ "rain": %.2f }]
            }]
            """.formatted(
                stationId.get(),
                reading.timestamp().getEpochSecond(),
                reading.temperature(),
                reading.humidity(),
                reading.pressure(),
                reading.windSpeed(),
                reading.windDirection(),
                reading.rainfall()
            );

        try (Client client = ClientBuilder.newClient()) {
            client.target(BASE_URL)
                .queryParam("appid", apiKey.get())
                .request(MediaType.APPLICATION_JSON)
                .post(Entity.json(json));
        }
    }
}
```

## 7. Scheduler (Main Loop)

```java
package com.example.weather;

import com.example.weather.api.OpenWeatherMapUploader;
import com.example.weather.api.WundergroundUploader;
import com.example.weather.model.WeatherReading;
import com.example.weather.mqtt.MqttPublisher;
import com.example.weather.sensor.SensorService;
import com.example.weather.storage.InfluxDbWriter;
import io.quarkus.logging.Log;
import io.quarkus.scheduler.Scheduled;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class WeatherScheduler {

    @Inject SensorService sensorService;
    @Inject MqttPublisher mqttPublisher;
    @Inject InfluxDbWriter influxDbWriter;
    @Inject WundergroundUploader wundergroundUploader;
    @Inject OpenWeatherMapUploader openWeatherMapUploader;

    @Scheduled(every = "30s")
    void collectAndPublish() {
        WeatherReading reading = sensorService.read();
        Log.infof("T=%.1f°C H=%.1f%% P=%.1fhPa W=%.1fkm/h R=%.2fmm",
            reading.temperature(), reading.humidity(), reading.pressure(),
            reading.windSpeed(), reading.rainfall());

        mqttPublisher.publish(reading);
        influxDbWriter.write(reading);
        wundergroundUploader.upload(reading);
        openWeatherMapUploader.upload(reading);
    }
}
```

## 8. Configuration

`src/main/resources/application.properties`:

```properties
# MQTT
mp.messaging.outgoing.weather-out.connector=smallrye-mqtt
mp.messaging.outgoing.weather-out.host=localhost
mp.messaging.outgoing.weather-out.port=1883
mp.messaging.outgoing.weather-out.topic=weather/station

# InfluxDB
influxdb.url=http://localhost:8086
influxdb.token=${INFLUXDB_TOKEN}
influxdb.org=home
influxdb.bucket=weather

# Weather Underground (optional)
wunderground.station-id=${WUNDERGROUND_STATION_ID:}
wunderground.station-key=${WUNDERGROUND_STATION_KEY:}

# OpenWeatherMap (optional)
owm.api-key=${OWM_API_KEY:}
owm.station-id=${OWM_STATION_ID:}

# Health check
quarkus.smallrye-health.root-path=/health
```

## 9. Dashboard

Three dashboard options are available. Pick one based on your preferences (see the comparison table in the Architecture section above).

### Option A: Node-RED Dashboard 2.0 (external)

Node-RED subscribes to the MQTT topic published by the Quarkus app and renders the data in a real-time dashboard using Dashboard 2.0 (`@flowfuse/node-red-dashboard`).

**Flow overview:**

```
[MQTT In] → [JSON Parse] → [Function: extract fields] → [Dashboard widgets]
                                    │
                        ┌───────────┼───────────┐
                        ▼           ▼           ▼
                   [Gauge:     [Chart:     [Text:
                    Temp]       History]    Wind/Rain]
```

**Import this flow into Node-RED:**

1. Open the Node-RED editor at `http://raspberrypi:1880`
2. Go to **Menu → Import** and paste the following JSON:

```json
[
    {
        "id": "mqtt-weather-in",
        "type": "mqtt in",
        "topic": "weather/station",
        "broker": "local-mosquitto",
        "datatype": "json",
        "name": "Weather Station MQTT",
        "wires": [["parse-weather"]]
    },
    {
        "id": "parse-weather",
        "type": "function",
        "name": "Extract readings",
        "func": "msg.temperature = msg.payload.temperature;\nmsg.humidity = msg.payload.humidity;\nmsg.pressure = msg.payload.pressure;\nmsg.windSpeed = msg.payload.windSpeed;\nmsg.rainfall = msg.payload.rainfall;\nreturn msg;",
        "wires": [["gauge-temp", "gauge-humidity", "gauge-pressure", "chart-history"]]
    },
    {
        "id": "local-mosquitto",
        "type": "mqtt-broker",
        "name": "Local Mosquitto",
        "broker": "localhost",
        "port": "1883"
    }
]
```

3. Add Dashboard 2.0 widgets from the palette:
   - **Gauge** nodes for temperature, humidity, and pressure (real-time)
   - **Chart** node for time-series history (line chart)
   - **Text** nodes for wind speed, wind direction, and rainfall

4. Configure each gauge/chart to read from the corresponding `msg` property (e.g., `msg.temperature`)
5. Deploy the flow and access the dashboard at `http://raspberrypi:1880/dashboard`

### Option B: Built-in Quarkus Dashboard (IBM Carbon Design System)

A self-contained dashboard served directly by the Quarkus application using IBM Carbon Web Components and Carbon Charts -- enterprise-grade UI with no Node.js runtime required. The Quarkus Web Bundler resolves Carbon npm packages via mvnpm at build time.

See the full development guide: [quarkus-carbon-dashboard.md](quarkus-carbon-dashboard.md)

Access the dashboard at `http://raspberrypi:8080/`.

### Option C: Grafana Dashboard

If you prefer Grafana, InfluxDB data is already available for querying:

```bash
sudo apt-get install grafana
sudo systemctl enable --now grafana-server
```

Access Grafana at `http://raspberrypi:3000`, add InfluxDB as a data source (Flux query language), and build dashboards with the `weather` measurement fields.

## 10. Native Build

Build the native executable on a machine with GraalVM (or use a container build for ARM64):

```bash
# Option A: build natively on the Pi (slow, needs GraalVM + 4GB+ RAM)
./mvnw package -Dnative

# Option B: cross-compile using a container (recommended)
./mvnw package -Dnative -Dquarkus.native.container-build=true \
  -Dquarkus.native.builder-image=quay.io/quarkus/ubi9-quarkiverse-mandrel-builder-image:jdk-21

# The native binary is at:
# target/quarkus-weather-station-1.0-runner
```

For installation on the Pi, see [weather-station.md](weather-station.md#option-b-quarkus-native-application-java).

## 11. Testing

```java
package com.example.weather;

import io.quarkus.test.junit.QuarkusTest;
import jakarta.inject.Inject;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

@QuarkusTest
class WeatherSchedulerTest {

    @Inject WeatherScheduler scheduler;

    @Test
    void schedulerIsInjectable() {
        assertNotNull(scheduler);
    }
}
```

For sensor testing without hardware, create a mock `SensorService` using `@io.quarkus.test.Mock` that returns fixed `WeatherReading` values.
