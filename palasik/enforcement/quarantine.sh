#!/bin/bash
DEVICE_IP=$1

echo "[PALASIK] Quarantine device $DEVICE_IP"
iptables -A INPUT -s $DEVICE_IP -j DROP
