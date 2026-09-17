import time

counter = 0
print("ESP32-C3 Serial Communication Starting...")

while True:
    print(f"Hello from ESP32-C3 Mini! Count: {counter}")
    counter += 1
    time.sleep(2)