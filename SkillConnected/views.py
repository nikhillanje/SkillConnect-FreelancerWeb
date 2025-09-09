from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import make_password, check_password
from .models import FreelancerLogin, ClientLogin, FreelancerInfo , ClientInfo,PostedJobs ,AppliedJobs, Chat
from .forms import FreelancerForm, ClientForm, FreelancerInfoForm , ClientInfoForm,PostedJobsForm  
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from functools import wraps
from django.shortcuts import redirect
from django.shortcuts import redirect
from decimal import Decimal, InvalidOperation
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import random
import json
from django.shortcuts import render, get_object_or_404
from .models import Chat, ClientLogin, FreelancerLogin
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from twilio.rest import Client
from datetime import datetime, timedelta
from django.utils import timezone


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
                return redirect('client_Signup')  # redirect instead of render

            # Save client with hashed password
            client = form.save(commit=False)
            client.password = make_password(form.cleaned_data['password'])
            client.save()

            messages.success(request, "Account created successfully! Please Wait For Admin Approval.")
            return redirect('login')  # redirect to login page

        else:
            # Invalid form → show field-specific errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('client_Signup')  # redirect instead of render

    else:
        # GET request → empty form
        form = ClientForm()

    return render(request, 'client_signup.html', {'form': form})





def login(request):
    if request.method == "POST":
        email = request.POST.get("email").lower().strip()
        password = request.POST.get("password")

        # Always clear old session before new login
        request.session.flush()

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
    
    freelancer_info = FreelancerInfo.objects.filter(freelancer=freelancer_login).first()
    if not freelancer_info:
        return redirect("freelancer_profile_setup")

    # Get search and sort parameters
    search_query = request.GET.get("search", "")
    pay_sort = request.GET.get("paySort", "")
    tech_sort = request.GET.get("techSort", "")

    # Get all posted jobs (with client relation for efficiency)
    posted_jobs = PostedJobs.objects.select_related('client').all()

    # Filter by search query (job title)
    if search_query:
        posted_jobs = posted_jobs.filter(title__icontains=search_query)

    # Filter by tech stack (assuming PostedJobs has a 'tech_stack' field)
    if tech_sort:
        posted_jobs = posted_jobs.filter(tech_stack__iexact=tech_sort)

    # Sort by pay
    if pay_sort == "low-high":
        posted_jobs = posted_jobs.order_by("pay")
    elif pay_sort == "high-low":
        posted_jobs = posted_jobs.order_by("-pay")
    else:
        posted_jobs = posted_jobs.order_by("-created_at")  # default

    # Get job IDs that this freelancer already applied for
    applied_jobs = AppliedJobs.objects.filter(
        freelancer=freelancer_login
    ).values_list("job_id", flat=True)

    jobs_with_client_info = []
    for job in posted_jobs:
        client = job.client
        client_info = ClientInfo.objects.filter(client=client).first()

        jobs_with_client_info.append({
            "job": job,
            "client": client,
            "client_full_name": f"{client.first_name} {client.last_name}",
            "profile_picture": client_info.profile_picture if client_info else None,
            "client_name": client_info.company_name if client_info else "",
        })

    return render(request, "freelancer_home.html", {
        "name": user_name,
        "user_id": user_id,
        "freelancer": freelancer_login,
        "freelancer_info": freelancer_info,
        "jobs_with_client_info": jobs_with_client_info,
        "applied_jobs": applied_jobs,
        "search_query": search_query,
        "pay_sort": pay_sort,
        "tech_sort": tech_sort,
    })



