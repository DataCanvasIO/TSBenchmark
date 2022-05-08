#!/bin/sh

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
        --venv-kind=*)
            venv_kind="${i#*=}"
            shift ;;
        --custom-py-executable=*)
            custom_py_executable="${i#*=}"
            shift ;;
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
echo "venv-kind: $venv_kind"
echo "custom-py-executable: $custom_py_executable"
echo "conda-home: $conda_home"
echo "venv-name: $venv_name"
echo "requirements-kind: $requirements_kind"
echo "requirements-txt-file: $requirements_txt_file"
echo "requirements-txt-py-version: $requirements_txt_py_version"
echo "python-script: $python_script"
echo "-----------------------"

function require_input() {
  if [ -z $1 ];then
    echo "$2 can not be none" 1>&2
    exit -1
  fi
}

require_input "$venv_kind" "venv-kind"
require_input "$python_script" "python-script"

#
if [ "$venv_kind" == "custom_python"  ];then
    if [ ! -f $custom_py_executable  ];then
      echo "$custom_py_executable is not exists" 1>&2
      exit -1
    fi
    py_exec=$custom_py_executable
elif [ "$venv_kind" == "conda"   ]; then
    # define vars
    conda_exec="$conda_home/bin/conda"
    venv_dir="$conda_home/envs/$venv_name"
    py_exec="$venv_dir/bin/python"

    # check conda executable
    if [ ! -f $conda_exec ];then
      echo "conda executable $conda_exec is not exists"  1>&2
      exit -1
    fi

    if [ -d $venv_dir ];then  # check env
      echo "venv dir $venv_dir already exists, skip to create"
    else
      require_input "$conda_home" "conda-home"
      require_input "$venv_name" "venv-name"
      require_input "$requirements_kind" "requirements-kind"

      # create env
      if [ "$requirements_kind" == "requirements_txt"  ];then
        echo "env is not already exists, create it"
        # handle requirement.txt
        $conda_exec create -n $venv_name python=$requirements_txt_py_version -y
        if [ ! -f $py_exec ];then
          echo "python executable $py_exec is not exists, create virtual env failed."  1>&2
          exit -1
        fi
        pip_exec="$venv_dir/bin/pip"
        $pip_exec install tsbenchmark
        $pip_exec install -r $requirements_txt_file
        echo "prepare virtual env succeed."
      fi
    fi
fi

# check pyton executable
if [ ! -f $py_exec ];then
  echo "py_exe $py_exec is not exists, can not execute python script"
fi

# run script
$py_exec $python_script
