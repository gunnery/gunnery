from guardian.shortcuts import get_objects_for_user


def sidebar(request):
    """ Returns data required by sidebar
    """
    current_department_id = request.current_department_id if request.user.is_authenticated() else None
    departments = get_objects_for_user(request.user, 'core.view_department')
    department = departments.filter(id=current_department_id).first()
    return {
        'departments': departments,
        'application_list_sidebar': get_objects_for_user(request.user, 'core.view_application').
            prefetch_related('environments').filter(department_id=current_department_id),
        'allowed_environments': get_objects_for_user(request.user, 'core.view_environment'),
        'allowed_tasks': get_objects_for_user(request.user, 'task.view_task'),
        'current_department_id': current_department_id,
        'department': department,
        'user': request.user,
        'can_manage_department': request.user.has_perm('core.change_department', department)
    }
