from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Room
from django.contrib.auth.models import auth

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

import cv2
import numpy as np
import time
import os.path
import wget


def login(request):
    if request.method=="POST":
        print("here")
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            return render(request,'home.html',{'email':email})
        else:
            print("no")
            messages.add_message(request, messages.ERROR, "Wrong username or password!")
            return render(request,'login.html')
    else:
        return render(request,'login.html')  
    # return render(request, 'login.html')


# @login_required(login_url='/login')
def home(request):
    # for i in room.objects.all():
    data={}
    for room in Room.objects.all():
        data[room.name]=room.cam_url
        
    return render(request, 'home.html', data)


@login_required(login_url='/login')
def liveCam(request, event, type):
    return render(request, 'app/liveCam.html', {'event': event, 'type': type})

class check_status(APIView):
    def get(self, request):
        data={"room":[],"status":[]}
        for room in Room.objects.all():
            if gen(room.cam_url):
                room.status=True
                
            else:
                room.status=False
            room.save()
            data["room"]+=[room.name]
            data["status"]+=[room.status]
        print(data)
            
        return Response(data, status=status.HTTP_200_OK)    
    

def gen(url):
    ctime=0
    ptime=0
    cap = cv2.VideoCapture(url)
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
    
    def findObjects(outputs,img):
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
    
    success, img = cap.read()

    blob = cv2.dnn.blobFromImage(img,1/255,(whT,whT),[0,0,0],1,crop=False)
    net.setInput(blob)
    layerNames = net.getLayerNames()

    outputNames = [layerNames[i-1] for i in net.getUnconnectedOutLayers()]
    outputs = net.forward(outputNames)
    cap.release()

    if (findObjects(outputs,img)):
        return True
    else:
        return False
    
    