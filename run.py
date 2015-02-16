#!/usr/bin/env python
'''
A script to run the InitialStateAnalysis analyzers on ntuples output from FinalStateAnalysis.

Author: Devin N. Taylor, UW-Madison
'''

import os
import sys
import glob
import argparse
import errno

from multiprocessing import Pool

from utilities.utilities import *
from analyzers.AnalyzerWZ import AnalyzerWZ

def run_analyzer(args):
    '''Run the analysis'''
    analysis, channel, location, outfile, period = args
    analyzerMap = {
        'WZ' : AnalyzerWZ,
    }
    theAnalyzer = analyzerMap[channel]
    with theAnalyzer(location,outfile,period) as analyzer:
        analyzer.analyze()

def run_ntuples(analysis, channel, period, samples):
    '''Run a given analyzer for the H++ analysis'''

    ntupleDict = {
        '7': {
            '3l': 'N/A',
            '4l': 'N/A', 
        },
        '8': {
            '3l': '2014-12-04-8TeV',
            '4l': 'N/A', 
        },
        '13': {
            'WZ': '2015-02-10-13TeV',
            '3l': '2015-02-11-13TeV-3l',
            '4l': '2015-02-11-13TeV-4l',
        },
    }
    root_dir = '/hdfs/store/user/dntaylor/data/%s' % ntupleDict[period][analysis]
    ntup_dir = './ntuples%s_%stev_%s' % (analysis, period, channel)
    python_mkdir(ntup_dir)

    p = Pool(8)

    sample_names = [os.path.basename(fname)
                    for string in samples
                    for fname in glob.glob("%s/%s" % (root_dir, string))]

    p.map(run_analyzer, [(analysis, channel, "%s/%s" % (root_dir, name), "%s/%s.root" % (ntup_dir, name), period) for name in sample_names])

    return 0

def parse_command_line(argv):
    parser = argparse.ArgumentParser(description="Run the desired analyzer on "
                                                 "FSA n-tuples")

    parser.add_argument('analysis', type=str, choices=['WZ'], help='Analysis to run')
    parser.add_argument('channel', type=str, choices=['WZ'], help='Channel to run for given analysis')
    parser.add_argument('period', type=str, choices=['7','8','13'], help='7, 8, 13')
    parser.add_argument('sample_names', nargs='+',
                        help='Sample names w/ UNIX wildcards')
    args = parser.parse_args(argv)

    return args

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    if args.period == '7':
        print "7 TeV not implemented"
    else:
        print "Running %s:%s %s TeV analyzer" %(args.analysis, args.channel, args.period)
        run_ntuples(args.analysis, args.channel, args.period, args.sample_names)

    return 0


if __name__ == "__main__":
    status = main()
    sys.exit(status)
