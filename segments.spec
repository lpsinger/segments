%global srcname segments
%global distname python-%{srcname}

Name:           %{distname}
Version:        0
Release:        1%{?dist}
Summary:        Blah

License:        GPLv3
URL:            https://github.com/duncanmmacleod/segments/
Source0:        https://files.pythonhosted.org/packages/source/p/%{distname}/%{distname}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-rpm-macros
BuildRequires:  python-devel
BuildRequires:  python%{python3_pkgversion}-devel
BuildRequires:  python2-setuptools
BuildRequires:  python%{python3_pkgversion}-setuptools
BuildRequires:  python-six
BuildRequires:  python%{python3_pkgversion}-six
BuildRequires:  pytest
BuildRequires:  python%{python3_pkgversion}-pytest
BuildRequires:  python%{python3_pkgversion}-pytest-runner

%description
Blah

%package -n python2-%{srcname}
Summary:  %{summary}
Requires: python-six

%{?python_provide:%python_provide python2-%{srcname}}

%description -n python2-%{srcname}

%package -n python%{python3_pkgversion}-%{srcname}
Summary:        %{summary}
Requires:       python%{python3_pkgversion}-six

%{?python_provide:%python_provide python%{python3_pkgversion}-%{srcname}}

%description -n python%{python3_pkgversion}-%{srcname}
Blah

%prep
%autosetup -n %{distname}-%{version}

%build
%py2_build
%py3_build

%install
%py2_install
%py3_install

%check
cd test
PYTHONPATH="${RPM_BUILD_ROOT}%{python_sitearch}" \
%{__python} -m pytest -x
PYTHONPATH="${RPM_BUILD_ROOT}%{python3_sitearch}" \
%{__python3} -m pytest -x

%files -n python2-%{srcname}
%license LICENSE
%doc README.md
%{python2_sitelib}/*

%files -n python%{python3_pkgversion}-%{srcname}
%license LICENSE
%doc README.md
%{python3_sitelib}/*

%changelog
