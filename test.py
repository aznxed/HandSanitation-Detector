import serial.tools.list_ports

ports = list(serial.tools.list_ports.comports())
connectedDevice = None

for p in ports:
    if 'Arduino' in p[1]:
        try:
            connectedDevice = Arduino(p[0])
            print ("Connected to" + str(connectedDevice))
            break
            except serial.SerialException:\
                print ("Arduino detected but unable to connect to " + p[0])
    if connectedDevice is None:
    	exit("Failed to connect to Arduino")
