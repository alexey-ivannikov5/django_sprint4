from django.contrib import admin


from .models import Post, Location, Category, Comment


admin.site.register([Category, Post, Location, Comment])
