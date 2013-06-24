from django.db import models
from devman.dmroot.models import DBMember, DBHome

# Create your models here.

class DBProject(models.Model):
    name = models.CharField(max_length=64)
    home = models.ForeignKey(DBHome, blank = True, null = True)
