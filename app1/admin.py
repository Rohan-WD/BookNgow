from django.contrib import admin
from app1.models import CustomUser,CustomerProfile,Movie,Theater,Show,Seat,Booking
from django.contrib.auth.admin import UserAdmin

# Register your models here.
# @admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username','first_name','last_name','email','contact','is_staff']
admin.site.register(CustomUser,CustomUserAdmin)

class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['dob','gender','profile_picture']
admin.site.register(CustomerProfile,CustomerProfileAdmin)

class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'language', 'duration', 'rating', 'release_date')

class TheaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'capacity')

class ShowAdmin(admin.ModelAdmin):
    list_display = ('movie', 'theater', 'date', 'time', 'total_seats', 'available_seats')

class SeatAdmin(admin.ModelAdmin):
    list_display = ('show', 'seat_number', 'seat_class', 'status')

class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'show', 'booking_date', 'total_amount')



# Register models to admin site

# admin.site.register(CustomUser)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Theater, TheaterAdmin)
admin.site.register(Show, ShowAdmin)
admin.site.register(Seat, SeatAdmin)
admin.site.register(Booking, BookingAdmin)

