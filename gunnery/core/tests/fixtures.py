from factory.django import DjangoModelFactory
import factory
from ..models import *


class DepartmentFactory(DjangoModelFactory):
    FACTORY_FOR = Department

    name = factory.Sequence(lambda n: 'Department_%s' % n)


class ApplicationFactory(DjangoModelFactory):
    FACTORY_FOR = Application

    name = factory.Sequence(lambda n: 'Application_%s' % n)
    department = factory.SubFactory(DepartmentFactory)


class EnvironmentFactory(DjangoModelFactory):
    FACTORY_FOR = Environment

    name = factory.Sequence(lambda n: 'Environment_%s' % n)
    application = factory.SubFactory(ApplicationFactory)


class ServerRoleFactory(DjangoModelFactory):
    FACTORY_FOR = ServerRole

    name = factory.Sequence(lambda n: 'ServerRole_%s' % n)
    department = factory.SubFactory(DepartmentFactory)

class ServerFactory(DjangoModelFactory):
    FACTORY_FOR = Server

    name = factory.Sequence(lambda n: 'Server_%s' % n)
    host = 'localhost'
    user = 'user'
    environment = factory.SubFactory(EnvironmentFactory)

    @factory.post_generation
    def roles(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for role in extracted:
                self.roles.add(role)