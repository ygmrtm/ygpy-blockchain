#! /bin/bash

DIR=$(cd "$(dirname "$0")" || exit; pwd)
LOGDIR="${DIR}/../logs/"
PORTS=1
ENABLE_LOGS=false

usage(){
  cat << EOF
  usage: $0 options

  This script run the flask server over a machine.

  OPTIONS:
     -h | --help         Show this message
     -l | --enableLogs   Logs Enabled (true or false)
     -p | --ports        Number of ports

EOF
}

while true; do
  case "$1" in
    -h | --help ) usage; exit 1 ;;
    -l | --enableLogs ) ENABLE_LOGS=true; shift ;;
    -p | --ports ) PORTS="$2"; shift 2 ;;
    * ) break ;;
  esac
done

enableLogs(){
  if [ ! -d "$logDir" ]; then
    mkdir "$logDir"
    echo "logDir: ${logDir}"
  fi
  exec 3>&1 4>&2
  trap 'exec 2>&4 1>&3' 0 1 2 3
  exec 1>>"${logDir}"loopForDuplicateImages.log 2>&1
}

runningMachine(){
  unameOut="$(uname -s)"
  case "${unameOut}" in
      Linux*)     machine=Linux;;
      Darwin*)    machine=Mac;;
      CYGWIN*)    machine=Cygwin;;
      MINGW*)     machine=MinGw;;
      *)          machine="UNKNOWN:${unameOut}"
  esac
  echo "Running under... $machine"
}

main(){
  runningMachine
  echo "Ports:${PORTS} EnableLog:${ENABLE_LOGS}"
#  if validUsage "${1}" "${2}" "${3}" && validExistingPath "${1}" "${2}"; then
#    [[ "${log_param}" == "--enablelog" ]] && enableLogs || echo "${log_param}"
#    start=$(date +%s)
#  fi
}

main