@login_required_custom(user_type="freelancer")
def freelancer_job_detail(request, job_id):
    job = get_object_or_404(PostedJobs, id=job_id)
    client_info = getattr(job.client, 'clientinfo', None)

    freelancer_id = request.session.get('user_id')
    freelancer = get_object_or_404(FreelancerLogin, id=freelancer_id)

    # Check if already applied
    already_applied = AppliedJobs.objects.filter(job=job, freelancer=freelancer).exists()

    context = {
        'job': job,
        'client_info': client_info,
        'already_applied': already_applied,  # pass this to template
    }
    return render(request, "freelancer_job_detail.html", context)



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
def freelancer_profile_setup(request):
    # Redirect the logged-in freelancer to their profile edit page
    client_id = request.session.get('user_id')
    if not client_id:
        return redirect('login')
    return redirect('freelancer_profile_for_C', client_id=client_id)




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





import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def send_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            phone = data.get("phone", "").strip()
        except Exception:
            return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

        # Always accept request (skip Twilio + DB check for testing)
        return JsonResponse({"success": True, "message": f"OTP sent to ****{phone[-4:]} (test mode)"}, status=200)

    return JsonResponse({"success": False, "message": "Invalid method"}, status=405)


@csrf_exempt
def verify_otp(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            # phone = data.get("phone", "").strip()
            # otp = data.get("otp", "").strip()
        except Exception:
            return JsonResponse({"success": False, "message": "Invalid request"}, status=400)

        # Always accept OTP in test mode
        request.session["otp_verified"] = True
        return JsonResponse({"success": True, "message": "OTP verified (test mode)"}, status=200)

    return JsonResponse({"success": False, "message": "Invalid method"}, status=405)



# # Temporary OTP storage
# OTP_STORE = {}

# @csrf_exempt
# def send_otp(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body.decode("utf-8"))
#             phone = data.get("phone", "").strip()
#         except Exception:
#             return JsonResponse({"success": False, "message": "Invalid request format"}, status=400)

#         # Validate phone
#         if len(phone) != 10 or not phone.isdigit():
#             return JsonResponse({"success": False, "message": "Enter a valid 10-digit mobile number."}, status=400)

#         # Check if number exists
#         if not FreelancerLogin.objects.filter(mobile_number=phone).exists():
#             return JsonResponse({"success": False, "message": "This mobile number is not registered."}, status=404)

#         phone_full = "+91" + phone
#         otp = str(random.randint(1000, 9999))
#         OTP_STORE[phone_full] = otp

#         try:
#             client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#             client.messages.create(
#                 body=f"Your SkillConnect OTP is: {otp}",
#                 from_=settings.TWILIO_PHONE_NUMBER,
#                 to=phone_full
#             )
#             return JsonResponse({"success": True, "message": f"OTP sent to ****{phone[-4:]}"} , status=200)
#         except Exception as e:
#             # Fallback: still send JSON error, never HTML
#             return JsonResponse({"success": False, "message": f"Failed to send OTP: {str(e)}"}, status=500)

#     return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)


# @csrf_exempt
# def verify_otp(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body.decode("utf-8"))
#             phone = data.get("phone", "").strip()
#             entered_otp = data.get("otp", "").strip()
#         except Exception:
#             return JsonResponse({"success": False, "message": "Invalid request format"}, status=400)

#         phone_full = "+91" + phone

#         if OTP_STORE.get(phone_full) == entered_otp:
#             OTP_STORE.pop(phone_full)
#             request.session["otp_verified"] = True
#             request.session["verified_phone"] = phone_full
#             return JsonResponse({"success": True, "message": "OTP verified successfully!"}, status=200)
#         else:
#             return JsonResponse({"success": False, "message": "Invalid OTP"}, status=400)

#     return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)




@login_required_custom(user_type="client")
def post_job(request, client_id):
    client = get_object_or_404(ClientLogin, id=client_id)
    error_message = None
    form_data = {}  # to keep values in case of error

    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        pay_per_hour_str = request.POST.get('pay_per_hour', '').strip()
        tech_stack = request.POST.get('tech_stack', '').strip()
        requirements = request.POST.get('requirements', '').strip()

        # Keep data to refill form in case of error
        form_data = {
            'title': title,
            'description' : description,
            'pay_per_hour': pay_per_hour_str,
            'tech_stack': tech_stack,
            'requirements': requirements
        }

        # Validate pay_per_hour
        try:
            pay_per_hour = Decimal(pay_per_hour_str)
            if pay_per_hour < 0:
                raise InvalidOperation
        except (InvalidOperation, ValueError):
            error_message = "Pay per hour must be a valid positive number."
            return render(request, "postJob.html", {"client": client, "error": error_message, "form_data": form_data})

        # Check all fields
        if not all([title, description,tech_stack, requirements]):
            error_message = "All fields are required."
            return render(request, "postJob.html", {"client": client, "error": error_message, "form_data": form_data})

        # Save the job
        PostedJobs.objects.create(
            client=client,
            title=title,
            description=description,
            pay_per_hour=pay_per_hour,
            tech_stack=tech_stack,
            requirements=requirements
        )
        return redirect('clientHome')  # redirect after success

    # GET request
    return render(request, "postJob.html", {"client": client, "form_data": form_data})



@login_required_custom(user_type="freelancer")
def apply_job(request, job_id):
    # Ensure user is logged in as freelancer
    if 'user_type' not in request.session or request.session['user_type'] != "freelancer":
        messages.error(request, "Only freelancers can apply for jobs. Please login as a freelancer.")
        return redirect("login")

    freelancer_id = request.session.get("user_id")
    freelancer = get_object_or_404(FreelancerLogin, id=freelancer_id)

    job = get_object_or_404(PostedJobs, id=job_id)

    # Check if already applied
    if AppliedJobs.objects.filter(job=job, freelancer=freelancer).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect("freelancerHome")

    # Save new application
    AppliedJobs.objects.create(
        job=job,
        freelancer=freelancer,
        applied_at=timezone.now(),
        status="Pending"
    )

    messages.success(request, f"You have successfully applied for {job.title}.")
    return redirect("freelancerHome")



@login_required_custom(user_type="client")
def client_applied_jobs(request):
    client_id = request.session.get("user_id")
    client = get_object_or_404(ClientLogin, id=client_id)

    # Get all jobs posted by this client
    jobs = PostedJobs.objects.filter(client=client)

    # Get all applications for these jobs
    applied_jobs = AppliedJobs.objects.filter(job__in=jobs).select_related('freelancer', 'job').order_by('-applied_at')

    return render(request, "client_applied_jobs.html", {
        "applied_jobs": applied_jobs
    })


@login_required_custom(user_type="client")
def update_application_status(request, applied_job_id, status):
    applied_job = get_object_or_404(AppliedJobs, id=applied_job_id)
    
    # Only allow updating if the client owns the job
    if applied_job.job.client.id != request.session.get("user_id"):
        messages.error(request, "You are not allowed to update this application.")
        return redirect("client_applied_jobs")

    if status in ["Hired", "Rejected"]:
        applied_job.status = status
        applied_job.save()
        messages.success(request, f"{applied_job.freelancer.first_name} marked as {status}.")
    return redirect("client_applied_jobs")


@login_required_custom(user_type="freelancer")
def freelancer_notifications(request):
    freelancer_id = request.session.get("user_id")
    freelancer = get_object_or_404(FreelancerLogin, id=freelancer_id)

    # Get all jobs where freelancer was hired
    hired_jobs = AppliedJobs.objects.filter(
        freelancer=freelancer,
        status="Hired"
    ).select_related('job', 'job__client')

    return render(request, "freelancer_notifications.html", {
        "hired_jobs": hired_jobs
    })

@login_required_custom()
def chat_view(request, receiver_type, receiver_id):
    user_type = request.session.get("user_type")
    user_id = request.session.get("user_id")

    # Fetch messages
    messages = Chat.objects.filter(
        (Q(sender_id=user_id, sender_type=user_type, receiver_id=receiver_id, receiver_type=receiver_type) |
         Q(sender_id=receiver_id, sender_type=receiver_type, receiver_id=user_id, receiver_type=user_type))
    ).order_by("timestamp")

    # Determine receiver info dynamically
    if receiver_type == "client":
        receiver = get_object_or_404(ClientLogin, id=receiver_id)
        profile_pic = receiver.clientinfo.profile_picture.url if hasattr(receiver, 'clientinfo') and receiver.clientinfo.profile_picture else '/static/images/default_profile.png'
        name = f"{receiver.first_name} {receiver.last_name}"
    else:
        receiver = get_object_or_404(FreelancerLogin, id=receiver_id)
        profile_pic = receiver.freelancerinfo.profile_picture.url if hasattr(receiver, 'freelancerinfo') and receiver.freelancerinfo.profile_picture else '/static/images/default_profile.png'
        name = f"{receiver.first_name} {receiver.last_name}"

    return render(request, "chat.html", {
        "messages": messages,
        "receiver_type": receiver_type,
        "receiver_id": receiver_id,
        "user_type": user_type,
        "user_id": user_id,
        "receiver_name": name,
        "receiver_profile_pic": profile_pic
    })


@csrf_exempt
def send_chat_ajax(request):
    if request.method == "POST":
        sender_type = request.session.get("user_type")     # 'client' or 'freelancer'
        sender_id = request.session.get("user_id")
        receiver_type = request.POST.get("receiver_type")
        receiver_id = request.POST.get("receiver_id")
        message = request.POST.get("message")
        file = request.FILES.get("file")

        if not sender_type or not sender_id:
            return JsonResponse({"error": "Not logged in"}, status=403)

        chat = Chat.objects.create(
            sender_type=sender_type,
            sender_id=sender_id,
            receiver_type=receiver_type,
            receiver_id=receiver_id,
            message=message,
            file=file,
            timestamp=timezone.now()
        )
        return JsonResponse({"status": "success", "id": chat.id})
    return JsonResponse({"error": "Invalid request"}, status=400)

def fetch_chat_ajax(request, receiver_type, receiver_id):
    sender_type = request.session.get("user_type")
    sender_id = request.session.get("user_id")

    messages = Chat.objects.filter(
        (Q(sender_type=sender_type, sender_id=sender_id,
            receiver_type=receiver_type, receiver_id=receiver_id) |
         Q(sender_type=receiver_type, sender_id=receiver_id,
            receiver_type=sender_type, receiver_id=sender_id))
    ).order_by("timestamp")

    data = []
    for msg in messages:
        data.append({
            "id": msg.id,
            "sender_type": msg.sender_type,
            "message": msg.message,
            "file": msg.file.url if msg.file else None,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        })

    return JsonResponse({"messages": data})



# List of chats for client
@login_required_custom(user_type="client")
def client_chat_list(request):
    client_id = request.session.get("user_id")

    # Get all freelancers client has chatted with
    freelancer_ids = Chat.objects.filter(
        Q(sender_type='client', sender_id=client_id) |
        Q(receiver_type='client', receiver_id=client_id)
    ).values_list('sender_id', 'receiver_id')

    freelancer_ids_flat = set()
    for s_id, r_id in freelancer_ids:
        if s_id != client_id:
            freelancer_ids_flat.add(s_id)
        if r_id != client_id:
            freelancer_ids_flat.add(r_id)

    freelancers = FreelancerLogin.objects.filter(id__in=freelancer_ids_flat).select_related('freelancerinfo')

    return render(request, 'client_chat_list.html', {"freelancers": freelancers})



@login_required_custom(user_type="client")
def client_chat_view(request, freelancer_id):
    client_id = request.session.get("user_id")
    user_type = "client"

    # Fetch messages between this client and freelancer
    messages = Chat.objects.filter(
        (Q(sender_id=client_id, sender_type='client', receiver_id=freelancer_id, receiver_type='freelancer') |
         Q(sender_id=freelancer_id, sender_type='freelancer', receiver_id=client_id, receiver_type='client'))
    ).order_by("timestamp")

    freelancer = get_object_or_404(FreelancerLogin, id=freelancer_id)
    profile_pic = (
        freelancer.freelancerinfo.profile_picture.url
        if hasattr(freelancer, 'freelancerinfo') and freelancer.freelancerinfo.profile_picture
        else '/static/images/default_profile.png'
    )
    name = f"{freelancer.first_name} {freelancer.last_name}"

    return render(request, 'chat.html', {
        "messages": messages,
        "receiver_type": "freelancer",   # unified key
        "receiver_id": freelancer_id,    # unified key
        "user_type": user_type,
        "user_id": client_id,
        "receiver_name": name,
        "receiver_profile_pic": profile_pic
    })




@login_required_custom(user_type="freelancer")
def freelancer_chat_list(request):
    freelancer_id = request.session.get("user_id")

    # Get all clients freelancer has chatted with
    client_ids = Chat.objects.filter(
        Q(sender_type='freelancer', sender_id=freelancer_id) |
        Q(receiver_type='freelancer', receiver_id=freelancer_id)
    ).values_list('sender_id', 'receiver_id')

    client_ids_flat = set()
    for s_id, r_id in client_ids:
        if s_id != freelancer_id:
            client_ids_flat.add(s_id)
        if r_id != freelancer_id:
            client_ids_flat.add(r_id)

    clients = ClientLogin.objects.filter(id__in=client_ids_flat).select_related('clientinfo')

    return render(request, 'freelancer_chat_list.html', {"clients": clients})


@login_required_custom(user_type="freelancer")
def freelancer_chat_view(request, client_id):
    freelancer_id = request.session.get("user_id")
    user_type = "freelancer"

    # Fetch messages between this freelancer and client
    messages = Chat.objects.filter(
        (Q(sender_id=freelancer_id, sender_type='freelancer', receiver_id=client_id, receiver_type='client') |
         Q(sender_id=client_id, sender_type='client', receiver_id=freelancer_id, receiver_type='freelancer'))
    ).order_by("timestamp")

    client = get_object_or_404(ClientLogin, id=client_id)
    profile_pic = client.clientinfo.profile_picture.url if hasattr(client, 'clientinfo') and client.clientinfo.profile_picture else '/static/images/default_profile.png'
    name = f"{client.first_name} {client.last_name}"

    return render(request, 'chat.html', {
        "messages": messages,
        "receiver_type": "client",
        "receiver_id": client_id,
        "user_type": user_type,
        "user_id": freelancer_id,
        "receiver_name": name,
        "receiver_profile_pic": profile_pic
    })


def freelancer_profile_view(request, freelancer_id):
    freelancer = get_object_or_404(FreelancerLogin, id=freelancer_id)
    profile = get_object_or_404(FreelancerInfo, freelancer=freelancer)

    context = {
        "freelancer": freelancer,
        "profile": profile,
    }
    return render(request, "freelancer_profile_view.html", context)



def client_profile_view(request, client_id):
    client = get_object_or_404(ClientLogin, id=client_id)
    profile = get_object_or_404(ClientInfo, client=client)  #using client FK
    context = {
        'client': client,
        'profile': profile,
    }
    return render(request, 'client_profile_view.html', context)


def client_posted_jobs(request):
    client_id = request.session.get("user_id")
    if not client_id:
        return redirect("client_login")

    jobs = PostedJobs.objects.filter(client_id=client_id).order_by('-created_at')
    context = {"jobs": jobs}
    return render(request, "client_posted_jobs.html", context)


def delete_posted_job(request, job_id):
    client_id = request.session.get("user_id")
    job = get_object_or_404(PostedJobs, id=job_id, client_id=client_id)
    job.delete()
    return redirect("client_posted_jobs")