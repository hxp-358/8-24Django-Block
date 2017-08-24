from django.contrib import admin
from .models import Comment
# Register your models here.

class CommentAdmin(admin.ModelAdmin):
    list_display = ['name','created_time','email','url']
admin.site.register(Comment,CommentAdmin)
