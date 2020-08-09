from django.db import models
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.utils.crypto import get_random_string
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from slugify import slugify
from myblog.utils import send_email_confirm
from social_django.models import UserSocialAuth

# Create your models here.

class Account(AbstractUser):
    is_confirmed_email = models.BooleanField(_('confirmed email'), default=False)
    is_sent_email = models.BooleanField(_('sent email'), default=False)
    avatar = models.ImageField(_('avatar'), upload_to="avatar", blank=True, null=True)
    thumbnail_tiny = models.ImageField(_('avatar thumbnail tiny'), upload_to="thumbnail_tiny", blank=True, null=True)
    thumbnail_small = models.ImageField(_('avatar thumbnail small'), upload_to="thumbnail_tiny", blank=True, null=True)
    display_name = models.CharField(_('display name'), max_length=100, blank=True)
    slug = models.SlugField(_('slug'), max_length=120, unique=True)
    introduction = models.CharField(_('introduction'), max_length=255, blank=True, null=True)
    last_mod_time = models.DateTimeField(_('last modified time'), default=now)
    relationships = models.ManyToManyField('self', through='Relationship',
                                           symmetrical=False,
                                           related_name='related_to')

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)
        self.old_email = self.email

    def save(self, *args, **kwargs):
        if self.old_email != self.email:
            self.is_confirmed_email = False
        super(Account, self).save( *args, **kwargs)
        self.old_email = self.email
    

    def add_relationship(self, person, status, description=None):
        relationship, created = Relationship.objects.get_or_create(
            from_person=self,
            to_person=person,
            status=status,
            defaults={'description': description},
            )
        return relationship

    def remove_relationship(self, person, status):
        Relationship.objects.filter(
            from_person=self,
            to_person=person,
            status=status).delete()
        return
    
    def get_relationships(self, status):
        return self.relationships.filter(
            to_people__status=status,
            to_people__from_person=self)

    def get_related_to(self, status):
        return self.related_to.filter(
            from_people__status=status,
            from_people__to_person=self)

    def get_following(self):
        return self.get_relationships(RELATIONSHIP_FOLLOWING)

    def get_followers(self):
        return self.get_related_to(RELATIONSHIP_FOLLOWING)

    # Chưa dùng được vì chưa chính xác. tạo thời truy vấn trục tiếp từ Relationship
    # def check_followed(self, who):
    #     return self.relationships.filter(
    #         to_people__status=status,
    #         to_people__from_person=self,
    #         to_people__to_person=who
    #     ).exists()

    def get_user_social(self):
        try:
            user_social = UserSocialAuth.objects.get(user=self.id)
        except UserSocialAuth.DoesNotExist:
            return None
        return user_social


def make_slug_random(instance):
    slug = ''
    UserModel = get_user_model()

    if instance.display_name:
        slug = slugify(instance.display_name)
        try:
            UserModel.objects.get(slug=slug)
        except UserModel.DoesNotExist:
            return slug

        while True:
            slug = slugify(instance.display_name) + '.' + get_random_string(8)
            try:
                UserModel.objects.get(slug=slug)
            except UserModel.DoesNotExist:
                return slug


@receiver(pre_save, sender=Account)
def pre_save_user_receiever(sender, instance, *args, **kwargs):
    if not instance.display_name:
        instance.display_name = instance.username
    
    if not instance.slug:
        instance.slug = make_slug_random(instance) 


@receiver(post_save, sender=Account)
def post_save_user_receiever(sender, instance, *args, **kwargs):
    if instance.email:
        try:
            user_social = UserSocialAuth.objects.get(user=instance.id)
            if user_social.provider == 'google':
                return 
        except UserSocialAuth.DoesNotExist:
            pass
        if not instance.is_confirmed_email and not instance.is_sent_email:
            send_email_confirm(instance)
            instance.is_sent_email = True
            instance.save()


RELATIONSHIP_FOLLOWING = 1
RELATIONSHIP_REPORT = 2
RELATIONSHIP_STATUSES = (
    (RELATIONSHIP_FOLLOWING, 'Following'),
    (RELATIONSHIP_REPORT, 'Report'),
)

DESCRIPTION_SPAM = 1
DESCRIPTION_RULES_VIOLATION = 2
DESCRIPTION_HARASHMENT = 3
DESCRIPTION_REPORT = (
    (DESCRIPTION_SPAM, 'Spam'),
    (DESCRIPTION_RULES_VIOLATION, 'Rules Violation'),
    (DESCRIPTION_HARASHMENT, 'Harashment')
)

class Relationship(models.Model):
    from_person = models.ForeignKey(Account, related_name='from_people', on_delete=models.CASCADE)
    to_person = models.ForeignKey(Account, related_name='to_people', on_delete=models.CASCADE)
    status = models.IntegerField(choices=RELATIONSHIP_STATUSES)
    description =  models.IntegerField(choices=DESCRIPTION_REPORT, null=True, blank=True)
