from django.conf import settings
from django.db.models.base import ModelBase
from django.utils import six
from django_lifecycle import LifecycleModelMixin, hook

from model_subscription.constants import OperationType
from model_subscription.subscriber import ModelSubscription


class SubscriptionMeta(ModelBase):
    """
    The Singleton base metaclass.
    """

    def __new__(cls, name, bases, attrs):
        for base in bases:
            if hasattr(bases, '_subscription'):
                del base['_subscription']
        _subscription = ModelSubscription()
        attrs['_subscription'] = _subscription
        return super(SubscriptionMeta, cls).__new__(cls, name, bases, attrs)


@six.add_metaclass(SubscriptionMeta)
class SubscriptionModelMixin(LifecycleModelMixin):
    def __init__(self, *args, **kwargs):
        if settings.SUBSCRIPTION_AUTO_DISCOVER:
            self._subscription.auto_discover()
        super(SubscriptionModelMixin, self).__init__(*args, **kwargs)

    @hook('after_create')
    def notify_create(self):
        self._subscription.notify(OperationType.CREATE, self)

    @classmethod
    def notify_bulk_create(cls, objs):
        cls._subscription.notify_many(OperationType.BULK_CREATE, objs)

    @hook('after_update')
    def notify_update(self):
        self._subscription.notify(OperationType.UPDATE, self)

    @classmethod
    def notify_bulk_update(cls, objs):
        cls._subscription.notify_many(OperationType.BULK_UPDATE, objs)

    @hook('after_delete')
    def notify_delete(self):
        self._subscription.notify(OperationType.DELETE, self)

    @classmethod
    def notify_bulk_delete(cls, objs):
        cls._subscription.notify_many(OperationType.BULK_DELETE, objs)
