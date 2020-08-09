from django.db import models
from accounts.models import Account
from django.utils.crypto import get_random_string
from slugify import slugify
# Create your models here.

# Generate unique slug
def unique_slug(title):
    slug = slugify(title)
    if not Tag.objects.filter(slug=slug).exists():
        return slug

    new_slug = slug + "-" + str(get_random_string(8))
    while Tag.objects.filter(slug=new_slug).exists():
        new_slug = slug + "-" + str(get_random_string(8))

    return new_slug

class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(blank=True, unique=True)
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        self.slug = unique_slug(self.title)
        return super(Tag, self).save(*args, **kwargs)