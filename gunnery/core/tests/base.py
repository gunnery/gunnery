from django.core.urlresolvers import reverse
from django.test import TestCase
from guardian.shortcuts import assign_perm
from account.tests.fixtures import UserFactory
from core.tests.fixtures import DepartmentFactory


class LoggedTestCase(TestCase):
    logged_is_superuser = False
    logged_is_manager = False
    department = False

    @classmethod
    def setUpClass(cls):
        cls.user = UserFactory(is_superuser=cls.logged_is_superuser)
        cls.setup_department()

    @classmethod
    def setup_department(cls):
        cls.department = DepartmentFactory()
        if cls.logged_is_manager:
            assign_perm('core.edit_department', cls.user, cls.department)
        assign_perm('core.view_department', cls.user, cls.department)

    def setUp(self):
        result = self.client.login(username=self.user.email, password=self.user.email)
        session = self.client.session
        session['current_department_id'] = self.department.id
        session.save()
        self.assertTrue(result, 'Login failed')


class BaseModalTestCase(LoggedTestCase):
    url_name = None
    url_params = {}
    object_factory = None

    @classmethod
    def setUpClass(cls):
        super(BaseModalTestCase, cls).setUpClass()
        cls.object = cls.object_factory()

    def url(self, *args, **kwargs):
        return reverse(self.url_name, args=args, kwargs=(dict(self.url_params.items() + kwargs.items())))

    def _test_create(self, data):
        response = self.client.post(self.url(), data)
        obj = self.get_created_object(data)
        self.assertContains(response, 'true')
        return response, obj

    def get_created_object(self, data):
        try:
            obj = self.object_factory.FACTORY_FOR.objects.get(**data)
        except self.object_factory.FACTORY_FOR.DoesNotExist:
            self.fail('Object not created')
        return obj

    def _test_edit(self, obj, data):
        response = self.client.post(self.url(id=obj.id), data)
        self.assertContains(response, 'true')
        obj_updated = self.object_factory.FACTORY_FOR.objects.get(pk=obj.id)
        return response, obj_updated


class BaseModalTests(object):
    def test_create_form(self):
        response = self.client.get(self.url())
        self.assertEquals(response.status_code, 200)

    def test_edit_form(self):
        response = self.client.get(self.url(id=self.object.id))
        self.assertEquals(response.status_code, 200)

    def test_delete(self):
        response = self.client.post(self.url(id=self.object.id))
        self.assertEquals(response.status_code, 200)
