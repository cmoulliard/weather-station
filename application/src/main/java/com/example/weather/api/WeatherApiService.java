package com.example.weather.api;

import com.example.weather.model.WeatherReading;
import io.quarkus.logging.Log;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.eclipse.microprofile.rest.client.inject.RestClient;

import java.time.Instant;
import java.util.Optional;

@ApplicationScoped
public class WeatherApiService {

    @RestClient
    OpenWeatherMapClient openWeatherMapClient;

    @ConfigProperty(name = "weather.api.key")
    Optional<String> apiKey;

    @ConfigProperty(name = "weather.api.city", defaultValue = "Brussels")
    String city;

    @ConfigProperty(name = "weather.datasource", defaultValue = "mock")
    String datasource;

    private volatile double latitude;
    private volatile double longitude;
    private volatile String stationName;

    public double getLatitude() { return latitude; }
    public double getLongitude() { return longitude; }
    public String getStationName() { return stationName != null ? stationName : city; }

    public boolean isApiEnabled() {
        return "api".equalsIgnoreCase(datasource) && apiKey.isPresent() && !apiKey.get().isBlank();
    }

    public WeatherReading fetchReading() {
        if (isApiEnabled()) {
            return fetchFromApi();
        }
        return generateMockReading();
    }

    private WeatherReading fetchFromApi() {
        try {
            OpenWeatherMapResponse response = openWeatherMapClient.getWeather(
                city, apiKey.get(), "metric"
            );

            if (response.coord != null) {
                latitude = response.coord.lat;
                longitude = response.coord.lon;
            }
            if (response.name != null) {
                stationName = response.name;
            }

            double rainfall = 0.0;
            if (response.rain != null) {
                rainfall = response.rain._1h;
            }

            return new WeatherReading(
                response.main.temp,
                response.main.humidity,
                response.main.pressure,
                response.wind.speed * 3.6,
                response.wind.deg,
                rainfall,
                Instant.ofEpochSecond(response.dt)
            );
        } catch (Exception e) {
            Log.errorf("Failed to fetch from OpenWeatherMap API: %s. Falling back to mock data.", e.getMessage());
            return generateMockReading();
        }
    }

    private WeatherReading generateMockReading() {
        double baseTemp = 20.0 + 5.0 * Math.sin(System.currentTimeMillis() / 60000.0);
        double baseHumidity = 55.0 + 15.0 * Math.cos(System.currentTimeMillis() / 90000.0);
        double basePressure = 1013.0 + 5.0 * Math.sin(System.currentTimeMillis() / 120000.0);
        double windSpeed = 8.0 + 4.0 * Math.sin(System.currentTimeMillis() / 45000.0);
        double windDir = (System.currentTimeMillis() / 1000 % 360);
        double rainfall = Math.max(0, 0.5 * Math.sin(System.currentTimeMillis() / 300000.0));

        return new WeatherReading(
            Math.round(baseTemp * 10.0) / 10.0,
            Math.round(baseHumidity * 10.0) / 10.0,
            Math.round(basePressure * 10.0) / 10.0,
            Math.round(windSpeed * 10.0) / 10.0,
            Math.round(windDir * 10.0) / 10.0,
            Math.round(rainfall * 100.0) / 100.0,
            Instant.now()
        );
    }
}
