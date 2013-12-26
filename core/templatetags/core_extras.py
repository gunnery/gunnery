from django import template
from core.models import Execution
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
}

status_mapping = {
	Execution.SUCCESS: ["success", "check", "Success"],
	Execution.RUNNING: ["warning", "spinner fa-spin", "Running"],
	Execution.FAILED: ["danger", "exclamation-triangle", "Failed"],
}

@register.simple_tag
def model_icon(model):
	if not model in icons_mapping:
		raise ValueError('Invalid icon name')
	return '<i class="fa fa-'+icons_mapping[model]+'"></i>'

@register.simple_tag
def execution_status(status):
	template = '<span class="label label-%s"><i class="fa fa-%s"></i> %s</span>' % tuple(status_mapping[status])
	return template