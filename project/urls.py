"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app1 import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('customer_signup/',views.customer_signup,name='customer_signup'),
    path('movie_details/<int:movie_id>/',views.movie_details,name='movie_details'),
    path('signin/',views.signin,name='signin'),
    path('signout/',views.signout,name='signout'),
    path('show_booking/<int:movie_id>/book/',views.show_booking, name='show_booking'),
    path('seat_booking/<int:show_id>/seats/', views.seat_booking, name='seat_booking'),
    path('booking/confirmation/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('pay/<int:id>/',views.pay,name='pay'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-failure/', views.payment_failure, name='payment_failure'),
    path('search/', views.search, name='search'),
    path('profile/<int:id>/', views.profile_view, name='profile'),
    path('booking_history/', views.booking_history, name='booking_history'),
    path('clear_booking_history/', views.clear_booking_history, name='clear_booking_history'),
     path('test-email/', views.test_email, name='test_email'),
    

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

