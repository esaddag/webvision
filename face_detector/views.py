# import necessary packages
from django.shortcuts import render, redirect
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
import numpy as np
import urllib.request as request
from urllib.request import Request
import json
import cv2
import os
from  .models import DetectedFace
import base64

# define the path to the face detector
FACE_DETECTOR_PATH = "{base_path}/cascades/haarcascade_frontalface_default.xml".format(
	base_path=os.path.abspath(os.path.dirname(__file__)))

@csrf_exempt	
def index(req):
	if req.user.is_authenticated:
		return render(req, "face_detector/index.html")
	else:
		messages.add_message(req, messages.ERROR, "You have to login first")
		return redirect("login")

# find faces and draw it on the image
@csrf_exempt
def detect(req):

	if req.user.is_authenticated:
		# initialize the data dictionary to be returned by the request
		data = {"success": False}
		
		# check to see if this is a post request
		if req.method == "POST":
			
			# check to see if an image was uploaded 
			if req.FILES.get("image", None) is not None:
				
				# grab the uploaded image
				image = _grab_image(stream=req.FILES["image"])
				color_image = image.copy()
			# otherwise, assume that a URL was passed in
			else:
				
				# grab the URL from the request
				url = req.POST.get("url", None)
				
				# if the URL is None, then return an error
				if url is None:
					data["error"] = "No URL provided."
					return JsonResponse(data)
				
				# load the image and convert
				image = _grab_image(url=url)
				color_image = image.copy()
			# convert the image to grayscale
			image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			
			# load the face cascade detector
			detector = cv2.CascadeClassifier(FACE_DETECTOR_PATH)
			
			# and detect faces in the image
			rects = detector.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5,
				minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
			
			# draw rectangles on image
			for rect in rects:
				color_image = cv2.rectangle(color_image, (rect[0], rect[1]), (rect[0]+rect[2], rect[1]+rect[3]), (255, 0, 0))

			# construct a list of bounding boxes from the detection
			rects = [(int(x), int(y), int(x + w), int(y + h)) for (x, y, w, h) in rects]
			
			# update the data dictionary with the faces detected
			data.update({"num_faces": len(rects), "faces": rects, "success": True})
			
			# encode image as base64
			ret, frame_buff = cv2.imencode('.jpg', color_image)
			frame_b64 = base64.b64encode(frame_buff)

			#added to get rid of b'
			decoded_image = frame_b64.decode("utf-8")
		
		# return a JSON response
		return render(req, 'face_detector/result.html', {'image': decoded_image, "face_list":data["faces"], "num_faces":data["num_faces"], "success":data["success"]})
		#return HttpResponseRedirect(reverse('face_detector:result',kwargs={'image': frame_b64}))

	else:
		messages.add_message(req, messages.ERROR, "You have to login first")
		return redirect("login")
		
def _grab_image(path=None, stream=None, url=None):
	
	# if the path is not None, then load the image from disk
	if path is not None:
		image = cv2.imread(path)
	
	# otherwise, the image does not reside on disk
	else:	
		
		# if the URL is not None, then download the image
		if url is not None:
			resp = request.urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.0'}))
			data = resp.read()  
		
		# if the stream is not None, then the image has been uploaded
		elif stream is not None:
			data = stream.read()
		
		# convert the image to a NumPy array
		image = np.asarray(bytearray(data), dtype="uint8")

		# read it into OpenCV format
		image = cv2.imdecode(image, cv2.IMREAD_COLOR)
 
	# return the image
	return image


# find faces and returns as json
@csrf_exempt
def detect_with_post(req):
	
	# initialize the data dictionary to be returned by the request
	data = {"success": False}
	
	# check to see if this is a post request
	if req.method == "POST":
		
		# check to see if an image was uploaded 
		if req.FILES.get("image", None) is not None:
			
			# grab the uploaded image
			image = _grab_image(stream=req.FILES["image"])
		
		# otherwise, assume that a URL was passed in
		else:
			
			# grab the URL from the request
			url = req.POST.get("url", None)
			
			# if the URL is None, then return an error
			if url is None:
				data["error"] = "No URL provided."
				return JsonResponse(data)
			
			# load the image and convert
			image = _grab_image(url=url)
		
		# convert the image to grayscale
		image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		
		# load the face cascade detector
		detector = cv2.CascadeClassifier(FACE_DETECTOR_PATH)
		
		# and detect faces in the image
		rects = detector.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5,
			minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)
		
		# construct a list of bounding boxes from the detection
		rects = [(int(x), int(y), int(x + w), int(y + h)) for (x, y, w, h) in rects]
		
		# update the data dictionary with the faces detected
		data.update({"num_faces": len(rects), "faces": rects, "success": True})
	
	# return a JSON response
	return JsonResponse(data)
