%{?_javapackages_macros:%_javapackages_macros}
%if 0%{?rhel} >= 6
%global debug_package %{nil}
%endif
%global install_loc         %{_datadir}/eclipse/dropins
%global rseserver_install   %{_datadir}/eclipse-rse-server
%global rseserver_java      %{_datadir}/java/eclipse-rse-server
%global rseserver_config    %{_sysconfdir}/sysconfig/rseserver
%global rse_snapshot        org.eclipse.tm

Name: eclipse-rse
Summary: Eclipse Remote System Explorer
Version: 3.5
Release: 3.0%{?dist}
License: EPL
URL: http://www.eclipse.org/dsdp/tm/

Source0: http://git.eclipse.org/c/tm/org.eclipse.tm.git/snapshot/org.eclipse.tm-R3_5GA.tar.bz2
Source4: notice.html
Source5: epl-v10.html

# Use Authen::pam to authenticate clients
Patch1: eclipse-rse-server-auth-pl.patch
# Fix classpath in daemon and server scripts to point
# to install locations
Patch2: eclipse-rse-server-scripts.patch
# Patch to remove eclipse-parent pom reference and multiple environments
Patch3: eclipse-rse-top-pom.patch
# Patch to remove dependency on org.apache.commons.net.source
Patch4: eclipse-rse-commons-net-source.patch
# Patch to allow junit4 to be used for building tests
Patch5: eclipse-rse-junit.patch
# Patch to remove tests from tm repo
Patch6: eclipse-rse-tm-repo.patch


BuildRequires:    java-devel >= 1.5.0

# All arches line up except i386 -> x86
%ifarch %{ix86}
%define eclipse_arch    x86
%else
%ifarch %{arm}
%define eclipse_arch    arm
%else
%define eclipse_arch   %{_arch}
%endif
%endif

%if 0%{?rhel} >= 6
ExclusiveArch: i686 x86_64
%else
BuildArch: noarch
%endif

BuildRequires: tycho
BuildRequires: tycho-extras
BuildRequires: maven >= 3.0.3
BuildRequires: junit

BuildRequires: eclipse-pde >= 1:3.8.0-0.21
BuildRequires: eclipse-emf >= 0:2.4.1
BuildRequires: apache-commons-net >= 0:1.4.1-5.4
Requires: eclipse-platform >= 1:3.8.0-0.21
Requires: eclipse-emf >= 0:2.4.1
Requires: apache-commons-net >= 0:2.0



%description
Remote System Explorer (RSE) is a framework and toolkit in Eclipse Workbench
that allows you to connect and work with a variety of remote systems.

%package server
Summary: Eclipse Remote System Explorer Server

Requires: perl
Requires: perl-Authen-PAM
Requires: java

%description server
The Remote System Explorer (RSE) framework server that can be used so clients can connect to this machine via RSE.

%prep
%setup -q -n org.eclipse.tm-R3_5GA

%patch3
%patch4
%patch5
%patch6

sed -i -e 's/<arch>x86<\/arch>/<arch>%{eclipse_arch}<\/arch>/g' pom.xml

pushd rse/plugins/org.eclipse.rse.services.dstore
%patch1
%patch2
popd
sed -i -e 's|3.2,3.3|3.2,3.9|g' pom.xml

%build
export MAVEN_OPTS="-XX:CompileCommand=exclude,org/eclipse/tycho/core/osgitools/EquinoxResolver,newState ${MAVEN_OPTS}"
mvn-rpmbuild -DskipTychoVersionCheck -Dmaven.test.skip=true clean install

cp %{SOURCE4} .
cp %{SOURCE5} .

%install

install -d -m 755 %{buildroot}%{_datadir}/eclipse
install -d -m 755 %{buildroot}%{install_loc}/rse/eclipse
install -d -m 755 %{buildroot}%{rseserver_install}
install -d -m 755 %{buildroot}%{rseserver_java}
install -d -m 755 %{buildroot}%{rseserver_config}

cp -R releng/org.eclipse.tm.repo/target/repository/features \
   %{buildroot}%{install_loc}/rse/eclipse \

cp -R releng/org.eclipse.tm.repo/target/repository/plugins \
   %{buildroot}%{install_loc}/rse/eclipse \

pushd %{buildroot}%{install_loc}/rse/eclipse/plugins
rm org.apache.commons.net_*.jar
ln -s %{_javadir}/commons-net.jar org.apache.commons.net.jar
popd

pushd %{buildroot}%{install_loc}/rse/eclipse/plugins
unzip -q -o -d %{buildroot}%{rseserver_java} org.eclipse.rse.services.dstore_*.jar dstore_miners.jar
unzip -q -o -d %{buildroot}%{rseserver_java} org.eclipse.dstore.core_*.jar dstore_core.jar
unzip -q -o -d %{buildroot}%{rseserver_java} org.eclipse.dstore.extra_*.jar dstore_extra_server.jar
unzip -q -o -d %{buildroot}%{rseserver_java} org.eclipse.rse.services_*.jar clientserver.jar
# Remove server-specific jar files from plug-ins
jarname=`ls org.eclipse.rse.services.dstore_*.jar`
zip -d $jarname dstore_miners.jar
jarname=`ls org.eclipse.dstore.core_*.jar`
zip -d $jarname dstore_core.jar
jarname=`ls org.eclipse.dstore.extra_*.jar`
zip -d $jarname dstore_extra_server.jar
jarname=`ls org.eclipse.rse.services_*.jar`
zip -d $jarname clientserver.jar
popd

