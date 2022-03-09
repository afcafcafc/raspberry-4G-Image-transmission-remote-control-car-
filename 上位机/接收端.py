import imshow
import sys,os
import cv2 as cv
import cv2
import socket,serial
import numpy as np
import time
from multiprocessing import Process,Queue,Pipe,freeze_support
import pygame
from PyQt5.QtWidgets import QMainWindow,QApplication
from PyQt5.QtCore import *

from PyQt5.QtGui import *#QImage

from PyQt5 import QtCore, QtGui, QtWidgets

import pynmea2
# q=Queue()
pipe=Pipe()


longitude,latitude=(117.34354133333333, 39.11021133333333)
yaw=0
velocity=0
status=0
numofuse=0
class rec_loc(QThread):
    sinOut = pyqtSignal(str)

    def __init__(self, parent=None):
        super(rec_loc, self).__init__(parent)
        #设置工作状态与初始num数值


        # self.ser=serial.Serial('COM13',38400)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client.bind(('', 3392))
        self.BUFSIZE=100000
    def run(self):
        global longitude,latitude,yaw,velocity,status,numofuse,status
        while True:
            data, client_addr = self.client.recvfrom(self.BUFSIZE)
            # print(data)
            try:
                data = data.decode()

                if data.split(',')[0] == '$GNRMC':
                    GNRMC = pynmea2.parse(data)
                    yaw = float(data.split(',')[8])
                    longitude, latitude = (GNRMC.longitude, GNRMC.latitude)
                    # print(yaw)
                    # print(GNRMC.longitude, GNRMC.latitude)
                if data.split(',')[0] == '$GNVTG':
                    velocity = data.split(',')[7]
                    # print(velocity)
                if data.split(',')[0] == '$GNGGA':
                    status = data.split(',')[6]
                    numofuse = data.split(',')[7]
                    # print(numofuse)
                    if status==0:
                        status='un_loc'
                    if status==1:
                        status = 'no chafen'
                    if status==2:
                        status = 'chafen'
                # print(status, num)
            except:
                pass

class PyQtMainEntry(QMainWindow, imshow.Ui_Form):
    def __init__(self,pipe):
        super().__init__()
        self.setupUi(self)
        # self.camera = cv2.VideoCapture(0)
        self.pipe=pipe

        # print('over')
        # cv2.imshow("imgr", self.frame)
        self.frame = cv.imread('295021.jpg')
        img_rows, img_cols, channels = self.frame.shape
        bytesPerLine = channels * img_cols
        QImg = QImage(self.frame.data, img_cols, img_rows, bytesPerLine, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(QImg).scaled(self.label.width(), self.label.height()))

        self._timer = QtCore.QTimer(self)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip_port = ('150.158.91.167', 3391)
        self.thread=rec_loc()


    def opencam(self):

        self._timer.timeout.connect(self.queryFrame)
        if self.comboBox.currentText()=='joystick':
            pygame.init()
            pygame.joystick.init()
            self.joystick = pygame.joystick.Joystick(0)
        else:
            self.label.grabKeyboard()
        self._timer.setInterval(20)#ms
        self._timer.start()
        self.thread.start()
        # print(1)

    def keyPressEvent(self, QKeyEvent):
        if self.comboBox.currentText() == 'keyboard':
            throttle = 0
            brake = 0
            turn = 0
            print('a')
            if QKeyEvent.key() == Qt.Key_Up:
                throttle = 0.8
            if QKeyEvent.key() == Qt.Key_Down:
                brake = 0.8
            if QKeyEvent.key() == Qt.Key_Left:
                turn -= 0.3
            if QKeyEvent.key() == Qt.Key_Right:
                turn += 0.3
            stringData = (str(turn) + ',' + str(brake) + ',' + str(throttle))
            self.client.sendto(stringData.encode('utf-8'), self.ip_port)
    def queryFrame(self):
        global longitude,latitude,yaw,velocity,status,numofuse,status
        # suc, self.frame = self.camera.read()

        # self.frame.reszie(320,240)
        # print('in')

        self.frame= self.pipe.recv()
        # print('over')
        # cv2.imshow("imgr", self.frame)
        self.frame=cv.cvtColor(self.frame,cv.COLOR_BGR2RGB)
        img_rows, img_cols, channels = self.frame.shape
        bytesPerLine = channels * img_cols
        QImg = QImage(self.frame.data, img_cols, img_rows, bytesPerLine, QImage.Format_RGB888)
        pixmap=QPixmap.fromImage(QImg)

        self.label.setPixmap(QPixmap.fromImage(QImg).scaled(self.label.width(), self.label.height()))
        # self.webEngineView.page().runJavaScript('refresh("' + 'iawhduihwdaiu' + '");')
        if self.comboBox.currentText()=='joystick':
            for event_ in pygame.event.get():
                self.joystick.get_axis(0)
                self.joystick.get_axis(4)
                print(self.joystick.get_axis(0), self.joystick.get_axis(4), self.joystick.get_axis(5))
                stringData = str(self.joystick.get_axis(0)) + ',' + str(self.joystick.get_axis(4)) + ',' + str(
                    self.joystick.get_axis(5))
                self.client.sendto(stringData.encode('utf-8'), self.ip_port)
        # if longitude!=longitude_o or latitude!=latitude_o :
        self.webEngineView.page().runJavaScript('refresh('+str(longitude)+','+str(latitude)+');')
            # longitude_o,latitude_o=longitude,latitude

        self.label_6.setText(str(longitude))
        self.label_5.setText(str(latitude))
        self.label_4.setText(str(velocity))
        self.label_3.setText(str(yaw))
        self.label_2.setText(numofuse)
        # print(numofuse,status)
        self.label_13.setText(str(status))
        # self.webEngineView.page().runJavaScript('refresh('+str(longitude)+','+str(latitude)+');')
        # print(longitude,latitude,'refresh('+'"'+str(longitude)+'"'+','+'"'+str(latitude)+'"'+');')
