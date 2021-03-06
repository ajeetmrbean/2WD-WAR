import os
from flask import Flask, request, render_template, jsonify, Response, redirect
# import firebase_admin
# from firebase_admin import credentials
from firebase import firebase
from datetime import date
import json
from socket import *
import python_jwt as jwt
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import datetime
import sys
try:
    from mfrc522 import SimpleMFRC522
except ModuleNotFoundError:
    pass
try:
    import RPi.GPIO as GPIO
except (RuntimeError, ModuleNotFoundError):
    import fake_rpigpio.utils as GPIO
from time import sleep
import time
from change_grid import edit_grid, display_route
from shortest_path import shortest_route
import functools
import glob
from PIL import ImageGrab

firebase = firebase.FirebaseApplication('https://wheeldrive-7c382.firebaseio.com/', None)
# cred = credentials.Certificate("public/wheeldrive-97d89-firebase-adminsdk-jbjqw-298491d2f2.json")
# firebase_admin.initialize_app(cred)


class Servo_Motor():
    def __init__(self, pin=37, frequency=50):
        self.pin = pin
        self.frequency = frequency
        GPIO.setup(self.pin, GPIO.OUT)                
        self.pwm3 = GPIO.PWM(self.pin, self.frequency)
        self.pwm3.start(7)
        sleep(3)
        pass

    def move_left(self):
        sleep(1)
        self.pwm3.ChangeDutyCycle(11)

    def move_right(self):
        sleep(1)
        self.pwm3.ChangeDutyCycle(2)

    def move_back(self):
        sleep(1)
        self.pwm3.ChangeDutyCycle(7)

    def clean_servo(self):
        self.pwm3.stop()


class Distance_Sensor:
    def __init__(self, TRIG=40, ECHO=38):
        self.TRIG = TRIG
        self.ECHO = ECHO
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)
        pass

    def get_distance(self):
        GPIO.output(self.TRIG, False)
        sleep(0.2)
        GPIO.output(self.TRIG, True)
        sleep(0.00001)
        GPIO.output(self.TRIG, False)

        while GPIO.input(self.ECHO) == 0:
            pulse_start = time.time()

        while GPIO.input(self.ECHO) == 1:
            pulse_end = time.time()
        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        return distance

    def is_path_clear(self, distance):
        if distance > 30:
            return True
        else:
            return False


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
        pass

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


class Controller:
    def __init(self):
        pass

    def move_robot(self, task):
        result = ''
        distance_sensor = Distance_Sensor()
        servo_motor = Servo_Motor()
        servo_motor.move_back()
        h_bridge_motor = H_Bridge_Motor()

        if task == 'up':
            distance = Distance_Sensor().get_distance()
            if (Distance_Sensor().is_path_clear(distance)):
                h_bridge_motor.move_forward(100, 1)
                result = 'done'
            else:
                h_bridge_motor.stop()
                result = 'There is an obstacle'
        elif task == 'down':
            h_bridge_motor.move_backward(50, 1)
            result = 'done'
        elif task == 'right':
            servo_motor.move_right()
            distance = distance_sensor.get_distance()
            sleep(2)
            servo_motor.move_back()
            if (distance_sensor.is_path_clear(distance)):
                h_bridge_motor.move_right(100, 50, 1)
                result = 'done'
            else:
                result = 'There is an obstacle at right'
        elif task == 'left':
            servo_motor.move_left()
            distance = distance_sensor.get_distance()
            sleep(2)
            servo_motor.move_back()
            if (distance_sensor.is_path_clear(distance)):
                h_bridge_motor.move_left(100, 50, 1)
                result = 'done'
            else:
                result = 'There is an obstacle at left'
        elif task == 'stop':
            h_bridge_motor.stop()
            result = 'done'
        GPIO.cleanup()
        return result


app = Flask(__name__, template_folder='views')
# app = Flask(__name__)


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route("/", methods=['GET'])
def home():
    return render_template('website.html')


