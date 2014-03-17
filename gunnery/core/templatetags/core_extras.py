from django import template

from task.models import Execution


register = template.Library()

icons_mapping = {
    "dashboard": "dashboard",
    "application": "desktop",
    "environment": "sitemap",
    "server": "puzzle-piece",
    "serverrole": "tags",
    "task": "tasks",
    "execution": "bars",
    "settings": "gear",
    "user": "user",
    "group": "group",
    "department": "building-o",
}

status_mapping = {
    Execution.PENDING: ["default", "clock-o", "Pending"],
    Execution.RUNNING: ["warning", "spinner fa-spin", "Running"],
    Execution.SUCCESS: ["success", "check", "Success"],
    Execution.FAILED: ["danger", "exclamation-triangle", "Failed"],
}


@register.simple_tag
def model_icon(model):
    if not model in icons_mapping:
        raise ValueError('Invalid icon name')
    return '<i class="fa fa-' + icons_mapping[model] + '"></i>'


@register.simple_tag
def execution_status(status):
    template = '<span class="label label-%s"><i class="fa fa-%s"></i> %s</span>' % tuple(status_mapping[status])
    return template