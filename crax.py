#!/usr/bin/python2.7
# -*- coding: UTF-8 -*-

import pexpect
import os
import socket
import time

###############################################################
# Constants / Read from XML definition
###############################################################

CRAX_DIR_WORK = '/home/linpc/u12/1112/run'
CRAX_DIR_BUILD = '/home/linpc/u12/1112/build'
CRAX_PATH_QEMU = 'qemu-release/i386-softmmu/qemu'
CRAX_PATH_S2E_QEMU = 'qemu-release/i386-s2e-softmmu/qemu'

CRAX_BIN_QEMU = os.path.join(CRAX_DIR_BUILD, CRAX_PATH_QEMU)
CRAX_BIN_S2E_QEMU = os.path.join(CRAX_DIR_BUILD, CRAX_PATH_S2E_QEMU)

CRAX_IMG = '/home/linpc/u12/1112/windows.qcow2'


CRAX_ARG_LOADVM = '-loadvm office2'
CRAX_AGR_NET = '-net user -net nic,model=pcnet'
CRAX_ARG_MONITOR = '-monitor stdio'
CRAX_ARG_VNC = '-vnc :1'

CRAX_ARG_S2E = '-s2e-config-file /home/linpc/u12/1112/windows.lua -s2e-verbose'

CRAX_ARGS = ' '.join((CRAX_IMG, CRAX_ARG_LOADVM, CRAX_AGR_NET, CRAX_ARG_MONITOR, CRAX_ARG_VNC))
CRAX_ARGS_S2E = ' '.join((CRAX_IMG, CRAX_ARG_LOADVM, CRAX_ARG_S2E, CRAX_AGR_NET, CRAX_ARG_MONITOR, CRAX_ARG_VNC))


CRAX_QEMU_PROMPT = '\(qemu\) '

# print "CRAX_ARGS = ", CRAX_ARGS
# print "CRAX_ARGS_S2E = ", CRAX_ARGS_S2E


###############################################################
# Main
###############################################################

# -----------------------------
# boot/loadvm with qemu
# -----------------------------

os.chdir(CRAX_DIR_WORK)
print "Current directory: ", os.getcwd()

crax_monitor = pexpect.spawn(' '.join((CRAX_BIN_QEMU, CRAX_ARGS)))
crax_monitor.expect(CRAX_QEMU_PROMPT)
crax_monitor.sendline('info snapshots')
crax_monitor.expect(CRAX_QEMU_PROMPT)
print crax_monitor.before

time.sleep(40)

crax_monitor.sendline('quit')

