from django import forms
from .models import FreelancerLogin,ClientLogin,FreelancerInfo,ClientInfo,PostedJobs,AppliedJobs

class FreelancerForm(forms.ModelForm):
    re_enter_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter Password'}),
        label="Confirm Password"
    )

    class Meta:
        model = FreelancerLogin
        fields = ['first_name', 'last_name', 'email', 'password', 'mobile_number', 'fimage']
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        re_password = cleaned_data.get("re_enter_password")

        if password and re_password and password != re_password:
            self.add_error('re_enter_password', "Passwords do not match!")  # 👈 attach error properly

        return cleaned_data


class ClientForm(forms.ModelForm):
    re_enter_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Re-enter Password'}),
        label="Confirm Password"
    )

    class Meta:
        model = ClientLogin
        fields = ['first_name', 'last_name', 'email', 'password', 'mobile_number', 'cimage']
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        re_password = cleaned_data.get("re_enter_password")

        if password and re_password and password != re_password:
            self.add_error('re_enter_password', "Passwords do not match!")

        return cleaned_data


class FreelancerInfoForm(forms.ModelForm):
    profile_picture = forms.ImageField(   # 👈 explicit file field
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )
    class Meta:
        model = FreelancerInfo
        fields = ['profile_picture', 'bio', 'education', 'skills', 'experience', 'language','address','resume']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control'}),
            'education': forms.TextInput(attrs={'class': 'form-control'}),
            'skills': forms.Textarea(attrs={'class': 'form-control'}),
            'experience': forms.Textarea(attrs={'class': 'form-control'}),
            'language': forms.Select(choices=[
                ('English', 'English'),
                ('Hindi', 'Hindi'),
                ('Marathi', 'Marathi'),
                ('Other', 'Other'),
            ], attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control'}),
        }




class ClientInfoForm(forms.ModelForm):
    class Meta:
        model = ClientInfo
        fields = [
            'profile_picture',   # include picture
            'company_name',
            'industry',
            'requirements',
            'budget',
            'location',
            'about',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control'}),
            'budget': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control'}),
        }

class PostedJobsForm(forms.ModelForm):
    class Meta:
        model = PostedJobs
        fields = ['title', 'description', 'pay_per_hour', 'tech_stack', 'requirements']

class AppliedJobsForm(forms.ModelForm):
    class Meta:
        model = AppliedJobs
        fields = ['freelancer', 'job', 'status']  # status is already in the model
        widgets = {
            'status': forms.Select(choices=[
                ('Pending', 'Pending'),
                ('Approved', 'Approved'),
                ('Rejected', 'Rejected'),
            ])
        }