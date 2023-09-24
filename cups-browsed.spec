#define _disable_lto 1
%define beta %{nil}
%define scmrev %{nil}

Name:		cups-browsed
Version:	2.0.0
%if "%{beta}" == ""
%if "%{scmrev}" == ""
Release:	1
Source0:	https://github.com/OpenPrinting/cups-browsed/releases/download/%{version}/cups-browsed-%{version}.tar.xz
%else
Release:	0.%{scmrev}.1
Source0:	%{name}-%{scmrev}.tar.xz
%endif
%else
%if "%{scmrev}" == ""
Release:	0.%{beta}.1
Source0:	%{name}-%{version}%{beta}.tar.bz2
%else
Release:	0.%{scmrev}.1
Source0:	%{name}-%{scmrev}.tar.xz
%endif
%endif
Summary:	Helper that browses the network for remote CUPS and IPP printers
URL:		http://www.linuxfoundation.org/collaborate/workgroups/openprinting/cups-browsed
Group:		System/Printing
BuildRequires:	pkgconfig(com_err)
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(libqpdf)
BuildRequires:	pkgconfig(poppler)
BuildRequires:	pkgconfig(poppler-cpp)
BuildRequires:	pkgconfig(lcms2)
BuildRequires:	pkgconfig(freetype2)
BuildRequires:	pkgconfig(fontconfig)
BuildRequires:	pkgconfig(ijs)
BuildRequires:	pkgconfig(krb5)
BuildRequires:	pkgconfig(libtiff-4)
BuildRequires:	pkgconfig(avahi-client)
BuildRequires:	pkgconfig(avahi-glib)
BuildRequires:	pkgconfig(libexif)
BuildRequires:	pkgconfig(libcupsfilters) >= 2.0.0
BuildRequires:	pkgconfig(libppd)
BuildRequires:	font(dejavusans)
BuildRequires:	ghostscript-devel >= 9.14
BuildRequires:	cups-devel
BuildRequires:	gettext-devel
BuildRequires:	python-cups
# pdftops needs to be found
BuildRequires:	poppler
BuildRequires:	mupdf
Requires:	font(dejavusans)
# For a breakdown of the licensing, see COPYING file
# GPLv2:   browsed: commandto*, imagetoraster, pdftops, rasterto*,
#                   imagetopdf, pstopdf, texttopdf
#         backends: parallel, serial
# GPLv2+:  browsed: gstopxl, textonly, texttops, imagetops
# GPLv3:   browsed: bannertopdf
# GPLv3+:  browsed: urftopdf
# MIT:     browsed: gstoraster, pdftoijs, pdftoopvp, pdftopdf, pdftoraster
License: GPLv2 and GPLv2+ and GPLv3 and GPLv3+ and MIT
# For pdftops
Requires:	poppler
Requires:	bc
Conflicts:	cups < 1.7-0.rc1.2
Requires(post,postun):	cups

%description
CUPS is a standards-based, open-source printing system.
CUPS uses the Internet Printing Protocol ("IPP") and provides System V and
Berkeley command-line interfaces, a web interface, and a C API to manage
printers and print jobs.

This package contains cups-browsed, a helper daemon to browse the network for
remote CUPS queues and IPP network printers and automatically create local
queues pointing to them.

cups-browsed has the following functionality:

* Auto-discover print services advertised via DNS-SD (network printers,
IPP-over-USB printers, Printer Applications, remote CUPS queues) and create
local queues pointing to them. CUPS usually automatically creates temporary
queues for such print services, but several print dialogs use old CUPS APIs
and therefore require permanent local queues to see such printers.

* Auto-discover shared printers on remote CUPS servers running CUPS 1.5.x or
older via legacy CUPS browsing. This is intended for settings with print
servers running long-term-support enterprise distributions.

* Broadcast shared local printers using legacy CUPS browsing (of CUPS 1.5.x)
for settings with printing clients running long-term-support enterprise
distributions.

* Creating printer clusters where jobs are printed to one single queue and get
automatically passed on to a suitable member printer.

* Manual (via config file) and automatic (equally-named remote CUPS printers
form local cluster, as in legacy CUPS 1.5.x and older) creation of cluster
queues

* If member printers are different models/types, the local queue gets the
totality of all their features, options, and choices. Job goes to printer
which actually supports the user-selected job settings. So in a cluster of
photo printer, fast laser, and large format selecting photo paper for example
makes the job go to the photo printer, duplex makes it go to the laser, A2
paper to the large format ... So user has one queue for all printers, they
select features, not printers for their jobs ...

* Automatic selection of destination printer depending on job option settings

* Load balancing on equally suitable printers

* implicitclass backend holds the job, waits for instructions about the
destination printer of cups-browsed, converts the (PDF) job to one of the
destination's (driverless) input formats, and passes on the job.

* Highly configurable: Which printers are considered? For which type of
printers queues are created? Cluster types and member printers? which names
auto-created queues should get? DNS-SD and/or legacy browsing? ...

* Multi-threading allows several tasks to be done in parallel and assures
responsiveness of the daemon when there is a large amount of printers
available in the network.

%prep
%if "%{scmrev}" == ""
%autosetup -p1 -n %{name}-%{version}%{beta}
%else
%autosetup -p1 -n %{name}
%endif
./autogen.sh

%configure \
	--disable-static \
	--with-pdftops=pdftops \
	--without-rcdir \
	--enable-avahi \
	--with-browseremoteprotocols=DNSSD,CUPS \
	--enable-auto-setup-driverless

%build
%make_build

%install
%make_install

%post
# Restart the CUPS daemon when it is running, but do not start it when it
# is not running.
/bin/systemctl try-restart --quiet cups.socket ||:
/bin/systemctl try-restart --quiet cups.path ||:
/bin/systemctl try-restart --quiet cups.service ||:

%postun
if [ $1 -eq 1 ]; then
    /bin/systemctl try-restart --quiet cups.socket ||:
    /bin/systemctl try-restart --quiet cups.path ||:
    /bin/systemctl try-restart --quiet cups.service ||:
fi

%files
%doc %{_docdir}/%{name}
%{_sysconfdir}/cups/cups-browsed.conf
%{_bindir}/cups-browsed
%{_prefix}/lib/cups/backend/implicitclass
%{_mandir}/man5/cups-browsed.conf.5*
%{_mandir}/man8/cups-browsed.8*
