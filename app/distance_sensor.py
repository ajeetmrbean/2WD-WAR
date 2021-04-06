import RPi.GPIO as GPIO
import time

TRIG = 40
ECHO = 38

class Distance_Sensor:
    def init(self, TRIG=40, ECHO=38):
        self.TRIG = TRIG
        self.ECHO = ECHO
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
    
    def get_distance():
        GPIO.output(TRIG, False)
        time.sleep(0.2)
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)
    
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
    
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        return distance

    def is_path_clear(distance):
        if distance > 30:
            return True
        else:
            return False

#while True:
    #distance = get_distance()
    #print('Can go: '+ str(is_path_clear(distance)) + ' Distance: ' + str(distance) + 'cm')
