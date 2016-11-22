# HoneyPoke

![HoneyPoke Logo](honeypoke.png)

## What is HoneyPoke?

HoneyPoke is a Python application that shows you what attackers are poking around with. It sets up listeners on certain ports and records whatever is sent to it. 

This information can be logged to different places, the currently supported outputs are:
* Files
* ElasticSearch

HoneyPoke supports both Python2 and Python 3.

## Installation

1. Clone or download this repo
2. Install dependencies (You'll need `libpcap-dev` or its equivalent to install Scapy, as well as the Python dev packages): 
    * Python 2: `sudo pip -r requirements2.txt` 
    * Python 3: `sudo pip3 -r requirements3.txt` 
3. Be sure the `large` and `logs` directories are writeable by the user and group you plan to have HoneyPoke running under.

## Setup and Usage

1. Copy `config.json.default`  to `config.json` Modify the config file. 
    * `loggers` enables and disables loggers. This done with the `active` key under the respective loggers. Some may need extra configuation, which is in the `config` key.
    * The `ports` key sets the listeners that you will be creating. Each sets the protocol (`tcp` or `udp`), and the port. `config.json.default` contains a curated list of ports. Modify as you want.
    * `ignore_watch` is used ignore connections that you create to particular systems. This is useful for things like ElasticSearch so that these connections are not recorded as missing ports.
    * `user` is the user you want the script to drop privileges to
    * `group` is the group you want the script to drop privileges to
2. Run HoneyPoke with:
    * Python 2 `sudo python2 start.py --config config.json`
    * Python 3 `sudo python3 start.py --config config.json`

**Note:** Be sure you have nothing listening on the selected ports, or else HoneyPoke will not fully start.

**Note:** HoneyPoke is run using sudo (aka root). It will drop privileges though, and it will not process any connections until permissions are dropped. The script should report when privileges are dropped.

**Note:** You can also use the `config.json.nmap` file, which contains all the common ports Nmap scans. Beware! Due to the number of ports, it takes awhile to start up.

## Binary and Large files

If HoneyPoke determines input is binary or too large, it will store the output into a file in the `large` directory. The location to the file is logged instead of the entire contents.

## Missed ports

Ports that have no listener are recorded in HoneyPoke in the `logs/missed.log` file. Use this is to modify your listeners with new ports.

## Contributing

Go at it! Open an issue, make a pull request, fork it, etc.

## License

This project is licensed under the GNU General Public License (GPL) v3.0