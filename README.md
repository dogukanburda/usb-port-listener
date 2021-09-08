USB Port Listener System Service
===========================

This is a tool that performs actions when a USB device is plugged in or out.

It consists of a python script that creates a daemon process to run `pyudev`'s `Monitor` object.  
The Python script is bundled as onefile with `Pyinstaller` and can be automatically started as a `systemd` service.

### Create executable files with Pyinstaller

	pyinstaller --onefile daemon_start.py
	pyinstaller --onefile daemon_stop.py

If there is any issue with `pyudev` not being included in the executable, edit the `daemon_start.spec` file's to add it to its hidden imports with `hiddenimports=['pyudev']`

### Copy the executables to /opt
	
	sudo cp ./dist/daemon_start /opt
	sudo cp ./dist/daemon_stop /opt

### Copy the file to the service folder and navigate to it

	sudo cp portlistener.service /etc/systemd/system/
	cd /etc/systemd/system

#### Start the service
	
	sudo systemctl start portlistener

#### Verify the service is running

	sudo systemctl status portlistener

#### Enable the service to run automatically when the os boots

	sudo systemctl enable portlistener




Python daemonizer class
====================

[![Build Status](https://travis-ci.org/serverdensity/python-daemon.svg?branch=master)](https://travis-ci.org/serverdensity/python-daemon)

This is a Python class that will daemonize your Python script so it can continue running in the background. It works on Unix, Linux and OS X, creates a PID file and has standard commands (start, stop, restart) + a foreground mode.

Based on [this original version from jejik.com](http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/).

Usage
---------------------

Define a class which inherits from `Daemon` and has a `run()` method (which is what will be called once the daemonization is completed.

	from daemon import Daemon
	
	class pantalaimon(Daemon):
		def run(self):
			# Do stuff
			
Create a new object of your class, specifying where you want your PID file to exist:

	pineMarten = pantalaimon('/path/to/pid.pid')
	pineMarten.start()

Actions
---------------------

* `start()` - starts the daemon (creates PID and daemonizes).
* `stop()` - stops the daemon (stops the child process and removes the PID).
* `restart()` - does `stop()` then `start()`.

Foreground
---------------------

This is useful for debugging because you can start the code without making it a daemon. The running script then depends on the open shell like any normal Python script.

To do this, just call the `run()` method directly.

	pineMarten.run()

Continuous execution
---------------------

The `run()` method will be executed just once so if you want the daemon to be doing stuff continuously you may wish to use the [sched][1] module to execute code repeatedly ([example][2]).


  [1]: http://docs.python.org/library/sched.html
  [2]: https://github.com/serverdensity/sd-agent/blob/master/agent.py#L339
