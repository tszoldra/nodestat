# Nodestat

![Python](https://img.shields.io/badge/Python-v^3.8-blue.svg?logo=python&longCache=true&logoColor=white&colorB=5e81ac&style=flat-square&colorA=4c566a)
![Paramiko](https://img.shields.io/badge/Paramiko-v^2.7.1-blue.svg?longCache=true&logo=python&style=flat-square&logoColor=white&colorB=5e81ac&colorA=4c566a)
![SCP](https://img.shields.io/badge/SCP-v0.13.2-blue.svg?longCache=true&logo=python&style=flat-square&logoColor=white&colorB=5e81ac&colorA=4c566a)

A simple commandline tool that connects to a list of hosts in the network and checks their basic usage statistics.
![nodestat](https://i.postimg.cc/d1YnSHnC/sample-output.png)
## Installation

**Simplest way: Compiled C version without any dependencies**:
```shell
$ git clone https://github.com/tszoldra/nodestat.git
$ cd nodestat
$ ./main ns.conf

# resize the terminal to have a wide window
```

**Python version: Installation of dependencies via `requirements.txt`**:

```shell
$ git clone https://github.com/tszoldra/nodestat.git
$ cd nodestat
$ python3 -m venv myenv
$ source myenv/bin/activate
$ pip3 install -r requirements.txt
$ python3 main.py ns.conf

# resize the terminal to have a wide window
```

## Usage
For C compiled version the program help:
```shell
$ ./main -h
```
or (in Python version)
```shell
$ python3 main.py -h
```
gives the following output:
```shell
usage: main.py [-h] [-n NAME [NAME ...]] [-s] config_file

Show usage of computation nodes. Warning: resize the terminal window to a large width.

positional arguments:
  config_file           configuration file

optional arguments:
  -h, --help            show this help message and exit
  -n NAME [NAME ...], --name NAME [NAME ...]
                        check only nodes given in the command line (discarding those from config file)
  -s, --short           show the basic info only

```

Replace the values in **ns.conf.example** with your values and rename this file to **ns.conf**:

* `REMOTE_HOSTNAME_LIST`: IP addresses or URLs of remote hosts with spaces between, eg. 'zoa8 clone108'
* `REMOTE_USERNAME`: Username for remote host.
* `REMOTE_PATH`: Remote directory to serve as destination for temporary script file uploads.

Example how to show stats for nodes specified in the command line rather than in the config file:
```shell
./main ns.conf -n zoa8 clone107 
```


*Remember to never commit secrets saved in config files to Github or anywhere else.*

-----

MIT License, forked from
https://github.com/hackersandslackers/paramiko-tutorial
