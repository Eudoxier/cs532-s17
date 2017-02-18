#!/bin/bash
#
# Create the SHA1 hash for the links in an input file,
# ouptput a csv to OUTPUT_FILE.

OUTPUT_FILE="../data/link_hash.csv"

usage() {
    echo >&2
    echo >&2 "Usage: $0 input_path output_path"
}

warning() {
    echo >&2    "[*] Warning: this script will overwrite data at $OUT_FILE waiting 10 seconds before starting."
    echo >&2

    sleep 10
}

fetch() {
    echo "link, hash" > $OUT_FILE
    while read uri; do
        local hash=$(echo -n "$uri" | sha1sum | cut -d ' ' -f 1)
        echo "$uri, $hash" | tee -a  $OUT_FILE
    done < "$IN_FILE"
}

stats() {
    echo >&2 "[*] Done"
}

if [ $# != 2 ] ; then 
    usage
    exit 1
else
    IN_FILE=$1
    OUT_FILE=$2
    echo >&2
    echo >&2 "[*] Generating [link, hash] csv file from input at $IN_FILE"
fi

warning
fetch
stats

exit 0
