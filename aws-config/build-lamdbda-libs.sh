#!/usr/bin/env bash

#set -e -o pipefail

sudo yum -y upgrade
sudo yum -y groupinstall "Development Tools"
sudo yum -y install blas blas-devel lapack lapack-devel Cython --enablerepo=epel

virtualenv ~/env
cd ~/env
source bin/activate
pip install numpy
pip install scipy
pip install imagehash
pip install elasticsearch
pip install six
pip install pillow
pip install opencv2

for dir in lib64/python2.7/site-packages lib/python2.7/site-packages
do
  if [ -d $dir ] ; then
    pushd $dir; zip -r ~/deps.zip .; popd
  fi
done
mkdir -p local/lib
cp /usr/lib64/liblapack.so.3 /usr/lib64/libblas.so.3 /usr/lib64/libgfortran.so.3 /usr/lib64/libquadmath.so.0 local/lib/
zip -r ~/deps.zip local/lib