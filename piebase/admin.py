from django.contrib import admin
from .models import User, Attachment, Project, Role, Milestone, Requirement, Ticket, TicketStatus, Timeline
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['username']

admin.site.register(User)
admin.site.register(Attachment)
admin.site.register(Project)
admin.site.register(Role)
admin.site.register(Milestone)
admin.site.register(Requirement)
admin.site.register(Ticket)
admin.site.register(TicketStatus)
admin.site.register(Timeline)
