# Gunnery

Gunnery is multipurpose task execution tool for distributed systems with easy to use interface.

### Features

* Supports capistrano, ant, phing, fabric, make, puppet, or any other tool
* Supports multistaging environments, and server grouping
* Usable for deployment, service control, backups
* Commands are executed via SHH with key authorization
* Clear, responsive interface

### Requirements

Gunnery is build on top of Django framework, and depends of few other technologies:

* Celery for background job handling
* Postgres which can be replaced by other supported by Django database

All python packages required by application are listend in pip requirements files.

### Installation

Recommended way:

// todo

Manual way:

1. Install Celery and Postgres
2. Install and configure python web stack: nginx and uwsgi
3. Clone gunnery
4. Configure project
5. python manage.py syncdb

### Feedback

Submit feedback, bugs, feature requests [here](https://github.com/Eyjafjallajokull/gunnery/issues).

### Contribute

Vagrant+Puppet configuration is available for easy development [gunnery-vagrant](https://github.com/Eyjafjallajokull/gunnery-vagrant).
