from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from .models import FreelancerLogin, ClientLogin, FreelancerInfo , ClientInfo
from .forms import FreelancerForm, ClientForm, FreelancerInfoForm , ClientInfoForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from functools import wraps
from django.shortcuts import redirect
from django.shortcuts import redirect
from django.contrib import messages
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from twilio.rest import Client
from datetime import datetime, timedelta


def login_required_custom(user_type=None):
    """
    Custom login decorator for session-based login.
    If user_type is "freelancer" or "client", it also checks the type.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if 'user_id' not in request.session:
                return redirect('login')
            if user_type and request.session.get('user_type') != user_type:
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator







def index(request):
    return render(request, 'index.html')

def role(request):
    return render(request, 'role.html')


def freelancer_Signup(request):
    if request.method == 'POST':
        form = FreelancerForm(request.POST, request.FILES)

        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if email already exists
            if FreelancerLogin.objects.filter(email=email).exists():
                messages.error(request, "Email already exists!")
                return redirect('freelancer_Signup')  # redirect instead of render

            # Save freelancer with hashed password
            freelancer = form.save(commit=False)
            freelancer.password = make_password(form.cleaned_data['password'])
            freelancer.save()

            messages.success(request, "Account created successfully! Please Wait For Admin Approval.")
            return redirect('login')

        else:
            # Invalid form
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('freelancer_Signup')  # redirect

    else:
        form = FreelancerForm()

    return render(request, 'freelancer_signup.html', {'form': form})





def client_Signup(request):
    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES)

        if form.is_valid():
            email = form.cleaned_data['email']

            # Check if email already exists
            if ClientLogin.objects.filter(email=email).exists():
                messages.error(request, "Email already exists!")
                return redirect('client_Signup')  # ✅ redirect instead of render

            # Save client with hashed password
            client = form.save(commit=False)
            client.password = make_password(form.cleaned_data['password'])
            client.save()

            messages.success(request, "Account created successfully! Please Wait For Admin Approval.")
            return redirect('login')  # ✅ redirect to login page

        else:
            # Invalid form → show field-specific errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('client_Signup')  # ✅ redirect instead of render

    else:
        # GET request → empty form
        form = ClientForm()

    return render(request, 'client_signup.html', {'form': form})







def login(request):
    if request.method == "POST":
        email = request.POST.get("email").lower().strip()
        password = request.POST.get("password")

        # Check Freelancer
        freelancer = FreelancerLogin.objects.filter(email=email).first()
        if freelancer and check_password(password, freelancer.password):
            if not freelancer.is_approved:
                messages.error(request, "Your account is pending approval by admin.")
                return redirect("login")
            request.session['user_type'] = "freelancer"
            request.session['user_id'] = freelancer.id
            request.session['user_name'] = f"{freelancer.first_name} {freelancer.last_name}"
            return redirect("freelancerHome")

        # Check Client
        client = ClientLogin.objects.filter(email=email).first()
        if client and check_password(password, client.password):
            if not client.is_approved:
                messages.error(request, "Your account is pending approval by admin.")
                return redirect("login")
            request.session['user_type'] = "client"
            request.session['user_id'] = client.id
            request.session['user_name'] = f"{client.first_name} {client.last_name}"
            return redirect("clientHome")

        messages.error(request, "Invalid Email or Password")
        return redirect("login")

    return render(request, "login.html")



@login_required_custom(user_type="freelancer")
def freelancer_home(request):
    user_name = request.session.get("user_name", "Freelancer")
    user_id = request.session.get("user_id")

    freelancer_login = get_object_or_404(FreelancerLogin, id=user_id)
    
    # Use .first() to avoid 404 if FreelancerInfo does not exist
    freelancer_info = FreelancerInfo.objects.filter(freelancer=freelancer_login).first()

    if not freelancer_info:
        return redirect("freelancer_profile_setup")

        # Option 2: Or pass None to template and handle it there
        # freelancer_info = None

    return render(request, "freelancer_home.html", {
        "name": user_name,
        "user_id": user_id,
        "freelancer": freelancer_login,
        "freelancer_info": freelancer_info,
    })





@login_required_custom(user_type="client")
def client_home(request):
    client_id = request.session.get("user_id")
    client_name = request.session.get("user_name", "Client")

    if not client_id:
        return redirect("login")

    client_login = get_object_or_404(ClientLogin, id=client_id)

    # Use .first() to avoid 404 if ClientInfo does not exist
    client_info = ClientInfo.objects.filter(client=client_login).first()

    if not client_info:
        return redirect("client_profile_setup")  # redirect to setup page if no info

    return render(request, "client_home.html", {
        "client": client_login,
        "client_info": client_info,
        "client_id": client_id,
        "client_name": client_name
    })





def user_logout(request):
    request.session.flush()
    return redirect("login")



@login_required_custom(user_type="freelancer")
def freelancer_profile(request, freelancer_id):
    freelancer = get_object_or_404(FreelancerLogin, id=freelancer_id)
    profile, created = FreelancerInfo.objects.get_or_create(freelancer=freelancer)

    if request.method == "POST":
        form = FreelancerInfoForm(request.POST, request.FILES, instance=profile)  # include request.FILES
        if form.is_valid():
            profile = form.save(commit=False)
            profile.freelancer = freelancer
            profile.save()
            return redirect('freelancer_profile', freelancer_id=freelancer.id)
    else:
        form = FreelancerInfoForm(instance=profile)

    return render(request, 'freelancer_profile.html', {
        'freelancer': freelancer,
        'form': form,
        'profile': profile   # pass profile so template can show picture
    })




@login_required_custom(user_type="client")
def client_profile(request, client_id):
    client = get_object_or_404(ClientLogin, id=client_id)
    profile, created = ClientInfo.objects.get_or_create(client=client)

    if request.method == "POST":
        form = ClientInfoForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.client = client
            profile.save()
            return redirect('client_profile', client_id=client.id)
    else:
        form = ClientInfoForm(instance=profile)

    return render(request, 'client_profile.html', {
        'client': client,
        'profile': profile,   
        'form': form,
    })





@login_required_custom(user_type="freelancer")
def freelancer_profile_setup(request):
    # Redirect the logged-in freelancer to their profile edit page
    freelancer_id = request.session.get('user_id')
    if not freelancer_id:
        return redirect('login')
    return redirect('freelancer_profile', freelancer_id=freelancer_id)



@login_required_custom(user_type="client")
def client_profile_setup(request):
    # Redirect the logged-in client to their profile edit page
    client_id = request.session.get('user_id')
    if not client_id:
        return redirect('login')
    return redirect('client_profile', client_id=client_id)


@login_required_custom()
def update_profile_picture(request):
    if request.method == "POST" and request.FILES.get('profile_picture'):
        user_type = request.session.get('user_type')  # 'client' or 'freelancer'
        user_id = request.session.get('user_id')

        if not user_id or not user_type:
            messages.error(request, "You must be logged in to update profile picture.")
            return redirect('login')

        # Handle profile update based on user type
        if user_type == "client":
            profile = get_object_or_404(ClientInfo, client_id=user_id)
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            return redirect('client_profile', client_id=user_id)

        elif user_type == "freelancer":
            profile = get_object_or_404(FreelancerInfo, freelancer_id=user_id)
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            return redirect('freelancer_profile', freelancer_id=user_id)

    # Default fallback
    return redirect('login')



# Temporary OTP storage
OTP_STORE = {}

@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        phone = data.get("phone", "").strip()

        if len(phone) != 10 or not phone.isdigit():
            return JsonResponse({"success": False, "message": "Enter a valid 10-digit mobile number."})

        # Check if number exists in FreelancerLogin
        if not FreelancerLogin.objects.filter(mobile_number=phone).exists():
            return JsonResponse({"success": False, "message": "This mobile number is not registered."})

        phone_full = "+91" + phone

        # Generate 4-digit OTP
        otp = str(random.randint(1000, 9999))
        OTP_STORE[phone_full] = otp

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f"Your SkillConnect OTP is: {otp}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_full
            )
            return JsonResponse({"success": True, "message": f"OTP sent to {phone_full[-4:]}****"})
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Failed to send OTP: {str(e)}"})






@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        phone = data.get("phone", "").strip()
        entered_otp = data.get("otp", "").strip()

        phone_full = "+91" + phone

        if OTP_STORE.get(phone_full) == entered_otp:
            OTP_STORE.pop(phone_full)
            request.session["otp_verified"] = True
            request.session["verified_phone"] = phone_full
            return JsonResponse({"success": True, "message": "OTP verified successfully!"})
        else:
            return JsonResponse({"success": False, "message": "Invalid OTP"})