def window_start(pipe1):

    app = QtWidgets.QApplication(sys.argv)
    window = PyQtMainEntry(pipe1)

    window.show()
    sys.exit(app.exec_())
def udp_receive(pipe0):
    BUFSIZE = 100000
    # ip_port = ('', 1390)
    ip_port = ('', 3390)
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp协议
    server.bind(ip_port)
    # cv2.namedWindow('imgr')

    # imde=np.zeros((IMAGE_BASE_SIZE_Y,IMAGE_BASE_SIZE_X,3),dtype=np.uint8)

    start_time = 0

    cnt = 0
    sum = 0
    flag = 1
    lastindex = [-1, -1]
    data_total0 = []
    data_total1 = []
    data_total = [data_total0, data_total1]
    pic_index = [0, 0]
    pic_cnt = [0, 0]
    cnt_lost = 0

    while True:
        # print('ok')
        data, client_addr = server.recvfrom(BUFSIZE)
        # print('server收到的数据', data)
        if data:
            # imde = np.zeros((720, 1280, 3), dtype=np.uint8)
            # print(len(data[2:]))

            i = int.from_bytes(data[0:1], byteorder='big')  # 一张中的第几组数据

            j = int.from_bytes(data[1:2], byteorder='big')  # 一张中的共有j组
            k = int.from_bytes(data[2:3], byteorder='big')  # 校验和
            l = int.from_bytes(data[3:4], byteorder='big')
            # print(i, j, k, l)

            if l % 2 == 0:

                if lastindex[0] != l:
                    pic_cnt[0] = 0

                pic_index[0] = int.from_bytes(data[3:4], byteorder='big')
                pic_cnt[0] += 1
                if i == j - 1:
                    data_total0[i * 1400:] = list(data[4:])
                else:
                    data_total0[i * 1400:(i + 1) * 1400] = list(data[4:])
                # print(i,j,k,pic_cnt[0],k,pic_index[0])
                if pic_cnt[0] == j:
                    b = bytes(data_total0)
                    stringdata = np.frombuffer(b, dtype='uint8')
                    length = len(stringdata)
                    if k == length % 100:
                        img = cv2.imdecode(stringdata, 1)
                        try:
                            if l == 200:
                                print(cnt_lost / 200)
                                cnt_lost = 0
                            cnt_lost += 1
                            pipe0.send(cv2.rotate(img, cv2.ROTATE_180))
                            # cv2.imshow("imgr", img)
                            # if cv2.waitKey(1) == ord('q'):
                            #     break
                        except:
                            print("show error")
                lastindex[0] = l
            else:

                if lastindex[1] != l:
                    pic_cnt[1] = 0

                pic_index[1] = int.from_bytes(data[3:4], byteorder='big')
                pic_cnt[1] += 1
                if i == j - 1:
                    data_total1[i * 1400:] = list(data[4:])
                else:
                    data_total1[i * 1400:(i + 1) * 1400] = list(data[4:])
                # print(i, j, k, pic_cnt[1], k, pic_index[1])
                if pic_cnt[1] == j:
                    b = bytes(data_total1)
                    stringdata = np.frombuffer(b, dtype='uint8')
                    length = len(stringdata)
                    if k == length % 100:
                        img = cv2.imdecode(stringdata, 1)
                        try:
                            # print(l)
                            cnt_lost += 1
                            pipe0.send(cv2.rotate(img, cv2.ROTATE_180) )
                            # cv2.imshow("imgr", img)
                            # if cv2.waitKey(1) == ord('q'):
                            #     break
                        except:
                            print("show error")
                lastindex[1] = l
        ########################################################################
        # suc, img = cap.read()
        # pipe[0].send(img)
def send_joystick(a):
    os.system("frpc.exe")

    pass

if __name__ == '__main__':
    freeze_support()
    os.system('taskkill /f /im test2.exe')
    p1=Process(target=window_start,args=(pipe[1],))
    p2=Process(target=udp_receive,args=(pipe[0],))
    p3 = Process(target=send_joystick,args=(0,))
    p1.start()
    # time.sleep(3)
    p2.start()
    p3.start()
    # pyinstaller -D -w test2.py
    #activate cv_qt
    #cd C:\Users\afc\Desktop\old\python proj\frp_udp
    #pyinstaller -D test2.py
