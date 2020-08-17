from django.db import models
from accounts.models import Account
from django.utils.crypto import get_random_string
from slugify import slugify
# Create your models here.

# Generate unique slug
def unique_slug(slug):
    new_slug = slug + "-" + str(get_random_string(8))
    if Tag.objects.filter(slug=new_slug).exists():
        return unique_slug(slug)
    return new_slug

class Tag(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(blank=True, unique=True)
    author = models.ForeignKey(Account, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        slug = slugify(self.title)
        try:
            tag = Tag.objects.get(slug=slug)
            if tag.id == self.id:
                self.slug = slug
            else:
                self.slug = unique_slug(slug)
        except Tag.DoesNotExist:
            self.slug = unique_slug(slug)
        
        return super(Tag, self).save(*args, **kwargs)