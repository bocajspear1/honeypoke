# HoneyPoke

![HoneyPoke Logo](honeypoke.png)

## What is HoneyPoke?

HoneyPoke is a Python application that shows you what attackers are poking around with. It sets up listeners on certain ports and records whatever is sent to it. 

This information can be logged to different places, the currently supported outputs are:
* Files
* ElasticSearch

HoneyPoke supports both Python2 and Python 3.

## Pre-Reqs

* You'll need the dev packages for your version of Python, as well as the libpcap dev libraries (`libpcap-dev`).
* (If using ElasticSearch output, which is recommended) To improve the IP to location lookup for ElasticSearch, you should install the `libmaxminddb` packages. Instructions can be found here: https://github.com/maxmind/libmaxminddb.
* Change the port your SSH server is listening on so you can place a HoneyPoke listener there instead.

## Installation

1. Clone or download this repo
2. Install dependencies: 
    * Python 2: `sudo pip -r requirements2.txt` 
    * Python 3: `sudo pip3 -r requirements3.txt` 
3. Be sure the `large` and `logs` directories are writeable by the user and group you plan to have HoneyPoke running under.

## Setup and Usage

1. Copy `config.json.default`  to `config.json` Modify the config file. 
    * `loggers` enables and disables loggers. This done with the `active` key under the respective loggers. Some may need extra configuation, which is in the `config` key.
    * The `ports` key sets the listeners that you will be creating. Each sets the protocol (`tcp` or `udp`), and the port. An optional settings is `ssl`, which wraps the socket with SSL. (NOTE: This means the socket will ignore non-SSL connections`config.json.default` contains a curated list of ports. Modify as you want.
    * `ignore_watch` is used ignore connections that you create to particular systems. This is useful for things like ElasticSearch so that these connections are not recorded as missing ports.
    * `ssh_port` is used ignore your SSH connections for missed port counts. Set this to the port SSH is listening on so that your 'missed' port count for your SSH server doesn't explode.
    * `user` is the user you want the script to drop privileges to.
    * `group` is the group you want the script to drop privileges to.
2. Run HoneyPoke with:
    * Python 2 `sudo python2 start.py --config config.json`
    * Python 3 `sudo python3 start.py --config config.json`

**Note:** Be sure you have nothing listening on the selected ports, or else HoneyPoke will not fully start.

**Note:** HoneyPoke is run using sudo (aka root). It will drop privileges though, and it will not process any connections until permissions are dropped. The script should report when privileges are dropped.

**Note:** You can also use the `config.json.nmap` file, which contains all the common ports Nmap scans. Beware! Due to the number of ports, it takes awhile to start up.

## Binary and Large files

Binary data is converted into the Python bytes format (`'\x00'`). This ensures the data is stored safely, but also keeps strings in the binary readable. For small binary data (<512 bytes), HoneyPoke will send the data as is to the output. If the data is larger than 512 bytes, HoneyPoke will store the output into a file in the `large` directory and the location to the file is logged instead of the entire contents.

See [here](https://stackoverflow.com/questions/43337544/read-bytes-string-from-file-in-python3) if you want to load the Python bytes format for manipulation or conversion.

## Missed ports

Ports that have no listener are recorded by HoneyPoke in the `logs/missed.json` file in JSON format with the number of misses for the port. Use this is to modify your listeners with new ports.

## Contributing

Go at it! Open an issue, make a pull request, fork it, etc.

## License

This project is licensed under the GNU General Public License (GPL) v3.0