from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.utils import timezone

from functools import wraps
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
import json
import random

from twilio.rest import Client
import google.generativeai as genai


from .models import PostedJobs  
from django.http import JsonResponse
import json
import google.generativeai as genai

from django.conf import settings
import google.generativeai as genai



# views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import pdfplumber
import docx


from . import models
from .models import (
    Company,
    FreelancerLogin,
    ClientLogin,
    FreelancerInfo,
    ClientInfo,
    PostedJobs,
    AppliedJobs,
    Chat,
    Feedback,
)
from .forms import (
    FreelancerForm,
    ClientForm,
    FreelancerInfoForm,
    ClientInfoForm,
    PostedJobsForm,
    FeedbackForm,
)




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
    feedbacks = Feedback.objects.all().order_by('-rating', '-created_at')[:3]
    return render(request, "index.html", {
        "feedbacks": feedbacks,
        "stars_range": range(1, 6), 
    })





def role(request):
    return render(request, 'role.html')




def freelancer_Signup(request):
    if request.method == 'POST':
        form = FreelancerForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email'].lower().strip()


            if FreelancerLogin.objects.filter(email=email).exists():
                messages.error(request, "Email already exists!")
                return redirect('freelancer_Signup')


            freelancer = form.save(commit=False)
            freelancer.password = make_password(form.cleaned_data['password'])
            freelancer.save()

            messages.success(request, "Account created successfully! Please wait for admin approval.")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('freelancer_Signup')
    else:
        form = FreelancerForm()
    return render(request, 'freelancer_signup.html', {'form': form})






def client_Signup(request):
    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email'].lower().strip()

            if ClientLogin.objects.filter(email=email).exists():
                messages.error(request, "Email already exists!")
                return redirect('client_Signup')

            client = form.save(commit=False)
            client.password = make_password(form.cleaned_data['password'])
            client.save()

            messages.success(request, "Account created successfully! Please wait for admin approval.")
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('client_Signup')
    else:
        form = ClientForm()
    return render(request, 'client_signup.html', {'form': form})


def login(request):
    if request.method == "POST":
        email = request.POST.get("email").lower().strip()
        password = request.POST.get("password")

        request.session.flush()  

        freelancer = FreelancerLogin.objects.filter(email=email).first()
        if freelancer and check_password(password, freelancer.password):
            if not freelancer.is_approved:
                messages.error(request, "Your account is pending approval by admin.")
                return redirect("login")
            request.session['user_type'] = "freelancer"
            request.session['user_id'] = freelancer.id
            request.session['user_name'] = f"{freelancer.first_name} {freelancer.last_name}"
            return redirect("freelancerHome")

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


    posted_jobs = PostedJobs.objects.select_related('client').all()


    if search_query:
        posted_jobs = posted_jobs.filter(title__icontains=search_query)


    if tech_sort:
        posted_jobs = posted_jobs.filter(tech_stack__iexact=tech_sort)

    # Sort by pay
    if pay_sort == "low-high":
        posted_jobs = posted_jobs.order_by("pay_per_hour")
    elif pay_sort == "high-low":
        posted_jobs = posted_jobs.order_by("-pay_per_hour")
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
            "company_name": client_info.company_name if client_info else "",
            "company_url": client_info.company_url if client_info else "",
        })

    # -------------------------------
    # Get all companies that have posted jobs
    # -------------------------------
    client_ids_with_jobs = posted_jobs.values_list('client_id', flat=True).distinct()
    companies = ClientInfo.objects.filter(client_id__in=client_ids_with_jobs).values(
        'company_name', 'company_url'
    ).distinct()
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
        "companies": companies,   # <-- add this for Companies button/section
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
def client_profile_setup(request):
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




