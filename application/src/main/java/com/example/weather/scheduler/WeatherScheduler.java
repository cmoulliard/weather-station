package com.example.weather.scheduler;

import com.example.weather.api.WeatherApiService;
import com.example.weather.model.WeatherReading;
import com.example.weather.storage.InfluxDbService;
import io.quarkus.logging.Log;
import io.quarkus.scheduler.Scheduled;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.util.concurrent.atomic.AtomicReference;

@ApplicationScoped
public class WeatherScheduler {

    @Inject
    WeatherApiService weatherApiService;

    @Inject
    InfluxDbService influxDbService;

    private final AtomicReference<WeatherReading> latestReading = new AtomicReference<>();

    public void collectNow() {
        collectAndStore();
    }

    @Scheduled(every = "${weather.collect.interval:30s}")
    void collectAndStore() {
        WeatherReading reading = weatherApiService.fetchReading();
        latestReading.set(reading);

        Log.infof("T=%.1f°C H=%.1f%% P=%.1fhPa W=%.1fkm/h R=%.2fmm [source=%s]",
            reading.temperature(), reading.humidity(), reading.pressure(),
            reading.windSpeed(), reading.rainfall(),
            weatherApiService.isApiEnabled() ? "api" : "mock");

        influxDbService.write(reading);
    }

    public WeatherReading getLatestReading() {
        return latestReading.get();
    }
}
