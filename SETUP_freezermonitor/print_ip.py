#! /usr/bin/python3

import netifaces

def get_wlan0_ip():
    interface = 'wlan0'
    if interface in netifaces.interfaces():
        addr_list = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addr_list:
            return addr_list[netifaces.AF_INET][0]['addr']
    return None

ip_address = get_wlan0_ip()
print(ip_address)
