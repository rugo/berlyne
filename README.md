# Docker-Compose branch
This branch makes the switch from Vagrant to docker-compose using a modified uptomate.

So far it seems to work to install and automatically start/stop the services.

TODO:

* Status doesnt seem to work. Problem is shown immediately in the course, even if container is not running yet.
* Test if all WUI actions work
* Maybe refactor to make code nicer
* Remove `vagrant_libs` folder

Deploy new Problems:

* Copy them into `problems` (probably in `/opt/berlyne/berlyne/problems`) folder, then add them via web interface.

# Berlyne 
Berlyne is a trainings platform for applied IT security.
 
The basic workflow is this:

* **Create a course**, activate scoreboard and write ups if wanted 
* **Assign software problems** - in the form of CTF tasks - to the course 
* Berlyne starts the required problems in virtual machines
* The problems description in the course gets updated with correct IP, ports and downloads
* **Participants join** the course and solve the problems
* Teacher accesses the course **write ups**

All that is done via a Web UI.

The platform is ready to be worked with, but is also still under heavy construction.

## Live Demo

Check out the live demo [here](https://hack.redrocket.club)!

Just register an account and join the course _Example_.

The given email adress is not used in any way except for the "Lost Password" function.

## Requirements

The current Version **0.1** is tested with **Python 3.4** and **Django 1.10** on Debian but should also work
with higher Python versions and other Unix derivates.

## Installing
On how to install Berlyne, please consult the wiki page [Installing Berlyne](https://github.com/rugo/berlyne/wiki/Installing-Berlyne)

## Problems
Tasks in Berlyne are called problems, for pun reasons.

It is very easy to create your own problems, see the [wiki](https://github.com/rugo/berlyne/wiki/Creating-Problems) 
for details.

Also have a look at the example problems:

* [Example Web Problem](https://github.com/rugo/berlyne/wiki/Example-Web-Problem)
* [Example Problem delivered with xinetd](https://github.com/rugo/berlyne/wiki/Example-xinetd-Problem)
* [Collection of example Problems](https://github.com/rugo/berlyne-example-problems)

## Finding Problems
Tasks can be shared via repository/download/usb stick/whatever, since they only consist of
[three files](https://github.com/rugo/berlyne/wiki/Creating-Problems).

Tasks shared by membes of the community are listed in the
[Problems Wiki Page](https://github.com/rugo/berlyne/wiki/Problem-list). 

On how to install them, please consult the [wiki](https://github.com/rugo/berlyne/wiki/Installing-Problems).

## Virtual Machines
Berlyne automatically creates and starts VMs in the background and maps required ports to
the host system.

Supported providers for launching those VMs are:

* Docker **for developement**, see [wiki](https://github.com/rugo/berlyne/wiki/Security-Considerations)
* VirtualBox
* DigitalOcean, which is a cloud provider (API-Key needed)

## Contributing
Pull-Requests are very welcome.

If you want to share a task, please make sure to add the url to our
[Berlyne Problems Blockhain](problems_blockchain.txt)
or just write an issue and I'll add it!

## Contact

You can directly contact me @ berlyne[at]ht11[dot]org
