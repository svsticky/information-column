# Network configuration

One of the most peculiar requirements for the server that has to connect to the information column, is its network configuration. After many attempts using a as-default-as-possible configuration, all the below settings were necessary for the system to successfully connect to the information column and send it new contents for its matrix display.

The IP address of the information column itself is more-or-less hard coded to be `131.211.83.245` (`infozuil.students.cs.uu.nl` also resolves to this).

## /etc/network/interfaces
```
auto lo
iface lo inet loopback

auto eth0
allow-hotplug eth0
iface eth0 inet static
        address 131.211.83.1
        netmask 255.255.255.0
        network 131.211.83.0
        broadcast 131.211.83.255

auto wlan0
allow-hotplug wlan0
iface wlan0 inet static
        address 10.0.1.220
        netmask 255.255.255.0
        network 10.0.1.0
        gateway 10.0.1.1
        dns-nameservers 10.0.1.1 8.8.8.8
wpa-passphrase <wpakey>
wpa-ssid <ssid>

iface default inet dhcp
```
The IP addresses associated with eth0 should not be changed, unless the configuration of the information column itself is changed accordingly.
Also, a local WLAN router is assumed at 10.0.1.1, that accepts static IP's in the 10.0.0/24 range.
Note that the wireless SSID and WPA key still has to be filled in.
