from django.contrib import admin
from .models import Character, Request, CharacterToRequest, CustomUser
from django.contrib.auth.admin import UserAdmin



admin.site.register(Character)
admin.site.register(Request)
admin.site.register(CharacterToRequest)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff')
    list_filter = ('is_staff',)  # Changed to a tuple
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)