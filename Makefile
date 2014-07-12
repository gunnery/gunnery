PYTHONBIN=python
APP=gunnery

.PHONY: build syncdb migrate collectstatic docs

build: syncdb migrate collectstatic docs

syncdb:
	(cd $(APP) && ${PYTHONBIN} manage.py syncdb)

migrate:
	(cd $(APP) && ${PYTHONBIN} manage.py migrate)

collectstatic:
	(cd $(APP) && ${PYTHONBIN} manage.py collectstatic --noinput)

docs:
	(cd docs && make htmlembedded)