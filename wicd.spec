Name:          wicd
Version:       1.7.0
Release:       %mkrel 1
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
BuildRoot:     %{tmpdir}/%{name}-%{version}-buildroot

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
rm -rf $RPM_BUILD_ROOT
python setup.py install \
       --optimize=2 \
       --root=$RPM_BUILD_ROOT

install -D %{SOURCE1} %{buildroot}/%{_initrddir}/%{name}

%find_lang %name

%clean
rm -rf $RPM_BUILD_ROOT

%pre

%postun

%post
%_preun_service network
%_preun_service network-up
%_post_service %{name}

%preun
%_preun_service %{name}
%_post_service network
%_post_service network-up

%files -f %name.lang
%defattr(644,root,root,755)
%doc AUTHORS README
%{_sysconfdir}/acpi/resume.d/80-wicd-connect.sh
%{_sysconfdir}/acpi/suspend.d/50-wicd-suspend.sh
%{_libdir}/pm-utils/sleep.d/55wicd
%{py_puresitedir}/%{name}/*
%{py_puresitedir}/*.egg-info
%{_datadir}/pixmaps/%{name}
%{_mandir}
%{_datadir}/locale
%{_datadir}/%{name}
%{_iconsdir}/hicolor
%{_sysconfdir}/dbus-1/system.d/wicd.conf
%{_sysconfdir}/wicd
%{_sysconfdir}/xdg/autostart/wicd-tray.desktop
%dir %{_libdir}/%{name}/
%attr(755,root,root) %{_libdir}/%{name}/*.py

%attr(755,root,root) %{_bindir}/wicd-client
%attr(755,root,root) %{_bindir}/wicd-curses
%{_libdir}/wicd/backends/be-external.py
%{_libdir}/wicd/backends/be-ioctl.py
%attr(755,root,root) %{_sbindir}/wicd
%{_datadir}/applications/wicd.desktop
/var/lib/%{name}
%attr(754,root,root) /etc/rc.d/init.d/%{name}
