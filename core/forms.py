from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class ExtendedRegisterForm(UserCreationForm):
    department = forms.ChoiceField(
        choices=Profile.DEPARTMENTS,
        widget=forms.Select(attrs={
            'class': 'w-full border-2 border-slate-200 p-4 rounded-xl font-bold focus:border-green-500 outline-none'
        })
    )

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)