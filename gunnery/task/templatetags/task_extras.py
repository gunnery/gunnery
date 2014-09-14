from django import template
from task.models import Execution

register = template.Library()

@register.inclusion_tag('partial/execution_list_inline.html', takes_context=True)
def last_activity_bar(context, related_to=None, no_title=False):
    if not related_to:
        raise Exception('related_to parameter is required')
    data = {}
    query = Execution.objects
    class_name = related_to.__class__.__name__
    if class_name == 'Application':
        query = query.filter(environment__application=related_to,
                     environment__in=context['allowed_environments'],
                     task__in=context['allowed_tasks'])
    elif class_name == 'Environment':
        query = query.filter(environment=related_to,
                     task__in=context['allowed_tasks'])
    elif class_name == 'Task':
        query = query.filter(task=related_to,
                     environment__in=context['allowed_environments'])
    elif class_name == 'CustomUser':
        query = query.filter(user=related_to,
                     environment__in=context['allowed_environments'],
                     task__in=context['allowed_tasks'])
        class_name = 'User'
    data['list'] = query.order_by('-time_created')[:4]
    data['model_name'] = class_name.lower()
    data['related_to'] = related_to
    data['no_title'] = no_title
    return data