@login_required_custom(user_type="client")
def post_job(request, client_id):
    client = get_object_or_404(ClientLogin, id=client_id)
    error_message = None
    form_data = {}

    # Get all companies to show in the form dropdown
    companies = Company.objects.all()

    if request.method == "POST":
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        pay_per_hour_str = request.POST.get('pay_per_hour', '').strip()
        tech_stack = request.POST.get('tech_stack', '').strip()
        requirements = request.POST.get('requirements', '').strip()
        job_image = request.FILES.get('job_image')  # uploaded image

        form_data = {
            'title': title,
            'description': description,
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
            return render(request, "postJob.html", {
                "client": client, "error": error_message,
                "form_data": form_data, "companies": companies
            })

        # Check all required fields
        if not all([title, description, tech_stack, requirements]):
            error_message = "All fields are required."
            return render(request, "postJob.html", {
                "client": client, "error": error_message,
                "form_data": form_data, "companies": companies
            })

        # Save the job
        job = PostedJobs.objects.create(
            client=client,
            title=title,
            description=description,
            pay_per_hour=pay_per_hour,
            tech_stack=tech_stack,
            requirements=requirements,
            job_image=job_image
        )

        messages.success(request, "Job posted successfully!")
        return redirect('client_posted_jobs')  # Redirect to your posted jobs page

    # GET request
    return render(request, "postJob.html", {
        "client": client, "form_data": form_data, "companies": companies
    })

    

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




from .models import Notification  # make sure to import your Notification model

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

    # 🔔 Create notification for the client
    Notification.objects.create(
        client=job.client,
        freelancer=freelancer,
        job=job,
        message=f"{freelancer.first_name} {freelancer.last_name} applied for your job '{job.title}'."
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

    # Allowed statuses
    valid_statuses = ["Hired", "Rejected", "Verified", "Shortlisted", "Interview"]

    if status in valid_statuses:
        applied_job.status = status
        applied_job.save()

        # Get freelancer and client info
        freelancer = applied_job.freelancer
        client = applied_job.job.client
        job = applied_job.job

        # Prepare email details
        subject = ""
        message = ""

        if status == "Hired":
            subject = f"Congratulations {freelancer.first_name}, You are Hired!"
            message = (
                f"Dear {freelancer.first_name},\n\n"
                f"🎉 Congratulations! You have been hired for the job '{job.title}'.\n\n"
                f"Client: {client.first_name} {client.last_name}\n"
                f"Job Description: {job.description}\n"
                f"Pay Per Hour: ₹{job.pay_per_hour}\n\n"
                f"The client will contact you soon with further details.\n\n"
                f"Best of Luck!\nSkillConnect Team"
            )

        elif status == "Rejected":
            subject = f"Application Update for {job.title}"
            message = (
                f"Dear {freelancer.first_name},\n\n"
                f"We appreciate your interest in the job '{job.title}'.\n"
                f"Unfortunately, you were not selected this time.\n\n"
                f"Don't be discouraged — keep applying to more opportunities on SkillConnect.\n\n"
                f"Best Wishes,\nSkillConnect Team"
            )

        elif status == "Verified":
            subject = f"Application Verified for {job.title}"
            message = (
                f"Dear {freelancer.first_name},\n\n"
                f"✅ Your application for the job '{job.title}' has been verified successfully.\n\n"
                f"The client {client.first_name} {client.last_name} will review your profile soon.\n\n"
                f"Stay tuned for further updates!\n\n"
                f"Best,\nSkillConnect Team"
            )

        elif status == "Shortlisted":
            subject = f"You Have Been Shortlisted for {job.title}"
            message = (
                f"Dear {freelancer.first_name},\n\n"
                f"📌 Congratulations! You have been shortlisted for the job '{job.title}'.\n\n"
                f"Client: {client.first_name} {client.last_name}\n"
                f"Next steps will be communicated to you soon.\n\n"
                f"Good Luck!\nSkillConnect Team"
            )

        elif status == "Interview":
            subject = f"Interview Scheduled for {job.title}"
            message = (
                f"Dear {freelancer.first_name},\n\n"
                f"🎤 Great news! You have been invited for an interview for the job '{job.title}'.\n\n"
                f"Client: {client.first_name} {client.last_name}\n"
                f"Please check your messages for scheduling details.\n\n"
                f"Best of Luck!\nSkillConnect Team"
            )

        # Send email
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,  # from email
                [freelancer.email],        # to email
                fail_silently=False,
            )
            messages.success(request, f"Email sent to {freelancer.first_name} ({status}).")
        except Exception as e:
            messages.error(request, f"Status updated but email not sent. Error: {str(e)}")

        messages.success(request, f"{freelancer.first_name} marked as {status}.")

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

    messages = Chat.objects.filter(
        (Q(sender_type=user_type, sender_id=user_id, receiver_type=receiver_type, receiver_id=receiver_id) |
         Q(sender_type=receiver_type, sender_id=receiver_id, receiver_type=user_type, receiver_id=user_id))
    ).order_by("timestamp")

    # Preprocess file type
    for msg in messages:
        msg.file_type = None
        if msg.file:
            file_url = msg.file.url.lower()
            if file_url.endswith(".mp4"):
                msg.file_type = "video"
            elif file_url.endswith(".jpg") or file_url.endswith(".jpeg") or file_url.endswith(".png"):
                msg.file_type = "image"
            else:
                msg.file_type = "other"

    return render(request, "chat.html", {
        "messages": messages,
        "receiver_type": receiver_type,
        "receiver_id": receiver_id,
        "receiver_name": "Receiver",  # pass actual name here
        "receiver_profile_pic": "/static/images/default.png",  # pass actual pic here
        "user_type": user_type,
    })



@csrf_exempt
def send_chat_ajax(request):
    if request.method == "POST":
        sender_type = request.session.get("user_type")  # 'client' or 'freelancer'
        sender_id = request.session.get("user_id")
        receiver_type = request.POST.get("receiver_type")
        receiver_id = request.POST.get("receiver_id")
        message = request.POST.get("message", "").strip()
        file = request.FILES.get("file")

        if not sender_type or not sender_id:
            return JsonResponse({"error": "Not logged in"}, status=403)

        chat = Chat.objects.create(
            sender_type=sender_type,
            sender_id=sender_id,
            receiver_type=receiver_type,
            receiver_id=receiver_id,
            message=message if message else None,
            file=file,
            timestamp=timezone.now()
        )

        return JsonResponse({
            "status": "success",
            "id": chat.id,
            "message": chat.message,
            "file": chat.file.url if chat.file else None,
            "timestamp": chat.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "sender_type": chat.sender_type
        })
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


@login_required_custom(user_type="client")
def client_posted_jobs(request):
    client_id = request.session.get("user_id")
    if not client_id:
        return redirect("login")

    client = get_object_or_404(ClientLogin, id=client_id)
    jobs = PostedJobs.objects.filter(client=client)  # use PostedJobs model

    context = {
        "jobs": jobs,
        "client": client, 
    }
    return render(request, "client_posted_jobs.html", context)




def delete_posted_job(request, job_id):
    client_id = request.session.get("user_id")
    job = get_object_or_404(PostedJobs, id=job_id, client_id=client_id)
    job.delete()
    return redirect("client_posted_jobs")

@login_required_custom(user_type="client")
def edit_posted_job(request, job_id):
    job = get_object_or_404(PostedJobs, id=job_id)

    if request.method == "POST":
        job.title = request.POST.get("title", job.title)
        job.description = request.POST.get("description", job.description)
        job.tech_stack = request.POST.get("tech_stack", job.tech_stack)
        job.pay_per_hour = request.POST.get("pay_per_hour", job.pay_per_hour)
        job.requirements = request.POST.get("requirements", job.requirements)
        job.save()

        return redirect("client_posted_jobs")

    return render(request, "edit_posted_job.html", {"job": job})

@login_required_custom(user_type="client")
def give_feedback(request):
    client_id = request.session.get("user_id")
    client_type = request.session.get("user_type")
    if not client_id or client_type != "client":
        return redirect('login')

    client = get_object_or_404(ClientLogin, id=client_id)
    client_info = ClientInfo.objects.filter(client=client).first()

    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.client = client
            feedback.client_name = f"{client.first_name} {client.last_name}"
            if client_info and client_info.profile_picture:
                feedback.client_profile_pic = client_info.profile_picture
            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('clientHome')
    else:
        form = FeedbackForm()

    return render(request, "feedback_form.html", {"form": form})


def notifications_view(request):
    client_id = request.session.get("user_id")
    client = get_object_or_404(ClientLogin, id=client_id)

    # Get latest notifications for this client
    notifications = Notification.objects.filter(client=client).order_by("-created_at")

    return render(request, "client_notifications.html", {
        "notifications": notifications
    })




@login_required_custom(user_type="client")
def client_overview(request):
    client_id = request.session.get("user_id")
    client = get_object_or_404(ClientLogin, id=client_id)
    client_info = ClientInfo.objects.filter(client=client).first()  # ✅ fetch profile info

    total_jobs = PostedJobs.objects.filter(client=client).count()
    active_jobs = PostedJobs.objects.filter(client=client, is_active=True).count()
    proposals = AppliedJobs.objects.filter(job__client=client).count()
    hires = AppliedJobs.objects.filter(job__client=client, status="Hired").count()

    # Percentages
    total_jobs_percent = 100
    active_jobs_percent = (active_jobs / total_jobs) * 100 if total_jobs else 0
    proposals_percent = (proposals / total_jobs) * 100 if total_jobs else 0
    hires_percent = (hires / proposals) * 100 if proposals else 0

    context = {
        "client": client,
        "client_info": client_info,   # ✅ pass to template
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "proposals": proposals,
        "hires": hires,
        "total_jobs_percent": total_jobs_percent,
        "active_jobs_percent": active_jobs_percent,
        "proposals_percent": proposals_percent,
        "hires_percent": hires_percent,
    }

    return render(request, "client_overview.html", context)
def companies_page(request):
    # Fetch all companies
    companies = ClientInfo.objects.exclude(company_name__isnull=True).exclude(company_name__exact='')
    context = {
        'companies': companies
    }
    return render(request, 'companies.html', context)


def ai_tools(request):
    return render(request, 'aitools.html')





from .models import PostedJobs  # adjust this to your job model

def job_recommendations(request):
    try:
        jobs = PostedJobs.objects.all()[:5]  # fetch the latest 5 jobs
        job_list = [
            {"title": job.title, "description": job.description[:120] + "..."}
            for job in jobs
        ]
        return JsonResponse({"recommended_jobs": job_list})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)




