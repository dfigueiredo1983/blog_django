from random import SystemRandom
import string
from django.utils.text import slugify


def random_letters(size=5):
    return ''.join(SystemRandom().choices(
        string.ascii_lowercase + string.digits,
        k=size
    ))


def slugify_new(text, size=5):
    return slugify(text) + '-' + random_letters(size)
