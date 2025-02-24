from django.contrib.auth.forms import UserCreationForm
from .models import CustomerProfile,CustomUser
from django import forms

class CustomerCreationForm(UserCreationForm):
    class Meta: 
        model = CustomerProfile
        fields = ['username', 'first_name','last_name','contact','email','dob','gender','profile_picture']

# {% url 'profile' id=user.id %}