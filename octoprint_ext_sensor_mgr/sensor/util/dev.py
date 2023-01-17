import glob


def gpio_dev_list():
    return sorted(glob.glob('/dev/gpiochip*'))

def serial_dev_list():
    return sorted(glob.glob('/dev/ttyS*'))