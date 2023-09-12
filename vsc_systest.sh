#!/bin/sh
#****************************************************************************
#* vsc_systest.sh
#*
#* Wrapper script for for launching vsc_systest in development environments
#****************************************************************************

script_dir=$(dirname $(realpath $0))

if test ! -d ${script_dir}/packages; then
  echo "Error: packages directory does not exist"
  exit 1
fi

export PYTHONPATH=${script_dir}/src
${script_dir}/packages/python/bin/python3 -m vsc_systest "$@"

exit $?


