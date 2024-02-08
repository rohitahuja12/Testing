#!/usr/bin/env bash
apt-get update
apt-get install python3
apt-get install python3-pip


phxReqFile=$PHOENIX_HOME/cli/requirements.txt
python3 -m pip install -r $phxReqFile

commonReqFile=$PHOENIX_HOME/common/requirements.txt
python3 -m pip install -r $commonReqFile
