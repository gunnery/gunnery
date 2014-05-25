from factory.django import DjangoModelFactory
import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password


class UserFactory(DjangoModelFactory):
    FACTORY_FOR = get_user_model()

    email = factory.Sequence(lambda n: 'account%s@test.com' % n)
    name = factory.Sequence(lambda n: 'John Doe %s' % n)
    password = factory.LazyAttribute(lambda o: make_password(o.email))
    is_superuser = False