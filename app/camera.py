import cv2

class VideoCamera(object):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
    
    def __del__(self):
        self.cap.release()

    def get_frame(self):
        _, frame = self.cap.read()
        return frame