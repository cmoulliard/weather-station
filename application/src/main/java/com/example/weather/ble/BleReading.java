package com.example.weather.ble;

import java.time.Instant;

public record BleReading(
    String value,
    String deviceName,
    String deviceAddress,
    Instant timestamp
) {}
