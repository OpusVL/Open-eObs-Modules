export HOST_IP="brhpvfs1003.slam.org.ad"
export CREDENTIALS="/root/.smbcredentials"
export MOUNT_OPTS="iocharset=utf8,file_mode=0777,dir_mode=0777,verbose,ip=10.16.32.200"
export REMOTE_MOUNT_POINT="achlys"
export LOCAL_MOUNT_POINT="/bcp/remote"
export LOCAL_RSYNC_DIR="/bcp/out/"

# A dictionary of ward names (as in the report prefix) and their shared folder locations relative to the mounted drive
# It's very important that if a location has any backslashes in the path that these are removed. This breaks Rsync
declare -A REMOTEDIRMAP
REMOTEDIRMAP[EileenSkellernWard2]="Shared/ES2Information/E-OBS"
REMOTEDIRMAP[JohnsonPICU]="Shared/Acute_CAG_Central/Lewisham Acute/Ladywell_Unit (achlysShared)/Johnson Unit/E-Obs"
declare -p REMOTEDIRMAP > wards_to_backup