# Copyright (c) 2019 Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Package unpacking and application installation."""

import os
import subprocess
import sys
import tarfile

from .utils import log
import mbl.app_manager.manager as apm
import mbl.app_lifecycle_manager.manager as alm
import mbl.app_lifecycle_manager.container as alc


IPKS_EXCTRACTION_PATH = os.path.join(os.sep, "mnt", "cache", "opkg", "src_ipk")
APPS_INSTALLATION_PATH = os.path.join(os.sep, "home", "app")


class AppUpdateManager:
    """
    Responsible for handling application package.

    An update package is a tar archive that can contain one or multiple ipks.
    Each application found in an ipk can also be installed and run.
    """

    def __init__(self, update_pkg):
        """Create an app package handler."""
        self._ipks = []
        self._pkg_arch_members = []
        self._installed_app_names = []
        self.update_pkg = update_pkg
        self.app_mng = apm.AppManager()

    # ---------------------------- Public Methods -----------------------------

    def unpack(self):
        """Unpack the ipk(s) from the update package."""
        log.info("Unpacking '{}'".format(self.update_pkg))

        if not tarfile.is_tarfile(self.update_pkg):
            msg = "Package '{}' is not a tar file".format(self.update_pkg)
            raise IllegalPackage(msg)

        with tarfile.open(self.update_pkg) as tar_file:
            self._get_ipks_from_pkg(tar_file)
            if not self._ipks:
                msg = "No 'ipk' file found in package '{}'".format(
                    self.update_pkg
                )
                raise IllegalPackage(msg)

            try:
                tar_file.extractall(
                    path=IPKS_EXCTRACTION_PATH, members=self._pkg_arch_members
                )
            except tarfile.TarError as error:
                msg = "Unarchiving package '{}' failed, error: {}".format(
                    self.update_pkg, str(error)
                )
                raise IllegalPackage(msg)
            else:
                log.info(
                    "Update package '{}' successfully unpacked".format(
                        self.update_pkg
                    )
                )

    def install_apps(self):
        """Install application(s) from ipk(s)."""
        if self._ipks:
            for ipk in self._ipks:
                self._manage_app_installation(
                    os.path.join(IPKS_EXCTRACTION_PATH, ipk)
                )

    def start_installed_apps(self):
        """Run applications that have been successfully installed if any."""
        if self._installed_app_names:
            log.info(
                "Run installed apps: {}".format(self._installed_app_names)
            )
            for app_name in self._installed_app_names:
                app_path = os.path.join(APPS_INSTALLATION_PATH, app_name)
                log.info("Run '{}' form '{}'".format(app_name, app_path))
                alm.run_app(app_name, app_path)

    # --------------------------- Private Methods -----------------------------

    def _validate_archive_member(self, tar_info):
        """Validate the tar archive member."""
        log.debug("Check that '{}' is a valid ipk".format(tar_info.name))

        if not tar_info.name.lower().endswith(".ipk"):
            msg = (
                "IPK(s) expected to be found in package '{}'"
                " however '{}' was found".format(
                    self.update_pkg, tar_info.name
                )
            )
            raise IllegalPackage(msg)
        elif not tar_info.isfile():
            msg = "'{}' found in package '{}' isn't regular file".format(
                tar_info.name, self.update_pkg
            )
            raise IllegalPackage(msg)
        elif os.path.dirname(tar_info.name):
            msg = (
                "Directories are not expected to be found in package '{}'"
                " however '{}' was found".format(
                    self.update_pkg, tar_info.name
                )
            )
            raise IllegalPackage(msg)

        log.info("'{}' is a valid ipk".format(tar_info.name))

    def _get_ipks_from_pkg(self, tar_file):
        """Retrieve ipks contained in a package."""
        for tar_info in tar_file:
            log.info(
                "Found archive member '{}' in '{}' archive".format(
                    tar_info.name, self.update_pkg
                )
            )

            self._validate_archive_member(tar_info)
            self._ipks.append(tar_info.name)
            self._pkg_arch_members.append(tar_info)

    def _install_app(self, app_name, ipk):
        """Install an application from an ipk."""
        log.info("Installing '{}' from '{}'".format(app_name, ipk))
        app_path = os.path.join(APPS_INSTALLATION_PATH, app_name)
        self.app_mng.install_app(ipk, app_path)
        self._installed_app_names.append(app_name)

    def _manage_app_installation(self, ipk):
        """Manage the process of installing application from ipk."""
        log.info("Installing app from '{}'".format(ipk))
        log.info("Get the name of application from the ipk")

        app_name = self.app_mng.get_app_name(ipk)

        log.info("Stopping application '{}'".format(app_name))
        try:
            alm.terminate_app(app_name)
        except alc.ContainerKillError as error:
            if alc.ContainerState.DOES_NOT_EXIST.value in str(error):
                log.info(
                    "Application '{}' does not exist,"
                    " proceed with installation".format(app_name)
                )
                self._install_app(app_name, ipk)
        else:
            app_path = os.path.join(APPS_INSTALLATION_PATH, app_name)
            log.info("Removing '{}' from'{}".format(app_name, app_path))
            self.app_mng.remove_app(app_name, app_path)
            self._install_app(app_name, ipk)


class IllegalPackage(Exception):
    """An exception for package containing incorrect data."""