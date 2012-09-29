import errno
import os
import socket


def sd_notifyd(env, unset_environment=False):
    """More pythonic sd_notify that takes a dictionary."""
    state = '\n'.join(['{0}={1}'.format(k,v) for (k,v) in env.iteritems()])
    return sd_notify(unset_environment, state)

def sd_notify(unset_environment, state):
    """Notify service manager about start-up completion and other daemon status changes.

    This is reimplementation of systemd's reference sd_notify.

    """
    sock = None

    try:
        if not state:
            return -errno.EINVAL

        e = os.environ.get('NOTIFY_SOCKET', None)
        if not e:
            return 0
        if e[0] not in ('@', '/') or len(e) == 1:
            return -errno.EINVAL

        if e[0] == '@':
            e = '\0' + e[1:]

        # SOCK_CLOEXEC was added in Python 3.2 and requires Linux >= 2.6.27.
        #sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM | socket.SOCK_CLOEXEC)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

        # sendmsg() was added in Python 3.3,
        # so using sendto() instead.
        # Python seems to lack MSG_NOSIGNAL flag.
        if sock.sendto(state, e) > 0:
            return 1
    except e:
        pass
    finally:
        if sock:
            sock.close()
        if unset_environment:
            if 'NOTIFY_SOCKET' in os.environ:
                del os.environ['NOTIFY_SOCKET']
    return 0
