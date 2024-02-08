#!/usr/bin/env bash

cd /Phoenix
echo "Ran Script!" > out.txt
source ./setup.sh
./phx run start-embedded-reader
