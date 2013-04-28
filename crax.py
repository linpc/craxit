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
CRAX_DIR_STAMP = os.path.join((CRAX_DIR_NFS, 'stamp'))

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
CRAX_VM_READY = 'Cready'
CRAX_VM_SYMFILE = 'Coffice2'

CRAX_ARG_LOADVM = ' '.join(('-loadvm', CRAX_VM_CLEAN))
CRAX_ARG_S2E_LOADVM = ' '.join(('-loadvm', CRAX_VM_SYMFILE))
CRAX_ARG_VERIFY_LOADVM = ' '.join(('-loadvm', CRAX_VM_READY))
CRAX_AGR_NET = '-net user -net nic,model=pcnet'
CRAX_ARG_MONITOR = '-monitor stdio'
CRAX_ARG_VNC = '-vnc :1'

CRAX_ARG_S2E = '-s2e-config-file /home/linpc/u12/1112/windows.lua -s2e-verbose'

CRAX_ARGS = ' '.join((CRAX_IMG, CRAX_ARG_LOADVM, CRAX_AGR_NET, CRAX_ARG_MONITOR, CRAX_ARG_VNC))
CRAX_ARGS_S2E = ' '.join((CRAX_IMG, CRAX_ARG_S2E_LOADVM, CRAX_ARG_S2E, CRAX_AGR_NET, CRAX_ARG_MONITOR, CRAX_ARG_VNC))
CRAX_ARGS_VERIFY = ' '.join((CRAX_IMG, CRAX_ARG_VERIFY_LOADVM, CRAX_AGR_NET, CRAX_ARG_MONITOR, CRAX_ARG_VNC))

CRAX_QEMU_PROMPT = '\(qemu\) '

CRAX_TIME_EXPLOIT = 20
CRAX_TIME_LONGWAIT = 5

# print "CRAX_ARGS = ", CRAX_ARGS
# print "CRAX_ARGS_S2E = ", CRAX_ARGS_S2E

###############################################################
# Global variables
###############################################################

# -----------------------------
# Create unique stamp
# -----------------------------

CRAX_STAMP = int(time.time())

while True:
    CRAX_DIR_STAMPING = os.path.join((CRAX_DIR_STAMP, CRAX_STAMP))
    if (os.path.isdir(CRAX_DIR_STAMPING)):
        CRAX_STAMP += 1
        continue
    else:
        os.mkdir(CRAX_DIR_STAMPING, 0777)
        break

CRAX_COOKIE_STAND_BY = os.path.join((CRAX_DIR_STAMPING, '.stand_by'))
CRAX_COOKIE_SYMFILE_OK = os.path.join((CRAX_DIR_STAMPING, '.symfile_ok'))
CRAX_COOKIE_TEST_VALIDATE = os.path.join((CRAX_DIR_STAMPING, '.test_validate'))
CRAX_COOKIE_CLEAN_SNAPSHOT_OK = os.path.join((CRAX_DIR_STAMPING, '.clean_snapshot_ok'))
CRAX_COOKIE_S2E_MODE = os.path.join((CRAX_DIR_STAMPING, '.symfile_s2e_mode'))
CRAX_COOKIE_VERIFY_OK = os.path.join((CRAX_DIR_STAMPING, '.verify_ok'))
CRAX_COOKIE_VERIFY_FAIL = os.path.join((CRAX_DIR_STAMPING, '.verify_fail'))

###############################################################
# functions
###############################################################

def touch(file):
    open(file, 'a').close()

###############################################################
# Main
###############################################################

# -----------------------------
# listen socket (daemon?)
# -----------------------------

# give guest an unique stamp

try:
    pid = os.fork()
except OSError, e:
    exit(1)

if pid == 0:
    # child process
    server = socket.socket()
    # host = socket.gethostname()
    host = "10.113.208.67"
    port = 12345

    server.bind(("", port))

    server.listen(5)
    while True:
        client, addr = server.accept()
        print 'Got connetction from', addr
        client.send(str(CRAX_STAMP))
        data = client.recv(512)
        print 'get data:', data
        client.close()
        # just accept one connection
        break

    # terminate child process
    exit(0)
else:
    # parent process
    pass

# -----------------------------
# boot/loadvm with qemu using snapshot_clean
# -----------------------------

os.chdir(CRAX_DIR_WORK)
print "Current directory: ", os.getcwd()

crax_monitor = pexpect.spawn(' '.join((CRAX_BIN_QEMU, CRAX_ARGS)))
crax_monitor.expect(CRAX_QEMU_PROMPT)

# -----------------------------
# savevm for ready state
# -----------------------------

# long wait the guest prepare to do a clean snapshot
# CRAX_COOKIE_STAND_BY

while True:
    if (os.path.exists(CRAX_COOKIE_STAND_BY)):
        break
    else:
	sleep(CRAX_TIME_LONGWAIT)
        continue

crax_monitor.sendline('savevm ' + CRAX_VM_READY)
crax_monitor.expect(CRAX_QEMU_PROMPT)

# inform guest that savevm is done, able go through to next step
touch(CRAX_COOKIE_CLEAN_SNAPSHOT_OK)

crax_monitor.sendline('info snapshots')
crax_monitor.expect(CRAX_QEMU_PROMPT)
print '=============== snapshots information ==============='
print crax_monitor.before

# -----------------------------
# savevm for symfile state
# -----------------------------

# wait till symfile is done
# CRAX_COOKIE_SYMFILE_OK
while True:
    if (os.path.exists(CRAX_COOKIE_SYMFILE_OK)):
        break
    else:
	sleep(CRAX_TIME_LONGWAIT)
        continue

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

touch(CRAX_COOKIE_S2E_MODE)

crax_monitor = pexpect.spawn(' '.join((CRAX_BIN_S2E_QEMU, CRAX_ARGS_S2E)))
crax_monitor.expect(CRAX_QEMU_PROMPT)

# wait guest to do openfile
# wait S2E do symbolic execution

# kill-state will terminate s2e-qemu => how to detect crax_monitor?
# using a while loop to check the monitor is still alive?
# wait user-defined maximum-timeout?
time.sleep(40)

# wait at most 600 seconds
CRAX_WAIT_TIMEOUT = 600

wait_time = 0

while (wait_time <= CRAX_WAIT_TIMEOUT):
    try:
        crax_monitor.sendline('info snapshots')
        crax_monitor.expect(CRAX_QEMU_PROMPT)

        # s2e-qemu not terminated, may be error
        #print crax_monitor.before
        time.sleep(10)
        wait_time += 10
    except pexpect.EOF:
        print 'EOF exception'
        # monitor process not exists, may be kill-state
        break
    except pexpect.TIMEOUT:
        print 'TIMEOUT exception'
        time.sleep(10)
        wait_time += 10

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

# inform guest to do verify routine instead of symfile
touch(CRAX_COOKIE_TEST_VALIDATE)

crax_monitor = pexpect.spawn(' '.join((CRAX_BIN_QEMU, CRAX_ARGS_VERIFY)))
crax_monitor.expect(CRAX_QEMU_PROMPT)

# -----------------------------
# check if the exploit successfully take effect
# -----------------------------

# do a long wait to be informed the result of varification

verify_result = 1

while True:
    if (os.path.exists(CRAX_COOKIE_VERIFY_OK)):
        print "Exploit verify passed"
        verify_result = 0
    else if (os.path.exists(CRAX_COOKIE_VERIFY_FAIL)):
        print "Exploit verify failed"
    else
        time.sleep(CRAX_TIME_LONGWAIT)

crax_monitor.sendline('quit')

# return verify result
exit(verify_result)
