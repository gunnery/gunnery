# Gunnery

[![Build Status](https://travis-ci.org/Eyjafjallajokull/gunnery.png?branch=master)](https://travis-ci.org/Eyjafjallajokull/gunnery)

Gunnery is a multipurpose task execution tool for distributed systems with web-based interface.

If your application is divided into multiple servers, you are probably connecting to them via ssh and executing over and over the same commands. Clearing caches, restarting services, backups, checking health. Wouldn't it be cool if you could do that from browser or smartphone? Gunnery is here for you!

### Features

    Support for wide variety of tools
        Thanks to simple design it's possible to integrate with tools like capistrano, ant, phing, fabric, make, or puppet

    Designed for distributed systems
        Handles multi-environment applications with many servers

    Usable for deployment, service control, backups
        Almost any command executed in shell can be turned into Gunnery task

    Secure remote execution
        Certificate based authentication provides secure access to your network

    Web-based interface
        Clear, responsive interface pleases eye and enables usage on mobile devices

    User notifications
        Team members will be notified when tasks are executed

### Screenshots

![test](https://raw.github.com/Eyjafjallajokull/gunnery/gh-pages/img/1.png)
![test](https://raw.github.com/Eyjafjallajokull/gunnery/gh-pages/img/2.png)
![test](https://raw.github.com/Eyjafjallajokull/gunnery/gh-pages/img/fig.gif)

### Installation

Step by step install instructions are described on [wiki page](https://github.com/Eyjafjallajokull/gunnery/wiki/Install).

### Feedback

Please submit feedback, bugs, feature requests [here](https://github.com/Eyjafjallajokull/gunnery/issues).

### Contribute

Vagrant configuration is available for easy development, included Puppet rules will build complete environment. [Read more](https://github.com/Eyjafjallajokull/gunnery/wiki/Develop)
