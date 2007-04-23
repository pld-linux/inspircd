Name:		inspircd
Summary:	Modular IRC daemon
Version:	1.1.6
Release:	1
License:	GPL
Group:		Networking/Daemons
URL:		http://www.inspircd.org/
BuildRequires:	gcc-c++
BuildRequires:	gnutls-devel
BuildRequires:	mysql-devel
BuildRequires:	pcre-devel
BuildRequires:	pkgconfig
BuildRequires:	postgresql-devel
BuildRequires:	sqlite3-devel >= 3.3
BuildRequires:	zlib-devel
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
Source0:	http://www.inspircd.org/downloads/InspIRCd-%{version}.tar.bz2
# Source0-md5:	b94e33527a10d15edc5a5b9291428cc0
Source1:	%{name}.init
Source2:	%{name}.conf
Patch1:		%{name}-1.1b8_default_config.patch
Patch2:		%{name}-1.1.2-m_no_op_on_channel_create.patch

%description
InspIRCd is a modular C++ IRC Daemon for Linux, BSD and Windows
systems created to provide a stable, modern, lightweight ircd (irc
server) from scratch and provide a vast number of features in a
modularised form using an advanced module API. By keeping the
functionality of the main core to a minimum we hope to increase the
stability and speed of our project and make it customisable to the
needs of many users. InspIRCd is designed primarily to be a custom irc
server for the chatspike irc network (irc.chatspike.net) but we are
releasing it into the public domain under GPL so that you may benefit
yourself from our work. The project is written from scratch, avoiding
the inherent instability under large loads which can be seen in many
other irc server distributions which have the same featureset.

%prep
%setup -q -n %{name}
%patch1
%patch2

find -type f -name \*.orig -print0 | xargs -r0 rm -v
cd src/modules/
for i in $(ls extra/*sql* extra/*pcre* extra/m_ssl_oper_cert.cpp extra/m_sslinfo.cpp | grep -v sqlite3 | grep -v mysql) ; do
	ln -s -v $i .
done
ln -s -v extra/m_sqlite3.cpp .
ln -s -v extra/m_mysql.cpp .
ln -s -v extra/m_ziplink.cpp .
cd ../../

%build
%configure \
	--enable-ipv6 \
	--enable-remote-ipv6 \
	--enable-epoll \
	--enable-gnutls \
	--prefix=%{_prefix}/lib/%{name}/ \
	--config-dir=%{_sysconfdir}/%{name} \
	--library-dir=%{_libdir}/%{name}/ \
	--module-dir=%{_libdir}/%{name}/modules \
	--binary-dir=%{_sbindir}
%configure --modupdate
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/var/lib/%{name},/var/run/%{name},/var/log/%{name},%{_sysconfdir}/rc.d/init.d}
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT INSTMODE="0755"
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/%{name}

for file in $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/*.example; do
	mv $file `echo $file | sed -e 's/.example//'`
done

install %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/

%pre
%groupadd -g 216 inspircd
%groupadd -g 75 ircd
%useradd -u 216 -d /var/lib/inspircd -c "InspIRCd User" -g inspircd inspircd
%addusertogroup inspircd ircd

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}

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

%posttrans
%service %{name} restart "InspIRCd IRC Daemon"
exit 0

%files
%defattr(644,root,root,755)
%doc docs/* extras/* conf/*
%attr(755,root,root) %{_sbindir}/inspircd
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %attr(750,root,inspircd) %{_sysconfdir}/%{name}/
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

%dir %{_libdir}/%{name}/
%attr(755,root,root) %{_libdir}/%{name}/cmd_*.so
%attr(755,root,root) %{_libdir}/%{name}/libIRCD*.so
%dir %{_libdir}/%{name}/modules/
%attr(755,root,root) %{_libdir}/%{name}/modules/m_alias.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_antibear.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_antibottler.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_banexception.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_blockamsg.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_blockcaps.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_blockcolor.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_botmode.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_cban.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_censor.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_cgiirc.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_chanfilter.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_chanprotect.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_check.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_chghost.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_chgident.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_cloaking.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_conn_lusers.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_conn_join.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_conn_umodes.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_conn_waitpong.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_connflood.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_denychans.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_devoice.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_filter.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_foobar.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_globalload.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_globops.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_helpop.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_hostchange.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_httpd.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_httpd_stats.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_ident.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_inviteexception.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_joinflood.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_kicknorejoin.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_knock.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_messageflood.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_namesx.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_nicklock.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_no_op_on_channel_create.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_noctcp.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_noinvite.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_nokicks.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_nonicks.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_nonotice.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_operchans.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_operjoin.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_operlevels.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_operlog.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_opermodes.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_opermotd.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_override.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_randquote.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_redirect.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_remove.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_restrictchans.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_restrictmsg.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_safelist.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_sajoin.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_samode.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_sanick.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_sapart.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_saquit.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_securelist.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_services.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_services_account.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_sethost.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_setident.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_setidle.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_setname.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_showwhois.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_silence.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_spanningtree.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_spy.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_ssl_dummy.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_ssl_gnutls.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_sslmodes.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_stripcolor.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_svshold.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_swhois.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_testcommand.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_timedbans.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_tline.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_uninvite.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_userip.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_vhost.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_watch.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_alltime.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_dccallow.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_hidechans.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_hideoper.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_restrictbanned.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_sqlauth.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_sqllog.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_sqloper.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_sqlutils.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_filter_pcre.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_ssl_oper_cert.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_sslinfo.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_deaf.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_dnsbl.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_lockserv.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_oper_hash.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_md5.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_sha256.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_silence_ext.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_banredirect.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_http_client.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_ziplink.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_pgsql.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_jumpserver.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_seenicks.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_mysql.so
%attr(755,root,root) %{_libdir}/%{name}/modules/m_sqlite3.so
