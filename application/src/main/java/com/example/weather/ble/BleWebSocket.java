package com.example.weather.ble;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.quarkus.logging.Log;
import io.quarkus.websockets.next.OnClose;
import io.quarkus.websockets.next.OnOpen;
import io.quarkus.websockets.next.OnTextMessage;
import io.quarkus.websockets.next.WebSocket;
import io.quarkus.websockets.next.WebSocketConnection;
import jakarta.inject.Inject;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;

@WebSocket(path = "/ws/ble")
public class BleWebSocket {

    @Inject
    BleService bleService;

    private final ObjectMapper mapper = new ObjectMapper();
    private final Set<WebSocketConnection> connections = ConcurrentHashMap.newKeySet();
    private final Map<WebSocketConnection, Consumer<BleEvent>> listenerMap = new ConcurrentHashMap<>();

    @OnOpen
    void onOpen(WebSocketConnection connection) {
        connections.add(connection);

        sendJson(connection, Map.of(
            "type", "status",
            "state", bleService.getState().name().toLowerCase(),
            "address", bleService.getConnectedAddress() != null ? bleService.getConnectedAddress() : ""
        ));

        List<BleReading> history = bleService.getHistory();
        int start = Math.max(0, history.size() - 100);
        for (int i = start; i < history.size(); i++) {
            BleReading r = history.get(i);
            sendJson(connection, Map.of(
                "type", "sensor",
                "value", r.value(),
                "ts", r.timestamp().toEpochMilli() / 1000.0
            ));
        }

        Consumer<BleEvent> listener = event -> {
            switch (event.type()) {
                case "sensor" -> sendJson(connection, Map.of(
                    "type", "sensor",
                    "value", event.value() != null ? event.value() : "",
                    "ts", event.timestamp().toEpochMilli() / 1000.0
                ));
                case "status" -> sendJson(connection, Map.of(
                    "type", "status",
                    "state", event.state() != null ? event.state().name().toLowerCase() : "",
                    "address", event.address() != null ? event.address() : ""
                ));
                case "led" -> sendJson(connection, Map.of(
                    "type", "led",
                    "state", Boolean.TRUE.equals(event.ledState()) ? 1 : 0
                ));
            }
        };

        listenerMap.put(connection, listener);
        bleService.addListener(listener);
    }

    @OnTextMessage
    void onMessage(WebSocketConnection connection, String message) {
        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> msg = mapper.readValue(message, Map.class);
            if ("led".equals(msg.get("cmd"))) {
                Object stateObj = msg.get("state");
                boolean on;
                if (stateObj instanceof Number n) {
                    on = n.intValue() != 0;
                } else {
                    on = Boolean.parseBoolean(String.valueOf(stateObj));
                }
                bleService.writeLed(on);
            }
        } catch (Exception e) {
            Log.debugf("BLE WebSocket message parse error: %s", e.getMessage());
        }
    }

    @OnClose
    void onClose(WebSocketConnection connection) {
        connections.remove(connection);
        Consumer<BleEvent> listener = listenerMap.remove(connection);
        if (listener != null) {
            bleService.removeListener(listener);
        }
    }

    private void sendJson(WebSocketConnection connection, Map<String, Object> data) {
        try {
            connection.sendTextAndAwait(mapper.writeValueAsString(data));
        } catch (Exception e) {
            Log.debugf("BLE WebSocket send error: %s", e.getMessage());
        }
    }
}
