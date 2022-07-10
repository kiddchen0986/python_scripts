#!/bin/sh
#
# Copyright (c) 2021 Fingerprint Cards AB <tech@fingerprints.com>
#
# All rights are reserved.
# Proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Any use is subject to an appropriate license granted by Fingerprint Cards AB.
#

# Exit immediately if a command returns a non-zero status.
# See https://www.gnu.org/software/bash/manual/bash.html#The-Set-Builtin

set -e

source_dir=".."
pushd ${source_dir}
pip install virtualenv
virtualenv env
source ./env/scripts/activate
pip install -r requirements.txt
cp ./scripts/hook-pygal.py ./env/Lib/site-packages/PyInstaller/hooks -v
rm ./dist -irf
pyinstaller -D -w -i FPC.ico MTT_Log_Parser.py
cp ./Doc/MTT_Log_Parser_User_Guide.pdf ./dist/MTT_Log_Parser -v
deactivate
popd
