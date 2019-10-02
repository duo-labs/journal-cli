#!/bin/bash

if ! sha256sum --ignore-missing --status -c "$1"; then
    echo "Invalid checksum detected for Hugo... exiting"
    exit 1
fi