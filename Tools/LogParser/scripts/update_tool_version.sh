#!/bin/bash
#
# Copyright (c) 2021-2022 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#
# Writes the tag version to the AssemblyInfo source files for a list of
# MTT projects (the projects_to_update array below).
#
# This bash script is meant to run on Jenkins which have the tag version
# to build set in a variable called BUILD_NUMBER.
# The tag has the format ToolName_N.N.N.NNN.

if [ -z "$BUILD_NUMBER" ]; then
  echo "Error: \$BUILD_NUMBER must be set in Jenkins prior to running this script"
  exit 1
fi

# Define which project we want to read major and minor number from
read_out_project=".."
assembly_info_file=MTT_Log_Parser.py

# Read out version number
major_minor_build=$(cat $read_out_project/$assembly_info_file | grep "tool_ver = " | cut -d'"' -f2| cut -d'.' -f1,2,3)
echo "Read out version number from "$assembly_info_file": "$major_minor_build

result=$(echo $JOB_BASE_NAME | grep "DPL")
if [[ "$result" != "" ]]; then
 tag_version=$(echo "$NEW_TAG" | sed -n "s/^.*_\([0-9\.]\+\)/\1/p")
 echo "Tag version: ${tag_version}"
 if [ -z "${tag_version}" ]; then
   echo "Error: Can't find version in NEW_TAG:" $NEW_TAG
   exit 1
 fi
 version=$tag_version
else
 version=$major_minor_build.$BUILD_NUMBER
fi
echo "New generated version number: "$version

echo "Write version number "$version" to "$read_out_project/$assembly_info_file

sed -i -e 's/tool_ver =."[^"]*"/tool_ver = \"'$version'\"/' $read_out_project/$assembly_info_file
