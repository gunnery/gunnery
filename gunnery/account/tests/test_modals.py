from account.tests.fixtures import UserFactory, DepartmentGroupFactory
from core.tests.base import BaseModalTestCase, BaseForbiddenModalTests, BaseModalTests


class ModalUserForbiddenTest(BaseModalTestCase, BaseForbiddenModalTests):
    url_params = {'app': 'account', 'form_name': 'user'}
    object_factory = UserFactory


class ModalUserTest(BaseModalTestCase, BaseModalTests):
    url_params = {'app': 'account', 'form_name': 'user'}
    object_factory = UserFactory
    logged_is_manager = True

    def get_admin_group(self):
        return self.department.groups.filter(system_name='admin')[0]

    def test_create(self):
        data = {'email': 'test@test.com', 'password': 'password', 'name': 'test test', 'groups': self.get_admin_group().id}
        response, obj = self._test_create(data)
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})

    def test_edit(self):
        obj = self.object_factory()
        data = {'email': 'test2@test.com', 'password': 'password', 'name': 'test2 test2', 'groups': self.get_admin_group().id}
        response, obj_updated = self._test_edit(obj, data)
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})
        self.assertEqual(obj_updated.name, 'test2 test2')

    def get_created_object(self, data):
        del data['password']
        return super(ModalUserTest, self).get_created_object(data)


class ModalDepartmentGroupForbiddenTest(BaseModalTestCase, BaseForbiddenModalTests):
    url_params = {'app': 'account', 'form_name': 'group'}
    object_factory = DepartmentGroupFactory

    @classmethod
    def getSetUpObjectData(cls):
        return {'department': cls.department}


class ModalDepartmentGroupTest(BaseModalTestCase, BaseModalTests):
    url_params = {'app': 'account', 'form_name': 'group'}
    object_factory = DepartmentGroupFactory
    logged_is_manager = True

    @classmethod
    def getSetUpObjectData(cls):
        return {'department': cls.department}

    def test_create(self):
        response, obj = self._test_create({'local_name': 'TestDepartmentGroup', 'department': self.department})
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})

    def test_edit(self):
        obj = self.object_factory(department=self.department)
        data = {'local_name': 'TestDepartmentGroup2'}
        response, obj_updated = self._test_edit(obj, data)
        self.assertJSONEqual(response.content, {"status": True, "action": "reload"})
        self.assertEqual(obj_updated.local_name, 'TestDepartmentGroup2')