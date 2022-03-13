from django.contrib import admin

from post.models import Post, Like

# admin.site.register(Post)
admin.site.register(Like)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'views', "likes")
