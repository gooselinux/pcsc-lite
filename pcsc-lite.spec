Name:           pcsc-lite
Version:        1.5.2
Release:        6%{?dist}
Summary:        PC/SC Lite smart card framework and applications
%define upstream_build 2795

Group:          System Environment/Daemons
License:        BSD
URL:            http://pcsclite.alioth.debian.org/
Source0:        http://alioth.debian.org/download.php/%{upstream_build}/%{name}-%{version}.tar.bz2
Patch0:         %{name}-1.4-docinst.patch
Patch1:         %{name}-1.4.100-rpath64.patch
Patch2:         %{name}-close_on_exec.patch
Patch3:         %{name}-1.5-permissions.patch
Patch4:         %{name}-1.5-unlock.patch
Patch5:         %{name}-1.5.2-overflow.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  libusb-devel >= 0.1.7
BuildRequires:  hal-devel 
BuildRequires:  doxygen
Requires(post): initscripts
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
Requires:       pcsc-ifd-handler

%description
The purpose of PC/SC Lite is to provide a Windows(R) SCard interface
in a very small form factor for communicating to smartcards and
readers.  PC/SC Lite uses the same winscard API as used under
Windows(R).  This package includes the PC/SC Lite daemon, a resource
manager that coordinates communications with smart card readers and
smart cards that are connected to the system, as well as other command
line tools.

%package        libs
Summary:        PC/SC Lite libraries
Group:          System Environment/Libraries
Provides:       libpcsc-lite = %{version}-%{release}

%description    libs
PC/SC Lite libraries.

%package        devel
Summary:        PC/SC Lite development files
Group:          Development/Libraries
Requires:       %{name}-libs = %{version}-%{release}
Requires:       pkgconfig
Provides:       libpcsc-lite-devel = %{version}-%{release}

%description    devel
PC/SC Lite development files.

%package        doc
Summary:        PC/SC Lite developer documentation
Group:          Documentation

%description    doc
%{summary}.


%prep
%setup -q
%patch0 -p0 -b .docinst
%patch1 -p1 -b .rpath64
%patch2 -p1 -b .close_on_exec
%patch3 -p0 -b .permissions
%patch4 -p0 -b .unlock
%patch5 -p0 -b .overflow

%build
%configure \
  --disable-dependency-tracking \
  --disable-static \
  --enable-runpid=%{_localstatedir}/run/pcscd.pid \
  --enable-confdir=%{_sysconfdir} \
  --enable-ipcdir=%{_localstatedir}/run \
  --enable-usbdropdir=%{_libdir}/pcsc/drivers
