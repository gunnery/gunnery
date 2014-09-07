from django.core.urlresolvers import reverse
from guardian.shortcuts import assign_perm, get_objects_for_user
from core.models import ServerRole
from core.tests.base import BaseModalTestCase, BaseModalTests, BaseForbiddenModalTests
from core.tests.fixtures import ServerRoleFactory, ApplicationFactory, EnvironmentFactory, ServerFactory


class ModalServerroleForbiddenTest(BaseModalTestCase, BaseForbiddenModalTests):
    url_params = {'form_name': 'serverrole'}
    object_factory = ServerRoleFactory


class ModalServerroleTest(BaseModalTestCase, BaseModalTests):
    url_params = {'form_name': 'serverrole'}
    object_factory = ServerRoleFactory
    logged_is_manager = True

    def test_create(self):
        response, obj = self._test_create({'name': 'ServerRoleName'})
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})

    def test_edit(self):
        obj = self.object_factory(department=self.department)
        data = {'name': 'ServerRoleName2'}
        response, obj_updated = self._test_edit(obj, data)
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})
        self.assertEqual(obj_updated.name, 'ServerRoleName2')


class ModalApplicationForbiddenTest(BaseModalTestCase, BaseForbiddenModalTests):
    url_params = {'form_name': 'application'}
    object_factory = ApplicationFactory


class ModalApplicationTest(BaseModalTestCase, BaseModalTests):
    url_params = {'form_name': 'application'}
    object_factory = ApplicationFactory
    logged_is_manager = True

    @classmethod
    def getSetUpObjectData(cls):
        return {'department': cls.department}

    def test_create(self):
        response, obj = self._test_create({'name': 'ApplicationName'})
        self.assertJSONEqual(response.content,
                             {"status": True,
                              "action": "redirect",
                              "target": reverse('application_page', kwargs={'application_id': obj.id})})

    def test_edit(self):
        obj = self.object_factory(department=self.department)
        data = {'name': 'ApplicationName2'}
        response, obj_updated = self._test_edit(obj, data)
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})
        self.assertEqual(obj_updated.name, 'ApplicationName2')


class ModalEnvironmentForbiddenTest(BaseModalTestCase, BaseForbiddenModalTests):
    url_params = {'form_name': 'environment', 'parent_name': 'application'}
    object_factory = EnvironmentFactory

    @classmethod
    def setUpClass(cls):
        super(ModalEnvironmentForbiddenTest, cls).setUpClass()
        cls.application = ApplicationFactory(department=cls.department)
        cls.url_params['parent_id'] = cls.application.id


class ModalEnvironmentTest(BaseModalTestCase, BaseModalTests):
    url_params = {'form_name': 'environment', 'parent_name': 'application'}
    object_factory = EnvironmentFactory
    logged_is_manager = True
    application = None

    @classmethod
    def setUpClass(cls):
        super(BaseModalTestCase, cls).setUpClass()
        cls.application = ApplicationFactory(department=cls.department)
        cls.url_params['parent_id'] = cls.application.id
        cls.object = cls.object_factory(**cls.getSetUpObjectData())

    @classmethod
    def getSetUpObjectData(cls):
        return {'application': cls.application}

    def test_create(self):
        response, obj = self._test_create({'name': 'EnvironmentName', 'application': self.application.id})
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})

    def test_edit(self):
        application = ApplicationFactory(department=self.department)
        obj = self.object_factory(application=application)
        data = {'name': 'EnvironmentName2', 'application': self.application.id}
        response, obj_updated = self._test_edit(obj, data)
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})
        self.assertEqual(obj_updated.name, 'EnvironmentName2')



class ModalServerForbiddenTest(BaseModalTestCase, BaseForbiddenModalTests):
    url_params = {'form_name': 'server', 'parent_name': 'environment'}
    object_factory = ServerFactory

    @classmethod
    def setUpClass(cls):
        super(ModalServerForbiddenTest, cls).setUpClass()
        cls.application = ApplicationFactory(department=cls.department)
        cls.url_params['parent_id'] = cls.application.id


class ModalServerTest(BaseModalTestCase, BaseModalTests):
    url_params = {'form_name': 'server', 'parent_name': 'environment'}
    object_factory = ServerFactory
    logged_is_manager = True
    environment = None

    @classmethod
    def setUpClass(cls):
        super(BaseModalTestCase, cls).setUpClass()
        cls.environment = EnvironmentFactory(application=ApplicationFactory(department=cls.department))
        cls.url_params['parent_id'] = cls.environment.id
        cls.object = cls.object_factory(**cls.getSetUpObjectData())

    @classmethod
    def getSetUpObjectData(cls):
        return {'environment': cls.environment}

    def test_create(self):
        server_role = ServerRole.objects.filter(department=self.department).first()
        response, obj = self._test_create({'name': 'ServerName',
                                           'environment': self.environment.id,
                                           'roles': server_role.id,
                                           'host': 'host',
                                           'port': 22,
                                           'user': 'user',
                                           'method': 1,
        })
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})

    def test_edit(self):
        environment = EnvironmentFactory(application=ApplicationFactory(department=self.department))
        obj = self.object_factory(environment=environment)
        server_role = ServerRole.objects.filter(department=self.department).first()
        data = {'name': 'ServerName2',
               'environment': self.environment.id,
               'roles': server_role.id,
               'host': 'host',
               'port': 22,
               'user': 'user',
               'method': 1,}
        response, obj_updated = self._test_edit(obj, data)
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})
        self.assertEqual(obj_updated.name, 'ServerName2')
