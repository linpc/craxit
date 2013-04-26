#!/usr/bin/python2.7
# -*- coding: UTF-8 -*-

import pexpect
import os
import socket
import time

###############################################################
# Constants / Read from XML definition
###############################################################

CRAX_DIR_NFS = '/home/CRF'
CRAX_DIR_NFS_STAMP = '/home/CRF/stamp'

CRAX_DIR_WORK = '/home/linpc/u12/1112/run'
CRAX_DIR_BUILD = '/home/linpc/u12/1112/build'
CRAX_PATH_QEMU = 'qemu-release/i386-softmmu/qemu'
CRAX_PATH_S2E_QEMU = 'qemu-release/i386-s2e-softmmu/qemu'

CRAX_PATH_OUTPUT = 's2e-last'
CRAX_DIR_OUTPUT = os.path.join((CRAX_DIR_WORK, CRAX_PATH_OUTPUT))

CRAX_BIN_QEMU = os.path.join(CRAX_DIR_BUILD, CRAX_PATH_QEMU)
CRAX_BIN_S2E_QEMU = os.path.join(CRAX_DIR_BUILD, CRAX_PATH_S2E_QEMU)

CRAX_IMG = '/home/linpc/u12/1112/windows.qcow2'

CRAX_VM_CLEAN = 'cleanfix'
CRAX_VM_SYMFILE = 'Coffice2'

CRAX_ARG_LOADVM = ' '.join(('-loadvm', CRAX_VM_CLEAN))
CRAX_ARG_S2E_LOADVM = ' '.join(('-loadvm', CRAX_VM_SYMFILE))
CRAX_AGR_NET = '-net user -net nic,model=pcnet'
CRAX_ARG_MONITOR = '-monitor stdio'
CRAX_ARG_VNC = '-vnc :1'

CRAX_ARG_S2E = '-s2e-config-file /home/linpc/u12/1112/windows.lua -s2e-verbose'

CRAX_ARGS = ' '.join((CRAX_IMG, CRAX_ARG_LOADVM, CRAX_AGR_NET, CRAX_ARG_MONITOR, CRAX_ARG_VNC))
CRAX_ARGS_S2E = ' '.join((CRAX_IMG, CRAX_ARG_S2E_LOADVM, CRAX_ARG_S2E, CRAX_AGR_NET, CRAX_ARG_MONITOR, CRAX_ARG_VNC))

CRAX_QEMU_PROMPT = '\(qemu\) '

# print "CRAX_ARGS = ", CRAX_ARGS
# print "CRAX_ARGS_S2E = ", CRAX_ARGS_S2E

###############################################################
# Main
###############################################################

# -----------------------------
# Create unique stamp
# -----------------------------

# -----------------------------
# listen socket (daemon?)
# -----------------------------

# s = socket.socket()
# # host = socket.gethostname()
# host = "10.113.208.67"
# port = 12345
# 
# s.bind((host, port))
# 
# s.listen(5)
# while True:
#     c, addr = s.accept()
#     print 'Got connetction from', addr
#     c.send('Thank you for connecting')
#     c.close()

# -----------------------------
# boot/loadvm with qemu using snapshot_clean
# -----------------------------

os.chdir(CRAX_DIR_WORK)
print "Current directory: ", os.getcwd()

crax_monitor = pexpect.spawn(' '.join((CRAX_BIN_QEMU, CRAX_ARGS)))
crax_monitor.expect(CRAX_QEMU_PROMPT)

# wait and listen guest to do symfile
time.sleep(40)

# -----------------------------
# get signal from guest, do: savevm
# -----------------------------

# wait till symfile is done

crax_monitor.sendline('savevm ' + CRAX_VM_SYMFILE)
crax_monitor.expect(CRAX_QEMU_PROMPT)

crax_monitor.sendline('info snapshots')
crax_monitor.expect(CRAX_QEMU_PROMPT)
print '=============== snapshots information ==============='
print crax_monitor.before

crax_monitor.sendline('quit')

# -----------------------------
# boot/loadvm with s2e-qemu using snapshot_symfile
# -----------------------------

crax_monitor = pexpect.spawn(' '.join((CRAX_BIN_S2E_QEMU, CRAX_ARGS_S2E)))
crax_monitor.expect(CRAX_QEMU_PROMPT)

# wait guest to do openfile
# wait S2E do symbolic execution

# kill-state will terminate s2e-qemu => how to detect crax_monitor?
# using a while loop to check the monitor is still alive?
# wait user-defined maximum-timeout?
time.sleep(40)

try:
    crax_monitor.sendline('info snapshots')
    crax_monitor.expect(CRAX_QEMU_PROMPT)

    # s2e-qemu not terminated, may be error
    print crax_monitor.before
except pexpect.EOF:
    print 'EOF exception'
except pexpect.TIMEOUT:
    print 'TIMEOUT exception'

# -----------------------------
# prepare to verify the generated exploit
# -----------------------------

# how to know which s2e-out-?? directory is this session use?

# check s2e-last
# what time is s2e-last being created?
# - the first time s2e-qemu start? or
# - the kill-state send to s2e-qemu?

if (os.path.exists(os.path.join((CRAX_DIR_OUTPUT, 'Exploit')))):
    # copy file to NFS
else:
    # no exploit generated, S2E run may be fail
    print "Fail, no exploit generated."
    exit(0)

# -----------------------------
# boot/loadvm with qemu using snapshot_clean
# -----------------------------

crax_monitor = pexpect.spawn(' '.join((CRAX_BIN_QEMU, CRAX_ARGS)))
crax_monitor.expect(CRAX_QEMU_PROMPT)

# -----------------------------
# check if the exploit successfully take effect
# -----------------------------

# how to?
# - check NFS's signal file? or
# - listen a socket to be signaled

