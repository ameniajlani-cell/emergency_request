import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import (
    Assignment,
    EmergencyRequest,
    EmergencyType,
    Requester,
    ResponseTeam,
)


PHONE_PATTERN = re.compile(r'^\+?[0-9\s().-]{8,20}$')




class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            widget = field.widget
            css_class = 'form-select' if isinstance(widget, forms.Select) else 'form-control'
            current_classes = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{current_classes} {css_class}'.strip()


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
        'autofocus': True,
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
    }))


class RequesterValidationMixin:
    def clean_name(self):
        name = self.cleaned_data['name'].strip()

        if len(name) < 2:
            raise forms.ValidationError('Name must contain at least 2 characters.')

        if not all(char.isalpha() or char in " '-" for char in name):
            raise forms.ValidationError('Name can contain only letters, spaces, apostrophes, and hyphens.')

        return name

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        digit_count = sum(char.isdigit() for char in phone)

        if not PHONE_PATTERN.match(phone) or digit_count < 8:
            raise forms.ValidationError('Enter a valid phone number between 8 and 20 characters.')

        return phone

    def clean_location(self):
        location = self.cleaned_data['location'].strip()

        if len(location) < 3:
            raise forms.ValidationError('Location must contain at least 3 characters.')

        return location


class RequesterIntakeForm(RequesterValidationMixin, BootstrapFormMixin, forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Name',
        widget=forms.TextInput(attrs={'placeholder': 'Name'}),
    )
    phone = forms.CharField(
        max_length=20,
        label='Phone',
        widget=forms.TextInput(attrs={'placeholder': 'Phone', 'inputmode': 'tel'}),
    )
    location = forms.CharField(
        max_length=255,
        label='Requester Location',
        widget=forms.TextInput(attrs={'placeholder': 'Location'}),
    )


class RequesterForm(RequesterValidationMixin, BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Requester
        fields = ['name', 'phone', 'location']
        labels = {
            'name': 'Name',
            'phone': 'Phone',
            'location': 'Requester Location',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone', 'inputmode': 'tel'}),
            'location': forms.TextInput(attrs={'placeholder': 'Location'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        phone = cleaned_data.get('phone')
        location = cleaned_data.get('location')

        if name and phone and location:
            duplicate = Requester.objects.filter(
                name=name,
                phone=phone,
                location=location,
            ).exclude(pk=self.instance.pk).exists()

            if duplicate:
                raise forms.ValidationError('A requester with the same name, phone, and location already exists.')

        return cleaned_data


class EmergencyRequestCreateForm(BootstrapFormMixin, forms.ModelForm):
    latitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput(),
    )
    longitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = EmergencyRequest
        fields = [
            'title',
            'description',
            'location',
            'before_image',
            'after_image',
            'emergency_type',
        ]
        labels = {
            'title': 'Title',
            'description': 'Description',
            'location': 'Emergency Location',
            'before_image': 'Before Image',
            'after_image': 'After Image',
            'emergency_type': 'Emergency Type',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Title'}),
            'description': forms.Textarea(attrs={'placeholder': 'Description', 'rows': 4}),
            'location': forms.TextInput(attrs={'placeholder': 'Emergency location'}),
            'before_image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
            'after_image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }

    def clean_title(self):
        title = self.cleaned_data['title'].strip()

        if len(title) < 3:
            raise forms.ValidationError('Title must contain at least 3 characters.')

        return title

    def clean_description(self):
        description = self.cleaned_data['description'].strip()

        if len(description) < 10:
            raise forms.ValidationError('Description must contain at least 10 characters.')

        return description

    def clean_location(self):
        location = self.cleaned_data['location'].strip()

        if len(location) < 3:
            raise forms.ValidationError('Emergency location must contain at least 3 characters.')

        return location



class EmergencyRequestUpdateForm(EmergencyRequestCreateForm):
    class Meta(EmergencyRequestCreateForm.Meta):
        fields = [
            'title',
            'description',
            'location',
            'before_image',
            'after_image',
            'emergency_type',
            'status',
        ]
        labels = {
            **EmergencyRequestCreateForm.Meta.labels,
            'status': 'Status',
        }


class EmergencyTypeForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = EmergencyType
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Emergency type name'}),
        }

    def clean_name(self):
        return self.cleaned_data['name'].strip()


class ResponseTeamForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ResponseTeam
        fields = ['name', 'contact']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Team name'}),
            'contact': forms.TextInput(attrs={'placeholder': 'Phone, radio, or email'}),
        }

    def clean_name(self):
        return self.cleaned_data['name'].strip()

    def clean_contact(self):
        contact = self.cleaned_data['contact'].strip()

        if len(contact) < 3:
            raise forms.ValidationError('Contact must contain at least 3 characters.')

        return contact


class AssignmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['emergency_request', 'response_team']
        labels = {
            'emergency_request': 'Emergency Request',
            'response_team': 'Response Team',
        }
