from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django import forms
from django.contrib.auth.models import User

@csrf_exempt	
def index(request):
	if request.user.is_authenticated:
		return render(request, "index.html")
	else:
		return redirect("login")

def logout_view(request):
	logout(request)
	messages.add_message(request, messages.SUCCESS, "You successfully logged out.")
	return redirect("login")
	
class SignUpForm(UserCreationForm):
	email = forms.EmailField(label="Email", required=True, widget=forms.EmailInput)

	class Meta:
		model = User
		fields = ["username", "email", "password1", "password2"]

	
class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


