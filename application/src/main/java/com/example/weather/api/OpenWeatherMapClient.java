package com.example.weather.api;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.QueryParam;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

@RegisterRestClient(configKey = "openweathermap")
public interface OpenWeatherMapClient {

    @GET
    OpenWeatherMapResponse getWeather(
        @QueryParam("q") String city,
        @QueryParam("appid") String apiKey,
        @QueryParam("units") String units
    );
}
