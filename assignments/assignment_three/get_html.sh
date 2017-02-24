#!/bin/bash
#
# Fetch the HTML for the links in an input file,
# the file should have one link per line.

FAILURES=0

usage() {
    echo >&2

    echo >&2 "Usage: $0 file"
}

warning() {
    echo >&2    '[*] Warning: this script will overwrite data in data/raw_html waiting 10 seconds before starting.'
    echo >&2

    sleep 10
}

fetch() {
    while read uri; do
        local hash=$(echo -n "$uri" | sha1sum | cut -d ' ' -f 1)
        local hash+=".html"
        wget -O data/raw_html/"$hash" "$uri"
        if [[ "$?" != 0 ]]; then
            echo >&2 '[*] Error downloading file'
            FAILURES=$(expr FAILURES + 1)
        else
            echo >&2 '[*] Success'
        fi
    done < "$FILE"
}

stats() {
    echo >&2 "[*] Finished with $FAILURES unsuccessful downloads."
}

if [ $# != 1 ] ; then 
    usage
    exit 1
else
    FILE=$1
    echo >&2
    echo >&2 "[*] Fetching HTML for links in file $FILE"
fi

warning
fetch
stats

exit 0
