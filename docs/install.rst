Installation
^^^^^^^^^^^^

Instructions on this page will guide you through installation process. You can choose to use puppet tool or setup everything manually.

Dependencies
~~~~~~~~~~~~

Supported python version is 2.7, below is the list of packages required to run project:

.. include:: ../requirements/common.txt
   :literal:

Provisioning with Puppet
~~~~~~~~~~~~~~~~~~~~~~~~

Gunnery repository contains puppet manifests, which can help setting up infrastructure required to run application.
Puppet manifests are supported for systems:

- Ubuntu 13.10 (raring)

Below are listed commands which will setup full-stack Gunnery instance on a bare bones server::

    su
    git clone --recurse-submodules https://github.com/Eyjafjallajokull/gunnery.git /var/gunnery
    cd /var/gunnery/puppet
    cp manifests/hieradata/local.template.yaml manifests/hieradata/local.yaml
    vim manifests/hieradata/local.yaml # set secrets
    chown 700 manifests/hieradata/local.yaml
    bash ./install.sh # ensure puppet 3 is installed
    FACTER_environment=production puppet apply manifests/base.pp --hiera_config manifests/hiera.yaml --modulepath=modules --manifestdir=manifests
    cd /var/gunnery
    export DJANGO_SETTINGS_MODULE="gunnery.settings.production"
    source /var/gunnery/virtualenv/production/bin/activate
    make build
    python manage.py createsuperuser

The last step is to edit ``/var/gunnery/gunnery/gunnery/settings/production.py`` and set the
``ALLOWED_HOSTS`` directive to the domain (or IP address) that your instance will be running on.
Boom, if everything went well you have working application.

Manual Installation
~~~~~~~~~~~~~~~~~~~

Gunnery may seem like a simple app, but it depends on a few components.
This document will guide you through the process of installing all of
them. For simplicity's sake, it's assumed that the host machine is
Debian-based and that all services are running on a single machine.

::

              Nginx
                |
                v
              uWSGI
                |
                v
              Gunnery <----> Database <----> Celery
                |                              |
                +----------> Queue <-----------+

Setup Database
--------------

PostgreSQL is the recommended database for Django projects, although
other types may be used as well.

-  Postgres installation instructions
   http://www.postgresql.org/docs/8.0/static/installation.html
-  Ubuntu guide https://help.ubuntu.com/community/PostgreSQL

A ``gunnery`` user without the ``createdb`` or ``superuser`` permissions
must be created along with a database ``gunnery``, which will be owned
by the ``gunnery`` user.

In short:

::

    sudo apt-get install postgresql postgresql-contrib
    sudo -u postgres psql postgres
    \password postgres
    sudo -u postgres createuser -D -S -P gunnery
    sudo -u postgres createdb -O gunnery gunnery

Setup Application
-----------------

Download the gunnery application by cloning the repository. The
recommended path is ``/var/gunnery``:

::

    sudo git clone --recurse-submodules git@github.com:Eyjafjallajokull/gunnery.git /var/gunnery
    sudo cd /var/gunnery

Under the ``requirements`` folder you will find lists of packages
required for different environments. To install production packages:

::

    pip install -r requirements/production.txt

Next, adjust the settings inside ``gunnery/settings/production.py``
file. In particular, add the domain (or IP address) of your instance to
the ``ALLOWED_HOSTS`` list.

Now we'll need to setup the database we created earlier for gunnery. To
do so, we'll need to synchronize the database's schema with gunnery and
run any necessary migrations. Then, we create the initial user and
prepare the static files.

::

    export DJANGO_SETTINGS_MODULE="gunnery.settings.production"
    export SECRET_KEY="<insert random string here>"
    python manage.py syncdb # synchronize gunnery schema to postgres
    python manage.py migrate # run any necessary database schema migrations
    python manage.py collectstatic # prepare static files to be served
    python manage.py createsuperuser # create the initial user

To test that the application is working, you can use Django's built-in HTTP server:

::

    python manage.py runserver

Optionally you can build html documentation with command: ::

    cd /var/gunnery/docs
    make htmlembedded

Install RabbitMQ
----------------

Celery requires a messaging queue for its operation, RabbitMQ being the
recommended option. Refer to the Celery documentation for information
about using alternatives.

::

    sudo apt-get install rabbitmq

Configure Celery
----------------

Celery was installed in a previous step (``pip install``), it needs to be configured now.

::

    # Copy provided init-script for Celery to /etc/init.d
    sudo cp /var/gunnery/puppet/modules/component/files/celery.initd /etc/init.d/celeryd
    # Copy provided Celery configuration defaults to /etc/default
    sudo cp /var/gunnery/puppet/modules/component/templates/celery.default.erb /etc/default/celeryd
    # Edit provided default to your satisfaction
    sudo vim /etc/default/celeryd
    sudo service celeryd start

Configure uWSGI
---------------

We're going to use uWSGI to manage our Python processes. Just like celery it was installed by pip as a dependency. We need
to create init script for it. Copy the example file and adjust variables (search for ``<% ... %>``)

::

    # Copy example file to /etc/init.d
    sudo cp /var/gunnery/puppet/modules/component/templates/uwsgi.erb /etc/init.d/uwsgi
    sudo chmod u+x /etc/init.d/uwsgi # Make init script executable
    sudo vim /etc/init.d/uwsgi

-  replace ``<%= @log_path %>`` with ``/var/gunnery/log``
-  replace ``<%= @run_path %>`` with ``/var/gunnery/run``
-  replace ``<%= @virtualenv_path %>`` with ``/var/gunnery/virtualenv``

Next, setup gunnery-specific configuration:

::

    sudo mkdir -p /etc/uwsgi/apps-enabled # Create directory for gunnery uWSGI config
    # Copy provided example config to newly created folder
    sudo cp /var/gunnery/puppet/modules/component/templates/uwsgi.ini.erb /etc/uwsgi/apps-enabled/gunnery.ini
    sudo vim /etc/uwsgi/apps-enabled/gunnery.ini

-  replace ``<%= @app_name %>`` with ``gunnery``
-  replace ``<%= @app_path %>`` with ``/var/gunnery/gunnery``
-  replace ``<%= @log_path %>`` with ``/var/gunnery/log``
-  replace ``<%= @run_path %>`` with ``/var/gunnery/run``
-  replace ``<%= @virtualenv_path %>`` with ``/var/gunnery/virtualenv``
-  replace ``<%= @environment %>`` with ``production``

To make sure your config works, try starting the uWSGI service, check
the logs for errors, and validate if the socket file exists.

::

    sudo service uwsgi start

Install Nginx
-------------

No magic here. Simply install, copy the provided template, and customize
to your needs.

::

    sudo apt-get install nginx
    sudo cp /var/gunnery/puppet/modules/component/templates/nginx.django.conf.erb /etc/nginx/sites-enabled/gunnery
    sudo vim /etc/nginx/sites-enabled/gunnery
    sudo service nginx reload

Support
~~~~~~~

If you run into trouble and can’t figure out how to solve it yourself, you can get help via `Github issue tracker <https://github.com/Eyjafjallajokull/gunnery/issues/new>`__.