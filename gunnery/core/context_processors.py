from django.utils.functional import SimpleLazyObject, cached_property
from guardian.shortcuts import get_objects_for_user
from core.models import Application


def sidebar(request):
    current_department_id = request.current_department_id if request.user.is_authenticated() else None
    departments = get_objects_for_user(request.user, 'core.view_department')
    return {
        'departments': departments,
        'application_list_sidebar': Application.objects.filter(
            department_id=current_department_id).prefetch_related('environments').order_by('name'),
        'current_department_id': current_department_id,
        'department': departments.filter(id=current_department_id).first(),
        'user': request.user
    }
