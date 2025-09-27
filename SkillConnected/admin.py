from django.contrib import admin
from .models import FreelancerLogin, ClientLogin, Images , FreelancerInfo,ClientInfo,PostedJobs,AppliedJobs,Company
from django.utils.html import format_html
from django.contrib import admin
from .models import Feedback

# Freelancer admin with image preview
@admin.register(FreelancerLogin)
class FreelancerAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'mobile_number', 'preview_image')

    def preview_image(self, obj):
        if obj.fimage:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.fimage.url)
        return "-"
    preview_image.short_description = 'ID Proof'




# Client admin
@admin.register(ClientLogin)
class ClientLoginAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'first_name', 
        'last_name', 
        'email', 
        'mobile_number', 
        'preview_image',   # fixed here
        'company_name',
        'company_url',
    )

    def preview_image(self, obj):
        if obj.cimage:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />', 
                obj.cimage.url
            )
        return "-"
    preview_image.short_description = 'ID Proof'



@admin.register(FreelancerInfo)
class FreelancerInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'freelancer', 'education', 'skills', 'experience', 'language')

@admin.register(ClientInfo)
class ClientInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'company_name', 'location', 'industry')


@admin.register(PostedJobs)
class PostedJobsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'client', 'pay_per_hour', 'tech_stack', 'created_at', 'job_image_tag')
    list_filter = ('client', 'created_at')  # filters in admin sidebar
    search_fields = ('title', 'tech_stack', 'description', 'requirements', 'client__first_name', 'client__last_name')
    ordering = ('-created_at',)  # newest jobs first

    # Display image thumbnail in admin list
    def job_image_tag(self, obj):
        if obj.job_image:
            return format_html('<img src="{}" width="100" height="70" style="object-fit: cover;" />', obj.job_image.url)
        return "-"
    job_image_tag.short_description = 'Job Image'



@admin.register(AppliedJobs)
class AppliedJobsAdmin(admin.ModelAdmin):
    list_display = ('id', 'freelancer', 'job', 'status', 'applied_at')
    list_filter = ('status', 'applied_at', 'job')
    search_fields = (
        'freelancer__first_name',
        'freelancer__last_name',
        'freelancer__email',
        'job__title',
    )
    ordering = ('-applied_at',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("client_name", "category", "freelancer", "rating", "created_at")
    list_filter = ("category", "rating", "created_at")
    search_fields = ("client_name", "feedback_text")
    ordering = ("-created_at",)
# Company admin
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'company_name', 'company_url', 'preview_logo')
    search_fields = ('company_name', 'company_url')

    # Display logo thumbnail
    def preview_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.logo.url)
        return "-"
    preview_logo.short_description = 'Logo'    