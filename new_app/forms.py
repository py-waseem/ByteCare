from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "service", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    # Any method named clean_<field> runs automatically to check that field
    def clean_phone(self):
        phone = self.cleaned_data["phone"].replace(" ", "").replace("-", "")
        if not phone.lstrip("+").isdigit() or len(phone) < 7:
            raise forms.ValidationError("Enter a valid phone number, for example 98XXXXXXXX.")
        return phone