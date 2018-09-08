import serial.tools.list_ports
import numpy 
import matplotlib
import cv2

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


def main():
    camera = cv2.VideoCapture(0)
    setup_trackbars('RGB')
    arduino = setUpArduino()
    if(arduino is None):
        print("Arduino not connected")
        exit()

    light = arduino.get_pin("d:5:p")

    while True:
        ret, image = camera.read()

        #Wait for an button press 
        key = cv2.waitKey(25) & 0xFF
        if key == ord("p"):

            processedImage, contours = processImage(image)
            cv2.imshow("Original", processedImage)
            
            key = cv2.waitKey(0) & 0xFF
            if key == ord('p'):
                break
            elif key == ord('q') or key == 27:
                cv2.destroyAllWindows()
                camera.release()
                continue

        elif key == ord('q') or key == 27:
			cv2.destroyAllWindows()
			camera.release()
			break
        
        
        processedImage , contours = processImage(image)
        cv2.imshow("Original", processedImage)

        if len(contours) > 0:
            c = max(contours, key=cv2.contourArea)
            if(cv2.contourArea(c) > 40):
                light.write(1)
            else:
                light.write(0)
        else:
            light.write(0)

if __name__ == '__main__':
    main()



