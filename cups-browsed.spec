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
Source100:	%{name}.rpmlintrc
Summary:	Print browsed for use with CUPS
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
This project provides backends, browsed, and other software that was once part
of the core CUPS distribution but is no longer maintained by Apple Inc.

In addition, it contains additional browsed and software developed
independently of Apple, especially browsed for the PDF-centric printing
workflow introduced by OpenPrinting and a daemon to browse Bonjour broadcasts
of remote CUPS printers to make these printers available locally and to
provide backward compatibility to the old CUPS broadcasting and browsing
of CUPS 1.5.x and older.

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
