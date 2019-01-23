Name:       screen
Summary:    A screen manager that supports multiple logins on one terminal
Version:    4.0.3
Release:    12
Group:      Applications/System
License:    GPLv2+
URL:        http://www.gnu.org/software/screen
Source0:    %{name}-%{version}.tar.gz
Source1:    screen.pam
Source2:    screen.conf
Patch0:     screen-4.0.3-libs.patch
Patch1:     screen-4.0.2-screenrc.patch
Patch2:     screen-4.0.3-stropts.patch
Patch3:     screen-4.0.1-args.patch
Patch4:     screen-4.0.2-maxstr.patch
Patch5:     screen-4.0.3-ipv6.patch
Patch6:     screen-CVE-2009-1214,1215.patch
Requires(pre):  /usr/sbin/groupadd
BuildRequires:  pkgconfig(ncurses)
BuildRequires:  pam-devel
BuildRequires:  libutempter-devel
BuildRequires:  autoconf
BuildRequires:  texinfo

%description
The screen utility allows you to have multiple logins on just one
terminal. Screen is useful for users who telnet into a machine or are
connected via a dumb terminal, but want to use more than just one
login.

Install the screen package if you need a screen manager that can
support multiple logins on one terminal.

%package doc
Summary:    Documentation for %{name}
Group:      Documentation
Requires:   %{name} = %{version}-%{release}
Requires(post):   /sbin/install-info
Requires(postun): /sbin/install-info
Obsoletes:  %{name}-docs

%description doc
Man and info pages for %{name}.

%prep
%setup -q -n %{name}-%{version}/%{name}/src

# screen-4.0.3-libs.patch
%patch0 -p1
# screen-4.0.2-screenrc.patch
%patch1 -p1
# screen-4.0.3-stropts.patch
%patch2 -p1
# screen-4.0.1-args.patch
%patch3 -p1
# screen-4.0.2-maxstr.patch
%patch4 -p1
# screen-4.0.3-ipv6.patch
%patch5 -p1
# screen-CVE-2009-1214,1215.patch
%patch6 -p1

%build
autoconf

%configure \
--enable-pam \
--enable-colors256 \
--enable-rxvt_osc \
--enable-locale \
--enable-telnet \
--with-pty-mode=0620 \
--with-pty-group=$(getent group tty | cut -d : -f 3) \
--with-sys-screenrc="%{_sysconfdir}/screenrc" \
--with-socket-dir="%{_localstatedir}/run/screen"

# We would like to have braille support.
sed -i -e 's/.*#.*undef.*HAVE_BRAILLE.*/#define HAVE_BRAILLE 1/;' config.h

sed -i -e 's/\(\/usr\)\?\/local\/etc/\/etc/g;' doc/screen.{1,texinfo}
rm doc/screen.info*

make %{?_smp_mflags}

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_sysconfdir}/tmpfiles.d/
cp -a %{SOURCE2} %{buildroot}%{_sysconfdir}/tmpfiles.d/

make install DESTDIR=$RPM_BUILD_ROOT
mv -f $RPM_BUILD_ROOT%{_bindir}/screen{-*,}

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}
install -m 0644 etc/etcscreenrc $RPM_BUILD_ROOT%{_sysconfdir}/screenrc
cat etc/screenrc >> $RPM_BUILD_ROOT%{_sysconfdir}/screenrc

# Better not forget to copy the pam file around
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pam.d
install -p -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/screen

# Create the socket dir
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/run/screen

# Remove files from the buildroot which we don't want packaged
rm -f $RPM_BUILD_ROOT%{_infodir}/dir

mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version}
install -m0644 -t $RPM_BUILD_ROOT%{_docdir}/%{name}-%{version} \
        NEWS README doc/FAQ doc/README.DOTSCREEN

%pre
/usr/sbin/groupadd -g 84 -r -f screen
:

%post doc
%install_info --info-dir=%_infodir %{_infodir}/screen.info.gz

%postun doc
if [ $1 = 0 ] ;then
%install_info_delete --info-dir=%{_infodir} %{_infodir}/screen.info.gz
fi

%files
%defattr(-,root,root,-)
%license COPYING
%attr(2755,root,screen) %{_bindir}/screen
%{_datadir}/screen
%attr(775,root,screen) %{_localstatedir}/run/screen
%config(noreplace) %{_sysconfdir}/screenrc
%config(noreplace) %{_sysconfdir}/pam.d/screen
%{_sysconfdir}/tmpfiles.d/screen.conf

%files doc
%defattr(-,root,root,-)
%{_infodir}/%{name}.info.gz
%{_mandir}/man1/%{name}.*
%{_docdir}/%{name}-%{version}
