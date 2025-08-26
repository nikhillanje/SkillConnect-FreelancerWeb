from django.db import models
from django.utils.safestring import mark_safe 

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
    #for approval
    is_approved = models.BooleanField(default=False)


    def __str__(self):
        return self.email
    

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
    

class ClientInfo(models.Model):
    client = models.OneToOneField(ClientLogin, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    industry = models.CharField(max_length=255, blank=True, null=True)
    requirements = models.TextField(blank=True, null=True)
    budget = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)  # new field

    def __str__(self):
        return f"Profile of {self.client.first_name}"


