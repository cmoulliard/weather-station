package com.example.weather.ble;

import jakarta.inject.Inject;
import jakarta.ws.rs.Consumes;
import jakarta.ws.rs.GET;
import jakarta.ws.rs.PUT;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;

import java.util.List;
import java.util.Map;

@Path("/api/ble")
public class BleResource {

    @Inject
    BleService bleService;

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, Object> status() {
        BleReading latest = bleService.getLatestReading();
        return Map.of(
            "state", bleService.getState().name().toLowerCase(),
            "address", bleService.getConnectedAddress() != null ? bleService.getConnectedAddress() : "",
            "ledState", bleService.getLedState(),
            "latestValue", latest != null ? latest.value() : "",
            "latestTimestamp", latest != null ? latest.timestamp().toString() : ""
        );
    }

    @GET
    @Path("/history")
    @Produces(MediaType.APPLICATION_JSON)
    public List<BleReading> history() {
        return bleService.getHistory();
    }

    @PUT
    @Path("/led")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Map<String, Object> led(Map<String, Object> body) {
        Object stateObj = body.get("state");
        boolean on;
        if (stateObj instanceof Boolean b) {
            on = b;
        } else if (stateObj instanceof Number n) {
            on = n.intValue() != 0;
        } else {
            on = "true".equalsIgnoreCase(String.valueOf(stateObj)) || "1".equals(String.valueOf(stateObj));
        }
        boolean success = bleService.writeLed(on);
        return Map.of("success", success, "ledState", bleService.getLedState());
    }
}
