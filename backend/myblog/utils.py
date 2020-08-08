from hashlib import md5
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail

def get_md5(str):
    m = md5(str.encode('utf-8'))
    return m.hexdigest()

def send_email_confirm(instance):
    title = "[{app_name}] Verify your email!".format(app_name=settings.APP_NAME)
    path = reverse('accounts:result')
    site = settings.SITE_NAME
    sign = get_md5(get_md5(settings.SECRET_KEY + str(instance.email) + str(instance.id)))
    url = "http://{site}{path}?type=validation&id={id}&sign={sign}".format(
                site=site, path=path, id=instance.id, sign=sign)
    content = """
    <p>Welcome {username} to Myblog </p>
    <p>Please click the link below to verify your email</p>
    Link here: <a href="{url}" rel="bookmark">{url}</a>
    <br />
    <p>If the link above cannot be opened, please copy this link into your browser.</p>
    <p>Thank you and have a great day!</p>
    """.format(username = instance.username, url=url)

    print(content) # In ra content để kiểm tra

    send_mail(
        title,
        content,
        settings.EMAIL_HOST_USER,
        ['phamvanthoaibk@gmail.com', instance.email],
        fail_silently=False
    )

