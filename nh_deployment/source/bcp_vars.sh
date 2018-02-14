export HOST="fqdn.tld"
export CREDENTIALS="/path/to/.smbcredentials"
export MOUNT_OPTS="iocharset=utf8,file_mode=0777,dir_mode=0777,verbose,ip=1.2.3.4"
export REMOTE_MOUNT_POINT="root_share"
export LOCAL_MOUNT_POINT="/bcp/remote"
export LOCAL_RSYNC_DIR="/bcp/out/"
declare -a REMOTEDIRMAP