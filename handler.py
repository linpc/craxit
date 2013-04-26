#!python

import os
import socket
import time

###############################################################
# Constants / Read from XML definition
###############################################################

CRAX_DIR_NFS = 'Z:\CRF'
CRAX_DIR_STAMP = os.path.join((CRAX_DIR_NFS, 'stamp'))

CRAX_HOST_IP = '10.113.208.67'
CRAX_HOST_PORT = 12345

CRAX_TIME_SYMFILE = 30

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
    optn(file, 'a').close()

def verify():
    # execute autoit script to do varify exploit

    # detect if `calc' process exists

    # touch NFS to signal the result

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

while True:
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((CRAX_HOST_IP, CRAX_HOST_PORT))

        client.send('12345abcde')
        CRAX_STAMP = client.recv(512)
        print CRAX_STAMP
        break
    except socket.error:
        print 'socket error'
        time.sleep(5)
        continue
    except socket.timeout:
        print 'socket timeout'

#############################################
# Symfile state
#############################################

# -----------------------------
# got stamp, prepare environment
# -----------------------------

CRAX_MY_HOSTNAME = socket.gethostname()
CRAX_MY_ADDR = socket.gethostbyname(CRAX_MY_HOSTNAME)

CRAX_DIR_STAMPING = os.path.join((CRAX_DIR_STAMP, CRAX_STAMP))

CRAX_COOKIE_STAND_BY = os.path.join((CRAX_DIR_STAMPING, '.stand_by'))
CRAX_COOKIE_SYMFILE_OK = os.path.join((CRAX_DIR_STAMPING, '.symfile_ok'))
CRAX_COOKIE_TEST_VALIDATE = os.path.join((CRAX_DIR_STAMPING, '.test_validate'))
CRAX_COOKIE_CLEAN_SNAPSHOT_OK = os.path.join((CRAX_DIR_STAMPING, '.clean_snapshot_ok'))
CRAX_COOKIE_S2E_MODE = os.path.join((CRAX_DIR_STAMPING, '.symfile_s2e_mode'))

if (os.path.isdir(CRAX_DIR_STAMPING)):
    pass
else:
    # may be error, stamp directory not exists
    exit(1)

# -----------------------------
# inform host to do 1st savevm for exploit validation
# -----------------------------

# - send signal to host? or
# - touch a file in NFS?

CRAX_STATUS = CRAX_STATUS_VALIDATE

touch(CRAX_COOKIE_STAND_BY)

# after inform, we should do a long wait here
# until snapshot has been created

while True:
    if (os.path.exists(CRAX_COOKIE_TEST_VALIDATE)):
	print "get file ", CRAX_COOKIE_TEST_VALIDATE
        verify()

        # verify done, should terminate vm instance
        exit(0)
    else if (os.path.exists(CRAX_COOKIE_CLEAN_SNAPSHOT_OK)):
	print "get file ", CRAX_COOKIE_CLEAN_SNAPSHOT_OK
	break
    else:
	sleep(5)


# -----------------------------
# do symfile
# -----------------------------

# execute autoit script to do symfile


# wait symfile process to be static
time.sleep(CRAX_TIME_SYMFILE)

# -----------------------------
# inform host to do 2nd savevm for symbolic execution
# -----------------------------

# - send signal to host? or
# - touch a file in NFS?

CRAX_STATUS = CRAX_STATUS_SYMFILE

touch(CRAX_COOKIE_SYMFILE_OK)

# after inform, we should do a long wait here
# until S2E mode is taken effect

while True:
    if (os.path.exists(CRAX_COOKIE_S2E_MODE)):
	print "get file ", CRAX_COOKIE_S2E_MODE
	break
    else:
	sleep(5)

#############################################
# Exploit generation state
#############################################

# -----------------------------
# do openfile
# -----------------------------

# execute autoit script to do openfile


# s2e-qemu may be killed in this state



# should not go here
exit(1)
