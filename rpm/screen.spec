# 
# Do NOT Edit the Auto-generated Part!
# Generated by: spectacle version 0.26
# 

Name:       screen

# >> macros
# << macros

Summary:    A screen manager that supports multiple logins on one terminal
Version:    4.0.3
Release:    12
Group:      Applications/System
License:    GPLv2+
URL:        http://www.gnu.org/software/screen
Source0:    ftp://ftp.uni-erlangen.de/pub/utilities/screen/screen-%{version}.tar.gz
Source1:    screen.pam
Source2:    screen.conf
Source100:  screen.yaml
Patch0:     screen-4.0.3-libs.patch
Patch1:     screen-4.0.2-screenrc.patch
Patch2:     screen-4.0.3-stropts.patch
Patch3:     screen-4.0.1-args.patch
Patch4:     screen-4.0.2-maxstr.patch
Patch5:     screen-4.0.3-ipv6.patch
Patch6:     screen-CVE-2009-1214,1215.patch
Requires(pre): /usr/sbin/groupadd
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


%package docs
Summary:    Documentation files for %{name}
Group:      Application/System
Requires:   %{name} = %{version}-%{release}
Requires(post): /sbin/install-info
Requires(postun): /sbin/install-info

%description docs
%{summary}.


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
# >> setup
# << setup

%build
# >> build pre
# << build pre



# >> build post
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
# << build post

%install
rm -rf %{buildroot}
# >> install pre
# << install pre
mkdir -p %{buildroot}%{_sysconfdir}/tmpfiles.d/
cp -a %{SOURCE2} %{buildroot}%{_sysconfdir}/tmpfiles.d/


# >> install post
make install DESTDIR=$RPM_BUILD_ROOT
mv -f $RPM_BUILD_ROOT%{_bindir}/screen{-%{version},}

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
# << install post

%pre
# >> pre
/usr/sbin/groupadd -g 84 -r -f screen
:
# << pre

%post docs
%install_info --info-dir=%_infodir %{_infodir}/screen.info.gz

%postun docs
if [ $1 = 0 ] ;then
%install_info_delete --info-dir=%{_infodir} %{_infodir}/screen.info.gz
fi

%files
%defattr(-,root,root,-)
# >> files
%doc COPYING
%attr(2755,root,screen) %{_bindir}/screen
%{_datadir}/screen
%attr(775,root,screen) %{_localstatedir}/run/screen
%config(noreplace) %{_sysconfdir}/screenrc
%config(noreplace) %{_sysconfdir}/pam.d/screen
%{_sysconfdir}/tmpfiles.d/screen.conf
# << files

%files docs
%defattr(-,root,root,-)
# >> files docs
%doc NEWS README doc/FAQ doc/README.DOTSCREEN COPYING
%doc %{_mandir}/man1/screen.*
%doc %{_infodir}/screen.info.gz
# << files docs