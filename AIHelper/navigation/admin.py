from django.contrib import admin
from .models import Level, Objective, Profile, Project
# Register your models here.

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    fields = ("name","transform", "project_id", "date_created", "date_modified", "level_id")

@admin.register(Objective)
class ObjectiveAdmin(admin.ModelAdmin):
    fields = ("name", "index", "team", "attackingTeam", "transform", "controlled")

@admin.register(Profile)
class UserAdmin(admin.ModelAdmin):
    fields = ("username", "profile_id", "user_level", "user")

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    fields = ("project_id", "name", "author", "date_created", "date_modified", "description")