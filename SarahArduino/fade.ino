float ledCurrent[3];
float ledTarget[3];
float ledFade[3];
unsigned long ledFadeTime;
unsigned long deltaMillis;
unsigned long lastMillis;

const int pins[3] = {9,10,11};

void setup() {
	ledFadeTime = 5000;
	lastMillis = millis();
	
	float ledCurrent[3] = {0.0,0.0,0.0};
	float ledTarget[3] = {0.0,0.0,0.0};
	float ledFade[3] = {0.0,0.0,0.0};
	
	for (int i = 0; i < 3; i++) {
		pinMode(pins[i], OUTPUT);
	}
	
	setLedColors(255,127,0);
}

void loop() {
	deltaMillis = millis() - lastMillis;
	for (int passes = 0; passes < deltaMillis; passes++) {
		for (int i = 0; i < 3; i++) {
			if (ledFade[i] > 0) {
				ledCurrent[i] = min(ledCurrent[i] + ledFade[i], ledTarget[i]);
			} else if (ledFade[i] < 0) {
				ledCurrent[i] = max(ledCurrent[i] + ledFade[i], ledTarget[i]);
			}
			if (ledCurrent[i] == ledTarget[i]) {
				ledFade[i] = 0.0;
			}
		}
	}
	lastMillis = millis();
	
	delay(10);
}

void setLedColors(int r,int g,int b) {
	float ledTarget[3] = {r,g,b};
	for (int i = 0; i < 3; i++) {
		ledFade[i] = (ledTarget[i]-ledCurrent[i])/ledFadeTime;
	}
}
