import django.dispatch

create_timeline = django.dispatch.Signal(
    providing_args=["user", "content_object", "event_type", "data"])
