%define debug_package %{nil}

Name:                wicd
Version:             1.7.2.3
Release:             1
Summary:             Wireless and wired network connection manager

Group:               System/Configuration/Networking
License:             GPLv2+
URL:                 http://wicd.sourceforge.net/
Source0:             https://launchpad.net/wicd/1.7/%{version}/+download/%{name}-%{version}.tar.gz
Source1:             wicd.logrotate
Source2:             org.wicd.daemon.service

Patch0:              wicd-1.7.0-remove-WHEREAREMYFILES.patch
Patch1:              wicd-1.7.1-dbus-failure.patch
Patch2:              wicd-1.7.0-dbus-policy.patch
Patch3:              wicd-1.7.1-DaemonClosing.patch

BuildRequires:       desktop-file-utils
BuildRequires:       systemd-units
BuildRequires:       python-babel

Requires:            pm-utils >= 1.2.4
Requires:            %{name}-common = %{version}-%{release}

%description
Wicd is designed to give the user as much control over behavior of network
connections as possible.  Every network, both wired and wireless, has its
own profile with its own configuration options and connection behavior.
Wicd will try to automatically connect only to networks the user specifies
it should try, with a preference first to a wired network, then to wireless.

This package provides the architecture-dependent components of wicd.

%package common
Summary:             Wicd common files
Group:               System/Base
BuildArch:           noarch
Requires:            dbus
Requires:            dbus-python
Requires:            dhclient
Requires:            ethtool
Requires:            iproute
Requires:            logrotate
Requires:            net-tools
Requires:            wireless-tools
Requires:            wpa_supplicant
Requires:            pygobject2
Requires(post):      systemd-units
Requires(preun):     systemd-units
Requires(postun):    systemd-units

%description common
This package provides the main wicd daemon and the wicd-cli front-end.

%package curses
Summary:             Curses client for wicd
Group:               System/Configuration/Networking
BuildArch:           noarch
Requires:            %{name}-common = %{version}-%{release}
Requires:            python-urwid >= 0.9.8.3

%description curses
Client program for wicd that uses a curses interface.

%package gtk
Summary:             GTK+ client for wicd
Group:               System/Configuration/Networking
BuildArch:           noarch
Requires:            %{name}-common = %{version}-%{release}
Requires:            notify-python
Requires:            pygtk2-libglade >= 2.10

%description gtk
Client program for wicd that uses a GTK+ interface.

%prep
%setup -q

# Remove the WHEREAREMYFILES and resetting of ~/.wicd/WHEREAREMYFILES
# This is pointless.  The documentation can just provide WHEREAREMYFILES,
# which we do in this package.
%patch0 -p1

# Handle D-Bus connection failures a little better
%patch1 -p1

# Allow users at the console to control wicd
%patch2 -p1

# Work around bug in DaemonClosing() calls
%patch3 -p1

%build
rm -f po/ast.po
%{__python} setup.py configure \
    --distro redhat \
    --lib %{_libdir} \
    --share %{_datadir}/wicd \
    --etc %{_sysconfdir}/wicd \
    --bin %{_bindir} \
    --pmutils %{_libdir}/pm-utils/sleep.d \
    --log %{_localstatedir}/log \
    --systemd %{_unitdir} --no-install-init

%{__python} setup.py build
%{__python} setup.py compile_translations

%install
rm -rf %{buildroot}
%{__python} setup.py install --skip-build --no-compile --root %{buildroot}
sed -i -e '/^#!\//, 1d'  %{buildroot}%{_datadir}/wicd/backends/be-external.py
sed -i -e '/^#!\//, 1d'  %{buildroot}%{_datadir}/wicd/backends/be-ioctl.py
sed -i -e '/^#!\//, 1d'  %{buildroot}%{_datadir}/wicd/cli/wicd-cli.py
sed -i -e '/^#!\//, 1d'  %{buildroot}%{_datadir}/wicd/curses/curses_misc.py
sed -i -e '/^#!\//, 1d'  %{buildroot}%{_datadir}/wicd/curses/netentry_curses.py
sed -i -e '/^#!\//, 1d'  %{buildroot}%{_datadir}/wicd/curses/prefs_curses.py
sed -i -e '/^#!\//, 1d'  %{buildroot}%{_datadir}/wicd/daemon/wicd-daemon.py
sed -i -e '/^#!\//, 1d'  %{buildroot}%{_datadir}/wicd/gtk/gui.py
sed -i -e '/^#!\//, 1d'  %{buildroot}%{_datadir}/wicd/gtk/prefs.py
sed -i -e '/^#!\//, 1d'  %{buildroot}%{_datadir}/wicd/gtk/wicd-client.py

rm -f %{buildroot}%{_localstatedir}/lib/wicd/WHEREAREMYFILES
rm -rf %{buildroot}%{_datadir}/doc
find %{buildroot} -type f -name ".empty_on_purpose" | xargs rm

