//#include <SPI.h>
//#include <Ethernet.h>
//#include <EEPROM.h>

byte mac[6] = { 0xBA, 0xBE, 0x00, 0x00, 0x00, 0x00 };

void setup() {
	Serial.begin(9600);
	// Random MAC address stored in EEPROM
	if (EEPROM.read(1) == '#') {
		for (int i = 2; i < 6; i++) {
			mac[i] = EEPROM.read(i);
		}
	} else {
		randomSeed(analogRead(0));
		for (int i = 2; i < 6; i++) {
			mac[i] = random(0, 255);
			EEPROM.write(i, mac[i]);
		}
		EEPROM.write(1, '#');
	}
}

void loop() {
}
