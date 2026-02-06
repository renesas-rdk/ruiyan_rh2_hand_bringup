#!/bin/bash
# This script initializes the RUIYAN RH2 hardware for the dexhand demo.
# Hardware used: RUIYAN RH2 dexhand, PEAK System PCAN-USB.
# Input:
# - can interface name (e.g., can0) is requested from the user.
# Usage: ./ruiyan_rh2_init.sh

### Common setup ###
# Map of modules to build: CONFIG_MAP[config_name]="module_name"
declare -A CONFIG_MAP

# User need to find the module names for their hardware setup.
# Syntax: CONFIG_MAP[<CONFIG_NAME>]="<module-name>"

# Dependencies are getted from: https://www.kernelconfig.io/config_can_peak_usb?q=&kernelversion=6.10.14&arch=arm64
CONFIG_MAP[CONFIG_CAN_PEAK_USB]="peak_usb"
# CONFIG_CAN_DEV already built-in
# CONFIG_CAN_NETLINK already built-in
# CONFIG_NETDEVICES already built-in
# CONFIG_USB already built-in

# === Check if modules are already built-in ===
for config in "${!CONFIG_MAP[@]}"; do
    module="${CONFIG_MAP[$config]}"

    # Check if module is built-in
    if zcat /proc/config.gz | grep -Eq "^${config}=(y)"; then
        echo "Module $module is built into the kernel."
        unset CONFIG_MAP[$config]
    fi
done

# === Load the modules ===
for config in "${!CONFIG_MAP[@]}"; do
    value="${CONFIG_MAP[$config]}"
    module="${value##* }"

    # Check if the module file exists before loading
    if ! modinfo "$module" &>/dev/null; then
        echo "Module file for $module not found. Please ensure it is built and available."
        exit 1
    fi

    sudo modprobe "$module"
    if [ $? -ne 0 ]; then
        echo "Failed to load module $module. Please check the build process."
        exit 1
    fi
    echo "Module $module loaded successfully."
done

### Hardware specific setup: RUIYAN RH2 dexhand and PEAK System PCAN-USB ###
# Request CAN interface name from user
echo
echo "Dmesg output for CAN interfaces:"
echo
sudo dmesg | grep -i --color=always can | tail -n 10
echo
echo "If you do not see your CAN interface, please check the hardware connection and ensure the PCAN-USB device is connected."
read -p "Enter the CAN interface name (e.g., can0): " CAN_INTERFACE

# Check if the CAN interface exists
if ! ip link show | grep -q "$CAN_INTERFACE"; then
    echo "CAN interface $CAN_INTERFACE does not exist. Please check the interface name."
    exit 1
fi

# Bring up the CAN interface
echo "Bringing up CAN interface $CAN_INTERFACE..."
sudo ip link set $CAN_INTERFACE up type can bitrate 1000000
if [ $? -ne 0 ]; then
    echo "Failed to bring up CAN interface $CAN_INTERFACE."
    exit 1
fi

sudo ip link set $CAN_INTERFACE txqueuelen 1000
if [ $? -ne 0 ]; then
    echo "Failed to set txqueuelen for CAN interface $CAN_INTERFACE."
    exit 1
fi

sudo ifconfig $CAN_INTERFACE up
if [ $? -ne 0 ]; then
    echo "Failed to set up CAN interface $CAN_INTERFACE."
    exit 1
fi

echo "CAN interface $CAN_INTERFACE is up and running."
echo "Please run the launch file to start the RUIYAN RH2 hand driver with the specified CAN interface."

