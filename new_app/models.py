from django.db import models


class ContactMessage(models.Model):

    # 1. Add this block first
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In progress"
        DONE = "done", "Serviced"

    SERVICE_CHOICES = [
        ("repair", "Laptop or desktop repair"),
        ("virus", "Virus or malware removal"),
        ("install", "Windows or software install"),
        ("data", "Data backup or recovery"),
        ("network", "Network or Wi-Fi setup"),
        ("pc", "Custom PC or upgrade"),
        ("other", "Something else"),
    ]

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES, default="repair")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # 2. Your three lines go here, after created_at
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True, help_text="Private notes. Customers never see this.")
    serviced_at = models.DateTimeField(null=True, blank=True)

    # 3. Delete the old line:  is_read = models.BooleanField(default=False)           # tick it in the admin once handled

    class Meta:
        ordering = ["-created_at"]    # newest first

    def __str__(self):
        return f"{self.name} - {self.get_service_display()}"