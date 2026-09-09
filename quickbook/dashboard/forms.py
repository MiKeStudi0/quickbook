from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from events.models import Event

User = get_user_model()

class StaffLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))


class VendorForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False, help_text="Leave blank if updating without changing password.")

    class Meta:
        model = User
        fields = ['username', 'email', 'is_vendor', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_vendor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_vendor = True
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'venue', 'event_date', 'total_seats', 'available_seats', 'vendor']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'venue': forms.TextInput(attrs={'class': 'form-control'}),
            'event_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'total_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'available_seats': forms.NumberInput(attrs={'class': 'form-control'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
        }
