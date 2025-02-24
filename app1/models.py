from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator,RegexValidator
from django.conf import settings
# from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from django.urls import path
# from django.contrib import admin
from django.utils.timezone import now
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.contrib.auth import login, authenticate, logout
# from django import forms

# Create your models here.
class CustomUser(AbstractUser):
    contact = models.CharField(max_length=10,validators=[RegexValidator(regex=r'^\d{10}$',message='contact number must be exactly of 10 digits')])
    groups = models.ManyToManyField('auth.Group',related_name='account_user_set',blank=True)
    user_permissions=models.ManyToManyField('auth.Permission',related_name='account_user_permission_set',blank=True)

    def __str__(self):
        return self.username

    class Meta:
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
        ]

class CustomerProfile(CustomUser):
    # user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='customer_profile')
    dob = models.DateField()
    gender = models.CharField(max_length=10,choices=(('male','Male'),('female','Female')))
    profile_picture = models.ImageField(upload_to='profile_pics/',null=True,blank=True)

    class Meta:
        db_table = 'CustomerProfile'

class Movie(models.Model):
    title = models.CharField(max_length=255)
    genre = models.CharField(max_length=100)
    language = models.CharField(max_length=50)
    duration = models.PositiveIntegerField()  # Duration in minutes
    rating = models.FloatField()
    release_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='movies/')

    def __str__(self):
        return self.title

class Theater(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.movie.title} at {self.theater.name}"

class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(default=now)
    total_amount = models.FloatField()
    def __str__(self):
        return f"Booking {self.id} for {self.user.username}"
    

class Seat(models.Model):
    CLASS_CHOICES = (
        ('Regular', 'Regular'),
        ('Premium', 'Premium'),
    )
    show = models.ForeignKey(Show, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    seat_class = models.CharField(max_length=20, choices=CLASS_CHOICES)
    status = models.BooleanField(default=True)  # True means Available
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Seat {self.seat_number} ({self.seat_class})"


