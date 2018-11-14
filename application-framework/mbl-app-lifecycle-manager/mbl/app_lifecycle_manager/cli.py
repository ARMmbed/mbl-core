#!/usr/bin/env python3
# Copyright (c) 2018 Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Simple command line interface for mbl app lifecycle manager."""

import argparse
import logging
import sys

import mbl.app_lifecycle_manager.app_lifecycle_manager as alm


def get_argument_parser():
    """
    Return argument parser.

    :return: parser
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="App lifecycle manager",
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-r",
        "--run-container",
        metavar="CONTAINER_ID",
        help="Run container, assigning the given container ID",
    )

    group.add_argument(
        "-s",
        "--stop-container",
        metavar="CONTAINER_ID",
        help="Stop container with the given container ID",
    )

    group.add_argument(
        "-k",
        "--kill-container",
        metavar="CONTAINER_ID",
        help="Kill container with the container ID",
    )

    parser.add_argument("-a", "--application-id", help="Application ID")

    parser.add_argument(
        "-t",
        "--sigterm-timeout",
        type=int,
        help="Maximum time (seconds) to wait for application container to exit"
        " after sending a SIGTERM. Default is {}".format(
            alm.DEFAULT_SIGTERM_TIMEOUT
        ),
    )

    parser.add_argument(
        "-j",
        "--sigkill-timeout",
        type=int,
        help="Maximum time (seconds) to wait for application container to exit"
        " after sending a SIGKILL. Default is {}".format(
            alm.DEFAULT_SIGKILL_TIMEOUT
        ),
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="Increase output verbosity",
        action="store_true",
    )

    return parser


def _main():
    parser = get_argument_parser()
    args = parser.parse_args()
    info_level = logging.DEBUG if args.verbose else logging.INFO

    logging.basicConfig(
        level=info_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("mbl-app-lifecycle-manager")
    logger.debug("Command line arguments:{}".format(args))

    ret = alm.Error.ERR_INVALID_ARGS
    try:
        app_manager_lifecycle_mng = alm.AppLifecycleManager()
        if args.run_container:
            if args.application_id is None:
                logger.info("Missing application-id argument")
                ret = alm.Error.ERR_INVALID_ARGS
            else:
                ret = app_manager_lifecycle_mng.run_container(
                    args.run_container, args.application_id
                )
        elif args.stop_container:
            sigterm_timeout = (
                args.sigterm_timeout or alm.DEFAULT_SIGTERM_TIMEOUT
            )
            sigkill_timeout = (
                args.sigkill_timeout or alm.DEFAULT_SIGKILL_TIMEOUT
            )
            ret = app_manager_lifecycle_mng.stop_container(
                args.stop_container, sigterm_timeout, sigkill_timeout
            )
        elif args.kill_container:
            sigkill_timeout = (
                args.sigkill_timeout or alm.DEFAULT_SIGKILL_TIMEOUT
            )
            ret = app_manager_lifecycle_mng.kill_container(
                args.kill_container, sigkill_timeout
            )
    except OSError:
        logger.exception("Operation failed with OSError")
        return alm.Error.ERR_OPERATION_FAILED.value
    except Exception:
        logger.exception("Operation failed exception")
        return alm.Error.ERR_OPERATION_FAILED.value
    if ret == alm.Error.SUCCESS:
        logger.info("Operation successful")
    else:
        logger.error("Operation failed: {}".format(ret))
    return ret.value
