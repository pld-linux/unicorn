#
# TODO
# - optflags
# - usb driver doesn't build
# - pci dirver doesn't with 2.6.14.6 (skb_unlink changed in kernel)
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
Summary(pl):	Oprogramowanie do modemów ADSL Unicorn
Name:		unicorn
Version:	0.9.0
Release:	0.1
License:	GPL v2
Group:		Base/Kernel
Source0:	http://www.bewan.com/bewan/drivers/bast-%{version}.tgz
# Source0-md5:	8b4f880e79d9d23029cc8f85e2f6478a
URL:		http://www.bewan.com/
BuildRequires:	gtk+-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Unicorn ADSL modem tools.

%description -l pl
Narzêdzia do modemów ADSL Unicorn.

%package -n kernel-net-%{name}
Summary:	Unicorn ADSL modem drivers for Linux kernel
Summary(pl):	Sterowniki do modemów ADSL Unicorn dla j±dra Linuksa
Group:		Base/Kernel
Requires:	%{name} = %{version}-%{release}

%description -n kernel-net-%{name}
Unicorn ADSL modem drivers for Linux kernel.

%description -n kernel-net-%{name} -l pl
Sterowniki do modemów ADSL Unicorn dla j±dra Linuksa.

%package -n kernel-smp-net-%{name}
Summary:	Unicorn ADSL modem drivers for Linux SMP kernel
Summary(pl):	Sterowniki do modemów ADSL Unicorn dla j±dra Linuksa SMP
Group:		Base/Kernel
Requires:	%{name}-devel = %{version}-%{release}

%description -n kernel-smp-net-%{name}
Unicorn ADSL modem drivers for Linux SMP kernel.

%description -n kernel-smp-net-%{name} -l pl
Sterowniki do modemów ADSL Unicorn dla j±dra Linuksa SMP.

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
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	touch include/config/MARKER
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		HOSTCC="%{__cc}" \
		CPP="%{__cpp}" \
		M=$PWD O=$PWD \
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
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	touch include/config/MARKER
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		HOSTCC="%{__cc}" \
		CPP="%{__cpp}" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
#	mv unicorn_usb{,-$cfg}.ko
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
%if %{with smp} && %{with dist_kernel}
install unicorn_pci/unicorn_pci_$mods-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/misc/unicorn_pci_$mods.ko
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
