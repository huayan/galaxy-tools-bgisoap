#!/bin/sh
#
# Galaxy init script written by Michael Rusch
#

### BEGIN INIT INFO
# Provides:                     galaxy
# Required-Start:               $local_fs $remote_fs $network
# X-UnitedLinux-Should-Start:   postgresql
# Required-Stop:                $local_fs $remote_fs $network
# X-UnitedLinux-Should-Stop:
# Default-Start:                3 5
# Default-Stop:                 0 1 2 6
# Short-Description:            Galaxy daemon
# Description:                  Start the Galaxy daemon
### END INIT INFO

#. /etc/rc.status
#rc_reset

GALAXY_RUN="./run.sh"
GALAXY_USER="peterli"

case "$1" in
    start)
        echo -n "Starting galaxy..."
        sudo -u $GALAXY_USER $GALAXY_RUN --daemon
        rc_done=$rc_done_up
        #rc_status -v
        ;;
    stop)
        echo -n "Stopping galaxy..."
        sudo -u $GALAXY_USER $GALAXY_RUN --stop-daemon
        #rc_status -v
        ;;
    restart)
        $0 stop
        $0 start
        #rc_status
        ;;
    *)
        echo "Usage: $0 start|stop|restart"
        exit 1
esac
#rc_exit