make %{?_smp_mflags}
doxygen doc/doxygen.conf ; rm -f doc/api/*.{map,md5}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

install -dm 755 $RPM_BUILD_ROOT%{_libdir}/pcsc/drivers

install -Dpm 755 etc/pcscd.init $RPM_BUILD_ROOT%{_initrddir}/pcscd

cat <<EOF > $RPM_BUILD_ROOT%{_sysconfdir}/reader.conf.d/README
All *.conf files in this directory are merged into %{_sysconfdir}/reader.conf
by %{_sbindir}/update-reader.conf.
EOF

rm $RPM_BUILD_ROOT{%{_sysconfdir}/reader.conf.d/reader.conf,%{_libdir}/lib*.la}
touch $RPM_BUILD_ROOT%{_sysconfdir}/reader.conf

# formaticc doesn't exist any more, don't include the man page
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/formaticc.1*


%clean
rm -rf $RPM_BUILD_ROOT


%post
/sbin/chkconfig --add pcscd

%preun
if [ $1 = 0 ] ; then
  /sbin/service pcscd stop >/dev/null 2>&1 || :
  /sbin/chkconfig --del pcscd
fi

%postun
if [ "$1" -ge "1" ]; then
  /sbin/service pcscd condrestart >/dev/null 2>&1 || :
fi

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog* COPYING DRIVERS HELP README SECURITY TODO
%dir %{_sysconfdir}/reader.conf.d/
%doc %{_sysconfdir}/reader.conf.d/README
%ghost %config(noreplace) %{_sysconfdir}/reader.conf
%{_initrddir}/pcscd
%{_sbindir}/pcscd
%{_sbindir}/update-reader.conf
%{_libdir}/pcsc/
%{_mandir}/man5/reader.conf.5*
%{_mandir}/man8/pcscd.8*
%{_mandir}/man8/update-reader.conf.8*

%files libs
%defattr(-,root,root,-)
%{_libdir}/libpcsclite.so.*

%files devel
%defattr(-,root,root,-)
%{_includedir}/PCSC/
%{_libdir}/libpcsclite.so
%{_libdir}/pkgconfig/libpcsclite.pc

%files doc
%defattr(-,root,root,-)
%doc doc/api/ doc/example/pcsc_demo.c


%changelog
* Mon Jul 12 2010  Bob Relyea <rrelyea@redhat.com> - 1.5.2-6
- Fix typo in patch

* Wed Jun 16 2010 Bob Relyea <rrelyea@redhat.com> - 1.5.2-5
- patch overflow issue

* Fri Apr 23 2010 Bob Relyea <rrelyea@redhat.com> - 1.5.2-4
- fix hang in Scard_Cancel

* Mon Nov 30 2009 Dennis Gregorovic <dgregor@redhat.com> - 1.5.2-3.1
- Rebuilt for RHEL 6

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.5.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jun 17 2009 Bob Relyea <rrelyea@redhat.com> - 1.5.2-2
- Pick up security fixes from upstream

* Fri Feb 27 2009 Bob Relyea <rrelyea@redhat.com> - 1.5.2-1
- Pick up 1.5.2
- Add FD_CLOEXEC flag
- make reader.conf a noreplace config file

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.102-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 11 2009 Karsten Hopp <karsten@redhat.com> 1.4.102-4
- remove excludearch s390, s390x (#467788)
  even though s390 does not have libusb or smartCards, the libusb
  packages are required to build other packages.

* Thu Aug 18 2008 Bob Relyea <rrelyea@redhat.com> - 1.4.102-3
- bump tag becaue the build system can't deal with mistakes.

* Thu Aug 18 2008 Bob Relyea <rrelyea@redhat.com> - 1.4.102-2
- mock build changes

* Wed Aug 17 2008 Bob Relyea <rrelyea@redhat.com> - 1.4.102-1
- Pick up 1.4.102

* Wed May 6 2008 Bob Relyea <rrelyea@redhat.com> - 1.4.101-1
- Pick up 1.4.101

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1.4.4-3
- Autorebuild for GCC 4.3

* Wed Jan 16 2008 Bob Relyea <rrelyea@redhat.com> - 1.4.4-2
- Silence libpcsc-lite even when the daemon isn't running.
- fix typo in init file which prevents the config file from being read.

* Tue Nov 22 2007 Bob Relyea <rrelyea@redhat.com> - 1.4.4-1
- Pick up 1.4.4

* Tue Feb 06 2007 Bob Relyea <rrelyea@redhat.com> - 1.3.3-1
- Pick up 1.3.3

* Thu Nov 02 2006 Bob Relyea <rrelyea@redhat.com> - 1.3.2-1
- Pick up 1.3.2

* Thu Sep 14 2006  Bob Relyea <rrelyea@redhat.com> - 1.3.1-7
- Incorporate patch from Ludovic to stop the pcsc daemon from
  unnecessarily waking up.

* Mon Jul 31 2006 Ray Strode <rstrode@redhat.com> - 1.3.1-6
- follow packaging guidelines for setting up init service
  (bug 200778)

* Sun Jul 24 2006 Bob Relyea <rrelyea@redhat.com> - 1.3.1-5
- start pcscd when pcsc-lite is installed

* Sun Jul 16 2006 Florian La Roche <laroche@redhat.com> - 1.3.1-4
- fix excludearch line

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 1.3.1-3.1
- rebuild

* Mon Jul 10 2006 Bob Relyea <rrelyea@redhat.com> - 1.3.1-3
- remove s390 from the build

* Mon Jun 5 2006 Bob Relyea <rrelyea@redhat.com> - 1.3.1-2
- Move to Fedora Core. 
- Remove dependency on graphviz. 
- Removed %%{_dist}

* Sat Apr 22 2006 Ville Skyttä <ville.skytta at iki.fi> - 1.3.1-1
- 1.3.1.

* Sun Mar  5 2006 Ville Skyttä <ville.skytta at iki.fi> - 1.3.0-1
- 1.3.0, init script and reader.conf updater included upstream.
- Split developer docs into a -doc subpackage, include API docs.
- libmusclecard no longer included, split into separate package upstream.

* Mon Feb 13 2006 Ville Skyttä <ville.skytta at iki.fi> - 1.2.0-14
- Avoid standard rpaths on multilib archs.
- Fine tune dependencies.

* Fri Nov 11 2005 Ville Skyttä <ville.skytta at iki.fi> - 1.2.0-13
- Don't ship static libraries.
- Don't mark the init script as a config file.
- Use rm instead of %%exclude.
- Specfile cleanups.

* Thu May 19 2005 Ville Skyttä <ville.skytta at iki.fi> - 1.2.0-12
- Rebuild.

* Fri Apr  7 2005 Michael Schwendt <mschwendt[AT]users.sf.net> - 1.2.0-11
- rebuilt

* Tue Aug 17 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-10
- Disable dependency tracking to speed up the build.
- Drop reader.conf patch, it's not needed any more.
- Rename update-reader-conf to update-reader.conf for consistency with Debian,
  and improve it a bit.

* Sat Jul 31 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-0.fdr.9
- Add update-reader-conf, thanks to Fritz Elfert.

* Thu Jul  1 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-0.fdr.8
- Own the %%{_libdir}/pcsc hierarchy.

* Thu May 13 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-0.fdr.7
- Make main package require pcsc-ifd-handler (idea from Debian).

* Wed May 12 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-0.fdr.6
- Improve package summary.
- Improvements based on suggestions from Ludovic Rousseau:
  - Don't install pcsc_demo but do include its source in -devel.
  - Sync reader.conf with current upstream CVS HEAD (better docs, less
    intrusive in USB-only setups where it's not needed).

* Fri Apr 16 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-0.fdr.5
- Move PDF API docs to -devel.
- Improve main package and init script descriptions.

* Thu Jan 29 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-0.fdr.4
- Init script fine tuning.

* Fri Jan  9 2004 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-0.fdr.3
- BuildRequires libusb-devel 0.1.6 or newer.

* Thu Oct 30 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-0.fdr.2
- s/pkgconfi/pkgconfig/ in -devel requirements.

* Tue Oct 28 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-0.fdr.1
- Update to 1.2.0.
- Add libpcsc-lite and libmusclecard provides to -libs and -devel.

* Thu Oct 16 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-0.fdr.0.2.rc3
- Update to 1.2.0-rc3.
- Trivial init script improvements.
- Enable %%{_smp_mflags}.
- Don't bother trying to enable SCF.

* Sun Sep 14 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-0.fdr.0.2.rc2
- Specfile cleanups.

* Fri Sep  5 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-0.fdr.0.1.rc2
- Update to 1.2.0-rc2.

* Wed Aug 27 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.2.0-0.fdr.0.1.rc1
- Update to 1.2.0-rc1.

* Sun Jun  1 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.1.2-0.fdr.0.1.beta5
- Update to 1.1.2beta5.

* Sat May 24 2003 Ville Skyttä <ville.skytta at iki.fi> - 0:1.1.2-0.fdr.0.1.beta4
- First build, based on PLD's 1.1.1-2.
