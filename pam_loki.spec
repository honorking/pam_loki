%define pam_loki_home /lib64/security/pam_loki

%define pam_loki_version 1.0.3

#---------------------------------------------------------------------------------
Name:           pam_loki
License:        MIT
Group:          System Environment/Base
Summary:        A Pluggable Authorization Module for LOKI
Version:        %{pam_loki_version}
Release:        0.%(perl -e 'print time()')%{?dist}
URL:            http://gitlab.wandoulabs.com/sre-team/pam_loki 
Source0:        pam_loki
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:  gcc >= 4.0.0
BuildRequires:  pam-devel
BuildRequires:  python-devel >= 2.6

Requires:       pam
Requires:       python

Provides:      pam_loki

%description
This is pam_loki, a pluggable authorization module that collaborate with LOKI API.
THis module provide privilege checking based on hostname & username.

%prep
exit 0

%build
cd $RPM_SOURCE_DIR/pam_loki
make clean
make %{?_smp_mflags}

%install
cd $RPM_SOURCE_DIR/pam_loki
make DESTDIR=%{buildroot} install
mkdir -p %{buildroot}%{pam_loki_home}
install -D -m 644 -o root -g root $RPM_SOURCE_DIR/pam_loki/pam_loki/pam_loki.py %{buildroot}%{pam_loki_home}

%pre
exit 0

%post
# Register the service
exit 0 

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{pam_loki_home}
%attr(755, root, root) /lib64/security/pam_python.so
