# Warning: this package is synchronized with Fedora!

%global libmajor 0
%global girapi 1.0
%global girlib %mklibname %{name}-gir %{girapi}
%global libname %mklibname %{name} %{libmajor}
%global devname %mklibname %{name} -d

# Minimum dependent components
%global bubblewrap_version 0.1.8
%global ostree_version 2017.14

%{?!_pkgdocdir:%define _pkgdocdir %{_docdir}/%{name}}

Name:           flatpak
Version:        1.0.1
Release:        1
Summary:        Application deployment framework for desktop apps
Group:        	System/Base
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
BuildRequires:	pkgconfig(appstream-glib) >= 0.5.10
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
BuildRequires:  libdwarf-devel
BuildRequires:  gpgme-devel
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  systemd
BuildRequires:  xsltproc
BuildRequires:  xmlto
BuildRequires:  bison
BuildRequires:  byacc
BuildRequires:  bubblewrap >= %{bubblewrap_version}
Requires(post):       rpm-helper
# Needed for the document portal.
Requires:       fuse
# TLS support
Requires:	glib-networking

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
	--with-systemdsystemunitdir=%{_systemunitdir} \
                 --with-system-bubblewrap --enable-docbook-docs $CONFIGFLAGS)

%make V=1


%install
%make_install
# The system repo is not installed by the flatpak build system.
install -d %{buildroot}%{_localstatedir}/lib/flatpak
install -d %{buildroot}%{_sysconfdir}/flatpak/remotes.d

%find_lang %{name}

%post
# Create an (empty) system-wide repo.
flatpak remote-list --system &> /dev/null || :

%files -f %{name}.lang
%{_bindir}/flatpak
%{_bindir}/flatpak-bisect
%{_bindir}/flatpak-coredumpctl
%{_libexecdir}/flatpak-system-helper
%{_libexecdir}/flatpak-session-helper
%{_libexecdir}/flatpak-portal
%{_libexecdir}/flatpak-dbus-proxy
%{_datadir}/bash-completion/completions/flatpak
%{_datadir}/zsh/site-functions/_flatpak
%{_datadir}/flatpak
%{_datadir}/dbus-1/interfaces/org.freedesktop.Flatpak*
%{_datadir}/dbus-1/interfaces/org.freedesktop.portal.Flatpak*
%{_datadir}/dbus-1/system-services/org.freedesktop.Flatpak*
%{_datadir}/dbus-1/services/org.freedesktop.Flatpak.*
%{_datadir}/dbus-1/services/org.freedesktop.portal.Flatpak.*
%{_datadir}/polkit-1/rules.d/org.freedesktop.Flatpak.*
%{_datadir}/polkit-1/actions/org.freedesktop.Flatpak.*
%{_mandir}/man1/flatpak*.1*
%{_mandir}/man5/flatpak*.5*
%{_localstatedir}/lib/flatpak
%{_prefix}/lib/systemd/user/flatpak*.service
%{_prefix}/lib/systemd/user/dbus.service.d/flatpak.conf
%{_systemunitdir}/flatpak*.service
%{_sysconfdir}/profile.d/flatpak.sh
%{_sysconfdir}/flatpak
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.Flatpak*
# FIXME this probably needs to move to where sddm can see it?
%{_datadir}/gdm
%doc %{_docdir}/%{name}

%files -n %{devname}
%{_includedir}/flatpak
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc
%doc %{_datadir}/gtk-doc/html/flatpak

%files -n %{libname}
%{_libdir}/libflatpak.so.%{libmajor}
%{_libdir}/libflatpak.so.%{libmajor}.*

%files -n %{girlib}
%{_libdir}/girepository-1.0/Flatpak-%{girapi}.typelib
%{_datadir}/gir-1.0/Flatpak-%{girapi}.gir
