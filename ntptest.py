"""
Example code for querying the NTP synchronized status over dbus

The Python version of the example at
https://docs.resin.io/runtime/runtime/#checking-if-device-time-is-ntp-synchronized

Using dbus-send, the command is:

$ dbus-send \
  --system \
  --print-reply \
  --reply-timeout=2000 \
  --type=method_call \
  --dest=org.freedesktop.timedate1 \
  /org/freedesktop/timedate1  \
  org.freedesktop.DBus.Properties.GetAll \
  string:"org.freedesktop.timedate1"

On balena.io devices need to set the system dbus address:
DBUS_SYSTEM_BUS_ADDRESS=unix:path=/host/run/dbus/system_bus_socket
"""
from time import sleep
import dbus

def python_from_dbus(obj):
    """dbus object to Python object conversion, simplified version from
    http://www.programcreek.com/python/example/13530/dbus.Boolean
    """
    if isinstance(obj, dbus.Boolean):
        python_obj = bool(obj)
    elif isinstance(object, dbus.String):
        python_obj = str(obj)
    elif isinstance(obj, (dbus.Byte,
                          dbus.Int16,
                          dbus.Int32,
                          dbus.Int64,
                          dbus.UInt16,
                          dbus.UInt32,
                          dbus.UInt64)):
        python_obj = int(obj)
    elif isinstance(obj, dbus.Double):
        python_obj = float(obj)
    else:
        raise TypeError("Unhandled %s" % obj)
    return python_obj


class NTPQuery:
    """ Querying the NTP status over dbus
    """

    def __init__(self):
        self._bus = dbus.SystemBus()
        self._proxy = self._bus.get_object('org.freedesktop.timedate1',
                                           '/org/freedesktop/timedate1')
        self._interface = dbus.Interface(self._proxy, 'org.freedesktop.DBus.Properties')
        self.status = self.get_status()

    def get_raw_status(self):
        """Get the dbus properties of timedate1
        """
        try:
            properties = self._interface.GetAll('org.freedesktop.timedate1')
        except dbus.exceptions.DBusException as err:
            raise err
        return properties

    def get_status(self):
        """Get all available status from timedate1
        """
        raw_status = self.get_raw_status()
        status = {}
        for key in raw_status:
            try:
                status[str(key)] = python_from_dbus(raw_status[key])
            except TypeError:
                # Should not have type returned that the conversion cannot handle
                pass
        self.status = status
        return self.status

    def get_ntp_syncronized(self):
        """Extract NTPSynchronized status
        """
        return self.get_status()['NTPSynchronized']

if __name__ == "__main__":
    NTP = NTPQuery()
    while True:
        if NTP.get_ntp_syncronized():
            print("NTP synchronized, good!")
        else:
            print("NTP not synchronized, bad.")
        sleep(15)
