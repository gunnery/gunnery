from factory.django import DjangoModelFactory
import factory
from ..models import *
from core.tests.fixtures import ApplicationFactory


class TaskFactory(DjangoModelFactory):
    FACTORY_FOR = Task

    name = factory.Sequence(lambda n: 'Task_%s' % n)
    application = factory.SubFactory(ApplicationFactory)