try:
    from django.views.decorators.csrf import csrf_exempt
except Exception:
    def csrf_exempt(view_func):
        return view_func




genai.configure(api_key=settings.GEMINI_API_KEY)


@csrf_exempt
def generate_interview_questions(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            job_description = body.get("job_description", "").strip()

            if not job_description:
                return JsonResponse({"error": "Job description is required"}, status=400)

            # Use supported Gemini model
            model = genai.GenerativeModel("gemini-2.5-flash")  # ✅ Updated model

            # Generate content
            response = model.generate_content(
                f"Generate 10 interview questions for the following job description:\n\n{job_description}"
            )

            # Extract questions
            questions = response.text.split("\n")
            questions = [q.strip("-• ").strip() for q in questions if q.strip()]

            return JsonResponse({"questions": questions})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=405)




genai.configure(api_key=settings.GEMINI_API_KEY)

def extract_text(file):
    name = file.name.lower()
    if name.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    elif name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return file.read().decode("utf-8", errors="ignore")

@csrf_exempt
def analyze_resume(request):
    if request.method == "POST":
        resume_file = request.FILES.get("resume")
        if not resume_file:
            return JsonResponse({"error": "No resume uploaded"}, status=400)

        try:
            content = extract_text(resume_file)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(
                f"Analyze this resume and provide ATS score, keyword match, highlighted skills, and optimization tips:\n\n{content}"
            )

            return JsonResponse({
                "resume_name": resume_file.name,
                "analysis": response.text
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=405)



def help_support(request):
    context = {}
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        query = request.POST.get('query')

        if name and email and query:
            subject = f"Support Request from {name}"
            message = f"Name: {name}\nEmail: {email}\n\nQuery:\n{query}"
            recipient_list = ['nikhillanje555@gmail.com']  # You can also send to another support email

            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    recipient_list,
                    fail_silently=False,
                )
                context['success'] = "✅ Your query has been sent successfully!"
            except Exception as e:
                context['error'] = f"⚠️ Failed to send query. Error: {e}"
        else:
            context['error'] = "⚠️ All fields are required."

    return render(request, "help_support.html", context)




from django.http import HttpResponse
from django.db import connections

def db_check(request):
    try:
        connections['default'].cursor()
        return HttpResponse("✅ Database connected successfully!")
    except Exception as e:
        return HttpResponse(f"❌ Database connection failed: {e}")
