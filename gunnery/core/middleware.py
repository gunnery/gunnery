from guardian.shortcuts import get_objects_for_user


class CurrentDepartment(object):
    """ Set current_department_id in request object
    """
    def process_request(self, request):
        if not request.user.is_authenticated():
            return
        if not 'current_department_id' in request.session:
            allowed_departments = get_objects_for_user(request.user, 'core.view_department')
            if allowed_departments.count():
                request.session['current_department_id'] = allowed_departments.first().id
                request.current_department_id = request.session['current_department_id']
            else:
                request.current_department_id = None
        else:
            request.current_department_id = request.session['current_department_id']

