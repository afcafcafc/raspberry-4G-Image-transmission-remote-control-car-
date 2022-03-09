#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from nav_msgs.msg import Odometry
from car_port.msg import header  #导入刚刚创建的消息类型
from geometry_msgs.msg import Twist
import serial
import time
import threading,queue
import tf
import math
import socket
BUFSIZE = 100000
ip_port = ('', 3391)
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp协议
server.bind(ip_port)


serialPort = "/dev/ttyUSB1"
baudRate = 115200
ser = serial.Serial(serialPort, baudRate, timeout=0.5)
print("serial port is %s ,baudRate is %d" % (serialPort, baudRate))
ser.write('w'.encode())
time.sleep(3)
ser.flushInput()
pub = rospy.Publisher('serial_data_odom', header, queue_size=1)
dic={
    'turn':0,
    'throttle':1,
    'brake':1
}
# q=queue.Queue(5)
R=threading.Lock()
def thread_job():    ##我们这个节点需要同时读取和写入出口，但rospy没有C++的spinOnce，所以需要多线程。
    global dic
    while True:
        data, client_addr = server.recvfrom(BUFSIZE)
        
        data=data.decode()
        data=data.split(",")
        turn=float(data[0])
        brake=float(data[1])
        throttle=float(data[2])
        # print(turn)
        R.acquire()
        dic={
            'turn':turn,
            'throttle':throttle,
            'brake':brake
        }
        R.release()
        # q.put(dic)
        # print(turn,throttle,brake)



def xianfu(a):
    if a<0:
        a=0
    if a>8000:
        a=8000
    return a




def SubscribeAndPublish():
    rospy.init_node('serial_data_contral', anonymous=True)  # 初始化节点
    
    # rospy.spin()
    br=tf.TransformBroadcaster()
    distance=0
    distance_x=0
    distance_y=0

    rate = rospy.Rate(50)  # 设置后面程序读取串口的频率
    add_thread = threading.Thread(target=thread_job)
    add_thread.start()  # 启动线程

    while not rospy.is_shutdown():  # 下面是用于读取串口发来的数据

        get_str = ser.readline()  # 读取串口数据，以换行符为结束
        get_str=get_str.decode()
        get_str = get_str.strip()
        # get_str = get_str.decode('utf-8','ignore')
        # print(get_str)
        list_str = get_str.split(' ')  ##将数据以逗号拆分
        # print(list_str)
        # print("######\n")

        msg = header()
        wheel_one = float(list_str[0])
        wheel_two = float(list_str[1])
        roll = float(list_str[2])
        yaw = float(list_str[3])/180*math.pi
        pitch = float(list_str[4])
        # print(wheel_one,wheel_two,yaw)
        distance=(wheel_one+wheel_two)/7668.41666666
        print(distance)
        distance_x=distance_x+distance*math.cos(yaw)
        distance_y=distance_y+distance*math.sin(yaw)
        print('x ',distance_x,' y ',distance_y,yaw)
        br.sendTransform((distance_x, distance_y, 0),
                     tf.transformations.quaternion_from_euler(0, 0, yaw),
                     rospy.Time.now(),
                     'base_link',
                     "odom")
        # dic=q.get()
        R.acquire()
        turn=dic['turn']
        throttle=dic['throttle'] 
        brake=dic['brake']
        R.release()
        # print(turn,throttle,brake)
        throttle_l=throttle*4000+4000+4000*turn
        throttle_r=throttle*4000+4000-4000*turn
        brake_l=brake*4000+4000-4000*turn
        brake_r=brake*4000+4000+4000*turn

        throttle_l=xianfu(throttle_l)
        throttle_r=xianfu(throttle_r)
        brake_l=xianfu(brake_l)
        brake_r=xianfu(brake_r)

        # print(brake_l,throttle_l,brake_r,throttle_r)
        # print('%f,%f,%f,%f\r\n'.encode()%(brake_l,throttle_l,brake_r,throttle_r))
        # if throttle_l>0 and throttle_r>0:
        ser.write('%f,%f,%f,%f\r\n'.encode()%(brake_l,throttle_l,brake_r,throttle_r))
            # print('0,%f,0,%f\r\n'.encode()%(throttle_l,throttle_r))
        
        # msg.wheel_one = wheel_one
        # msg.wheel_two = wheel_two
        # msg.roll = roll
        # msg.yaw = yaw
        # msg.pitch = pitch
        # pub.publish(msg)  ##发布
        rate.sleep()


if __name__ == '__main__':
    try:
        SubscribeAndPublish()
    except rospy.ROSInterruptException:
        pass





