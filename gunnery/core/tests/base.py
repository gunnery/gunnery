from django.test import TestCase
from guardian.shortcuts import assign_perm
from account.tests.fixtures import UserFactory
from core.tests.fixtures import DepartmentFactory


class LoggedTestCase(TestCase):
    logged_is_superuser = False

    @classmethod
    def setUpClass(cls):
        cls.user = UserFactory(is_superuser=cls.logged_is_superuser)
        cls.setup_department()

    @classmethod
    def setup_department(cls):
        cls.department = DepartmentFactory()
        assign_perm('core.view_department', cls.user, cls.department)

    def setUp(self):
        result = self.client.login(username=self.user.email, password=self.user.email)
        session = self.client.session
        session['current_department_id'] = self.department.id
        session.save()
        self.assertTrue(result, 'Login failed')


class BaseModalTestCase(LoggedTestCase):
    url = None
    object_factory = None

    @classmethod
    def setUpClass(cls):
        super(BaseModalTestCase, cls).setUpClass()
        cls.object = cls.object_factory()


class BaseModalTests(object):
    def test_create_form(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_edit_form(self):
        response = self.client.get(self.get_url_with_id())
        self.assertEquals(response.status_code, 200)

    def test_delete(self):
        response = self.client.post(self.get_url_with_id())
        self.assertEquals(response.status_code, 200)

    def get_url_with_id(self):
        return self.url + str(self.object.id) + '/'