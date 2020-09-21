from django.db import models

# Create your models here.

class DetectedFace(models.Model):
	face_id = models.IntegerField("face id")

	def __str__(self):
		return self.face_id
	