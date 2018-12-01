#!/usr/bin/env python3

##############################################
# The MIT License (MIT)
# Copyright (c) 2016 Kevin Walchko
# see LICENSE for full details
##############################################
from __future__ import print_function
from pyservos import Packet
from pyservos import ServoSerial
import sys
import time
import pyservos
from collections import OrderedDict


def makeAngleReadPacket(id):
    servo = Packet(pyservos.AX12)  # remove
    pkt = servo.makeReadPacket(id, 36,2)  # self.base.makeReadPacket()
    return pkt


def get(port, IDs, bcm_pin, retry=3):
    """
    Sends a ping packet to ID's from 0 to maximum and prints out any returned
    messages.
    Actually send a broadcast and will retry (resend) the ping 3 times ...
    """
    valid_return = False

    s = ServoSerial(port, pi_pin=bcm_pin)

    try:
        s.open()
    except Exception as e:
        print('-'*40)
        print(sys.argv[0], ':')
        print(e)
        exit(1)

    servo = Packet(pyservos.AX12)

    found_servos = {}

    # print("read:")
    for id in IDs:
        # print(id, end=' ')
        pkt = makeAngleReadPacket(id)
        s.write(pkt)

        valid_return = False

        # as more servos add up, I might need to increase the cnt number???
        for cnt in range(retry):
            ans = s.read()

            if ans:
                valid_return = True
                pkts = servo.decodePacket(ans)
                # print(pkts)
                for pkt in pkts:
                    if pkt[:5] == [0xff,0xff,id,4,0]:
                        angle = ((pkt[6] << 8) + pkt[5]) * 0.29  # cnts to deg
                        found_servos[id] = angle
                # print('Found')
                break
            if not valid_return:
                print(id, 'ERROR: Could not read servo angle')

            time.sleep(0.1)

    s.close()

    return valid_return, found_servos


if __name__ == "__main__":
    port = '/dev/serial0'
    ok, servos = get(port, range(1,17), 17)

    if ok:
        servos = OrderedDict(servos)

        print('-[Servos 0-300 deg]---------------------------')
        for k, v in servos.items():
            print(" {:.<10} {:5.1f} deg".format(k,v))
    else:
        print('No servos found')
