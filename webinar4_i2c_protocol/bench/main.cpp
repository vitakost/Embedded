#include <Arduino.h>  // required by PlatformIO (.cpp instead of .ino)
#include <Wire.h>

static const uint8_t REAL_SENSOR_ADDR = 0x68;
static const uint8_t FAULT_ADDR       = 0x69; // no device here -> NACK
static const uint8_t TEMP_OUT_H       = 0x41;
static const uint8_t FAULT_PIN        = 27;

uint8_t activeAddress() {
  return digitalRead(FAULT_PIN) ? FAULT_ADDR : REAL_SENSOR_ADDR;
}

void setup() {
  Serial.begin(115200);
  pinMode(FAULT_PIN, INPUT);
  Wire.begin(21, 22);

  Serial.println();
  Serial.println("=== WEBINAR 4: I2C PRACTICE / BUGGY ===");
  Serial.println("Find the defect using trace + firmware behavior.");
  Serial.println("FAULT OFF = normal sensor; FAULT ON = simulated peripheral loss.");
  Serial.println();

  Wire.beginTransmission(REAL_SENSOR_ADDR);
  Wire.write(0x6B);
  Wire.write(0x00);
  Wire.endTransmission();
}

float readTemperatureBuggy() {
  bool sensorReady = false;

  // INTENTIONAL BUG:
  // no retry limit and no timeout policy at application level.
  while (!sensorReady) {
    const uint8_t addr = activeAddress();

    Wire.beginTransmission(addr);
    Wire.write(TEMP_OUT_H);
    uint8_t result = Wire.endTransmission(false);

    if (result == 0) {
      sensorReady = true;
    } else {
      Serial.printf("[WARN] No response from 0x%02X... retry\n", addr);
      delay(100);
    }
  }

  const uint8_t addr = activeAddress();
  Wire.requestFrom(addr, (uint8_t)2, (uint8_t)true);

  // INTENTIONAL BUG #2:
  // wait forever if expected bytes never arrive.
  while (Wire.available() < 2) {
  }

  int16_t raw = ((int16_t)Wire.read() << 8) | Wire.read();
  return (raw / 340.0f) + 36.53f;
}

void loop() {
  float t = readTemperatureBuggy();
  Serial.printf("[DATA] Temperature: %.2f C\n", t);

  // This should keep appearing. During the fault it stops.
  Serial.println("[SYSTEM] Main loop alive");

  delay(1000);
}
