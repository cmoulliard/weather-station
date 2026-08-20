package com.example.weather.model;

import java.time.Instant;

public record ForecastEntry(
    double temperature,
    double humidity,
    double pressure,
    double windSpeed,
    double rainfall,
    String description,
    String icon,
    Instant timestamp
) {}
