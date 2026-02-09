from django.db import models
from django.utils import timezone
# Create your models here.



class ImageKey(models.Model):
    key = models.CharField(max_length=50 , default="" , unique=True)
    is_used = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.key} - {self.is_used}"

class Note(models.Model):
    title = models.CharField(max_length=50 , default="")
    content = models.TextField(max_length=1000 , default="")
    created_at = models.DateTimeField(default=timezone.now)
    image = models.ImageField(upload_to='images/', null=True, blank=True , default=None)
    image_key = models.ForeignKey(ImageKey, on_delete=models.SET_NULL , null=True, blank=True , default=None)
    
    def __str__(self):
        return f"{self.title} - {self.created_at}"
    


class Qoute(models.Model):
    qoute = models.TextField(max_length=1000 , default="")
    
    def __str__(self):
        return f"{self.qoute}"    

