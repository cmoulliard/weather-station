package com.example.weather.ble;

import com.welie.blessed.BluetoothCentralManager;
import com.welie.blessed.BluetoothCentralManagerCallback;
import com.welie.blessed.BluetoothCommandStatus;
import com.welie.blessed.BluetoothGattCharacteristic;
import com.welie.blessed.BluetoothGattService;
import com.welie.blessed.BluetoothPeripheral;
import com.welie.blessed.BluetoothPeripheralCallback;
import com.welie.blessed.ScanResult;
import io.quarkus.logging.Log;
import io.quarkus.runtime.Startup;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import jakarta.enterprise.context.ApplicationScoped;
import org.eclipse.microprofile.config.inject.ConfigProperty;

import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Consumer;

@ApplicationScoped
@Startup
public class BleService {

    @ConfigProperty(name = "ble.enabled", defaultValue = "false")
    boolean enabled;

    @ConfigProperty(name = "ble.device.name", defaultValue = "ESP32")
    String deviceName;

    @ConfigProperty(name = "ble.service.uuid", defaultValue = "19b10000-e8f2-537e-4f6c-d104768a1214")
    String serviceUuidStr;

    @ConfigProperty(name = "ble.sensor.char.uuid", defaultValue = "19b10001-e8f2-537e-4f6c-d104768a1214")
    String sensorCharUuidStr;

    @ConfigProperty(name = "ble.led.char.uuid", defaultValue = "19b10002-e8f2-537e-4f6c-d104768a1214")
    String ledCharUuidStr;

    @ConfigProperty(name = "ble.reconnect.delay.seconds", defaultValue = "5")
    int reconnectDelay;

    private UUID serviceUuid;
    private UUID sensorCharUuid;
    private UUID ledCharUuid;

    private BluetoothCentralManager centralManager;
    private BluetoothPeripheral connectedPeripheral;
    private ScheduledExecutorService scheduler;

    private final AtomicReference<BleState> state = new AtomicReference<>(BleState.DISABLED);
    private final AtomicReference<BleReading> latestReading = new AtomicReference<>();
    private final CopyOnWriteArrayList<BleReading> history = new CopyOnWriteArrayList<>();
    private final List<Consumer<BleEvent>> listeners = new CopyOnWriteArrayList<>();

    private volatile String connectedAddress;
    private volatile boolean ledState;

    @PostConstruct
    void init() {
        if (!enabled) {
            Log.info("BLE is disabled (set ble.enabled=true on a Linux host with BlueZ)");
            return;
        }

        serviceUuid = UUID.fromString(serviceUuidStr);
        sensorCharUuid = UUID.fromString(sensorCharUuidStr);
        ledCharUuid = UUID.fromString(ledCharUuidStr);

        scheduler = Executors.newSingleThreadScheduledExecutor(r -> {
            Thread t = new Thread(r, "ble-reconnect");
            t.setDaemon(true);
            return t;
        });

        try {
            centralManager = new BluetoothCentralManager(centralCallback);
            Log.info("BLE central manager initialized");
            startScan();
        } catch (Exception e) {
            Log.errorf("Failed to initialize BLE: %s (is BlueZ available?)", e.getMessage());
            setState(BleState.ERROR);
        }
    }

    private void startScan() {
        setState(BleState.SCANNING);
        Log.infof("BLE scanning for device '%s' ...", deviceName);
        centralManager.scanForPeripheralsWithNames(new String[]{deviceName});
    }

    private void scheduleReconnect() {
        if (scheduler != null && !scheduler.isShutdown()) {
            scheduler.schedule(this::startScan, reconnectDelay, TimeUnit.SECONDS);
        }
    }

    // --- Central callbacks ---

