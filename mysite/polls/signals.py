from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from polls.models import Answer


# Singnal that will be executed when answer is deleted or updated.
@receiver(post_save, sender=Answer)
@receiver(post_delete, sender=Answer)
def clear_cache(sender, instance, **kwargs):
    cache.clear()
