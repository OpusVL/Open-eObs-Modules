#!/bin/bash

# Neova Health BCP Script
# Used to mount a remote CIFS share before RSYNC of PDFs from local BCP output path to destination

# Global variables
declare SCRIPT_NAME="${0##*/}"
declare SCRIPT_DIR="$(cd ${0%/*} ; pwd)"
declare ROOT_DIR="$PWD"

usage() {
cat << EOF
USAGE
[options] pathToVariablesFile

OPTIONS
	o - Print opts from filename
	d - Dry Run
	l - Live Run

VARIABLES FILE
The variables file should contain the following key-value pairs:

HOST_IP="fqdn.tld"
CREDENTIALS="/path/to/.smbcredentials"
MOUNT_OPTS="iocharset=utf8,file_mode=0777,dir_mode=0777,verbose,ip=1.2.3.4"
REMOTE_MOUNT_POINT="root_share"
LOCAL_MOUNT_POINT="/bcp/remote"
REMOTE_RSYNC_DIR="path/on/remote"
LOCAL_RSYNC_DIR="/bcp/out/"

CREDENTIALS FILE
username=NameOfUser
password=PasswordOfUser
domain=the.domain.of.the.server.com
EOF
exit 0
}

# Checks output for non-zero exit
function checkErrors() {
	# Function. Parameter 1 is the return code
	if [ "${1}" -ne "0" ]; then
		echo "ERROR: ${1} : ${2}"
		# as a bonus, make script exit with the right error code.
		exit ${1}
	fi
}

# Handles failures
function failed() {
	echo -e "ERROR: Run failed"
	echo -e "$1"
	exit 1
}

# Confirm action
function confirm() {
	# Tell the user what they are about to do.
	echo "INFO: About to $1";
	# Ask for confirmation from user
	read -r -p "Are you sure? [Y/n] : " response
	case "$response" in
	    [yY][eE][sS]|[yY]) 
          # If yes, then execute the passed parameters
           $2 $3
           ;;
	    *)
          # Otherwise exit...
          echo "INFO: End"
          exit
          ;;
	esac
}

#######################################################################################
# Set environment VARs here
SELF=(`id -u -n`)
VERSION=0.1

#######################################################################################
# Script functions below

getOptions() {
	# vars file is passed to function as $1
	echo ""
	echo "INFO: Sourcing options from $1"	
	source $1
}

printOptions() {
	source wards_to_backup
	echo "INFO: Display vars from conf file"
	echo "HOST_IP = $HOST_IP"
	echo "CREDENTIALS = $CREDENTIALS"
	echo "MOUNT_OPTS = $MOUNT_OPTS"
	echo "REMOTE_MOUNT_POINT = $REMOTE_MOUNT_POINT"
	echo "LOCAL_MOUNT_POINT = $LOCAL_MOUNT_POINT"
	echo "REMOTEDIRMAP = ${REMOTEDIRMAP[@]}"
	echo "LOCAL_RSYNC_DIR = $LOCAL_RSYNC_DIR"
}

# Ping the host
pingDestination(){
	ping -c 1 ${HOST_IP} > /dev/null 2>&1
	checkErrors $? "ERROR: unable to ping host ${HOST_IP}"
}

mountDestination() {
	if [ ! "`mount | grep ${LOCAL_MOUNT_POINT}`" ] ; then #if its not alread mounted, mount it
		mount -v -t cifs -o credentials=${CREDENTIALS},${MOUNT_OPTS} "//${HOST_IP}/${REMOTE_MOUNT_POINT}" ${LOCAL_MOUNT_POINT}
		checkErrors $? "ERROR: Directory did not mount correctly. Return code was: $?."
	fi
}

dryrunDestination() {
	source wards_to_backup
	DATE=$(date +"%Y-%m-%d %H:%M:%S")
	echo ""
	for K in "${!REMOTEDIRMAP[@]}"
	do
	    echo "INFO: rsync for $K started at $DATE"
	    find ${LOCAL_RSYNC_DIR} -type f -a -iname "${K}_*.pdf" -exec basename {} \; > files_to_copy && rsync --dry-run -rv --files-from=files_to_copy ${LOCAL_RSYNC_DIR} "${LOCAL_MOUNT_POINT}/${REMOTEDIRMAP[$K]}"
	    checkErrors $? "ERROR: rsync errored for some reason. Return code was: $?."
	done
}

rsyncDestination() {
	source wards_to_backup
	DATE=$(date +"%Y-%m-%d %H:%M:%S")
	echo ""
	for K in "${!REMOTEDIRMAP[@]}"
	do
	    echo "INFO: rsync for $K started at $DATE"
	    find ${LOCAL_RSYNC_DIR} -type f -a -iname "${K}_*.pdf" -exec basename {} \; > files_to_copy && rsync -rv --files-from=files_to_copy ${LOCAL_RSYNC_DIR} "${LOCAL_MOUNT_POINT}/${REMOTEDIRMAP[$K]}"
	    checkErrors $? "ERROR: rsync errored for some reason. Return code was: $?."
	done
}

completeRun() {
	DATE=$(date +"%Y-%m-%d %H:%M:%S")
	echo ""
	echo "INFO: rsync completed successfully"
}

umountDestination() {
	echo ""
	echo "INFO: Unmounting ${LOCAL_MOUNT_POINT}"
	umount  ${LOCAL_MOUNT_POINT}
	checkErrors $? "ERROR: Directory did not mount correctly. Return code was: $?."
}

#######################################################################################
# Handles options passed to script

while getopts “odl” OPTION
do
    case $OPTION in
        o)
            ACTION="optsrun"
            VARS=$1
            ;;
        d)
            ACTION="dryrun"
            VARS=$1
            ;;
        l)
	    ACTION="liverun"
	    VARS=$1
	    ;;
        ?)
            usage
            ;;
    esac
done

# If there isn't an action, show usage
if [[ -z $ACTION ]] ; then
	usage
    exit 1
fi

#######################################################################################
# Execute!

if [ $ACTION = optsrun ] ; then
	echo "INFO: Action = Opts";
	getOptions $2;
	printOptions;
fi

if [ $ACTION = dryrun ] ; then
	echo "INFO: Action = Dry";
	getOptions $2;
	printOptions;
	pingDestination;
	mountDestination;
	dryrunDestination;
	completeRun;
	umountDestination;
fi

if [ $ACTION = liverun ] ; then
	echo "INFO: Action = Live";
	getOptions $2;
	pingDestination
	mountDestination;
	rsyncDestination;
	completeRun;
	umountDestination;
fi

#######################################################################################
# Done

cd ${ROOT_DIR}
echo -e "INFO: Exit with code 0"
echo
exit 0
