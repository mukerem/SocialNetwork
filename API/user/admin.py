from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import SetPasswordForm
from django.utils.html import mark_safe
from django.utils.safestring import mark_safe

from user.models import User, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    reset_password_form = SetPasswordForm
    list_display = ('first_name', 'last_name', 'email', "phone_number", 'is_active', 'last_seen')
    list_filter = ('is_active', )
    fieldsets = (
        (None, {'fields': ('email', "phone_number",)}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'address',
         'profile_image', 'last_seen')}),
        ('Permissions', {'fields': ('is_active', )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', "phone_number", 'email', 'password1', 'password2', 'is_active', 'last_seen')}
         ),
    )
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('first_name', )
    readonly_fields = ('profile_image', )
    filter_horizontal = ()

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields

        return list(set(
            [field.name for field in self.opts.local_fields] +
            [field.name for field in self.opts.local_many_to_many] + ['profile_image']
        ))

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(is_staff=False)

    def profile_image(self, obj):
        profile_picture = '<img src="{url}" width="{width}" height={height} />'.format(
            url=obj.picture.url,
            # width=obj.picture.width,
            # height=obj.picture.height,
            width=200, height=20
        )
        return mark_safe(profile_picture)
    profile_image.short_description = 'Profile Picture'

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser and 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_fieldsets(self, request, obj=None):
        if obj:
            if request.user.is_superuser:
                fieldsets = (
                    (None, {'fields': ('email', "phone_number",)}),
                    ('Personal info', {'fields': ('first_name', 'last_name', 'address',
                    'picture', 'profile_image', 'last_seen')}),
                    ('Permissions', {'fields': (
                        'is_staff', 'is_active')}),
                )
                return fieldsets
            return super().get_fieldsets(request, obj)
        else:
            return self.add_fieldsets

    def get_list_filter(self, request, obj=None):
        if request.user.is_superuser:
            list_filter = ('is_active', 'is_superuser', 'is_staff')
            return list_filter
        return self.list_filter

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if not request.user.is_superuser:
            extra_context['show_save_and_continue'] = False
            extra_context['show_save'] = False
        return super().changeform_view(request, object_id, form_url, extra_context=extra_context)

    def has_add_permission(self, request, *args, **kwargs):
        return request.user.is_superuser

    def has_delete_permission(self, request, *args, **kwargs):
        return request.user.is_superuser

@admin.register(OTP)
class UserOTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'key', 'count')

