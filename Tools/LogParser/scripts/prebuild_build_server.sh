#!/bin/sh
#
# Copyright (c) 2021 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#
# Script called in the Jenkins setup before building the workspace.
#
# Source files in the workspace are modified to contain the correct version info.
#

if [ -f update_tool_version.sh ]; then
  ./update_tool_version.sh
fi
