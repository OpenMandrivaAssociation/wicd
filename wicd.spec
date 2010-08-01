Name:          wicd
Version:       1.7.0
Release:       %mkrel 2
License:       GPLv2
Group:         System/Configuration/Networking
Source0:       http://dl.sourceforge.net/wicd/%{name}-%{version}.tar.gz
Source1:       %{name}.init
# Install pm-utils scripts in %{libdir}/pm-utils, not in /usr/lib/pm-utils
Patch0:        wicd-libdir.patch
URL:           http://wicd.net/
Summary:       wired and wireless network manager
BuildRequires: python-devel
Requires:      python
Requires:      python-urwid
BuildRoot:     %{tmpdir}/%{name}-%{version}

%description
Wicd is an open source wired and wireless network manager for Linux
which aims to provide a simple interface to connect to networks with a
wide variety of settings.

%prep
%setup -q
%patch0 -p1 -b .libdir
python setup.py configure --no-install-kde

%build
python setup.py build

%install
rm -rf %{buildroot}
python setup.py install \
       --optimize=2 \
       --root=%{buildroot}

install -D %{SOURCE1} %{buildroot}/%{_initrddir}/%{name}

%find_lang %name

%clean
rm -rf %{buildroot}

%post
%_preun_service network
%_preun_service network-up
%_post_service %{name}

%preun
%_preun_service %{name}
%_post_service network
%_post_service network-up

%files -f %name.lang
%defattr(-,root,root)
%doc AUTHORS README
%{_bindir}/*
%{_sysconfdir}/acpi/resume.d/80-wicd-connect.sh
%{_sysconfdir}/acpi/suspend.d/50-wicd-suspend.sh
%{_libdir}/pm-utils/sleep.d/91wicd
%{py_puresitedir}/%{name}/*
%{py_puresitedir}/*.egg-info
%{_datadir}/pixmaps/*
%{_mandir}
%{_datadir}/%{name}
%{_iconsdir}/hicolor
%{_sysconfdir}/dbus-1/system.d/wicd.conf
%{_sysconfdir}/wicd
%{_sysconfdir}/xdg/autostart/wicd-tray.desktop
%attr(755,root,root) %{_sbindir}/wicd
%{_datadir}/applications/wicd.desktop
%{_var}/lib/%{name}
%_logdir/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
