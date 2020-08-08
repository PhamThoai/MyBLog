from uuid import uuid4
from social_core.utils import module_member
from slugify import slugify
from django.conf import settings
from PIL import Image
from io import BytesIO
from accounts.custom_pipeline.utils import download
from accounts.models import Account
from django.utils.crypto import get_random_string
from PIL import Image
from django.core.files.base import ContentFile
  
USER_FIELDS = ['username', 'email']


def get_username(strategy, details, backend, user=None, *args, **kwargs):
    if 'username' not in backend.setting('USER_FIELDS', USER_FIELDS):
        return
    storage = strategy.storage

    if not user:
        email_as_username = strategy.setting('USERNAME_IS_FULL_EMAIL', False)
        uuid_length = strategy.setting('UUID_LENGTH', 16)
        max_length = storage.user.username_max_length()
        do_slugify = strategy.setting('SLUGIFY_USERNAMES', True)
        do_clean = strategy.setting('CLEAN_USERNAMES', True)

        if do_slugify:
            override_slug = strategy.setting('SLUGIFY_FUNCTION')
            if override_slug:
                slug_func = module_member(override_slug)
            else:
                slug_func = slugify
        else:
            slug_func = lambda val: val
            
        if do_clean:
            override_clean = strategy.setting('CLEAN_USERNAME_FUNCTION')
            if override_clean:
                clean_func = module_member(override_clean)
            else:
                clean_func = storage.user.clean_username
        else:
            clean_func = lambda val: val


        if email_as_username and details.get('email'):
            username = details['email']
        elif details.get('username'):
            username = details['username']
        else:
            username = uuid4().hex

        short_username = (username[:max_length - uuid_length]
                          if max_length is not None
                          else username)
        final_username = clean_func(slug_func(username[:max_length]))

        # Generate a unique username for current user using username
        # as base but adding a unique hash at the end. Original
        # username is cut to avoid any field max_length.
        # The final_username may be empty and will skip the loop.
        while not final_username or \
              storage.user.user_exists(username=final_username):
            username = short_username + uuid4().hex[:uuid_length]
            final_username = slug_func(clean_func(username[:max_length]))
    else:
        final_username = storage.user.get_username(user)
    return {'username': final_username}

def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    fields = dict((name, kwargs.get(name, details.get(name)))
                  for name in backend.setting('USER_FIELDS', USER_FIELDS))
    if not fields:
        return

    return {
        'is_new': True,
        'user': strategy.create_user(**fields)
    }

def user_details(strategy, details, backend, user=None, *args, **kwargs):
    """Update user details using data from provider."""
    if not user:
        return

    changed = False  # flag to track changes

    # Default protected user fields (username, id, pk and email) can be ignored
    # by setting the SOCIAL_AUTH_NO_DEFAULT_PROTECTED_USER_FIELDS to True
    if strategy.setting('NO_DEFAULT_PROTECTED_USER_FIELDS') is True:
        protected = ()
    else:
        protected = ('username', 'id', 'pk', 'email', 'password',
                     'is_active', 'is_staff', 'is_superuser',)

    protected = protected + tuple(strategy.setting('PROTECTED_USER_FIELDS', []))

    # Update user model attributes with the new data sent by the current
    # provider. Update on some attributes is disabled by default, for
    # example username and id fields. It's also possible to disable update
    # on fields defined in SOCIAL_AUTH_PROTECTED_USER_FIELDS.
    field_mapping = strategy.setting('USER_FIELD_MAPPING', {}, backend)
    for name, value in details.items():
        # Convert to existing user field if mapping exists
        name = field_mapping.get(name, name)
        if value is None or not hasattr(user, name) or name in protected:
            continue

        current_value = getattr(user, name, None)
        if current_value == value:
            continue

        changed = True
        setattr(user, name, value)
    
    # set default display name and slug
    if backend.name in ['facebook', 'google-oauth2'] :
        setattr(user, 'display_name', details.get('fullname'))
        slug = slugify(details.get('fullname'))
        new_slug = slug
        if user.slug != slug:
            while Account.objects.filter(slug=new_slug).exists():
                new_slug = slug + get_random_string(8)
            setattr(user, 'slug', new_slug)
        changed = True
    
    if changed:
        strategy.storage.user.changed(user)

def get_avatar(backend, strategy, details, response, user=None, *args, **kwargs):
    """Update user avatar using data from response."""
    if not user:
        return

    if not kwargs.get('is_new'):
        return

    url = None
    if backend.name == 'facebook':
        try:
            url = response["picture"]["data"]['url']
        except:
            return
    if backend.name == 'google-oauth2':
        try:
            url = response["picture"]
        except:
            return
        
    get_file = download(url)
    if get_file:
        print("vao tron get file")
        f = BytesIO(get_file)
        uuid_image_name = uuid4().hex
        image = Image.open(f)

        image.thumbnail(settings.THUMBNAIL_SIZE_MEDIUM, Image.ANTIALIAS)
        image_io_thumb = BytesIO()
        image.save(image_io_thumb, format="JPEG")
        user.avatar.save(uuid_image_name + '.jpg',
                                ContentFile(image_io_thumb.getvalue()))
        image_io_thumb.close()

        image.thumbnail(settings.THUMBNAIL_SIZE_SMALL, Image.ANTIALIAS)
        image_io_thumb = BytesIO()
        image.save(image_io_thumb, format="JPEG")
        user.thumbnail_small.save(uuid_image_name + '.jpg',
                                ContentFile(image_io_thumb.getvalue()))
        image_io_thumb.close()

        image.thumbnail(settings.THUMBNAIL_SIZE_TINY, Image.ANTIALIAS)
        image_io_thumb = BytesIO()
        image.save(image_io_thumb, format="JPEG")
        user.thumbnail_tiny.save(uuid_image_name + '.jpg',
                                ContentFile(image_io_thumb.getvalue()))
        image_io_thumb.close()

        user.save()
