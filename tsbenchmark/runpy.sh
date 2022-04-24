#!/usr/bin/env bash

# unset https_proxy
# unset http_proxy

usage() {
    echo "Usage: $0  [options]" 1>&2;
}

# read vars from command
POSITIONAL=()
for i in "$@"; do
    case $i in
        -h | --help)
            usage
            exit ;;
        --conda-home=*)
            conda_home="${i#*=}"
            shift ;;
        --venv-name=*)
            venv_name="${i#*=}"
            shift ;;
        --requirements-kind=*)
            requirements_kind="${i#*=}"
            shift ;;
        --requirements-txt-file=*)
            requirements_txt_file="${i#*=}"
            shift ;;
        --requirements-txt-py-version=*)
            requirements_txt_py_version="${i#*=}"
            shift ;;
        --python-script=*)
            python_script="${i#*=}"
            shift ;;
        -*|--*=)
            echo "unsupported args"
            usage
            exit 1 ;;
        *)
            POSITIONAL+=("$i")
      shift ;;
    esac
done

echo -e "\n"
echo "-----------------------"
echo "conda_home: $conda_home"
echo "venv_name: $venv_name"
echo "requirements_kind: $requirements_kind"
echo "requirements_txt_file: $requirements_txt_file"
echo "requirements_txt_py_version: $requirements_txt_py_version"
echo "python_script: $python_script"
echo "-----------------------"

function require_input() {
  if [ -z $1 ];then
    echo "$2 can not be none" 1>&2
    exit -1
  fi
}

require_input "$conda_home" "conda-home"
require_input "$venv_name" "venv-name"
require_input "$requirements_kind" "requirements-kind"
require_input "$python_script" "python-script"


# define vars
conda_exec="$conda_home/bin/conda"
venv_dir="$conda_home/envs/$venv_name"
py_exec="$venv_dir/bin/python"

# check env
if [ -d $venv_dir ];then
  echo "env already exists, skipped create env"
else
  # create env
  if [ "$requirements_kind" == "requirements_txt"  ];then
    echo "env is not already exists, create it"
    # handle requirement.txt
    $conda_exec create -n $venv_name python=$requirements_txt_py_version -y
    pip_exec="$venv_dir/bin/pip"
    $pip_exec install tsbenchmark
    $pip_exec install -r $requirements_txt_file
  fi
fi

# run script
$py_exec $python_script
