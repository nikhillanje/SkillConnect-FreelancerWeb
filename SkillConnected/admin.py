from django.contrib import admin
from .models import FreelancerLogin, ClientLogin, Images , FreelancerInfo,ClientInfo
from django.utils.html import format_html

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
    list_display = ('id', 'first_name', 'last_name', 'email', 'mobile_number', 'preview_image')

    def preview_image(self, obj):
        if obj.cimage:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.cimage.url)
        return "-"
    preview_image.short_description = 'ID Proof'


@admin.register(FreelancerInfo)
class FreelancerInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'freelancer', 'education', 'skills', 'experience', 'language')

@admin.register(ClientInfo)
class ClientInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'company_name', 'location', 'industry')
