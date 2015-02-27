# socketio-transport

SocketIO transport built on top of gevent-socketio and gearman as queue for tasks

# Instalation

All requirements are contains in requirements/production.txt file and could be installed by

pip install -r requirements/production.txt

# Run

Server could be run by

python process.py <options>

# Options

-p, --port - port for socketio server

-f, --policy-port - port for flash policy server

-l, --logfile - file for log