pushd rse/plugins/org.eclipse.rse.services.dstore
pushd serverruntime/scripts/linux
cp *.pl %{buildroot}%{rseserver_install}
popd
pushd serverruntime/data
cp *.properties %{buildroot}%{rseserver_config}
cp *.dat %{buildroot}%{rseserver_install}
popd

%files
%{install_loc}/rse
%doc rse/features/org.eclipse.rse.sdk-feature/epl-v10.html
%doc rse/features/org.eclipse.rse.sdk-feature/license.html

%files server
%{rseserver_install}
%{rseserver_java}
%dir %{rseserver_config}
%config(noreplace) %{rseserver_config}/ssl.properties
%config(noreplace) %{rseserver_config}/rsecomm.properties
%doc notice.html
%doc epl-v10.html

%changelog
* Mon Aug 5 2013 Krzysztof Daniel <kdaniel@redhat.com> 3.5-3
- Fix FTBFS.

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Jul 1 2013 Alexander Kurtakov <akurtako@redhat.com> 3.5-1
- Update to Kepler final.

* Fri Jun 7 2013 Alexander Kurtakov <akurtako@redhat.com> 3.5-0.4.rc3
- Update to Kepler RC3.

* Wed Apr 10 2013 Jeff Johnston <jjohnstn@redhat.com> 3.5-0.3.m6
- Add terminal view feature to category.xml.

* Tue Apr 09 2013 Jeff Johnston <jjohnstn@redhat.com> 3.5-0.2.m6
- Build terminal view feature.

* Fri Apr 05 2013 Jeff Johnston <jjohnstn@redhat.com> 3.5-0.1.m6
- Update rse to 3.5M6 which is what was shipped for Kepler M6.
- Need to use full git tree and tycho to build.

* Thu Feb 21 2013 Alexander Kurtakov <akurtako@redhat.com> 3.4-5
- Strip version from commons-net symlink.

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul 6 2012 Alexander Kurtakov <akurtako@redhat.com> 3.4-2
- Fix the commons-net link for rawhide.

* Thu Jul 05 2012 Jeff Johnston <jjohnstn@redhat.com> - 3.4-1
- Update to RSE 3.4

* Wed May 2 2012 Alexander Kurtakov <akurtako@redhat.com> 3.3.1-2
- Use apache-commons-net instead of jakarta-commons-net.
- Drop old stuff.

* Mon Apr 02 2012 Jeff Johnston <jjohnstn@redhat.com> - 3.3.1-1
- Update to RSE 3.3.1

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.3-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Dec 28 2011 Orion Poplawski <orion@cora.nwra.com> 3.3-4
- Build org.eclipse.rse.useractions feature

* Wed Dec 14 2011 Jeff Johnston <jjohnstn@redhat.com> 3.3-3
- Create server sub-package
- Remove nested jars from plug-ins
- Remove reconciler %%post and %%postun sections
- Bump release

* Mon Nov 28 2011 Jeff Johnston <swagiaal@redhat.com> 3.3-1
- Upgrade to RSE 3.3

* Wed Oct 5 2011 Sami Wagiaalla <swagiaal@redhat.com> 3.2-4
- Use the reconciler to install/uninstall plugins during rpm
  post and postun respectively.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Jan 5 2011 Alexander Kurtakov <akurtako@redhat.com> 3.2-2
- Fix broken symlink.

* Fri Jul 9 2010 Alexander Kurtakov <akurtako@redhat.com> 3.2-1
- Update to 3.2 (Helios).

* Fri Mar 19 2010 Jeff Johnston <jjohnstn@redhat.com> 3.1.2-1
- Rebase to 3.1.2 (Galileo SR2 version).

* Thu Feb 25 2010 Jeff Johnston <jjohnstn@redhat.com> 3.1.1-3
- Resolves: #567874
- Remove oro requirement as it is not needed.

* Tue Oct 27 2009 Jeff Johnston <jjohnstn@redhat.com> 3.1.1-2
- Update plugin and feature version property files.

* Tue Oct 20 2009 Jeff Johnston <jjohnstn@redhat.com> 3.1.1-1
- Move to 3.1.1 tarball.

* Fri Aug 21 2009 Jeff Johnston <jjohnstn@redhat.com> 3.1-2
- Add BuildArch noarch.

* Mon Aug 17 2009 Jeff Johnston <jjohnstn@redhat.com> 3.1-1
- Move to 3.1 tarball.

* Wed Jul 29 2009 Jeff Johnston <jjohnstn@redhat.com> 3.0.3-4
- Resolves #514630

* Tue Jul 28 2009 Jeff Johnston <jjohnstn@redhat.com> 3.0.3-3
- Restrict arch support to those supported by prereq CDT.

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 23 2009 Jeff Johnston <jjohnstn@redhat.com> 3.0.3-1
- Initial release.
