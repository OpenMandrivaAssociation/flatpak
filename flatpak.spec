# Warning: this package is synchronized with Fedora!

%global libmajor 0
%global girapi 1.0
%global girlib %mklibname %{name}-gir %{girapi}
%global libname %mklibname %{name} %{libmajor}
%global devname %mklibname %{name} -d

# Minimum dependent components
%global bubblewrap_version 0.1.7
%global ostree_version 2017.1

%{?!_pkgdocdir:%define _pkgdocdir %{_docdir}/%{name}}

Name:           flatpak
Version:        0.8.7
Release:        1
Summary:        Application deployment framework for desktop apps

License:        LGPLv2+
URL:            https://flatpak.org/
Source0:        https://github.com/flatpak/flatpak/releases/download/%{version}/%{name}-%{version}.tar.xz

BuildRequires:  pkgconfig(fuse)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libarchive) >= 2.8.0
BuildRequires:  pkgconfig(libelf) >= 0.8.12
BuildRequires:  pkgconfig(libsoup-2.4)
BuildRequires:  pkgconfig(ostree-1) >= %{ostree_version}
BuildRequires:  pkgconfig(polkit-gobject-1)
BuildRequires:  pkgconfig(libseccomp)
BuildRequires:  pkgconfig(xau)
BuildRequires:  pkgconfig(gtk-doc)
BuildRequires:  gobject-introspection-devel >= 1.40.0
BuildRequires:  docbook-dtds
BuildRequires:  docbook-style-xsl
BuildRequires:  intltool
BuildRequires:  attr-devel
BuildRequires:  libcap-devel
BuildRequires:  dwarf-devel
BuildRequires:  pkgconfig(systemd)
BuildRequires:  xsltproc
BuildRequires:  xmlto
BuildRequires:  bubblewrap >= %{bubblewrap_version}

# Needed for the document portal.
Requires:       fuse

# Needed for confinement
Requires:       bubblewrap >= %{bubblewrap_version}
Requires:       ostree >= %{ostree_version}

# Required to ensure flatpak functions
Requires:       %{libname} = %{version}-%{release}
Requires:       %{girlib} = %{version}-%{release}

%description
flatpak is a system for building, distributing and running sandboxed desktop
applications on Linux. See https://wiki.gnome.org/Projects/SandboxedApps for
more information.

%package builder
Summary:        Build helper for %{name}
License:        LGPLv2+
Requires:       %{name} = %{version}-%{release}
Requires:       bzr
Requires:       git-core
Requires:       patch
Requires:       binutils
Requires:       tar
Requires:       unzip

%description builder
flatpak-builder is a tool that makes it easy to build applications and their
dependencies by automating the configure && make && make install steps.

%package -n %{devname}
Summary:        Development files for %{name}
Group:          Development/C
License:        LGPLv2+
Provides:       %{name}-devel = %{version}-%{release}
Provides:       %{name}-devel = %{version}-%{release}
Requires:       %{name} = %{version}-%{release}
Requires:       %{libname} = %{version}-%{release}
Requires:       %{girlib} = %{version}-%{release}

%description -n %{devname}
This package contains the pkg-config file and development headers for %{name}.

%package -n %{libname}
Summary:        Libraries for %{name}
Group:          System/Libraries
License:        LGPLv2+
Requires:       bubblewrap >= %{bubblewrap_version}
Requires:       ostree >= %{ostree_version}

%description -n %{libname}
This package contains libflatpak.

%package -n %{girlib}
Summary:        GObject Introspection Libraries for %{name}
Group:          System/Libraries
License:        LGPLv2+
Requires:       %{libname} = %{version}-%{release}

%description -n %{girlib}
This package contains libflatpak GObject libraries.

%prep
%setup -q
%apply_patches

%build
(if ! test -x configure; then NOCONFIGURE=1 ./autogen.sh; CONFIGFLAGS=--enable-gtk-doc; fi;
 # User namespace support is sufficient.

%configure --with-dwarf-header=%{_includedir}/libdwarf --with-priv-mode=none \
	--with-systemdsystemunitdir=%{_unitdir} \
                 --with-system-bubblewrap --enable-docbook-docs $CONFIGFLAGS)

%make V=1


%install
%make_install
# The system repo is not installed by the flatpak build system.
install -d %{buildroot}%{_localstatedir}/lib/flatpak
install -d %{buildroot}%{_sysconfdir}/flatpak/remotes.d
rm -f %{buildroot}%{_libdir}/libflatpak.la

%find_lang %{name}

%post
# Create an (empty) system-wide repo.
flatpak remote-list --system &> /dev/null || :

%files -f %{name}.lang
%{_bindir}/flatpak
%{_datadir}/bash-completion
%{_datadir}/dbus-1/interfaces/org.freedesktop.Flatpak.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.portal.Documents.xml
%{_datadir}/dbus-1/interfaces/org.freedesktop.impl.portal.PermissionStore.xml
%{_datadir}/dbus-1/services/org.freedesktop.Flatpak.service
%{_datadir}/dbus-1/services/org.freedesktop.impl.portal.PermissionStore.service
%{_datadir}/dbus-1/services/org.freedesktop.portal.Documents.service
%{_datadir}/dbus-1/system-services/org.freedesktop.Flatpak.SystemHelper.service
# Co-own directory.
%{_datadir}/gdm/env.d
%{_datadir}/%{name}
%{_datadir}/polkit-1/actions/org.freedesktop.Flatpak.policy
%{_datadir}/polkit-1/rules.d/org.freedesktop.Flatpak.rules
%{_libexecdir}/flatpak-dbus-proxy
%{_libexecdir}/flatpak-session-helper
%{_libexecdir}/flatpak-system-helper
%{_libexecdir}/xdg-document-portal
%{_libexecdir}/xdg-permission-store
%dir %{_localstatedir}/lib/flatpak
%dir %{_sysconfdir}/flatpak/remotes.d
%{_mandir}/man1/%{name}*.1*
%{_mandir}/man5/%{name}-metadata.5*
%{_mandir}/man5/%{name}-flatpakref.5*
%{_mandir}/man5/%{name}-flatpakrepo.5*
%exclude %{_mandir}/man1/flatpak-builder.1*
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.Flatpak.SystemHelper.conf
%{_sysconfdir}/profile.d/flatpak.sh
%{_systemunitdir}/flatpak-system-helper.service
%{_userunitdir}/flatpak-session-helper.service
%{_userunitdir}/xdg-document-portal.service
%{_userunitdir}/xdg-permission-store.service
# Co-own directory.
%{_userunitdir}/dbus.service.d


%files builder
%{_bindir}/flatpak-builder
%{_mandir}/man1/flatpak-builder.1*

%files -n %{devname}
%doc COPYING
%doc NEWS README.md
%doc %{_pkgdocdir}
%{_datadir}/gir-1.0/Flatpak-%{girapi}.gir
%{_datadir}/gtk-doc/
%{_includedir}/%{name}/
%{_libdir}/libflatpak.so
%{_libdir}/pkgconfig/%{name}.pc

%files -n %{libname}
%{_libdir}/libflatpak.so.%{libmajor}
%{_libdir}/libflatpak.so.%{libmajor}.*

%files -n %{girlib}
%{_libdir}/girepository-1.0/Flatpak-%{girapi}.typelib
