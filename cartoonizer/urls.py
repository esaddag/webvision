from django.urls import path
from . import views

app_name="cartoonizer"

urlpatterns = [
	 path('', views.index, name="index"),
	 path('cartoonize/', views.cartoonize, name='cartoonize')
]