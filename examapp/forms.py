# forms.py
from django import forms
from .models import Profile,YouTubeVideo


class YouTubeVideoForm(forms.ModelForm):
    class Meta:
        model = YouTubeVideo
        fields = ['title', 'description', 'url']

        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'location', 'birth_date']

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, label='OTP')

class PasswordResetForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True, label='Email')

class SetPasswordForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput, label='New Password')
    new_password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm New Password')

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data
