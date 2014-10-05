
import serial
import platform
import time
import zephyr
from zephyr.testing import simulation_workflow

def callback(value_name, value):
	#print value_name, value
	if value_name == "heartbeat_interval":
		print "RR {0:1.4f} at {1}".format(value, time.time())


def main():
    zephyr.configure_root_logger()

    serial_port_dict = {"Darwin": "/dev/tty.HXM016473-BluetoothSeri",
                        "Windows": 23}

    

    serial_port = serial_port_dict[platform.system()]
    ser = serial.Serial(serial_port)

    simulation_workflow([callback], ser)

if __name__ == "__main__":
    main()
