from django.db import models
from django.db.models.signals import pre_save
from django.conf import settings
from accounts.models import Account
from django.utils.translation import gettext_lazy as _
from image_files.models import ImageForPost
from tags.models import Tag
from django.utils.safestring import mark_safe
from slugify import slugify
from markdown import markdown
from django.utils.crypto import get_random_string
from django.utils.timezone import now
# Create your models here.
 
class Post(models.Model):
    title = models.CharField(_('title'), max_length=120)
    slug = models.SlugField(_('slug'), unique=True)
    description = models.CharField(_('description'), max_length=255)
    content = models.TextField(_('content'), )
    is_draft = models.BooleanField(_('is draft'), default=True)
    is_publish = models.BooleanField(_('is publish'), default=False)
    enable_cmt = models.BooleanField(_('enable comment'), default=True) 
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name=_('author'), 
        on_delete=models.CASCADE,
        related_name='author_of'
    )
    create_at = models.DateTimeField(_('create at'), auto_now_add=True)
    update_at = models.DateTimeField(_('update at'), auto_now=True)
    publish_at = models.DateTimeField(_('publish at'), null=True, blank=True)
    read_time = models.PositiveSmallIntegerField(_('read time'), null=True, blank=True)
    publish_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name=_('publishing manager'),
        on_delete=models.CASCADE, null=True, blank=True,
        related_name='publish'
    )
    tags = models.ManyToManyField(Tag)
    views = models.IntegerField(_('views'), default=0)
    # images = models.ManyToManyField(ImageForPost)

    class Meta:
        ordering = ['-publish_at']
    
    def __str__(self):
        return self.title

    # def get_absolute_url(self):
    #     return reverse("posts:detail", kwargs={"slug": self.slug})

    def get_api_url(self):
        return reverse("posts-api:detail", kwargs={"slug": self.slug})

    def get_markdown(self):
        content = self.content
        markdown_text = markdown(content)
        return mark_safe(markdown_text)

    def get_author_object(self):
        try:
            user = Account.objects.get(id=self.author)
        except Account.DoesNotExist:
            user = None
        return user


def create_unique_slug(instance):
    slug = slugify(instance.title) + '-' + str(get_random_string(6))

    if Post.objects.filter(slug=slug).count() == 0:
        return slug
    
    return create_unique_slug(instance)

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    
    slug = slugify(instance.title)
    try:
        post = Post.objects.get(slug=slug)
        if post.id == instance.id:
            instance.slug = slug
        else:
            instance.slug = create_unique_slug(instance)
    except Post.DoesNotExist:
        instance.slug = slug

    if not instance.id:
        instance.publish_at = now()

pre_save.connect(pre_save_post_receiver, sender=Post)

