from django import forms
from .models import AddOnCourse, Department

class AddOnCourseForm(forms.ModelForm):
    class Meta:
        model = AddOnCourse
        fields = ['course_id', 'course_name', 'department', 'course_description', 'course_price']
        widgets = {
            'course_id': forms.TextInput(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'CS101',
                'id': 'course_id',
                'oninput': 'this.value = this.value.toUpperCase()'
            }),
            'course_name': forms.TextInput(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'placeholder': 'Introduction to Programming',
                'id': 'course_name'
            }),
            'department': forms.Select(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 appearance-none bg-white',
                'id': 'department'
            }),
            'course_description': forms.Textarea(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none',
                'rows': 8,
                'placeholder': 'Brief description of the course including syllabus, learning outcomes, prerequisites...',
                'id': 'description'
            }),
            'course_price': forms.NumberInput(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500',
                'min': '0',
                'step': '100',
                'placeholder': '0',
                'id': 'course_price'
            })
        }
        labels = {
            'course_id': 'Course ID *',
            'course_name': 'Course Name *',
            'department': 'Department *',
            'course_description': 'Course Description *',
            'course_price': 'Course Price'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure department choices are always available
        self.fields['department'].queryset = Department.objects.all()
        
        # Add required attribute to fields
        self.fields['course_id'].required = True
        self.fields['course_name'].required = True
        self.fields['department'].required = True
        self.fields['course_description'].required = True
        

    
    def clean_course_id(self):
        course_id = self.cleaned_data.get('course_id', '').strip().upper()
        if not course_id:
            raise forms.ValidationError('Course ID is required')
        
        # Check for duplicate (excluding current instance if editing)
        query = AddOnCourse.objects.filter(course_id=course_id)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        
        if query.exists():
            raise forms.ValidationError(f'Course ID "{course_id}" already exists')
        
        return course_id
    
    def clean_course_price(self):
        price = self.cleaned_data.get('course_price')
        if price < 0:
            raise forms.ValidationError('Price cannot be negative')
        return price