from django.contrib import admin
from django.contrib.auth.admin  import UserAdmin as BaseUserAdmin
from core import models
from django.utils.translation import gettext_lazy as _


class UserAdmin(BaseUserAdmin):
    """ Custom UserAdmin class """

    ordering =['id']
    list_display = ['email', 'username']
    fieldsets = (
        (None,{'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {'fields': ('is_active', 'is_staff', 'is_superuser')}
        ),
        (
            _('Important Dates'),
            {'fields': ('last_login', )}
        ),
    )
    readonly_fields = ['last_login']
    add_fieldsets =(
        (None,{
            'classes': ('wide',),
            'fields': ( 
                'email',
                'password1',
                'password2',
                'username',
                'is_staff',
                'is_active',
                'is_superuser',
            ),
        }),
    )

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)

