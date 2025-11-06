from django.contrib import admin


from .models import Post, Location, Category


admin.site.register([Category, Post, Location])
