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
