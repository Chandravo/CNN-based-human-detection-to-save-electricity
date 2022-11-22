from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Room
from django.contrib.auth.models import auth
from django.core.mail import send_mail
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

import cv2
import numpy as np
import time
import os.path
import wget

import random,string


def login(request):
    if request.user.is_authenticated:
        return redirect("/")
    if request.method=="POST":
        print("here")
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            # return render(request,'home2.html',{'email':email})
            return redirect('/')
        else:
            print("no")
            messages.add_message(request, messages.ERROR, "Wrong username or password!")
            return render(request,'login.html')
    else:
        return render(request,'login.html')  
    # return render(request, 'login.html')

@login_required(login_url='/login')
def logout(request):
    if request.user.is_anonymous:
        return redirect('/login')
    auth.logout(request)
    return redirect('/login')

@login_required(login_url='/login')
def home(request):
    # for i in room.objects.all():
    # data={}
    # for room in Room.objects.all():
    #     data[room.name]=room.cam_url
    data=Room.objects.all()
    # for room in Room.objects.all():
    #     d={}
    #     d['name']=room.name
    #     d['cam']=room.cam_url
        # data.append(d)
    # print(data)
        
    return render(request, 'home2.html', {'data':data})


@login_required(login_url='/login')
def liveCam(request, event, type):
    return render(request, 'app/liveCam.html', {'event': event, 'type': type})


def otp(request):
    if (request.method=="POST"):
        email=request.POST['email']
        user=User.objects.filter(email=email).first()
        if (user is not None):
            otp=''.join(random.choice(string.digits) for _ in range(7))
            user.otp=otp
            user.save()
            sub="OTP for Password reset"
            message="Your OTP to reset password is "+otp
            from_email= settings.EMAIL_HOST_USER
            send_mail(sub, message, from_email, [email], fail_silently=False)
            return redirect('/reset_password')
        else:
            messages.add_message(request, messages.ERROR, "User does not exist!")
            return render(request, 'otp.html')
    return render(request, 'otp.html')

def reset_password(request):
    if (request.method=="POST"):
        otp=request.POST['otp']
        password=request.POST['password']
        user=User.objects.filter(otp=otp).first()
        if (user is not None):
            user.set_password(password)
            user.save()
            return redirect('/login')
        else:
            messages.add_message(request, messages.ERROR, "OTP is incorrect!")
            return render(request, 'reset_password.html')
    return render(request, 'reset.html')

class check_status(APIView):
    def get(self, request):
        data={"room":[],"status":[]}
        for room in Room.objects.all():
            cap=cv2.VideoCapture(room.cam_url)
            success, img = cap.read()
            cap.release()
            if (not gen(room.cam_url,img)) and light(room.cam_url,img):
                room.status=True
                
            else:
                room.status=False
            room.save()
            data["room"]+=[room.name]
            data["status"]+=[room.status]
        print(data)
            
        return Response(data, status=status.HTTP_200_OK)    
    


def gen(url,img):
    ctime=0
    ptime=0
    # cap = cv2.VideoCapture(url)
    whT = 320
    confThreshold = 0.5
    nmsThreshold = 0.3

    classesFile = r"C:\Users\chand\Software_Eng\project\config\app\YOLO\yolo\coco.names"
    classNames = []

    with open(classesFile,'rt') as f:
        classNames = f.read().rstrip('\n').split('\n')
    modelConfiguration = r'C:\Users\chand\Software_Eng\project\config\app\YOLO\yolo\yolov3.cfg'
    modelWeights = r'C:\Users\chand\Software_Eng\project\config\app\YOLO\yolo\yolov3.weights'

    net = cv2.dnn.readNetFromDarknet(modelConfiguration,modelWeights)
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    
    def findObjects(outputs, img):
        hT,wT,cT = img.shape
        bbox = []
        classIds = []
        confs = []

        for output in outputs:
            for det in output:
                scores = det[5:]
                classId = np.argmax(scores)
                # if classId==0:
                #     print("hello")
                confidence = scores[classId]
                if confidence > confThreshold and classId==0:
                    return True
                    # print("person detected")
        return False
    
    # success, img = cap.read()
    blob = cv2.dnn.blobFromImage(img,1/255,(whT,whT),[0,0,0],1,crop=False)
    net.setInput(blob)
    layerNames = net.getLayerNames()

    outputNames = [layerNames[i-1] for i in net.getUnconnectedOutLayers()]
    outputs = net.forward(outputNames)
    # cap.release()

    if (findObjects(outputs,img)):
        return True
    else:
        return False
    
def light(url,img):
    def img_estim(img, thrshld):
        is_light = np.mean(img) > thrshld
        # print(np.mean(img))
        return True if is_light else False


    # cap=cv2.VideoCapture(url)

    # success, img = cap.read()
    # cap.release()
    if (img_estim(img, 120)):
        return True
    else:
        return False
    