from django.contrib import admin, messages
from django.db.models import Case, IntegerField, Value, When
from django.utils import timezone
from django.utils.html import format_html
from django.utils.text import Truncator

from .models import ContactMessage

# Text shown at the top of the admin pages
admin.site.site_header = "ByteCare Admin"
admin.site.site_title = "ByteCare Admin"
admin.site.index_title = "Service requests"

# Badge colors: (text color, background color)
STATUS_COLORS = {
    "pending": ("#b42318", "#fee4e2"),      # red    = waiting for you
    "in_progress": ("#b54708", "#fef0c7"),  # amber  = you are working on it
    "done": ("#067647", "#d1fadf"),         # green  = finished
}


class ProgressFilter(admin.SimpleListFilter):
    """Sidebar filter: 'Left to service' vs 'Already serviced', with counts."""

    title = "progress"
    parameter_name = "progress"

    def lookups(self, request, model_admin):
        all_requests = model_admin.get_queryset(request)
        left = all_requests.exclude(status="done").count()
        done = all_requests.filter(status="done").count()
        return [
            ("left", f"Left to service ({left})"),
            ("done", f"Already serviced ({done})"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "left":
            return queryset.exclude(status="done")
        if self.value() == "done":
            return queryset.filter(status="done")
        return queryset


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    # ----- the list page -----
    list_display = ("status_badge", "name", "contact", "service", "short_message", "received", "waiting")
    list_display_links = ("name",)
    list_filter = (ProgressFilter, "status", "service")
    search_fields = ("name", "phone", "message", "notes")
    date_hierarchy = "created_at"
    list_per_page = 25
    actions = ["mark_pending", "mark_in_progress", "mark_done"]

    def get_ordering(self, request):
        # Requests still waiting come first (oldest first); serviced ones go to the bottom.
        not_done_first = Case(
            When(status="done", then=Value(1)),
            default=Value(0),
            output_field=IntegerField(),
        )
        return [not_done_first.asc(), "created_at"]

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        color, background = STATUS_COLORS[obj.status]
        return format_html(
            '<span style="color:{};background:{};padding:3px 10px;border-radius:12px;'
            'font-weight:600;font-size:12px;white-space:nowrap">{}</span>',
            color, background, obj.get_status_display(),
        )

    @admin.display(description="Phone")
    def contact(self, obj):
        # Build a WhatsApp link: use Nepal's code 977 unless the number already has a country code
        digits = "".join(ch for ch in obj.phone if ch.isdigit())
        if not digits.startswith("977"):
            digits = "977" + digits.lstrip("0")
        return format_html(
            '{} &nbsp;<a href="https://wa.me/{}" target="_blank" rel="noopener">WhatsApp</a>',
            obj.phone, digits,
        )

    @admin.display(description="Message")
    def short_message(self, obj):
        return Truncator(obj.message).chars(60)

    @admin.display(description="Received", ordering="created_at")
    def received(self, obj):
        return timezone.localtime(obj.created_at).strftime("%d %b %Y, %H:%M")

    @admin.display(description="Waiting")
    def waiting(self, obj):
        if obj.status == "done":
            return "-"
        days = (timezone.now() - obj.created_at).days
        if days == 0:
            return "Today"
        label = f"{days} day{'s' if days != 1 else ''}"
        if days >= 3:  # long wait: show in red
            return format_html('<strong style="color:#b42318">{}</strong>', label)
        return label

    # ----- the single request page -----
    readonly_fields = ("name", "phone", "service", "message", "created_at", "serviced_at")
    fieldsets = (
        ("Customer request", {"fields": ("name", "phone", "service", "message", "created_at")}),
        ("Your work on it", {"fields": ("status", "notes", "serviced_at")}),
    )

    def has_add_permission(self, request):
        return False  # requests come only from the website form

    def save_model(self, request, obj, form, change):
        # Keep the "serviced at" time in step with the status
        if obj.status == "done" and not obj.serviced_at:
            obj.serviced_at = timezone.now()
        elif obj.status != "done":
            obj.serviced_at = None
        super().save_model(request, obj, form, change)

    # ----- bulk actions (tick rows, choose an action, press Go) -----
    @admin.action(description="Mark selected as Pending")
    def mark_pending(self, request, queryset):
        count = queryset.update(status="pending", serviced_at=None)
        self.message_user(request, f"{count} request(s) marked as Pending.", messages.SUCCESS)

    @admin.action(description="Mark selected as In progress")
    def mark_in_progress(self, request, queryset):
        count = queryset.update(status="in_progress", serviced_at=None)
        self.message_user(request, f"{count} request(s) marked as In progress.", messages.SUCCESS)

    @admin.action(description="Mark selected as Serviced")
    def mark_done(self, request, queryset):
        count = queryset.update(status="done", serviced_at=timezone.now())
        self.message_user(request, f"{count} request(s) marked as Serviced.", messages.SUCCESS)