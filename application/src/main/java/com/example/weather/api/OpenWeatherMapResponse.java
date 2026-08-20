package com.example.weather.api;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class OpenWeatherMapResponse {

    public Coord coord;
    public Main main;
    public Wind wind;
    public List<Weather> weather;
    public Rain rain;
    public String name;
    public long dt;

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Coord {
        public double lat;
        public double lon;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Main {
        public double temp;
        public double humidity;
        public double pressure;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Wind {
        public double speed;
        public double deg;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Weather {
        public String main;
        public String description;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Rain {
        public double _1h;
    }
}
