from django.dispatch import receiver
from . import signals
from piebase.models import Timeline


@receiver(signals.create_timeline)
def timeline_activity(sender, **kwargs):
    Timeline.objects.create(user=sender, content_object=kwargs.get("content_object"),namespace=kwargs.get("namespace"),event_type=kwargs.get("event_type"), project=kwargs.get("project"))
