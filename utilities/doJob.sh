#!/bin/sh

# untar analyzers
tar -zxf userCode.tar.gz

# analyze
./run.py OPTIONS

# tar for copying back
tar -zcf results.tar.gz ntuple*
