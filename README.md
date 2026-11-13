# Embedded QA — портфоліо

**Фінальний кейс:** [Smart Boiler Safety Controller](final_case_study_boiler_controller/) — Master Test Plan, Test Matrix, evidence і рішення про реліз для IoT-контролера котла на ESP32.

## Домашні завдання

| Папка | Тема |
|---|---|
| [webinar1_smart_gate](webinar1_smart_gate/) | Smart Gate Controller (Arduino Uno, Wokwi): функціональне black-box тестування станів, реле, кінцевиків і таймаутів |
| [webinar2_button_debounce](webinar2_button_debounce/) | Кнопка з перериваннями на ESP32 (Wokwi): дребезг, шум, debounce; Serial Logger, Logic Analyzer, сценарії Wokwi CLI |
| [webinar3_uart_cli](webinar3_uart_cli/) | UART CLI на ESP32 (Wokwi): межі значень, довжина рядка, регістр, невалідний ввід, послідовності станів |
| [webinar4_i2c_protocol](webinar4_i2c_protocol/) | I2C-датчик MPU6050 на ESP32 (Wokwi): Logic Analyzer + PulseView, ACK/NACK, fault injection FAULT ON/OFF, 5 повторних прогонів |
| [webinar5_recovery_fault_injection](webinar5_recovery_fault_injection/) | Recovery / fault injection на ESP32 (Wokwi): watchdog, deep sleep, power loss, цілісність NVS, стан реле після аварійного reset |
| [webinar6_pytest_automation](webinar6_pytest_automation/) | Python/pytest автотести для ESP32 JSON CLI (Wokwi + RFC2217): власні тести, класифікація FAIL, evidence |
| [webinar7_iot_network_testing](webinar7_iot_network_testing/) | IoT-нода ESP32 у нестабільній мережі (Wokwi): втрата зв'язку, reconnect/backoff, offline buffer, duplicates, stress і стабільність пам'яті |
| [final_case_study_boiler_controller](final_case_study_boiler_controller/) | Фінальний проєкт: Master Test Plan, Test Matrix, Evidence Package, Case Study, Release Decision |
