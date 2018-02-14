export HOST_IP="172.31.15.40"
export CREDENTIALS="/root/.smbcredentials"
export MOUNT_OPTS="iocharset=utf8,file_mode=0777,dir_mode=0777,verbose"
export REMOTE_MOUNT_POINT="bcp"
export LOCAL_MOUNT_POINT="/bcp/remote"
export LOCAL_RSYNC_DIR="/bcp/out/"

declare -A REMOTEDIRMAP
REMOTEDIRMAP[WardA]="Ward A"
REMOTEDIRMAP[WardB]="Ward B"
declare -p REMOTEDIRMAP > wards_to_backup
