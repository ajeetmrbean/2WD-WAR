import RPi.GPIO as GPIO                 ## Import GPIO Library.
from time import sleep                            ## Import ‘time’ library for a delay.
 
class ServoMotor():
    def __init__(self):
        #GPIO.setmode(GPIO.BOARD) 
        GPIO.setup(37, GPIO.OUT)                ## set output.
        self.pwm = GPIO.PWM(37,50)                    ## PWM Frequency
        self.pwm.start(7)
        pass

    def move_left(self):
        sleep(2)
        self.pwm.ChangeDutyCycle(11)
        

    def move_right(self):
        sleep(2)
        self.pwm.ChangeDutyCycle(2)

    def move_back(self):
        sleep(2)
        self.pwm.ChangeDutyCycle(7)

    def clean_servo(self):
        self.pwm.stop()
        GPIO.cleanup()

