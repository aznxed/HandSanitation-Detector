import serial.tools.list_ports
import numpy 
import matplotlib
import cv2
import threading

from random import randint
from pyfirmata import Arduino, util
from time import clock, sleep


def wait(lengthMS):
    s = clock()
    while (clock() - s) * 1000 < lengthMS:
        pass


def callback(value):
    pass


def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)

    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255

        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)


def setUpArduino():
    ports = list(serial.tools.list_ports.comports())
    connectedDevice = None

    for p in ports:
        if 'Arduino' in p[1]:
            try:
                connectedDevice = Arduino(p[0])
                print("Connected to " + str(connectedDevice))
                break
            except serial.SerialException:
                print("Arduino detected but unable to connect to " + p[0])
        if connectedDevice is NoneType:
            exit("Failed to connect to Arduino")

    return connectedDevice


def buttonDetect():
    global buttonPressed
    global sensing
    global sensor

    while sensing:
        sleep(.01)
        t = clock()
        if(sensor.read() == 1.0):
            buttonPressed = True


def get_trackbar_values(range_filter):
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)

    return values


def processImage(image):
    v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values('RGB')
    thresh = cv2.inRange(image, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
    
    mask = cv2.inRange(image, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE)[-2]
            
    cv2.drawContours(image, cnts, -1, (0,255,0), 1)
    return image,cnts

def getDirtyPercent(image):
    return randint(1, 3)


def main():
    global sensing
    global buttonPressed
    global sensor

    sensing = True
    buttonPressed = False

    camera = cv2.VideoCapture(0)
    setup_trackbars('RGB')
    arduino = setUpArduino()
    if(arduino is None):
        print("Arduino not connected")
        exit()

    light = arduino.get_pin("d:5:p")
    sensor = arduino.get_pin("a:0:i")

    it = util.Iterator(arduino)
    it.daemon = True
    it.start()
    sensor.enable_reporting()
    light.write(0)

    buttonThread = threading.Thread(target=buttonDetect)
    buttonThread.start()

    while sensing:
        ret, image = camera.read()

        #Wait for an button press 
        #key = cv2.waitKey(25) & 0xFF
        #if key == ord("p"):
        if(buttonPressed):
            sensing = False
            processedImage, contours = processImage(image)
            cv2.imshow("Original", processedImage)

            dirty = getDirtyPercent(image)
            print(dirty)
            if(dirty > 1):
                light.write(1)

            # if len(contours) > 0:
            #     c = max(contours, key=cv2.contourArea)
            #     if(cv2.contourArea(c) > 40):
            #         light.write(1)
            #     else:
            #         light.write(0)

            key = cv2.waitKey(0) & 0xFF
            light.write(0)
            
            cv2.destroyAllWindows()
            camera.release()
            exit()
            
            # if key == ord('p'):
            #     break
            # elif key == ord('q') or key == 27:
            #     cv2.destroyAllWindows()
            #     camera.release()
            #     continue
                
        key = cv2.waitKey(25) & 0xFF
        if key == ord('q') or key == 27:
			cv2.destroyAllWindows()
			camera.release()
			break
        
        cv2.imshow("Original", image)

if __name__ == '__main__':
    main()



