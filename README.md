# rpi
Dont tamper with the step sleep variable it can mess up the rotation speed of the stepper motor.
The desiered rotation amount can be set manually by changing the rotation variable and it is allowed to be decimal as well.
The device index variable should match with that of the lsusb of the usb device else it will throw an error upon initialisation.
The recording duration can be adjusted by changing the duration consatnt (r.record(source, duration = x)).
The method listen and record be used in exchange.
