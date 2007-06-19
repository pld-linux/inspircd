Summary:	Modular IRC daemon
Summary(pl.UTF-8):	Modularny demon IRC
Name:		inspircd
Version:	1.1.9
Release:	1
License:	GPL v2
Group:		Networking/Daemons
Source0:	http://www.inspircd.org/downloads/InspIRCd-%{version}.tar.bz2
# Source0-md5:	9ca6edbf89ae013ef211b56eeec9fdfb
Source1:	%{name}.init
Source2:	%{name}.conf
Patch0:		%{name}-1.1b8_default_config.patch
Patch1:		%{name}-1.1.2-m_no_op_on_channel_create.patch
Patch2:		%{name}-modesoncreate.patch
URL:		http://www.inspircd.org/
BuildRequires:	libstdc++-devel
BuildRequires:	mysql-devel
BuildRequires:	openssl-devel
BuildRequires:	pcre-devel
BuildRequires:	pkgconfig
BuildRequires:	postgresql-devel
BuildRequires:	sqlite3-devel >= 3.3
BuildRequires:	zlib-devel
Provides:	group(inspircd)
Provides:	group(ircd)
Provides:	user(inspircd)
Obsoletes:	bircd
Obsoletes:	ircd
Obsoletes:	ircd-hybrid
Obsoletes:	ircd-ptlink
Obsoletes:	ircd6
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
InspIRCd is a modular C++ IRC Daemon for Linux, BSD and Windows
systems created to provide a stable, modern, lightweight ircd (IRC
server) from scratch and provide a vast number of features in a
modularised form using an advanced module API. By keeping the
functionality of the main core to a minimum we hope to increase the
stability and speed of our project and make it customisable to the
needs of many users. InspIRCd is designed primarily to be a custom IRC
server for the chatspike IRC network (irc.chatspike.net) but we are
releasing it into the public domain under GPL so that you may benefit
yourself from our work. The project is written from scratch, avoiding
the inherent instability under large loads which can be seen in many
other IRC server distributions which have the same featureset.

%description -l pl.UTF-8
InspIRCd to modularny, napisany w C++ demon IRC dla Linuksa, BSD i
Windows stworzony od zera, aby zapewnić stabilny, nowoczesny i lekki
ircd (serwer IRC) o dużych możliwościach w zmodularyzowanej postaci
przy użyciu zaawansowanego API dla modułów. Utrzymując minimalną
funkcjonalność podstawowego serwera autorzy mają nadzieję zwiększyć
stabilność i szybkość, a także umożliwić dostosowywanie do potrzeb
wielu użytkowników. InspIRCd został zaprojektowany głównie jako własny
serwer IRC dla sieci chatspike (irc.chatspike.net), ale autorzy mają
nadzieję, że po udostępnieniu go na GPL także inni będą mogli
skorzystać z ich pracy. Projekt jest pisany od początku, aby uniknąć
dziedziczenia niestabilności pod dużym obciążeniem, jaką można
zaobserwować w wielu innych serwerach IRC o podobnych możliwościach.

%prep
%setup -q -n %{name}
%patch0
%patch1
%patch2

find -type f -name '*.orig' -print0 | xargs -r0 rm -v
cd src/modules
for i in $(ls extra/*sql* extra/*pcre* extra/m_ssl_oper_cert.cpp extra/m_sslinfo.cpp | grep -v sqlite3 | grep -v mysql); do
	ln -s -v $i .
done
ln -s -v extra/m_sqlite3.cpp .
ln -s -v extra/m_mysql.cpp .
ln -s -v extra/m_ziplink.cpp .

%build
%configure \
	--enable-ipv6 \
	--enable-remote-ipv6 \
	--enable-epoll \
	--enable-openssl \
	--prefix=%{_prefix}/lib/%{name}/ \
	--config-dir=%{_sysconfdir}/%{name} \
	--library-dir=%{_libdir}/%{name}/ \
	--module-dir=%{_libdir}/%{name}/modules \
	--binary-dir=%{_sbindir}

# XXX: two configures?
%configure \
	--modupdate

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/var/lib/%{name},/var/run/%{name},/var/log/%{name},/etc/rc.d/init.d}
%{__make} install \
	INSTMODE="0755" \
	DESTDIR=$RPM_BUILD_ROOT
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

for file in $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/*.example; do
	mv $file `echo $file | sed -e 's/.example//'`
done

install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 216 inspircd
%groupadd -g 75 ircd
%useradd -u 216 -d /var/lib/inspircd -c "InspIRCd User" -g inspircd inspircd
%addusertogroup inspircd ircd

%post
/sbin/chkconfig --add %{name}
%service %{name} restart "InspIRCd IRC Daemon"

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
	%userremove inspircd
	%groupremove inspircd
	%groupremove ircd
fi

%files
%defattr(644,root,root,755)
%doc docs/* extras/* conf/*
%attr(755,root,root) %{_sbindir}/inspircd
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %attr(750,root,inspircd) %{_sysconfdir}/%{name}
%config(noreplace) %attr(640,root,inspircd) %{_sysconfdir}/%{name}/inspircd.conf
%config(noreplace) %attr(640,root,inspircd) %{_sysconfdir}/%{name}/inspircd.quotes
%config(noreplace) %attr(640,root,inspircd) %{_sysconfdir}/%{name}/inspircd.rules
%config(noreplace) %attr(640,root,inspircd) %{_sysconfdir}/%{name}/inspircd.censor
%config(noreplace) %attr(640,root,inspircd) %{_sysconfdir}/%{name}/inspircd.filter
%config(noreplace) %attr(640,root,inspircd) %{_sysconfdir}/%{name}/inspircd.helpop
%config(noreplace) %attr(640,root,inspircd) %{_sysconfdir}/%{name}/inspircd.helpop-full
%config(noreplace) %attr(640,root,inspircd) %{_sysconfdir}/%{name}/inspircd.motd
%attr(750,inspircd,inspircd) /var/lib/%{name}
%attr(750,inspircd,inspircd) /var/run/%{name}
%attr(750,inspircd,inspircd) /var/log/%{name}

%dir %{_libdir}/%{name}
%attr(755,root,root) %{_libdir}/%{name}/cmd_*.so
%attr(755,root,root) %{_libdir}/%{name}/libIRCD*.so
%dir %{_libdir}/%{name}/modules
%attr(755,root,root) %{_libdir}/%{name}/modules/m_*.so
