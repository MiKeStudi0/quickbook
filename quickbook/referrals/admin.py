from django.contrib import admin
from .models import ReferralNode

@admin.register(ReferralNode)
class ReferralNodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'parent', 'left', 'right', 'created_at')
    search_fields = ('user__username', 'parent__user__username')
