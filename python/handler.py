#!python

import os
import psutil
import socket
import sys
import time

###############################################################
# Constants / Read from XML definition
###############################################################

CRAX_DIR_NFS = 'Z:\CRF'
CRAX_DIR_STAMP = os.path.join(CRAX_DIR_NFS, 'stamp')
CRAX_DIR_AUTOIT = os.path.join(CRAX_DIR_NFS, 'autoit')

CRAX_HOST_IP = '10.113.208.67'
CRAX_HOST_PORT = 12345

CRAX_TIME_SYMFILE = 90
CRAX_TIME_EXPLOIT = 20
CRAX_TIME_LONGWAIT = 5

CRAX_STATUS_READY = 0
CRAX_STATUS_SYMFILE = 1
CRAX_STATUS_VALIDATE = 2

###############################################################
# Global variables
###############################################################

CRAX_STATUS = CRAX_STATUS_READY

CRAX_STAMP = ''

###############################################################
# functions
###############################################################

def touch(file):
    open(file, 'a').close()

def verify():
    # execute autoit script to do varify exploit
    os.system('Z:\\CRF\\autoit\\wakeup.exe')
    os.system('Z:\\CRF\\autoit\\verify.exe ' + CRAX_STAMP)
    # wait the exploit execute
    time.sleep(CRAX_TIME_EXPLOIT)

    # detect if `calc' process exists
    # touch NFS to signal the result
    if "calc.exe" in [psutil.Process(i).name for i in psutil.get_pid_list()]:
        print "Found a calc window"
        touch(CRAX_COOKIE_VERIFY_OK)
    else:
        print "Not found"
        touch(CRAX_COOKIE_VERIFY_FAIL)

    return

###############################################################
# Main
###############################################################

#############################################
# Prepare state
#############################################

# -----------------------------
# wait stamp exist
# -----------------------------

# while loop to wait stamp
# try to connect to local server to get stamp

CRAX_MY_HOSTNAME = socket.gethostname()
CRAX_MY_ADDR = socket.gethostbyname(CRAX_MY_HOSTNAME)

sys.stdout.write("Waiting for socket connection to server...")

while True:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((CRAX_HOST_IP, CRAX_HOST_PORT))

        client.send(CRAX_MY_ADDR)
        CRAX_STAMP = client.recv(512)
        print "\nget stamp from host: ", CRAX_STAMP
        break
    except socket.error:
        sys.stdout.write('.')
        time.sleep(CRAX_TIME_LONGWAIT)
        continue
    except socket.timeout:
        print 'socket timeout'
#CRAX_STAMP = '1367300645'

#############################################
# Symfile state
#############################################

# -----------------------------
# got stamp, prepare environment
# -----------------------------

CRAX_DIR_STAMPING = os.path.join(CRAX_DIR_STAMP, CRAX_STAMP)

CRAX_COOKIE_STAND_BY = os.path.join(CRAX_DIR_STAMPING, '.stand_by')
CRAX_COOKIE_SYMFILE_OK = os.path.join(CRAX_DIR_STAMPING, '.symfile_ok')
CRAX_COOKIE_TEST_VALIDATE = os.path.join(CRAX_DIR_STAMPING, '.test_validate')
CRAX_COOKIE_CLEAN_SNAPSHOT_OK = os.path.join(CRAX_DIR_STAMPING, '.clean_snapshot_ok')
CRAX_COOKIE_S2E_MODE = os.path.join(CRAX_DIR_STAMPING, '.symfile_s2e_mode')
CRAX_COOKIE_VERIFY_OK = os.path.join(CRAX_DIR_STAMPING, '.verify_ok')
CRAX_COOKIE_VERIFY_FAIL = os.path.join(CRAX_DIR_STAMPING, '.verify_fail')

os.system('Z:\\CRF\\autoit\\wakeup.exe')

while True:
    if (os.path.isdir(CRAX_DIR_STAMPING)):
        print CRAX_DIR_STAMPING, "directory checking passed"
        break
    else:
        # may be error, stamp directory not exists
        print "Error: stamp directory", CRAX_DIR_STAMPING, "not exists"
        time.sleep(CRAX_TIME_LONGWAIT)
        continue
        #exit(1)

# -----------------------------
# inform host to do 1st savevm for exploit validation
# -----------------------------

# - send signal to host? or
# - touch a file in NFS?

CRAX_STATUS = CRAX_STATUS_VALIDATE

touch(CRAX_COOKIE_STAND_BY)

# after inform, we should do a long wait here
# until snapshot has been created

# after the savevm point, the vm may run into 2 path:
# - boot/loadvm by qemu in exploit-validate stage
#   (host should create cookie file before booting)
# - go through to do symfile
#
# so we check these 2 situations in the long wait

sys.stdout.write("Waiting for SAVEVM done...")

while True:
    if (os.path.exists(CRAX_COOKIE_TEST_VALIDATE)):
	print "\nget file ", CRAX_COOKIE_TEST_VALIDATE
        print "Do VERIFY process now"
        verify()

        # verify done, should terminate vm instance
        exit(0)
    elif (os.path.exists(CRAX_COOKIE_CLEAN_SNAPSHOT_OK)):
	time.sleep(CRAX_TIME_LONGWAIT)
        if (os.path.exists(CRAX_COOKIE_TEST_VALIDATE)):
            print "\nget file ", CRAX_COOKIE_TEST_VALIDATE
            print "Do VERIFY process now"
            verify()
            exit(0)

	print "\nget file ", CRAX_COOKIE_CLEAN_SNAPSHOT_OK
	break
    else:
        sys.stdout.write('.')
	time.sleep(CRAX_TIME_LONGWAIT)


# -----------------------------
# do symfile
# -----------------------------

# execute autoit script to do symfile
os.system('Z:\\CRF\\autoit\\symfile.exe')


# wait symfile process to be static
time.sleep(CRAX_TIME_SYMFILE)

# -----------------------------
# inform host to do 2nd savevm for symbolic execution
# -----------------------------

# - send signal to host? or
# - touch a file in NFS?

CRAX_STATUS = CRAX_STATUS_SYMFILE

touch(CRAX_COOKIE_SYMFILE_OK)

sys.stdout.write("Wating for SAVEVM done...")

# after inform, we should do a long wait here
# until S2E mode is taken effect

while True:
    if (os.path.exists(CRAX_COOKIE_S2E_MODE)):
	print "\nget file ", CRAX_COOKIE_S2E_MODE
        print "Running in S2E mode now"
	break
    else:
        sys.stdout.write('.')
	time.sleep(CRAX_TIME_LONGWAIT)

#############################################
# Exploit generation state
#############################################

# -----------------------------
# do openfile
# -----------------------------

# execute autoit script to do openfile
# to let symfile program static
time.sleep(10)
os.system('Z:\\CRF\\autoit\\openfile.exe')

# s2e-qemu may be killed in this state

# should not go here
exit(1)
