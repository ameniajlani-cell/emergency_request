from django.contrib import admin

from .models import (
    Assignment,
    EmergencyRequest,
    EmergencyType,
    Requester,
    ResponseTeam,
)


@admin.register(Requester)
class RequesterAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'location')
    search_fields = ('name', 'phone', 'location')


@admin.register(EmergencyType)
class EmergencyTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(EmergencyRequest)
class EmergencyRequestAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'requester',
        'emergency_type',
        'location',
        'status',
        'has_before_image',
        'has_after_image',
        'created_at',
    )
    list_filter = ('status', 'emergency_type', 'created_at')
    search_fields = ('title', 'description', 'location', 'requester__name')
    autocomplete_fields = ('requester', 'emergency_type')
    date_hierarchy = 'created_at'

    @admin.display(boolean=True, description='Before')
    def has_before_image(self, obj):
        return bool(obj.before_image)

    @admin.display(boolean=True, description='After')
    def has_after_image(self, obj):
        return bool(obj.after_image)


@admin.register(ResponseTeam)
class ResponseTeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact')
    search_fields = ('name', 'contact')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('emergency_request', 'response_team', 'assigned_at')
    list_filter = ('response_team', 'assigned_at')
    search_fields = ('emergency_request__title', 'response_team__name')
    autocomplete_fields = ('emergency_request', 'response_team')
