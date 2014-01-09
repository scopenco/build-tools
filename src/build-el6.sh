#!/bin/sh
# scripts is usefull for beginners that would like
# to understand how constructor works
#

set -e
set -x

# local tmp directory where rpm packages will download to
TMPDIR="repo-el6" 
# path to repository 
XML_DIR="repository"
# path to project xml
PROJECT="hosts/myproject/centos-6-example.xml"
# uri of repo where to search yum repository after creation in production
PROJECT_REPO="http://repo.domain.con/repo"

# rpm old env
rm -rf $TMPDIR
# fild all packages and download to repo/RPMS
python constructor.py -c $PROJECT -x $XML_DIR -p $TMPDIR/RPMS
# exit if status is no 0
if [ $? -ne 0 ]; then
    exit 1
fi

# create rpmbuild env for project and release rpm building
mkdir -p ~/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
echo '%_topdir %(echo $HOME)/rpmbuild' > ~/.rpmmacros

# build project rpm
python gen_spec.py -x $XML_DIR -c $PROJECT -s project_template > project.spec
if [ $? -ne 0 ]; then
    exit 1
fi
RPM=`rpmbuild -bb --rmspec project.spec 2>&1 | grep 'Wrote:' | cut -d ' ' -f2`

# copy project rpm to RPMS directory
cp -rvf $RPM $TMPDIR/RPMS

# build release rpm
python gen_spec.py -x $XML_DIR -c $PROJECT -s release_template > release.spec
if [ $? -ne 0 ]; then
    exit 1
fi
RPM=`rpmbuild -bb --rmspec release.spec 2>&1 | grep 'Wrote:' | cut -d ' ' -f2`

# copy project rpm to RPMS directory
cp -rvf $RPM $TMPDIR/RPMS

# get anaconda iso need for pxe/kickstart setup
mkdir $TMPDIR/images
wget http://mirror.yandex.ru/centos/6/os/x86_64/images/install.img -O $TMPDIR/images/install.img

# get comps.xml need for anaconda installer and create yum rrepository 
wget http://mirror.yandex.ru/centos/6/os/x86_64/repodata/b4e0b9342ef85d3059ff095fa7f140f654c2cb492837de689a58c581207d9632-c6-x86_64-comps.xml \
    -O $TMPDIR/comps.xml
createrepo -g $(pwd)/$TMPDIR/comps.xml -d $TMPDIR
rm -f $TMPDIR/comps.xml