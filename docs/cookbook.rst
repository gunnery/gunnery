Cookbook
~~~~~~~~

Following section contains common recipes for integrating Gunnery with external tools.

Capistrano
----------

1. In department settings create *build* role
2. Create application and environment.
3. Create server pointing to your build server (where capistrano is installed).
4. Assign *build* role to this server
5. For every capistrano task - create gunnery task. For example if you have deploy task enter following command in gunnery task form
   ``cd /path/to/capistrano/dir; cap deploy``.

If your capistrano task requires parameter, for example ``cap deploy -S branch=master``,
define required parameter ``branch`` in gunnery form and change command to ``cap deploy -S branch=${branch}``

Example capistrano tasks:

- :download:`With no parameters <_static/capistrano-example1.png>`
- :download:`With env and branch parameters <_static/capistrano-example2.png>`
