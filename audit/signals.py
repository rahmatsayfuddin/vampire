from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from .models import AuditLog

_OLD_STATE = {}


def _build_changes(instance):
    cache_key = (instance._meta.model_name, instance.pk)
    old_instance = _OLD_STATE.pop(cache_key, None)
    if old_instance is None:
        return ''
    changes = []
    for field in instance._meta.fields:
        name = field.name
        if name in ('updated_at', 'closed_at'):
            continue
        new_val = getattr(instance, name)
        old_val = getattr(old_instance, name)
        if str(new_val) != str(old_val):
            changes.append(f'{name}: {old_val} → {new_val}')
    return '; '.join(changes)


def _log_action(instance, action, user=None):
    content_type = ContentType.objects.get_for_model(instance)
    changes = ''
    if action == 'update':
        changes = _build_changes(instance)
    AuditLog.objects.create(
        content_type=content_type,
        object_id=instance.pk,
        action=action,
        user=user,
        changes=changes,
    )


def _get_user(instance):
    if hasattr(instance, '_audit_user'):
        return instance._audit_user
    return None


def _is_tracked(sender):
    return sender.__name__ in ('Finding', 'Project')


@receiver(pre_save)
def capture_old(sender, instance, **kwargs):
    if not _is_tracked(sender) or instance.pk is None:
        return
    cache_key = (instance._meta.model_name, instance.pk)
    try:
        _OLD_STATE[cache_key] = type(instance).objects.get(pk=instance.pk)
    except Exception:
        _OLD_STATE[cache_key] = None


@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if not _is_tracked(sender):
        return
    action = 'create' if created else 'update'
    _log_action(instance, action, _get_user(instance))


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if not _is_tracked(sender):
        return
    _log_action(instance, 'delete', _get_user(instance))
