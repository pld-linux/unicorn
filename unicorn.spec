#
# TODO
# - optflags
# - bewan_adsl_status is linked with gtk+, maybe subpackage
# - rc-scripts support?
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
%bcond_with	usb		# build usb driver
#
Summary:	Unicorn ADSL modem software
Summary(pl.UTF-8):	Oprogramowanie do modemów ADSL Unicorn
Name:		unicorn
Version:	0.9.3
%define	_rel	0.1
Release:	%{_rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://www.bewan.com/bewan/drivers/A1012-A1006-A904-A888-A983-%{version}.tgz
# Source0-md5:	ff9829f03168279a079d05aea780ee99
URL:		http://www.bewan.com/
BuildRequires:	gtk+-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Unicorn ADSL modem tools.

%description -l pl.UTF-8
Narzędzia do modemów ADSL Unicorn.

%package -n kernel-net-%{name}
Summary:	Unicorn ADSL modem drivers for Linux kernel
Summary(pl.UTF-8):	Sterowniki do modemów ADSL Unicorn dla jądra Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
Requires:	%{name} = %{version}-%{_rel}

%description -n kernel-net-%{name}
Unicorn ADSL modem drivers for Linux kernel.

%description -n kernel-net-%{name} -l pl.UTF-8
Sterowniki do modemów ADSL Unicorn dla jądra Linuksa.

%package -n kernel-smp-net-%{name}
Summary:	Unicorn ADSL modem drivers for Linux SMP kernel
Summary(pl.UTF-8):	Sterowniki do modemów ADSL Unicorn dla jądra Linuksa SMP
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
Requires:	%{name}-devel = %{version}-%{_rel}

%description -n kernel-smp-net-%{name}
Unicorn ADSL modem drivers for Linux SMP kernel.

%description -n kernel-smp-net-%{name} -l pl.UTF-8
Sterowniki do modemów ADSL Unicorn dla jądra Linuksa SMP.

%prep
%setup -q -n %{name}

%build
%if %{with userspace}
%{__make} applis
%endif

%if %{with kernel}
%{__make} -C libm

cd unicorn_pci
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%if %{with dist_kernel}
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} clean \
		KERNEL_SOURCES="$PWD/o" \
		RCS_FIND_IGNORE="-name '*.ko' -o -name nv-kernel.o -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		KERNEL_SOURCES="$PWD/o" \
		CC="%{__cc}" CPP="%{__cpp}" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}

	mv unicorn_pci_atm{,-$cfg}.ko
	mv unicorn_pci_eth{,-$cfg}.ko
done

%if %{with usb}
cd ../unicorn_usb
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%if %{with dist_kernel}
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o -name nv-kernel.o -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	mv unicorn_usb_atm{,-$cfg}.ko
	mv unicorn_usb_eth{,-$cfg}.ko
done
%endif
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
%{__make} applis_install \
	prefix=%{_prefix} \
	DESTDIR=$RPM_BUILD_ROOT

%find_lang bewan_adsl_status
%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/misc
for mods in atm eth ; do
install unicorn_pci/unicorn_pci_$mods-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/unicorn_pci_$mods.ko
%if %{with usb}
install unicorn_usb/unicorn_usb_$mods-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/misc/unicorn_usb_$mods.ko
%endif
%if %{with smp} && %{with dist_kernel}
install unicorn_pci/unicorn_pci_$mods-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/unicorn_pci_$mods.ko
%if %{with usb}
install unicorn_usb/unicorn_usb_$mods-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/unicorn_usb_$mods.ko
%endif
%endif
done
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel-net-%{name}
%depmod %{_kernel_ver}

%postun -n kernel-net-%{name}
%depmod %{_kernel_ver}

%post -n kernel-smp-net-%{name}
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-net-%{name}
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files -f bewan_adsl_status.lang
%defattr(644,root,root,755)
%doc COPYING README scripts
%attr(755,root,root) %{_bindir}/*
%{_datadir}/bewan_adsl_status
%endif

%if %{with kernel}
%files -n kernel-net-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-net-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/misc/*
%endif
%endif
