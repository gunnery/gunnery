Contributing
^^^^^^^^^^^^

Gunnery is open source project managed using Git and hosted on Github.

#. `Check for open issues <https://github.com/Eyjafjallajokull/gunnery/issues>`_ or open a fresh issue to start a discussion around a feature idea or a bug.
#. Fork the `repository on Github <https://github.com/Eyjafjallajokull/gunnery>`_ to start making your changes.
#. Write a test which shows that the bug was fixed or that the feature works as expected.
#. Send a pull request and bug the maintainer until it gets merged and published. :)

Setup Vagrant environment
~~~~~~~~~~~~~~~~~~~~~~~~~

Project repository contains Vagrant configuration and Puppet provisioning manifests.

Puppet rules will install and configure, everything you need to start working on gunnery:

-  nginx
-  uwsgi
-  postgresql
-  celery
-  rabbitmq
-  virtualenv
-  gunnery application

Before you get started be sure you have installed
`VirtualBox <https://www.virtualbox.org/>`__ and `Vagrant
1.1+ <http://www.vagrantup.com>`__. Start by cloning this repository.

.. code:: bash

    git clone --recurse-submodules https://github.com/Eyjafjallajokull/gunnery.git
    cd gunnery
    vagrant up

By now you have working infrastructure for Gunnery application. In the
next steps you will create database tables, prepare static files and
create first user.

::

    vagrant ssh
    cd /vagrant/gunnery
    python manage.py syncdb
    python manage.py migrate
    python manage.py collectstatic
    python manage.py createsuperuser

Gunnery should be now accessible via address http://localhost:8080/.

Source code is mounted inside virtual machine under /vagrant/gunnery. With this setup you can easily edit code, test, commit and create pull requests to official repository.

Run tests
~~~~~~~~~

Gunnery uses nose test runner:

::

    python manage.py test --settings=gunnery.settings.test

Running a specyfic test:

::

    python manage.py test --settings=gunnery.settings.test task.tests.test_views:ApplicationTest.test_application

To print test coverage report:

::

    coverage run --source='.' manage.py test --settings=gunnery.settings.test
    coverage report

Create pull request
~~~~~~~~~~~~~~~~~~~

Please note the following guidelines for contributing:

* Contributed code must be written in the existing style.
* Run the tests before committing your changes. If your changes cause the tests to break, they won’t be accepted.
* If you are adding new functionality, you must include basic tests and documentation.

Pull request should be submitted to develop branch.
