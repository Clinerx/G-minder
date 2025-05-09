from django import forms
from .models import CustomUser
from .models import Task, MentalHealthEntry
from datetime import datetime
from django.forms.widgets import DateInput, TimeInput
from django.utils import timezone
from django.forms.widgets import SelectDateWidget, TimeInput


class MentalHealthEntryForm(forms.ModelForm):
    class Meta:
        model = MentalHealthEntry
        fields = [
            'date', 'mood', 'mood_rating',
            'thoughts', 'reflection', 'gratitude',
            'goal', 'self_care'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'mood': forms.Select(attrs={'class': 'form-select'}),
            'mood_rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'thoughts': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'reflection': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'gratitude': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'goal': forms.TextInput(attrs={'class': 'form-control'}),
            'self_care': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
class TaskForm(forms.ModelForm):
    due_date = forms.DateField(
        required=False,
        widget=DateInput(attrs={'type': 'date'})
    )

    time = forms.TimeField(
        required=False,
        widget=TimeInput(attrs={'type': 'time'}),
        input_formats=['%H:%M']
    )

    class Meta:
        model = Task
        fields = ['name', 'description', 'completed', 'due_date', 'time', 'status']

    def __init__(self, *args, **kwargs):
        # Merge the __init__ logic to handle the initial values for date and time
        instance = kwargs.get('instance')
        initial = kwargs.setdefault('initial', {})

        if instance and instance.due_date:
            initial['due_date'] = instance.due_date.date()
            initial['time'] = instance.due_date.time().strftime('%H:%M')

        super().__init__(*args, **kwargs)
        self.fields['status'].empty_label = "Select Status"

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('due_date')
        time = cleaned_data.get('time')

        if date and time:
            combined = datetime.combine(date, time)
            cleaned_data['due_date'] = timezone.make_aware(combined)
        elif date:
            combined = datetime.combine(date, datetime.min.time())
            cleaned_data['due_date'] = timezone.make_aware(combined)
        else:
            cleaned_data['due_date'] = None

        return cleaned_data
    
class UpdateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['completed']
        
class CustomUserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = CustomUser
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


