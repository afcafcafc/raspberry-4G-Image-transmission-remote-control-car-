#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import cv2
import numpy as np
import datetime
import time
import struct
BUFSIZE = 60000

IMAGE_SIZE_X = 480
IMAGE_SIZE_Y = 320

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cap=cv2.VideoCapture(0)
cap.set(3,IMAGE_SIZE_X)
cap.set(4,IMAGE_SIZE_Y)
fps = cap.get(cv2.CAP_PROP_FPS)
print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))

cnt = 0
def img_send(stringData):
    #ip_port = ('127.0.0.1', 1390)
    ip_port = ('你的服务器ip', 3390)
    client.sendto(stringData, ip_port)

def img_encode(img,i,j):
    global cnt
    cnt+=1
    if cnt>200:
        cnt=0
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 40]
    img_encode = cv2.imencode('.jpg', img,encode_param)[1]
    data = np.array(img_encode)
    stringData = data.tostring()
    length = len(stringData)
    length_num=length//1400+1
    print(length,length_num)
    i=length-(length//100)*100
    print(i)
    for k in range(length_num):

        j = length_num
        if k==length_num-1:
            # img_send(k.to_bytes(1, byteorder='big') + j.to_bytes(1, byteorder='big') + i.to_bytes(1, byteorder='big') + cnt.to_bytes(1, byteorder='big') + stringData[k * 1400:length])
            img_send((struct.pack('B',k)) + (struct.pack('B',j)) + (struct.pack('B',i)) + (struct.pack('B',cnt)) + stringData[k * 1400:length])
        else:
            # img_send(k.to_bytes(1, byteorder='big') + j.to_bytes(1, byteorder='big') + i.to_bytes(1, byteorder='big') + cnt.to_bytes(1, byteorder='big')+stringData[k*1400:(k+1)*1400])
            img_send((struct.pack('B',k)) + (struct.pack('B',j)) + (struct.pack('B',i)) + (struct.pack('B',cnt))+stringData[k*1400:(k+1)*1400])
        
        
        # while m>0:
        #     m-=1
        
def img_split(img):
    # for i in range(IMAGE_ROW):
    #     # print(160 * (i + 1))
    #     for j in range(IMAGE_COLUMN):
    #         cv2.imshow('test'+str(i)+' '+str(j),img[j*IMAGE_BASE_SIZE_Y:(j+1)*IMAGE_BASE_SIZE_Y,i*IMAGE_BASE_SIZE_X:(i+1)*IMAGE_BASE_SIZE_X])
    #         img_encode(img[j*IMAGE_BASE_SIZE_Y:(j+1)*IMAGE_BASE_SIZE_Y,i*IMAGE_BASE_SIZE_X:(i+1)*IMAGE_BASE_SIZE_X],i,j)
    #         pass
    a=datetime.datetime.now()
    img_encode(img, 1, 1)
    print(datetime.datetime.now()-a)
if __name__ == '__main__':


    while True:

        start_time = time.time()
        suc, img = cap.read()
        # img=cv2.imread('test.png')
        img_split(img)
        #cv2.namedWindow("imgt", 0)
        #cv2.imshow("imgt",img)
        #cv2.resizeWindow("imgt", IMAGE_SIZE_X, IMAGE_SIZE_Y)
        # print(img.shape)

        # print(img[355:640,475:480])
        # print(img.shape)
        # time.sleep(0.1)

        # if cv2.waitKey(1)&0xff==ord("1"):
        #     break
        # print("FPS: ", 1.0 / (time.time() - start_time))





        # client.sendto(fhead, ('127.0.0.1', 9999))

        # data, server_addr = client.recvfrom(BUFSIZE)
        # client.sendto(str(length), ip_port)
        # try:
        #     client.sendto(stringData, ip_port)
        # except:
        #     print('error')

        # data1, server_addr = client.recvfrom(BUFSIZE)
        # print('客户端recvfrom ', data, server_addr)

    # client.close()