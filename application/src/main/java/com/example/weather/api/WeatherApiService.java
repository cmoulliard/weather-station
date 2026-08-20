package com.example.weather.api;

import com.example.weather.model.ForecastEntry;
import com.example.weather.model.WeatherReading;
import io.quarkus.logging.Log;
import io.quarkus.runtime.StartupEvent;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;
import jakarta.inject.Inject;
import org.eclipse.microprofile.config.inject.ConfigProperty;
import org.eclipse.microprofile.rest.client.inject.RestClient;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Stream;

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

    @ConfigProperty(name = "weather.api.cities", defaultValue = "Silenrieux,Brussels,Ottignies,Namur,Charleroi,Liege")
    String citiesList;

    private volatile String activeCity;
    private volatile double latitude;
    private volatile double longitude;
    private volatile String stationName;
    private volatile String currentDescription = "";
    private volatile String currentIcon = "01d";

    void onStartup(@Observes StartupEvent ev) {
        activeCity = city;
        if (isApiEnabled()) {
            Log.infof("Weather datasource: API (OpenWeatherMap) — city: %s", activeCity);
        } else {
            Log.infof("Weather datasource: mock (simulated data) — city: %s", activeCity);
        }
    }

    public double getLatitude() { return latitude; }
    public double getLongitude() { return longitude; }
    public String getStationName() { return stationName != null ? stationName : getActiveCity(); }
    public String getCurrentDescription() { return currentDescription; }
    public String getCurrentIcon() { return currentIcon; }

    public String getActiveCity() { return activeCity != null ? activeCity : city; }

    public void setActiveCity(String newCity) {
        this.activeCity = newCity;
        this.stationName = null;
        Log.infof("City changed to: %s", newCity);
    }

    public List<String> getCities() {
        return Stream.of(citiesList.split(","))
            .map(String::trim)
            .filter(s -> !s.isEmpty())
            .toList();
    }

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
                getActiveCity(), apiKey.get(), "metric"
            );

            if (response.coord != null) {
                latitude = response.coord.lat;
                longitude = response.coord.lon;
            }
            if (response.name != null) {
                stationName = response.name;
            }
            if (response.weather != null && !response.weather.isEmpty()) {
                currentDescription = response.weather.get(0).description;
                currentIcon = response.weather.get(0).icon;
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

    public List<ForecastEntry> fetchForecast() {
        if (isApiEnabled()) {
            return fetchForecastFromApi();
        }
        return generateMockForecast();
    }

    private List<ForecastEntry> fetchForecastFromApi() {
        try {
            OpenWeatherMapForecastResponse response = openWeatherMapClient.getForecast(
                getActiveCity(), apiKey.get(), "metric"
            );
            List<ForecastEntry> entries = new ArrayList<>();
            if (response.list != null) {
                for (OpenWeatherMapForecastResponse.ForecastItem item : response.list) {
                    String desc = "";
                    String icon = "01d";
                    if (item.weather != null && !item.weather.isEmpty()) {
                        desc = item.weather.get(0).description;
                        icon = item.weather.get(0).icon;
                    }
                    double rain = 0.0;
                    if (item.rain != null) {
                        rain = item.rain.threeHour;
                    }
                    entries.add(new ForecastEntry(
                        item.main.temp,
                        item.main.humidity,
                        item.main.pressure,
                        item.wind.speed * 3.6,
                        rain,
                        desc,
                        icon,
                        Instant.ofEpochSecond(item.dt)
                    ));
                }
            }
            return entries;
        } catch (Exception e) {
            Log.errorf("Failed to fetch forecast from OpenWeatherMap API: %s. Falling back to mock data.", e.getMessage());
            return generateMockForecast();
        }
    }

    private List<ForecastEntry> generateMockForecast() {
        List<ForecastEntry> entries = new ArrayList<>();
        Instant now = Instant.now();
        String[] conditions = {"clear sky", "few clouds", "scattered clouds", "light rain", "overcast clouds"};
        String[] icons = {"01d", "02d", "03d", "10d", "04d"};
        for (int i = 0; i < 40; i++) {
            Instant ts = now.plusSeconds(i * 3L * 3600);
            double hourOfDay = (System.currentTimeMillis() / 3600000.0 + i * 3) % 24;
            double temp = 18.0 + 7.0 * Math.sin((hourOfDay - 6) * Math.PI / 12.0) + (Math.random() - 0.5) * 2;
            double humidity = 60.0 + 20.0 * Math.cos(hourOfDay * Math.PI / 12.0) + (Math.random() - 0.5) * 5;
            double pressure = 1013.0 + 3.0 * Math.sin(i * 0.2);
            double windSpeed = 6.0 + 4.0 * Math.sin(i * 0.3) + Math.random() * 2;
            double rain = Math.max(0, 1.5 * Math.sin(i * 0.4) + (Math.random() - 0.5));
            int condIdx = i % conditions.length;
            entries.add(new ForecastEntry(
                Math.round(temp * 10.0) / 10.0,
                Math.round(humidity * 10.0) / 10.0,
                Math.round(pressure * 10.0) / 10.0,
                Math.round(windSpeed * 10.0) / 10.0,
                Math.round(rain * 10.0) / 10.0,
                conditions[condIdx],
                icons[condIdx],
                ts
            ));
        }
        return entries;
    }

    private WeatherReading generateMockReading() {
        String[] mockDescs = {"clear sky", "few clouds", "scattered clouds", "light rain", "overcast clouds"};
        String[] mockIcons = {"01d", "02d", "03d", "10d", "04d"};
        int idx = (int) ((System.currentTimeMillis() / 60000) % mockDescs.length);
        currentDescription = mockDescs[idx];
        currentIcon = mockIcons[idx];

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
