# Warning: this package is synchronized with Fedora!

%global libmajor 0
%global girapi 1.0
%global girlib %mklibname %{name}-gir %{girapi}
%global libname %mklibname %{name} %{libmajor}
%global devname %mklibname %{name} -d

# Minimum dependent components
%global bubblewrap_version 0.3.1
%global ostree_version 2019.1

%{?!_pkgdocdir:%define _pkgdocdir %{_docdir}/%{name}}

Name:		flatpak
Version:	1.10.0
Release:	1
Summary:	Application deployment framework for desktop apps
Group:		System/Base
License:	LGPLv2+
URL:		https://flatpak.org/
Source0:	https://github.com/flatpak/flatpak/releases/download/%{version}/%{name}-%{version}.tar.xz
Source1:	flatpak-init.service
Source2:	flatpak.tmpfiles
BuildRequires:	pkgconfig(fuse)
BuildRequires:	pkgconfig(gio-unix-2.0)
BuildRequires:	pkgconfig(json-glib-1.0)
BuildRequires:	pkgconfig(libarchive) >= 2.8.0
BuildRequires:	pkgconfig(libelf) >= 0.8.12
BuildRequires:	pkgconfig(libsoup-2.4)
BuildRequires:	pkgconfig(ostree-1) >= %{ostree_version}
BuildRequires:	pkgconfig(appstream-glib) >= 0.5.10
BuildRequires:	pkgconfig(polkit-gobject-1)
BuildRequires:	pkgconfig(libseccomp)
BuildRequires:	pkgconfig(xau)
BuildRequires:	pkgconfig(gtk-doc)
BuildRequires:	python3dist(pyparsing)
BuildRequires:	gobject-introspection-devel >= 1.40.0
BuildRequires:	docbook-dtds
BuildRequires:	docbook-style-xsl
BuildRequires:	intltool
BuildRequires:	attr-devel
BuildRequires:	pkgconfig(libcap)
BuildRequires:	libdwarf-devel
BuildRequires:	gpgme-devel
BuildRequires:	pkgconfig(libsystemd)
BuildRequires:	systemd-macros
BuildRequires:	xsltproc
BuildRequires:	xmlto
BuildRequires:	bison
BuildRequires:	byacc
BuildRequires:	bubblewrap >= %{bubblewrap_version}
Requires(post):	rpm-helper
# Needed for the document portal.
Requires:	fuse
# TLS support
Requires:	glib-networking

# Needed for confinement
Requires:	bubblewrap >= %{bubblewrap_version}
Requires:	ostree >= %{ostree_version}

# Required to ensure flatpak functions
Requires:	%{libname} = %{EVRD}
Requires:	%{girlib} = %{EVRD}

%description
flatpak is a system for building, distributing and running sandboxed desktop
applications on Linux. See https://wiki.gnome.org/Projects/SandboxedApps for
more information.

%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/C
License:	LGPLv2+
Provides:	%{name}-devel = %{EVRD}
Requires:	%{name} = %{EVRD}
Requires:	%{libname} = %{EVRD}
Requires:	%{girlib} = %{EVRD}

%description -n %{devname}
This package contains the pkg-config file and development headers for %{name}.

%package -n %{libname}
Summary:	Libraries for %{name}
Group:		System/Libraries
License:	LGPLv2+
Requires:	bubblewrap >= %{bubblewrap_version}
Requires:	ostree >= %{ostree_version}

%description -n %{libname}
This package contains libflatpak.

%package -n %{girlib}
Summary:	GObject Introspection Libraries for %{name}
Group:		System/Libraries
License:	LGPLv2+
Requires:	%{libname} = %{EVRD}

%description -n %{girlib}
This package contains libflatpak GObject libraries.

%prep
%autosetup -p1

%build
# as of Flatpak 1.5.2 and LLVM/Clang 9.0.1-0.20191216.1 build failed with many error like:
#error: passing 'typeof (*(&g_define_type_id__volatile)) *' (aka 'volatile unsigned long *') 
#to parameter of type 'gsize *' (aka 'unsigned long *') discards qualifiers 
#[-Werror,-Wincompatible-pointer-types-discards-qualifiers]
# Switch to GCC fix it
#export CC=gcc
#export CXX=g++

(if ! test -x configure; then NOCONFIGURE=1 ./autogen.sh; CONFIGFLAGS=--enable-gtk-doc; fi;
 # User namespace support is sufficient.

%configure --with-dwarf-header=%{_includedir}/libdwarf --with-priv-mode=none \
	--with-systemdsystemunitdir=%{_unitdir} \
	--enable-sandboxed-triggers --enable-xauth \
        --with-system-bubblewrap --enable-docbook-docs $CONFIGFLAGS)

%make_build V=1

%install
%make_install
# The system repo is not installed by the flatpak build system.
install -d %{buildroot}%{_localstatedir}/lib/flatpak
install -d %{buildroot}%{_sysconfdir}/flatpak/remotes.d

install -m 0644 %{SOURCE1} -D %{buildroot}%{_unitdir}/flatpak-init.service
install -m 0644 %{SOURCE2} -D %{buildroot}%{_tmpfilesdir}/flatpak.conf

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-%{name}.preset << EOF
enable %{name}-init.service
EOF

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
%{_libexecdir}/flatpak-validate-icon
%{_libexecdir}/flatpak-oci-authenticator
%{_libexecdir}/revokefs-fuse
%{_datadir}/bash-completion/completions/flatpak
%{_datadir}/zsh/site-functions/_flatpak
%{_datadir}/flatpak
%{_datadir}/dbus-1/interfaces/org.freedesktop.Flatpak*
%{_datadir}/dbus-1/interfaces/org.freedesktop.portal.Flatpak*
%{_datadir}/dbus-1/system-services/org.freedesktop.Flatpak*
%{_datadir}/dbus-1/services/org.freedesktop.Flatpak.*
%{_datadir}/dbus-1/services/org.freedesktop.portal.Flatpak.*
%{_datadir}/dbus-1/services/org.flatpak.Authenticator.Oci.service
%{_datadir}/polkit-1/rules.d/org.freedesktop.Flatpak.*
%{_datadir}/polkit-1/actions/org.freedesktop.Flatpak.*
%{_datadir}/fish/vendor_completions.d/flatpak.fish
%{_mandir}/man1/flatpak*.1*
%{_mandir}/man5/flatpak*.5*
%{_localstatedir}/lib/flatpak
%{_presetdir}/86-%{name}.preset
%{_userunitdir}/flatpak*.service
#{_userunitdir}/dbus.service.d/flatpak.conf
%{_unitdir}/flatpak*.service
%{_systemd_user_env_generator_dir}/60-flatpak
%{_tmpfilesdir}/flatpak.conf
%{_sysconfdir}/profile.d/flatpak.sh
%{_sysconfdir}/flatpak
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.Flatpak*
# FIXME this probably needs to move to where sddm can see it?
#{_datadir}/gdm
%doc %{_docdir}/%{name}
%{_sysusersdir}/flatpak.conf

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
