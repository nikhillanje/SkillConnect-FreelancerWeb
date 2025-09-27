from django.db import models
from django.utils.safestring import mark_safe 
from django.db import models
from django.db import models
from django.utils import timezone
from django.utils import timezone

class FreelancerLogin(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=10)
    fimage = models.ImageField(upload_to='freelancer_IDs/', null=True, blank=True)
    #for approval
    is_approved = models.BooleanField(default=False)



    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class ClientLogin(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=10)
    cimage = models.ImageField(upload_to='client_IDs/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    # Use string reference to avoid import issues
   # Instead of ForeignKey to Company, use fields directly:
    company_name = models.CharField(max_length=255, null=True, blank=True)
    company_url = models.URLField(max_length=500, null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    

class Images(models.Model):
    image = models.ImageField(upload_to='images')
    
    def __str__(self):
        return self.title

    class Meta:
        db_table = "images"



class FreelancerInfo(models.Model):
    freelancer = models.OneToOneField(FreelancerLogin, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    education = models.CharField(max_length=255, blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.freelancer.first_name}"
    
class Company(models.Model):
    company_name = models.CharField(max_length=255)
    company_url = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    def __str__(self):
        return self.company_name
    
class ClientInfo(models.Model):
    client = models.OneToOneField(ClientLogin, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    company_url = models.URLField(max_length=500, null=True, blank=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    budget = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)  # new field

    def __str__(self):
        return f"{self.client.first_name} {self.client.last_name}"

class PostedJobs(models.Model):
    client = models.ForeignKey(ClientLogin, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    pay_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    tech_stack = models.CharField(max_length=300)
    requirements = models.TextField()
    job_image = models.ImageField(upload_to='job_images/', null=True, blank=True)  # Image field
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)   

    def __str__(self):
        return f"{self.title} - {self.client.first_name} {self.client.last_name}"


class AppliedJobs(models.Model):
    freelancer = models.ForeignKey(FreelancerLogin, on_delete=models.CASCADE)
    job = models.ForeignKey(PostedJobs, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ("Applied", "Applied"),
        ("Verified", "Verified"),
        ("Shortlisted", "Shortlisted"),
        ("Interview", "Interview"),
        ("Rejected", "Rejected"),
        ("Hired", "Hired"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Applied")

    def __str__(self):
        return f"{self.freelancer.first_name} applied for {self.job.title} ({self.status})"
    


class Chat(models.Model):
    SENDER_CHOICES = [
        ("freelancer", "Freelancer"),
        ("client", "Client"),
    ]

    sender_id = models.IntegerField()  
    sender_type = models.CharField(max_length=20, choices=SENDER_CHOICES)
    receiver_id = models.IntegerField()
    receiver_type = models.CharField(max_length=20, choices=SENDER_CHOICES)

    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="chat_files/", blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["timestamp"]  # messages in order

    def __str__(self):
        return f"{self.sender_type} {self.sender_id} -> {self.receiver_type} {self.receiver_id}"




class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ("IT", "IT"),
        ("Web Development", "Web Development"),
        ("App Development", "App Development"),
        ("Design", "Design"),
        ("Other", "Other"),
    ]

    client = models.ForeignKey(ClientLogin, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=200)
    client_profile_pic = models.ImageField(upload_to="feedback_client_pics/", blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    freelancer = models.ForeignKey(FreelancerLogin, on_delete=models.SET_NULL, null=True, blank=True)
    feedback_text = models.TextField()
    rating = models.IntegerField()  # 1-5
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.client_name} ({self.rating}/5)"




class Notification(models.Model):
    client = models.ForeignKey("ClientLogin", on_delete=models.CASCADE, related_name="notifications")
    freelancer = models.ForeignKey("FreelancerLogin", on_delete=models.CASCADE, null=True, blank=True)
    job = models.ForeignKey("PostedJobs", on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Notification for {self.client} - {self.message[:30]}"
