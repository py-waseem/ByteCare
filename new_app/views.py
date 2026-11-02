from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail

from .forms import ContactForm
# Create your views here.
def home_view(request):
    return render(request, 'home.html')

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)       # fill the form with what the visitor sent
        if form.is_valid():
            form.save()
            return redirect("thank_you")     # was: messages.success(...) and redirect("contact")        # redirect after POST so a refresh does not resubmit
    else:
        form = ContactForm()                   # first visit: an empty form

    return render(request, "contact.html", {"form": form})
def about_view(request):
    return render(request, 'about.html')

def services_view(request):
    return render(request, 'services.html')

def thank_you(request):
    return render(request, "thank_you.html")