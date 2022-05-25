#!/bin/bash

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
#        --conda-home=*)
#            conda_home="${i#*=}"
#            shift ;;
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
        --requirements-yaml-file=*)
            requirements_yaml_file="${i#*=}"
            shift ;;
        --datasets-cache-path=*)
            datasets_cache_path="${i#*=}"
            shift ;;
        --python-path=*)
            python_path="${i#*=}"
            shift ;;
        --python-script=*)
            python_script="${i#*=}"
            shift ;;
        -*|--*=)
            unknown_args="${i#*=}"
            echo "unknown_args $unknown_args" >2 1>&2
            usage
            exit 1 ;;
        *)
            POSITIONAL+=("$i")
      shift ;;
    esac
done

conda_home="$TSB_CONDA_HOME"

echo -e "\n"
echo "-----------------------"
echo "venv-kind: $venv_kind"
echo "custom-py-executable: $custom_py_executable"
echo "conda-home: $conda_home"
echo "venv-name: $venv_name"
echo "requirements-kind: $requirements_kind"
echo "requirements-txt-file: $requirements_txt_file"
echo "requirements-txt-py-version: $requirements_txt_py_version"
echo "requirements-yaml-file: $requirements_yaml_file"
echo "python-path: $python_path"
echo "datasets-cache_path: $datasets_cache_path"
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

if [ "$venv_kind" == "custom_python"  ];then
    if [ ! -f $custom_py_executable  ];then
      echo "$custom_py_executable is not exists" 1>&2
      exit -1
    fi
    py_exec=$custom_py_executable

elif [ "$venv_kind" == "conda"   ]; then

    require_input "$conda_home" "TSB_CONDA_HOME"
    require_input "$venv_name" "venv-name"
    require_input "$requirements_kind" "requirements-kind"

    # define vars
    conda_exec="$conda_home/bin/conda"
    venv_dir="$conda_home/envs/$venv_name"
    py_exec="$venv_dir/bin/python"

    # check conda executable
    if [ ! -f $conda_exec ];then
      echo "conda executable $conda_exec is not exists"  1>&2
      exit -1
    fi

    # create env
    if [ ! -d $venv_dir ];then
      echo "env is not already exists, create it"
      if [ "$requirements_kind" == "requirements_txt"  ];then
        require_input "$requirements_kind" "requirements-kind"
        # handle requirement.txt
        $conda_exec create -n $venv_name python=$requirements_txt_py_version pip -y
        pip_exec="$venv_dir/bin/pip"
        $pip_exec install -r $requirements_txt_file
        echo "prepare virtual env succeed."
      elif [  "$requirements_kind" == "conda_yaml" ]; then
        require_input "$requirements_yaml_file" "requirements-yaml-file"
        $conda_exec env create -f $requirements_yaml_file -n "$venv_name"
      else
        echo "unseen requirements $requirements_kind for conda"  1>&2
        exit -1
      fi

      if [ ! -f $py_exec ];then
          echo "python executable $py_exec is not exists, create virtual env failed."  1>&2
          exit -1
      fi

      # pip install tsbenchmark
      # $conda_exec install -n $venv_name -y pip
      # "$venv_dir/bin/pip" install tsbenchmark

    else
      echo "venv dir $venv_dir already exists, skip to create"
    fi
fi

# check pyton executable
if [ ! -f "$py_exec" ];then
  echo "py_exe $py_exec is not exists, can not execute python script"
  exit -1
fi

# check pyton path
if [ ! -z "$python_path" ];then
  export PYTHONPATH=$python_path
fi

# check dataset cache path
if [ ! -z "$datasets_cache_path" ];then
  export TSB_DATASETS_CACHE_PATH=$datasets_cache_path
fi

# run script
$py_exec $python_script
