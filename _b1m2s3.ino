#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// LCD address
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Pins
#define VOLTAGE_PIN A0
#define RELAY_PIN 7

// Voltage divider factor (0–25V module)
float voltageFactor = 5.0;

// Safety limits (Li-ion)
float overVoltage = 4.20;
float underVoltage = 3.00;

void setup()
{
  pinMode(RELAY_PIN, OUTPUT);

  // Relay OFF initially (safety)
  digitalWrite(RELAY_PIN, HIGH);   // Active LOW relay

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("BMS System");
  lcd.setCursor(0, 1);
  lcd.print("Initializing");
  delay(2000);
  lcd.clear();
}

void loop()
{
  int sensorValue = analogRead(VOLTAGE_PIN);

  // Convert ADC value to voltage
  float batteryVoltage = (sensorValue * 5.0 / 1023.0) * voltageFactor;

  // Display voltage
  lcd.setCursor(0, 0);
  lcd.print("Voltage: ");
  lcd.print(batteryVoltage, 2);
  lcd.print(" V ");

  lcd.setCursor(0, 1);

  // Protection logic
  if (batteryVoltage > overVoltage)
  {
    lcd.print("OVER VOLTAGE ");
    digitalWrite(RELAY_PIN, HIGH);   // Relay OFF
  }
  else if (batteryVoltage < underVoltage)
  {
    lcd.print("UNDER VOLTAGE");
    digitalWrite(RELAY_PIN, HIGH);   // Relay OFF
  }
  else
  {
    lcd.print("STATUS: SAFE ");
    digitalWrite(RELAY_PIN, LOW);    // Relay ON
  }

  delay(1000);
}
