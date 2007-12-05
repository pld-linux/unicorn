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
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.22}
BuildRequires:	rpmbuild(macros) >= 1.379
BuildRequires:	gtk+-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Unicorn ADSL modem tools.

%description -l pl.UTF-8
Narzędzia do modemów ADSL Unicorn.

%package -n kernel%{_alt_kernel}-net-%{name}
Summary:	Unicorn ADSL modem drivers for Linux kernel
Summary(pl.UTF-8):	Sterowniki do modemów ADSL Unicorn dla jądra Linuksa
Release:	%{_rel}@%{_kernel_ver_str}
Provides:	%{name}
%{?with_dist_kernel:%requires_releq_kernel}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
Requires:	module-init-tools >= 3.2.2-2

%description -n kernel%{_alt_kernel}-net-%{name}
Unicorn ADSL modem drivers for Linux kernel.

%description -n kernel%{_alt_kernel}-net-%{name} -l pl.UTF-8
Sterowniki do modemów ADSL Unicorn dla jądra Linuksa.

%prep
%setup -q -n %{name}

%build
%if %{with userspace}
%{__make} applis
%endif

%if %{with kernel}
#mv include/linux/autoconf.h include/linux/autoconf-smp.h
cp config-dist config-smp
%build_kernel_modules -m unicorn_{pci_atm,pci_eth,usb_atm,usb_eth} cfgs=dist

#	mv unicorn_pci_atm{,-$cfg}.ko
#	mv unicorn_pci_eth{,-$cfg}.ko
#	mv unicorn_usb_atm{,-$cfg}.ko
#	mv unicorn_usb_eth{,-$cfg}.ko
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
%install_kernel_modules -s %{_mod_suffix} -n %{name} -m unicorn_{pci_atm,pci_eth,usb_atm,usb_eth} -d net
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel%{_alt_kernel}-net-%{name}
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-net-%{name}
%depmod %{_kernel_ver}

%if %{with userspace}
%files -f bewan_adsl_status.lang
%defattr(644,root,root,755)
%doc COPYING README scripts
%attr(755,root,root) %{_bindir}/*
%{_datadir}/bewan_adsl_status
%endif

%if %{with kernel}
%files -n kernel%{_alt_kernel}-net-%{name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/misc/*
%endif
