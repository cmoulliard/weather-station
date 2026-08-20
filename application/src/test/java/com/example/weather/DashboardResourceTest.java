package com.example.weather;

import io.quarkus.test.junit.QuarkusTest;
import org.junit.jupiter.api.Test;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.*;

@QuarkusTest
class DashboardResourceTest {

    @Test
    void currentWeatherEndpointReturnsData() {
        given()
            .when().get("/api/weather")
            .then()
            .statusCode(anyOf(is(200), is(204)));
    }

    @Test
    void historyEndpointReturns200() {
        given()
            .when().get("/api/weather/history?range=-1h")
            .then()
            .statusCode(200);
    }

    @Test
    void statusEndpointReturnsJson() {
        given()
            .when().get("/api/weather/status")
            .then()
            .statusCode(200)
            .body("$", hasKey("influxdb"))
            .body("$", hasKey("hasData"));
    }

    @Test
    void healthEndpoint() {
        given()
            .when().get("/health")
            .then()
            .statusCode(200);
    }
}
