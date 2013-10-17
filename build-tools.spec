# $Id$
#

Summary: tools for build creation
Name: build-tools
Version: 1.1
Release: 1
Packager: Andrey V. Scopenco <andrey@scopenco.net>
License: GPL
Group: Applications/System

Source: %{name}-%{version}.tar.gz
Source1: build.sh
Requires: bash, grep
Requires: yum, python, rhpl, createrepo, repoview

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch

%description
tools for build creation

%prep
%setup

%install
rm -rf $RPM_BUILD_ROOT

# Install the code
mkdir -p $RPM_BUILD_ROOT/%{_datadir}/%{name}
cp -a *.py *.sh modules $RPM_BUILD_ROOT/%{_datadir}/%{name}

# build.sh
mkdir -p $RPM_BUILD_ROOT/%{_bindir}
install -m 0755 %{SOURCE1} \
                $RPM_BUILD_ROOT/%{_bindir}/build.sh

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_datadir}/%{name}
%{_bindir}/build.sh

%changelog
* Wed Apr 14 2010 Andrey Scopenco <andrey@scopenco.net>
- create spec
