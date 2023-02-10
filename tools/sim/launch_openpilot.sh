#!/bin/bash

export PASSIVE="0"
export NOBOARD="1"
export SIMULATION="1"
export FINGERPRINT="HONDA CIVIC 2016"
export BLOCK="camerad,encoderd"

while getopts 'i' OPTION;
do
  case "$OPTION" in
    i)
      read -p "Do you want to enable Driver Monitoring in the simulator? (y/n)";
      if [ "${REPLY}" == "y" ]; then
        export DM_SIM="1"
      fi
      ;;
    esac
done

if [[ "$CI" ]]; then
  # TODO: offscreen UI should work
  export BLOCK="${BLOCK},ui"
fi


DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd ../../selfdrive/manager && exec ./manager.py

