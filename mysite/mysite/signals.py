from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from polls.models import Answer


@receiver(post_save, sender=Answer)
def clear_cache(sender, instance, **kwargs):
    cache.delete()
    print("Cache cleared!")
