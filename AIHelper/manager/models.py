from django.db import models

# Create your models here.


class ProjectTaskJSON(models.Model):
    name = models.TextField(default='DefaultTask')
    data = models.JSONField(null=True, blank=True, default=dict)
    project_id = models.IntegerField()
    level_id = models.IntegerField(default = -1)