@app.route("/home/addTodaysTask", methods=['POST', 'GET'])
def addTodaysTasks():
    range_of_grids = []
    alphabets = [
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'
    ]
    for alphabet in alphabets:
        for i in range(14):
            range_of_grids.append(alphabet+str(i))

    if request.method == "POST":
        try:
            dictionary_data = eval(request.get_data().decode('utf-8'))
            taskDate = dictionary_data['date']
            itemID = dictionary_data['itemID']
            item = dictionary_data['item']
            itemDes = dictionary_data['itemDescription'].upper()
            itemStatus = dictionary_data['itemStatus']
            if str(itemDes) in range_of_grids:
                result = addTasksToDatabase(
                    taskDate, itemID, item, itemDes, itemStatus
                )
                edit_grid(itemDes, itemID)
                return jsonify({
                    "status": 200,
                    "msg": "Task added successfully",
                    "data": result
                })
            else:
                return jsonify({
                    "status": 400, "msg": "Task not added", "data": []
                })
        except:
            return jsonify({
                "status": 400, "msg": "Task not added", "data": []
            })
    if request.method == "GET":
        return jsonify({"status": 400, "msg": "Task not added", "data": []})


def addTasksToDatabase(taskDate, itemID, item, itemDes, itemStatus):
    path = "/tasks/"+ str(taskDate)
    data = {
        "item": item,
        "itemID": itemID,
        "itemDescription": itemDes,
        "status": itemStatus
    }
    return firebase.put(path, str(item), data)


@app.route("/home/getTodaysTask", methods=['POST', 'GET'])
def getTodaysTasks():
    if request.method == "POST":
        dictionary_data = eval(request.get_data().decode('utf-8'))
        taskDate = dictionary_data['date']
        result = getTaskFromDatabase(taskDate)
        if result is None:
            os.system("cp views/website.html.BAK views/website.html")
            destinations = ['Start']
            display_route(shortest_route(destinations)[0])
            return jsonify({
                "status": 200, "msg": "No items in this date", "data": []
            })
        else:
            os.system("cp views/website.html.BAK views/website.html")
            destinations = ['Start']
            for key in result:
                edit_grid(result[key]['itemDescription'], result[key]['itemID'])
                destinations.append(result[key]['itemDescription'])
            calculated_route = shortest_route(destinations)
            display_route(calculated_route)
            with open('nodes.txt', 'w') as nodes_f:
                for node in destinations:
                    nodes_f.write(node + '\n')
            with open('nodes.txt', 'r') as nodes_f:
                lines = nodes_f.readlines()
                nodes = []
                for line in lines:
                    nodes.append(line.strip('\n'))

                all_routes = []
                all_routes_costs = []
                first_route = shortest_route(nodes)
                all_routes.append(first_route[0])
                all_routes_costs.append(first_route[1])

                for i in range(10):
                    test_route = shortest_route(nodes)
                    test_list2 = test_route[0]
                    check_identical = []
                    for each_route in all_routes:
                        test_list1 = each_route
                        if functools.reduce(lambda i, j: i and j, map(lambda m, k: m == k, test_list1, test_list2), True):
                            check_identical.append('Y')
                        else:
                            check_identical.append('N')
                    if 'Y' in check_identical:
                        pass
                    else:
                        all_routes.append(test_list2)
                        all_routes_costs.append(test_route[1])

                with open('all_routes.txt', 'w') as all_routes_f:
                    for (route, distance_cost) in zip(all_routes, all_routes_costs):
                        all_routes_f.write(', '.join(route) + ': ')
                        all_routes_f.write(str(distance_cost))
                        all_routes_f.write('\n')
            # os.system("python shortest_path.py")
            return jsonify({
                "status": 200, "msg": "Successfully get items", "data": result
            })
    if request.method == "GET":
        print("GET")
        return jsonify({"status": 200, "msg": "Failed to add", "data": []})


def getTaskFromDatabase(taskDate):
    path = "/tasks/"+ str(taskDate) + "/"
    return firebase.get(path, None)


def putServerIPtoFirebase(ip):
    path = '/raspberryPiServer/'
    result = firebase.put(path, 'ip_address', ip)


def get_items_from_database(detected_code):
    x = datetime.datetime.now()
    date = str(x.day)+"-"+str(x.month)+"-"+str(x.year)+""
    data_path = "/tasks/" + date + "/" + str(detected_code) + "/status/"
    data = firebase.get(data_path, None)
    if data:
        if data == "pending" or data == "Pending":
            result = firebase.put(
                "/tasks/" + date + "/" + str(detected_code) + "/", "status", "Scanned"
            )
            print(result)
        # print(data, detected_code)


