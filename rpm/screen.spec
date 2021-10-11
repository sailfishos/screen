Name:       screen
Summary:    A screen manager that supports multiple logins on one terminal
Version:    4.7.0
Release:    1
License:    GPLv3+
URL:        http://www.gnu.org/software/screen
Source0:    %{name}-%{version}.tar.gz
Source1:    screen.pam
Source2:    screen.conf
Patch0:     screen-4.7.0-libs.patch
Patch1:     screen-4.7.0-screenrc.patch
Patch2:     screen-4.7.0-maxstr.patch
Requires(pre):  /usr/sbin/groupadd
BuildRequires:  pkgconfig(ncurses)
BuildRequires:  pkgconfig(libcrypt)
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
Requires:   %{name} = %{version}-%{release}
Requires(post):   /sbin/install-info
Requires(postun): /sbin/install-info
Obsoletes:  %{name}-docs

%description doc
Man and info pages for %{name}.

%prep
%setup -q -n %{name}-%{version}/%{name}

# screen-4.7.0-libs.patch
%patch0 -p1
# screen-4.7.0-screenrc.patch
%patch1 -p1
# screen-4.7.0-maxstr.patch
%patch2 -p1

%build
cd src
autoreconf -vfi

%configure \
--enable-pam \
--enable-colors256 \
--enable-rxvt_osc \
--enable-use-locale \
--enable-telnet \
--with-pty-mode=0620 \
--with-pty-group=$(getent group tty | cut -d : -f 3) \
--with-sys-screenrc="%{_sysconfdir}/screenrc" \
--with-socket-dir="%{_localstatedir}/run/screen"

# We would like to have braille support.
sed -i -e 's/.*#.*undef.*HAVE_BRAILLE.*/#define HAVE_BRAILLE 1/;' config.h

sed -i -e 's/\(\/usr\)\?\/local\/etc/\/etc/g;' doc/screen.{1,texinfo}

make %{?_smp_mflags}

%install
rm -rf %{buildroot}

cd src
%make_install

mkdir -p %{buildroot}%{_sysconfdir}/tmpfiles.d/
cp -a %{SOURCE2} %{buildroot}%{_sysconfdir}/tmpfiles.d/

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
%config %{_sysconfdir}/screenrc
%config %{_sysconfdir}/pam.d/screen
%{_sysconfdir}/tmpfiles.d/screen.conf

%files doc
%defattr(-,root,root,-)
%{_infodir}/%{name}.info.gz
%{_mandir}/man1/%{name}.*
%{_docdir}/%{name}-%{version}