    private final BluetoothCentralManagerCallback centralCallback = new BluetoothCentralManagerCallback() {

        @Override
        public void onDiscoveredPeripheral(BluetoothPeripheral peripheral, ScanResult scanResult) {
            Log.infof("BLE discovered %s (%s)", peripheral.getName(), peripheral.getAddress());
            centralManager.stopScan();
            setState(BleState.CONNECTING);
            centralManager.connectPeripheral(peripheral, peripheralCallback);
        }

        @Override
        public void onConnectedPeripheral(BluetoothPeripheral peripheral) {
            connectedPeripheral = peripheral;
            connectedAddress = peripheral.getAddress();
            setState(BleState.CONNECTED);
            Log.infof("BLE connected to %s (%s)", peripheral.getName(), peripheral.getAddress());
        }

        @Override
        public void onConnectionFailed(BluetoothPeripheral peripheral, BluetoothCommandStatus status) {
            Log.errorf("BLE connection failed to %s: %s", peripheral.getName(), status);
            connectedPeripheral = null;
            setState(BleState.DISCONNECTED);
            scheduleReconnect();
        }

        @Override
        public void onDisconnectedPeripheral(BluetoothPeripheral peripheral, BluetoothCommandStatus status) {
            Log.infof("BLE disconnected from %s: %s", peripheral.getName(), status);
            connectedPeripheral = null;
            setState(BleState.DISCONNECTED);
            scheduleReconnect();
        }
    };

    // --- Peripheral callbacks ---

    private final BluetoothPeripheralCallback peripheralCallback = new BluetoothPeripheralCallback() {

        @Override
        public void onServicesDiscovered(BluetoothPeripheral peripheral,
                                         List<BluetoothGattService> services) {
            BluetoothGattCharacteristic sensorChar =
                peripheral.getCharacteristic(serviceUuid, sensorCharUuid);
            if (sensorChar != null) {
                peripheral.setNotify(sensorChar, true);
                peripheral.readCharacteristic(sensorChar);
                Log.info("BLE subscribed to sensor characteristic notifications");
            } else {
                Log.errorf("BLE sensor characteristic %s not found on device", sensorCharUuidStr);
            }
        }

        @Override
        public void onCharacteristicUpdate(BluetoothPeripheral peripheral, byte[] value,
                                           BluetoothGattCharacteristic characteristic,
                                           BluetoothCommandStatus status) {
            if (status != BluetoothCommandStatus.COMMAND_SUCCESS) return;

            String decoded = new String(value, StandardCharsets.UTF_8);
            BleReading reading = new BleReading(
                decoded, peripheral.getName(), peripheral.getAddress(), Instant.now()
            );
            latestReading.set(reading);
            history.add(reading);
            while (history.size() > 500) {
                history.remove(0);
            }
            fireEvent(BleEvent.sensor(reading));
            Log.debugf("BLE sensor: %s", decoded);
        }

        @Override
        public void onNotificationStateUpdate(BluetoothPeripheral peripheral,
                                              BluetoothGattCharacteristic characteristic,
                                              BluetoothCommandStatus status) {
            Log.debugf("BLE notification state updated for %s: %s",
                characteristic.getUuid(), status);
        }
    };

    // --- Public API ---

    public BleState getState() {
        return state.get();
    }

    public BleReading getLatestReading() {
        return latestReading.get();
    }

    public List<BleReading> getHistory() {
        return List.copyOf(history);
    }

    public String getConnectedAddress() {
        return connectedAddress;
    }

    public boolean getLedState() {
        return ledState;
    }

    public boolean writeLed(boolean on) {
        if (connectedPeripheral == null || state.get() != BleState.CONNECTED) {
            return false;
        }
        BluetoothGattCharacteristic ledChar =
            connectedPeripheral.getCharacteristic(serviceUuid, ledCharUuid);
        if (ledChar == null) return false;

        byte[] data = new byte[]{(byte) (on ? 1 : 0)};
        connectedPeripheral.writeCharacteristic(ledChar, data, BluetoothGattCharacteristic.WriteType.WITH_RESPONSE);
        ledState = on;
        fireEvent(BleEvent.led(on));
        return true;
    }

    public void addListener(Consumer<BleEvent> listener) {
        listeners.add(listener);
    }

    public void removeListener(Consumer<BleEvent> listener) {
        listeners.remove(listener);
    }

    // --- Internal ---

    private void setState(BleState newState) {
        state.set(newState);
        fireEvent(BleEvent.status(newState, connectedAddress));
    }

    private void fireEvent(BleEvent event) {
        for (Consumer<BleEvent> listener : listeners) {
            try {
                listener.accept(event);
            } catch (Exception e) {
                Log.debugf("BLE listener error: %s", e.getMessage());
            }
        }
    }

    @PreDestroy
    void shutdown() {
        if (scheduler != null) {
            scheduler.shutdownNow();
        }
        if (connectedPeripheral != null && centralManager != null) {
            centralManager.cancelConnection(connectedPeripheral);
        }
        if (centralManager != null) {
            centralManager.shutdown();
        }
        Log.info("BLE service shut down");
    }
}
