from django.db import models
from accounts.models import Account

class ImageForPost(models.Model):
    image = models.ImageField(upload_to='photos')
    # thumbnail_mobile_api = models.ImageField(upload_to='thumbnail_mobile_api')
    owner = models.ForeignKey(Account, on_delete=models.CASCADE)
    add_on = models.DateTimeField(auto_now_add=True)

