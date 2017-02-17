#!/bin/bash

docker run --rm -i -t -p 8888:8888 registry.gitlab.com/datenstrom/cs532-s17:assignment-2 \
    ./main.py -l search $1
