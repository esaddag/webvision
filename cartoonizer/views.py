from django.shortcuts import render, redirect
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import messages
import numpy as np
import urllib.request as request
from urllib.request import Request
import json
import cv2
import os
import base64

@csrf_exempt	
def index(req):
	if req.user.is_authenticated:
		return render(req, "cartoonizer/index.html")
	else:
		messages.add_message(req, messages.ERROR, "You have to login first")
		return redirect("login")
@csrf_exempt
def cartoonize(req):
	if req.user.is_authenticated:
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

			numBilateralFilters = 4
			img_color = image.copy()
			

			for _ in range(numBilateralFilters):
				img_color = cv2.bilateralFilter(img_color, 15, 30, 20)
				
			img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			img_blur = cv2.medianBlur(img_gray, 7)

			img_edge = cv2.adaptiveThreshold( img_blur, 2, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3,2)

			img_painted = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
			img_painted = cv2.bitwise_or(img_color, img_painted)
			
			# encode image as base64
			ret, frame_buff = cv2.imencode('.jpg', img_painted)
			frame_b64 = base64.b64encode(frame_buff)

			#added to get rid of b'
			decoded_image = frame_b64.decode("utf-8")
		
		# return a JSON response
		return render(req, 'cartoonizer/result.html', {'image': decoded_image, "success":data["success"]})
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
