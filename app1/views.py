from pyexpat.errors import messages
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from .models import CustomUser,CustomerProfile,Movie,Theater,Show,Seat,Booking
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomerCreationForm
from django.contrib.auth import login,logout
from django.utils.timezone import now
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required
import razorpay
from django.http import HttpResponse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import os

from app1 import models

# Create your views here.
def index(request):
    movies = Movie.objects.all()
    return render(request, 'index.html', {'movies': movies})

def movie_details(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    context = {
        'movie': movie,
    }
    return render(request, 'movie_details.html', {'movie': movie})

def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request,data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('index')
        else:
            return render(request,"signin.html",{'form':form})

    else:
        form = AuthenticationForm()
    return render(request,"signin.html",{'form':form})


def customer_signup(request):
    if request.method == 'POST':
        form = CustomerCreationForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
            return redirect('index')
        else:
            error = "Something went wrong"
            return render(request,'customer_signup.html',{'error':error,'form':form})

    else:
        form = CustomerCreationForm()
    return render(request,"customer_signup.html",{'form':form})


def signout(request):
    logout(request)
    return redirect('index')


def show_booking(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(show__movie=movie).distinct()
    shows = Show.objects.filter(movie=movie)
    return render(request, 'show_booking.html', {
        'movie': movie,
        'theaters': theaters,
        'shows': shows,
    })


@login_required
def seat_booking(request, show_id):
    show = get_object_or_404(Show, id=show_id)
    seats = Seat.objects.filter(show=show).order_by('seat_number')
    booking = None
    regular = 200  # Price for available seats
    premium = 400

    if request.method == 'POST':
        selected_seat_ids = request.POST.get('selected_seats', '')

        try:
            # Parse seat IDs and filter available seats
            seat_ids = list(map(int, filter(None, selected_seat_ids.split(','))))
            selected_seats = Seat.objects.filter(id__in=seat_ids, status=True)

            # Validate seat availability
            if len(selected_seats) != len(seat_ids):
                messages.error(request, "Some selected seats are no longer available.")
                return redirect('seat_booking', show_id=show.id)

            # Calculate total amount
            total_amount = sum(200 if seat.seat_class == 'Regular' else 400 for seat in selected_seats)

            # Create booking and update seats
            booking = Booking.objects.create(user=request.user, show=show, total_amount=total_amount)
            selected_seats.update(status=False, booking=booking)

            messages.success(request, "Booking confirmed!")
            return render(request, 'seat_booking.html',{'show': show, 'seats': seats, 'booking': booking, 'regular': regular, 'premium': premium,})

        except (ValueError, TypeError):
            messages.error(request, "Invalid seat selection. Please try again.")
            return redirect('seat_booking', show_id=show.id)

    return render(request, 'seat_booking.html', {'show': show, 'seats': seats, 'booking': booking, 'regular': regular, 'premium': premium,})
@login_required
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    seats = Seat.objects.filter(booking=booking)
    total_amount = booking.total_amount
    show = booking.show  # Get the show from the booking

    context = {
        'booking': booking,
        'seats': seats,
        'total_amount': total_amount,
        'show': show,  # Pass the show to the context
    }

    return render(request, 'confirm_booking.html', context)

    #     except Booking.DoesNotExist:
    #         messages.error(request, "Booking not found.")
    #         return redirect('booking_history')  # Redirect to a booking history page or another relevant page
    # else:
    #     return redirect('signin')

@login_required
def pay(request, id):
    booking = get_object_or_404(Booking, id=id, user=request.user)
    seats = Seat.objects.filter(booking=booking)
    total_amount = booking.total_amount

    client = razorpay.Client(auth=("rzp_test_n0lhpmrEfeIhGJ", "UOrbXQGnsEc2dhB1IFg0zNWZ"))
    data = {"amount": int(total_amount * 100), "currency": "INR", "receipt": str(booking.id)}
    payment = client.order.create(data=data)

    context = {
        'booking': booking,
        'seats': seats,
        'total_amount': total_amount,
        'payment': payment,
    }

    return render(request, 'pay.html', context)

    return render(request, 'pay.html', {'booking': booking, 'total_amount': total_amount})
    
@login_required
def payment_success(request):
    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('order_id')
    
    # Assuming you have a way to get the booking from the order_id
    booking = get_object_or_404(Booking, id=order_id, user=request.user)
    show = booking.show
    theater = show.theater
    movie = show.movie
    # seats = booking.seats.all()  # Assuming you have a related_name 'seats' in your Booking model

    send_payment_success_email(request.user.email, booking)

    context = {
        'payment_id': payment_id,
        'order_id': order_id,
        'booking': booking,
        'show': show,
        'theater': theater,
        'movie': movie,
        # 'seats': seats,
    }
    return render(request, 'payment_success.html', context)

@login_required
def payment_failure(request):
    return HttpResponse("Payment failed. Please try again.")

@login_required
def search(request):
    query = request.GET.get('q')
    movies = Movie.objects.none()

    if query is not None:
        genre = Movie.objects.filter(genre__icontains=query)
        title = Movie.objects.filter(title__icontains=query)
        movies = genre | title

    context = {
        'movies': movies,
        'query': query
    }
    return render(request, "index.html", context)

@login_required
def profile_view(request, id):
    user = get_object_or_404(CustomUser, id=id)
    profile = get_object_or_404(CustomerProfile, id=user.id)

    bookings = Booking.objects.filter(user=user).order_by('-booking_date')
    last_booking_date = bookings.first().booking_date if bookings.exists() else None
    total_bookings = bookings.count()
    total_spend = bookings.aggregate(total=Sum('total_amount'))['total'] or 0.00
    
    context = {
        'user': user,
        'profile': profile,
        'last_booking_date': last_booking_date,
        'total_bookings': total_bookings,
        'total_spend': total_spend
    }
    return render(request, 'profile_view.html', context)


@login_required
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    context = {
        'bookings': bookings
    }
    return render(request, 'booking_history.html', context)

@login_required
def clear_booking_history(request):
    if request.method == 'POST':
        Booking.objects.filter(user=request.user).delete()
        return redirect('booking_history')
    return redirect('booking_history')

def send_payment_success_email(user_email, booking):
    subject = 'Your Payment Confirmation'
    message = render_to_string('payment_success_email.html', {
        'booking': booking,
    })

    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
    )
    email.content_subtype = "html"  # Set the email content type to HTML

    # File path to the image in the media folder
    image_path = os.path.join(settings.MEDIA_ROOT, 'images/sample_image.jpg')
    
    # Check if the file exists and attach it to the email
    if os.path.exists(image_path):
        email.attach_file(image_path)
    
    email.send()

def test_email(request):
    # Create a mock booking object for testing
    movie = Movie(title="Test Movie", genre="Action", language="English", duration=120, rating=4.5, release_date="2025-01-01", description="Test description", image="path/to/image.jpg")
    theater = Theater(name="Test Theater", location="Test Location", capacity=100)
    show = Show(movie=movie, theater=theater, date="2025-01-01", time="18:00")
    booking = Booking(id=1, show=show, user=request.user, total_amount=500)

    # Render the email template with the mock booking object
    message = render_to_string('payment_success_email.html', {
        'booking': booking,
    })

    # Send the email
    email = EmailMessage(
        'Test Payment Confirmation',
        message,
        settings.DEFAULT_FROM_EMAIL,
        ['romanrohan91@gmail.com'],  # Replace with the recipient's email address
    )
    email.content_subtype = "html"  # Set the email content type to HTML
    email.send()

    return HttpResponse('Test email sent successfully.')



