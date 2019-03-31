#!/bin/bash

# Copyright (c) 2019 Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

# Add non root user and call script creating hello_pelion_connect application package.
#
# This script run inside the container; it adds non root user and switchs to it.
set -e

CMD="$*" # command to be executed inside container

if ! getent passwd "$USER_NAME" > /dev/null ; then

  # Add group and user.
  groupadd -g "$USER_ID" "$USER_NAME"
  useradd -u "$USER_ID" -g "$USER_ID" "$USER_NAME"
  mkdir -p "/home/$USER_NAME"

fi

echo "Container entry point: run ${CMD}"

# Create package with a non root user
sudo -i -u "$USER_NAME" /bin/bash -c "${CMD}"