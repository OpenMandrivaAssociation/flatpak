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
Version:	1.15.6
Release:	1
Summary:	Application deployment framework for desktop apps
Group:		System/Base
License:	LGPLv2+
URL:		https://flatpak.org/
Source0:	https://github.com/flatpak/flatpak/releases/download/%{version}/%{name}-%{version}.tar.xz
Source1:	flatpak-init.service
Source2:	flatpak.tmpfiles
# (tpg) wget https://dl.flathub.org/repo/flathub.flatpakrepo
Source3:	https://dl.flathub.org/repo/flathub.flatpakrepo
Patch0:		flatpak-1.15.2-compile.patch
BuildRequires:	pkgconfig(appstream) < 1.0-0
BuildRequires:	pkgconfig(fuse)
BuildRequires:	pkgconfig(gio-unix-2.0)
BuildRequires:	pkgconfig(json-glib-1.0)
BuildRequires:	pkgconfig(libarchive) >= 2.8.0
BuildRequires:	pkgconfig(libcurl)
BuildRequires:	pkgconfig(libelf) >= 0.8.12
BuildRequires:	pkgconfig(ostree-1) >= %{ostree_version}
BuildRequires:	pkgconfig(appstream-glib) >= 0.5.10
BuildRequires:	pkgconfig(polkit-gobject-1)
BuildRequires:	pkgconfig(libseccomp)
BuildRequires:	pkgconfig(xau)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	pkgconfig(dconf)
BuildRequires:	pkgconfig(gtk-doc)
# OPTIONAL dep -- sadly if included, introduces a
# GTK 4 dependency we really don't want to have in
# Plasma or even LXQt
#BuildRequires:	pkgconfig(malcontent-0)
BuildRequires:	python3dist(pyparsing)
BuildRequires:	gobject-introspection-devel >= 1.40.0
BuildRequires:	docbook-dtds
BuildRequires:	docbook-style-xsl
BuildRequires:	intltool
BuildRequires:	pkgconfig(libattr)
BuildRequires:	pkgconfig(libcap)
BuildRequires:	pkgconfig(libdwarf)
BuildRequires:	pkgconfig(gpgme)
BuildRequires:	pkgconfig(libsystemd)
BuildRequires:	systemd-rpm-macros
BuildRequires:	xsltproc
BuildRequires:	xmlto
BuildRequires:	bison
BuildRequires:	byacc
BuildRequires:	bubblewrap >= %{bubblewrap_version}
BuildRequires:	meson
BuildRequires:	polkit
BuildRequires:	socat
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
%systemd_requires

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
%meson \
	-Dmalcontent=disabled \
	-Dselinux_module=disabled \
	-Dsystem_bubblewrap=%{_bindir}/bwrap

%if 0
From old autoconf setup -- doesn't seem to be needed anymore:   '
	--with-dwarf-header=%{_includedir}/libdwarf \
	--with-priv-mode=none \
	--with-systemdsystemunitdir=%{_unitdir} \
	--enable-sandboxed-triggers \
	--enable-xauth \
	--with-system-bubblewrap \
	--enable-docbook-docs $CONFIGFLAGS)
%endif


%build
%meson_build

%install
%meson_install

# The system repo is not installed by the flatpak build system.
install -d %{buildroot}%{_localstatedir}/lib/flatpak
install -d %{buildroot}%{_sysconfdir}/flatpak/remotes.d

install -m 0644 %{SOURCE1} -D %{buildroot}%{_unitdir}/flatpak-init.service
install -m 0644 %{SOURCE2} -D %{buildroot}%{_tmpfilesdir}/flatpak.conf
install -m 0644 %{SOURCE3} -D %{buildroot}%{_sysconfdir}/flatpak/remotes.d/flathub.flatpakrepo

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-%{name}.preset << EOF
enable %{name}-init.service
EOF

%find_lang %{name}

%pre
%sysusers_create_package %{name} %{_sysusersdir}/flatpak.conf

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
%{_datadir}/fish/vendor_conf.d/flatpak.fish
%doc %{_mandir}/man1/flatpak*.1*
%doc %{_mandir}/man5/flatpak*.5*
%{_localstatedir}/lib/flatpak
%{_presetdir}/86-%{name}.preset
%{_userunitdir}/flatpak*.service
%{_systemd_system_env_generator_dir}/60-flatpak-system-only
%{_unitdir}/flatpak*.service
%{_systemd_user_env_generator_dir}/60-flatpak
%{_tmpfilesdir}/flatpak.conf
%{_sysconfdir}/profile.d/flatpak.sh
%{_sysconfdir}/flatpak
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.Flatpak*
# FIXME this probably needs to move to where sddm can see it?
#{_datadir}/gdm
%doc %{_docdir}/%{name}
%doc %{_datadir}/gtk-doc/html/
%{_sysusersdir}/flatpak.conf

%files -n %{devname}
%{_includedir}/flatpak
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*.pc

%files -n %{libname}
%{_libdir}/libflatpak.so.%{libmajor}
%{_libdir}/libflatpak.so.%{libmajor}.*

%files -n %{girlib}
%{_libdir}/girepository-1.0/Flatpak-%{girapi}.typelib
%{_datadir}/gir-1.0/Flatpak-%{girapi}.gir
