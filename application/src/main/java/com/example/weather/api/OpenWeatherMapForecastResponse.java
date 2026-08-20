package com.example.weather.api;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public class OpenWeatherMapForecastResponse {

    public List<ForecastItem> list;

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ForecastItem {
        public long dt;
        public Main main;
        public Wind wind;
        public List<Weather> weather;
        public Rain rain;
        public double pop;
        @JsonProperty("dt_txt")
        public String dtTxt;
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
        public String icon;
    }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Rain {
        @JsonProperty("3h")
        public double threeHour;
    }
}
