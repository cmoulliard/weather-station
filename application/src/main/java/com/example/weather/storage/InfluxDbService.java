package com.example.weather.storage;

import com.example.weather.model.WeatherReading;
import com.influxdb.v3.client.InfluxDBClient;
import com.influxdb.v3.client.Point;
import io.quarkus.logging.Log;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import jakarta.enterprise.context.ApplicationScoped;
import org.eclipse.microprofile.config.inject.ConfigProperty;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;

@ApplicationScoped
public class InfluxDbService {

    @ConfigProperty(name = "influxdb.url", defaultValue = "http://localhost:8181")
    String url;

    @ConfigProperty(name = "influxdb.token")
    Optional<String> token;

    @ConfigProperty(name = "influxdb.database", defaultValue = "weather")
    String database;

    @ConfigProperty(name = "influxdb.enabled", defaultValue = "true")
    boolean enabled;

    private InfluxDBClient client;

    @PostConstruct
    void init() {
        if (enabled && token.isPresent() && !token.get().isBlank()) {
            try {
                client = InfluxDBClient.getInstance(url, token.get().toCharArray(), database);
                Log.infof("InfluxDB v3 client connected to %s (database=%s)", url, database);
            } catch (Exception e) {
                Log.errorf("Failed to connect to InfluxDB: %s", e.getMessage());
            }
        } else {
            Log.info("InfluxDB is disabled or token not configured — data will not be persisted");
        }
    }

    public void write(WeatherReading reading) {
        if (client == null) return;
        try {
            Point point = Point.measurement("weather")
                .setTimestamp(reading.timestamp())
                .setFloatField("temperature", reading.temperature())
                .setFloatField("humidity", reading.humidity())
                .setFloatField("pressure", reading.pressure())
                .setFloatField("wind_speed", reading.windSpeed())
                .setFloatField("wind_direction", reading.windDirection())
                .setFloatField("rainfall", reading.rainfall());
            client.writePoint(point);
        } catch (Exception e) {
            Log.errorf("Failed to write to InfluxDB: %s", e.getMessage());
        }
    }

    public WeatherReading getLatest() {
        if (client == null) return null;
        try (Stream<Object[]> rows = client.query(
                "SELECT time, temperature, humidity, pressure, wind_speed, wind_direction, rainfall "
                + "FROM weather ORDER BY time DESC LIMIT 1")) {
            return rows.findFirst()
                .map(this::toWeatherReading)
                .orElse(null);
        } catch (Exception e) {
            Log.errorf("Failed to query InfluxDB: %s", e.getMessage());
            return null;
        }
    }

    public List<WeatherReading> getHistory(String range) {
        if (client == null) return List.of();
        try {
            String interval = rangeToInterval(range);
            String sql = "SELECT time, temperature, humidity, pressure, wind_speed, wind_direction, rainfall "
                + "FROM weather WHERE time >= now() - interval '" + interval + "' ORDER BY time";

            List<WeatherReading> readings = new ArrayList<>();
            try (Stream<Object[]> rows = client.query(sql)) {
                rows.forEach(row -> readings.add(toWeatherReading(row)));
            }
            return readings;
        } catch (Exception e) {
            Log.errorf("Failed to query InfluxDB history: %s", e.getMessage());
            return List.of();
        }
    }

    public boolean isConnected() {
        return client != null;
    }

    private WeatherReading toWeatherReading(Object[] row) {
        return new WeatherReading(
            toDouble(row[1]),
            toDouble(row[2]),
            toDouble(row[3]),
            toDouble(row[4]),
            toDouble(row[5]),
            toDouble(row[6]),
            toInstant(row[0])
        );
    }

    private double toDouble(Object value) {
        return value instanceof Number n ? n.doubleValue() : 0.0;
    }

    private Instant toInstant(Object value) {
        if (value instanceof Instant i) return i;
        if (value instanceof Number n) return Instant.ofEpochSecond(n.longValue() / 1_000_000_000L);
        return Instant.now();
    }

    private String rangeToInterval(String range) {
        if (range == null) return "1 hour";
        return switch (range) {
            case "-1h" -> "1 hour";
            case "-6h" -> "6 hours";
            case "-24h" -> "24 hours";
            case "-7d" -> "7 days";
            case "-30d" -> "30 days";
            default -> "1 hour";
        };
    }

    @PreDestroy
    void shutdown() {
        if (client != null) {
            try {
                client.close();
            } catch (Exception e) {
                Log.errorf("Failed to close InfluxDB client: %s", e.getMessage());
            }
        }
    }
}
