# student/forms.py
from django import forms
from .models import Student
from datetime import date
from django.contrib.auth.forms import UserCreationForm
# from principal.models import Department

CURRENT_YEAR = date.today().year
YEAR_CHOICES = [(y, y) for y in range(CURRENT_YEAR, CURRENT_YEAR - 10, -1)]

class StudentForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )
    
    class Meta:
        model = Student
        fields = [
            "first_name",
            "last_name", 
            "email",
            "std_reg_no",
            "std_dept",
            "std_year_of_admission",
            "std_phone_no",
            "std_pic",
            "std_age",
            "password1",
            "password2"
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            "last_name": forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            "email": forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
            "std_reg_no": forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            "std_dept": forms.Select(attrs={'class': 'form-select', 'required': True}),
            "std_year_of_admission": forms.NumberInput(attrs={'class': 'form-control', 'required': True}),
            "std_phone_no": forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile'}),
            "std_age": forms.NumberInput(attrs={'class': 'form-control'}),
            "std_pic": forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
            "std_reg_no": "Register No",
            "std_dept": "Department",
            "std_year_of_admission": "Year Of Admission",
            "std_phone_no": "Phone No",
            "std_age": "Age",
            "std_pic": "Profile Picture",
        }


class StudentProfileForm(forms.ModelForm):
    """Form for editing student profile (excluding password and registration info)"""
    
    class Meta:
        model = Student
        fields = [
            "first_name",
            "last_name",
            "std_age",
            "std_phone_no",
            "std_year_of_admission",
        ]
        widgets = {
            "first_name": forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200',
                'required': True
            }),
            "last_name": forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200',
                'required': True
            }),
            "std_age": forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200',
                'min': '16',
                'max': '50'
            }),
            "std_phone_no": forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200',
                'pattern': '[0-9]{10}',
                'maxlength': '10',
                'placeholder': '10-digit phone number'
            }),
            "std_year_of_admission": forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200',
                'required': True,
                'min': '2000',
                'max': str(CURRENT_YEAR + 1)
            }),
        }
        labels = {
            "first_name": "First Name",
            "last_name": "Last Name",
            "std_age": "Age",
            "std_phone_no": "Phone Number",
            "std_year_of_admission": "Year of Admission",
        }
    
    def clean_std_phone_no(self):
        phone = self.cleaned_data.get('std_phone_no')
        if phone:
            # Remove any non-digit characters
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) != 10:
                raise forms.ValidationError('Phone number must be exactly 10 digits.')
        return phone
    
    def clean_std_age(self):
        age = self.cleaned_data.get('std_age')
        if age:
            if age < 16 or age > 50:
                raise forms.ValidationError('Age must be between 16 and 50.')
        return age
    
    def clean_std_year_of_admission(self):
        year = self.cleaned_data.get('std_year_of_admission')
        if year:
            if year < 2000 or year > CURRENT_YEAR + 1:
                raise forms.ValidationError(f'Year of admission must be between 2000 and {CURRENT_YEAR + 1}.')
        return year


class StudentProfilePictureForm(forms.Form):
    """Simple form for profile picture without PIL validation"""
    
    std_pic = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*',
            'id': 'id_std_pic'
        }),
        label="Profile Picture"
    )
    
    def clean_std_pic(self):
        profile_pic = self.cleaned_data.get('std_pic')
        if profile_pic:
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.avif', '.webp']
            ext = profile_pic.name.lower()
            
            # Check if extension is valid
            if not any(ext.endswith(valid_ext) for valid_ext in valid_extensions):
                raise forms.ValidationError('Unsupported file format. Please upload JPG, PNG, GIF, AVIF, or WebP.')
            
            # Validate file size (5MB max)
            max_size = 5 * 1024 * 1024  # 5MB
            if profile_pic.size > max_size:
                raise forms.ValidationError('Image file too large (maximum 5MB).')
        
        return profile_pic