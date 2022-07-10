#!/bin/sh
#
# Copyright (c) 2021 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#
# Script called in the Jenkins setup after building the workspace.
#
# Run unit tests and create the release packages.
#
# Exit immediately if a command returns a non-zero status.
# See https://www.gnu.org/software/bash/manual/bash.html#The-Set-Builtin

set -e

release_dir="../dist/MTT_Log_Parser"
if [ ! -d "${release_dir}" ]; then
  echo "Error: Can't find out dir: ${release_dir}"
  echo "Please run from the scripts folder."
  exit 1
fi

if [ -z "$TAG_VERSION" ]; then
  echo "ERROR: \$TAG_VERSION must be set in Jenkins prior to running this script."
  exit 1
fi

echo "TAG_VERSION = $TAG_VERSION"
#tag_version=$(echo "$TAG_VERSION" | sed -n "s/^.*_\([0-9\.]\+\)/\1/p")

Tool_zip_file_name="MTT_Log_Parser_v${TAG_VERSION}.zip"
echo "Packaging python tool binary code"
pushd ${release_dir}
7z a "${Tool_zip_file_name}" . -tzip
mv "${Tool_zip_file_name}" ..
popd