for lib in %{buildroot}%{python_sitelib}/wicd/*.py ; do
    sed '/\/usr\/bin\/env/d' $lib > $lib.new &&
    touch -r $lib $lib.new &&
    mv $lib.new $lib
done

mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
install -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/logrotate.d/wicd

mkdir -p %{buildroot}%{_datadir}/dbus-1/system-services
install -m 0644 %{SOURCE2} %{buildroot}%{_datadir}/dbus-1/system-services/org.wicd.daemon.service

desktop-file-install \
    --remove-category="Application" \
    --delete-original \
    --dir=%{buildroot}%{_datadir}/applications \
    %{buildroot}%{_datadir}/applications/wicd.desktop

desktop-file-install \
    --dir=%{buildroot}%{_sysconfdir}/xdg/autostart \
    %{buildroot}%{_sysconfdir}/xdg/autostart/wicd-tray.desktop

%find_lang %{name}

%post common
if [ $1 -eq 1 ]; then
    # Package install, not upgrade
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun common
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl disable wicd.service > /dev/null 2>&1 || :
    /bin/systemctl stop wicd.service > /dev/null 2>&1 || :
fi

%postun common
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart wicd.service >/dev/null 2>&1 || :
fi

%triggerun -- wicd-common < 1.7.0-5
if /sbin/chkconfig --level 3 wicd ; then
    /bin/systemctl enable wicd.service >/dev/null 2>&1 || :
fi

%post gtk
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun gtk
if [ $1 -eq 0 ]; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans gtk
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files
%{_libdir}/pm-utils/sleep.d/55wicd

%files common -f %{name}.lang
%doc AUTHORS CHANGES LICENSE NEWS README other/WHEREAREMYFILES
%dir %{python_sitelib}/wicd
%dir %{_sysconfdir}/wicd
%dir %{_sysconfdir}/wicd/encryption
%dir %{_sysconfdir}/wicd/encryption/templates
%dir %{_sysconfdir}/wicd/scripts
%dir %{_sysconfdir}/wicd/scripts/postconnect
%dir %{_sysconfdir}/wicd/scripts/postdisconnect
%dir %{_sysconfdir}/wicd/scripts/preconnect
%dir %{_sysconfdir}/wicd/scripts/predisconnect
%{_sysconfdir}/acpi/resume.d/80-wicd-connect.sh
%{_sysconfdir}/acpi/suspend.d/50-wicd-suspend.sh
%{_sysconfdir}/logrotate.d/wicd.logrotate
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/wicd.conf
%config(noreplace) %{_sysconfdir}/wicd/dhclient.conf.template.default
%config(noreplace) %{_sysconfdir}/logrotate.d/wicd
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/active
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/active_wired
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/eap
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/eap-tls
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/leap
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/peap
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/peap-tkip
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/psu
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/ttls
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/wep-hex
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/wep-passphrase
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/wep-shared
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/wired_8021x
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/wpa
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/wpa-psk
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/wpa-peap
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/wpa2-leap
%config(noreplace) %{_sysconfdir}/wicd/encryption/templates/wpa2-peap
/%{_unitdir}/wicd.service
%{python_sitelib}/wicd/*
%{python_sitelib}/wicd-%{version}*.egg-info
%{_bindir}/wicd-cli
%{_bindir}/wicd-client
%{_sbindir}/wicd
%{_datadir}/applications/wicd.desktop
%{_datadir}/dbus-1/system-services/org.wicd.daemon.service
%{_datadir}/man/man1/wicd-client.1*
%{_datadir}/man/man5/wicd-manager-settings.conf.5*
%{_datadir}/man/man5/wicd-wired-settings.conf.5*
%{_datadir}/man/man5/wicd-wireless-settings.conf.5*
%{_datadir}/man/man8/wicd-cli.8*
%{_datadir}/man/man8/wicd.8*
%lang(nl) %{_datadir}/man/nl/man1/wicd-client.1*
%lang(nl) %{_datadir}/man/nl/man5/wicd-manager-settings.conf.5*
%lang(nl) %{_datadir}/man/nl/man5/wicd-wired-settings.conf.5*
%lang(nl) %{_datadir}/man/nl/man5/wicd-wireless-settings.conf.5*
%lang(nl) %{_datadir}/man/nl/man8/wicd.8*
%dir %{_datadir}/wicd
%dir %{_datadir}/wicd/backends
%dir %{_datadir}/wicd/cli
%dir %{_datadir}/wicd/daemon
%{_datadir}/wicd/backends/*
%{_datadir}/wicd/cli/*
%{_datadir}/wicd/daemon/*
%dir %{_localstatedir}/lib/wicd
%dir %{_localstatedir}/lib/wicd/configurations

%files curses
%dir %{_datadir}/wicd/curses
%{_datadir}/wicd/curses/*
%{_bindir}/wicd-curses
%{_datadir}/man/man8/wicd-curses.8*
%lang(nl) %{_datadir}/man/nl/man8/wicd-curses.8*

%files gtk
%dir %{_datadir}/wicd/gtk
%dir %{_datadir}/pixmaps/wicd
%{_sysconfdir}/xdg/autostart/wicd-tray.desktop
%{_datadir}/wicd/gtk/*
%{_datadir}/pixmaps/wicd/*
%{_datadir}/pixmaps/wicd-gtk.xpm
%{_bindir}/wicd-gtk
%{_datadir}/icons/hicolor/*/apps/wicd-gtk.png
%{_datadir}/icons/hicolor/scalable/apps/wicd-gtk.svg
