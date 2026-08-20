package com.example.weather.dashboard;

import com.example.weather.api.WeatherApiService;
import com.example.weather.model.ForecastEntry;
import com.example.weather.model.WeatherReading;
import com.example.weather.scheduler.WeatherScheduler;
import com.example.weather.storage.InfluxDbService;
import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.PUT;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.QueryParam;
import jakarta.ws.rs.core.MediaType;

import java.util.List;
import java.util.Map;

@Path("/api/weather")
public class DashboardResource {

    @Inject
    WeatherScheduler weatherScheduler;

    @Inject
    InfluxDbService influxDbService;

    @Inject
    WeatherApiService weatherApiService;

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public WeatherReading current() {
        if (influxDbService.isConnected()) {
            WeatherReading fromDb = influxDbService.getLatest();
            if (fromDb != null) return fromDb;
        }
        return weatherScheduler.getLatestReading();
    }

    @GET
    @Path("/history")
    @Produces(MediaType.APPLICATION_JSON)
    public List<WeatherReading> history(@QueryParam("range") String range) {
        return influxDbService.getHistory(range != null ? range : "-1h");
    }

    @GET
    @Path("/status")
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, Object> status() {
        return Map.of(
            "influxdb", influxDbService.isConnected(),
            "hasData", weatherScheduler.getLatestReading() != null
        );
    }

    @GET
    @Path("/forecast")
    @Produces(MediaType.APPLICATION_JSON)
    public List<ForecastEntry> forecast() {
        return weatherApiService.fetchForecast();
    }

    @GET
    @Path("/location")
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, Object> location() {
        return Map.of(
            "name", weatherApiService.getStationName(),
            "latitude", weatherApiService.getLatitude(),
            "longitude", weatherApiService.getLongitude(),
            "description", weatherApiService.getCurrentDescription(),
            "icon", weatherApiService.getCurrentIcon()
        );
    }

    @GET
    @Path("/cities")
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, Object> cities() {
        return Map.of(
            "cities", weatherApiService.getCities(),
            "active", weatherApiService.getActiveCity()
        );
    }

    @PUT
    @Path("/city")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, Object> changeCity(Map<String, String> body) {
        String newCity = body.get("city");
        if (newCity != null && !newCity.isBlank()) {
            weatherApiService.setActiveCity(newCity.trim());
            weatherScheduler.collectNow();
        }
        return Map.of("active", weatherApiService.getActiveCity());
    }
}