def gen():
    try:
        camera = cv2.VideoCapture(0)
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        while True:
            ret, img = camera.read()

            i = 0
            if i != 1:
                key = cv2.waitKey(1)
                if key == ord('c'):
                    cv2.imwrite('test.jpg', img)

            for barcode in decode(img):

                myData = barcode.data.decode('utf-8')
                if myData:
                    get_items_from_database(myData)

                pts = np.array([barcode.polygon], np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(img, [pts], True, (255, 0, 255), 5)
                pts2 = barcode.rect

                cv2.putText(
                    img, myData, (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX,
                    0.9, (255, 0, 255)
                )

            if ret:
                frame = cv2.imencode('.jpg', img)[1].tobytes()
                yield (
                    b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
                )
                # cv2.imwrite('test.png', ret)
            else:
                break

        # return img

    except:
        print("Exception: ", sys.exc_info()[0])


@app.route('/video_feed')
def video_feed():
    return Response(
        gen(), mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/snapshot')
def snapshot():

    image = ImageGrab.grab()

    # if cv2.VideoCapture(0):
    #     cv2.VideoCapture(0).release()
    #     cv2.destroyAllWindows()

    # camera = cv2.VideoCapture(0, cv2.CAP_V4L)
    # camera.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
    # camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # for i in range(30):
    #     temp = camera.read()
    # ret, frame = cv2.VideoCapture(0).read()
    # if frame:
    #     print('YAY!')
    count = [0]
    if glob.glob('frame*.jpg'):
        for each_img in glob.glob('frame*.jpg'):
            terms = each_img.split('.')
            count.append(int(terms[0].split('_')[1]))
    next_count = max(count) + 1
    image.save('frame_' + str(next_count) + '.jpg')
    # cv2.imwrite('frame_' + str(next_count) + '.jpg', frame)

    # camera.release()

    return redirect("/")


@app.route('/home/scan_rfid', methods=['POST'])
def scan_rfid():
    if request.method == "POST":
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        rfid_reader = RFID_Sensor()
        rfid = rfid_reader.get_rfid()
        print(rfid)
        GPIO.cleanup()
        if rfid != "":
            status = update_rfid_status(rfid)
            if status == 'scanned':
                return jsonify({
                    "status": 200, "msg": "RFID scanned", "data": [rfid]
                })
            elif status == 'already scanned':
                return jsonify({
                    "status": 200,
                    "msg": "RFID already scanned",
                    "data": [rfid]
                })
            else:
                return jsonify({
                    "status": 200, "msg": "RFID not found", "data": []
                })
        else:
            return jsonify({
                "status": 400,
                "msg": "Some error in getting rfid. Scan again",
                "data": []
            })


def update_rfid_status(rfid):
    x = datetime.datetime.now()
    date = str(x.day)+"-"+str(x.month)+"-"+str(x.year)+""
    data_path = "/tasks/" + date + "/" + str(rfid) + "/status/"
    data = firebase.get(data_path, None)
    if data:
        if data == "pending" or data == "Pending":
            result = firebase.put(
                "/tasks/" + date + "/" + str(rfid) + "/", "status", "Scanned"
            )
            print(result)
            return 'scanned'
        else:
            return 'already scanned'
    else:
        return 'not found'


@app.route('/home/robot_control', methods=['POST'])
def robot_control():
    if request.method == "POST":
        dictionary_data = eval(request.get_data().decode('utf-8'))
        task = dictionary_data['task']
        if task != "":
            GPIO.setmode(GPIO.BOARD)
            GPIO.setwarnings(False)
            controller = Controller()
            result = controller.move_robot(task)
            print('Task given: ' + task)
            print('Task result: ' + result)
            GPIO.cleanup()
            return jsonify({"status": 200, "msg": str(result), "data": []})
        else:
            return jsonify({
                "status": 400, "msg": "task not performed", "data": []
            })


if __name__ == "__main__":
    # app.debug = True
    # host = os.environ.get('IP', '0.0.0.0')
    # port = int(os.environ.get('PORT', '5000'))
    # app.run(host=host, port=port)
    app.run(host='0.0.0.0', port=5000, debug=True)
