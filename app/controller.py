import RPi.GPIO as GPIO
from time import sleep
import distance_sensor
from servo_motor import ServoMotor
from mfrc522 import SimpleMFRC522

class H_Bridge_Motor:
    def __init__(self, Ena=35, In1=33, In2=31, In3=36, In4=29, Enb=32):
        self.Ena = Ena
        self.In1 = In1
        self.In2 = In2
        self.In3 = In3
        self.In4 = In4
        self.Enb = Enb
        GPIO.setup(self.Ena, GPIO.OUT)
        GPIO.setup(self.In1, GPIO.OUT)
        GPIO.setup(self.In2, GPIO.OUT)
        self.pwm1 = GPIO.PWM(self.Ena, 100)
        GPIO.setup(self.In3, GPIO.OUT)
        GPIO.setup(self.In4, GPIO.OUT)
        GPIO.setup(self.Enb, GPIO.OUT)
        self.pwm2 = GPIO.PWM(self.Enb, 100)
        self.pwm1.start(0)
        self.pwm2.start(0)

    def move_forward(self, x=50, t=0):
        GPIO.output(self.In1, GPIO.LOW)
        GPIO.output(self.In2, GPIO.HIGH)
        GPIO.output(self.In3, GPIO.LOW)
        GPIO.output(self.In4, GPIO.HIGH)
        self.pwm1.ChangeDutyCycle(x)
        self.pwm2.ChangeDutyCycle(x)
        sleep(t)

    def move_backward(self, x=50, t=0):
        GPIO.output(self.In1, GPIO.HIGH)
        GPIO.output(self.In2, GPIO.LOW)
        GPIO.output(self.In3, GPIO.HIGH)
        GPIO.output(self.In4, GPIO.LOW)
        self.pwm1.ChangeDutyCycle(x)
        self.pwm2.ChangeDutyCycle(x)
        sleep(t)

    def stop(self, t=0):
        self.pwm1.ChangeDutyCycle(0)
        self.pwm2.ChangeDutyCycle(0)
        self.pwm1.stop()
        self.pwm2.stop()
        sleep(t)

    def move_right(self, x=100, y=50, t=0):
        GPIO.output(self.In1, GPIO.LOW)
        GPIO.output(self.In2, GPIO.HIGH)
        GPIO.output(self.In3, GPIO.LOW)
        GPIO.output(self.In4, GPIO.HIGH)
        self.pwm1.ChangeDutyCycle(y)
        self.pwm2.ChangeDutyCycle(x)
        sleep(t)

    def move_left(self, x=100, y=50, t=0):
        GPIO.output(self.In1, GPIO.LOW)
        GPIO.output(self.In2, GPIO.HIGH)
        GPIO.output(self.In3, GPIO.LOW)
        GPIO.output(self.In4, GPIO.HIGH)
        self.pwm1.ChangeDutyCycle(x)
        self.pwm2.ChangeDutyCycle(y)
        sleep(t)


class RFID_Sensor:
    def __inti__(self):
        pass

    def get_rfid(self):
        for i in range(1, 100):
            try:
                reader = SimpleMFRC522()
                id, text = reader.read()
                return id
            except Exception as exp:
                print(str(exp))
                continue

    def set_rfid(self, text):
        try:
            reader = SimpleMFRC522()
            reader.write(text)
        except Exception as exp:
            print(str(exp))




#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)
#motor1 = H_Bridge_Motor()
#count = 1
#while count < 5:
#print('Foward')
#motor1.move_forward(100, 10)
#print('Backward')
#motor1.move_backward(50, 10)
#print('Right')
#motor1.move_right(100, 50, 10)
#print('Left')
#motor1.move_left(100, 50, 10)
#print('Stop')
#motor1.stop()
#GPIO.cleanup()
    #count += 1
class Controller:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        self.servo = ServoMotor()
        sleep(2)
        

    def can_go_left(self):
        print('Checking Left')
        self.servo.move_left()
        sleep(2)
        distance = distance_sensor.get_distance()
        print('Distance on left: '+ str(distance))
        can_go = distance_sensor.is_path_clear(distance)
        self.servo.move_back()
        sleep(2)
        return can_go

    def can_go_right(self):
        print('Checking Right')
        self.servo.move_right()
        sleep(2)
        distance = distance_sensor.get_distance()
        print('Distance on right: '+ str(distance))
        can_go = distance_sensor.is_path_clear(distance)
        self.servo.move_back()
        sleep(2)
        return can_go

    def controlling(self):
        while True:
            distance = distance_sensor.get_distance()
            can_go = distance_sensor.is_path_clear(distance)
            if can_go:
                print('Go')
            else:
                print('Stop')
                if self.can_go_right():
                    print('Go Right')
                elif self.can_go_left():
                    print('Go Left')
                else:
                    print('Dead end')
                    self.servo.clean_servo()
                    break


#Controller().controlling()
#while True:
 #   rfid_reader = RFID_Sensor()
 #   print(rfid_reader.get_rfid())
