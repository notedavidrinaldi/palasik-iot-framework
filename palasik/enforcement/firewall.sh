#!/bin/bash
DEVICE_IP=$1

iptables -A INPUT -s $DEVICE_IP -j ACCEPT
