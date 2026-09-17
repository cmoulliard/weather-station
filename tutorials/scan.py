from machine import I2C, Pin
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
print(i2c.scan())  # should print the sensor's address