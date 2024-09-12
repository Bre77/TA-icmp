#!/bin/bash
cd "${0%/*}"
OUTPUT="${1:-TA-icmp.spl}"
pip install --upgrade --no-dependencies -t lib -r lib/requirements.txt
rm -rf lib/splunklib/__pycache__
rm -rf lib/splunklib/searchcommands/__pycache__
rm -rf lib/splunklib/modularinput/__pycache__
rm -rf lib/*/__pycache__
cd ..
tar -cpzf $OUTPUT --exclude=.* --exclude=package.json --overwrite TA-icmp 