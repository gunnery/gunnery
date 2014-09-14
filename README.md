# Gunnery

[![Build Status](https://travis-ci.org/gunnery/gunnery.png?branch=master)](https://travis-ci.org/gunnery/gunnery)

Gunnery is a multipurpose task execution tool for distributed systems with web-based interface.

If your application is divided into multiple servers, you are probably connecting to them via ssh and executing over and over the same commands. Clearing caches, restarting services, backups, checking health. Wouldn't it be cool if you could do that from browser or smartphone? Gunnery is here for you!

### Features

* **Support for a wide variety of tools** <br>
  Thanks to simple design it's possible to integrate with tools like capistrano, ant, phing, fabric, make, or puppet
* **Designed for distributed systems** <br>
  Handles multi-environment applications with many servers
* **Usable for deployment, service control, backups** <br>
  Every command executed in shell can be turned into a Gunnery task
* **Secure remote execution** <br>
  Certificate based authentication provides secure access to your network
* **Web-based interface** <br>
  Clear, responsive interface pleases eye and enables usage on mobile devices
* **User notifications** <br>
  Team members will be notified when tasks are executed
* **Permission system** <br>
  Create custom user groups and limit their access to specific environments or tasks

### Screenshots

![test](https://raw.github.com/Eyjafjallajokull/gunnery/gh-pages/img/1.png)
![test](https://raw.github.com/Eyjafjallajokull/gunnery/gh-pages/img/2.png)
![test](https://raw.github.com/Eyjafjallajokull/gunnery/gh-pages/img/fig.gif)

### Documentation

Step by step install instructions, and usage notes are available in [documentation](http://gunnery.readthedocs.org/en/latest/).

### Feedback

Please submit feedback, bugs, feature requests [here](https://github.com/Eyjafjallajokull/gunnery/issues).

### Contribute

Vagrant configuration is available for easy development, included Puppet rules will build complete environment. [Read more](http://gunnery.readthedocs.org/en/latest/develop.html)
