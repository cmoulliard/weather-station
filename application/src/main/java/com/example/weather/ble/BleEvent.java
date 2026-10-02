package com.example.weather.ble;

import java.time.Instant;

public record BleEvent(
    String type,
    BleState state,
    String address,
    String value,
    Instant timestamp,
    Boolean ledState
) {
    static BleEvent status(BleState state, String address) {
        return new BleEvent("status", state, address, null, Instant.now(), null);
    }

    static BleEvent sensor(BleReading reading) {
        return new BleEvent("sensor", null, reading.deviceAddress(),
            reading.value(), reading.timestamp(), null);
    }

    static BleEvent led(boolean on) {
        return new BleEvent("led", null, null, null, Instant.now(), on);
    }
}
