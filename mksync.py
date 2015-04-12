#!/usr/bin/env python

from plotters.Plotter import Plotter
from plotters.plotUtils import *
import argparse
import itertools
import sys

ZMASS = 91.1876

def sync(analysis,channel,period,**kwargs):
    '''Print sync information to file.'''
    runTau = kwargs.pop('runTau',False)
    blind = kwargs.pop('blind',True)
    cut = kwargs.pop('cut','select.passTight')

    # WZ only for now
    if not (analysis == channel == 'WZ'): return

    # sync on WZ sample
    # sync on channels: eee, eem, emm, mmm
    ntuples = 'ntuples%s_%stev_%s' % (analysis,period,channel)
    saves = '%s_%s_%sTeV' % (analysis,channel,period)
    mergeDict = getMergeDict(period)
    nl = 3 if analysis == 'WZ' or analysis == 'Hpp3l' else 4
    sigMap = getSigMap(nl,0)
    channelBackground = {
        'WZ' : ['T','TT', 'TTV', 'Z', 'ZZ','WZ'],
        'Hpp3l' : ['T', 'TT', 'TTV','Z','DB'],
        'Hpp4l' : ['T', 'TT', 'Z', 'TTV','DB']
    }
    plotter = Plotter(channel,ntupleDir=ntuples,saveDir=saves,period=period,mergeDict=mergeDict)
    plotter.initializeBackgroundSamples([sigMap[period][x] for x in channelBackground[channel]])
    plotter.setIntLumi(1000)
    for chan in ['eee','eem','mme','mmm']:
        num = plotter.getNumEntries('%s&channel=="%s"' %(cut,chan), sigMap[period]['WZ'], doUnweighted=True)
        print '%s: %i' % (chan, num)

def parse_command_line(argv):
    parser = argparse.ArgumentParser(description="Plot a given channel and period")

    parser.add_argument('analysis', type=str, choices=['WZ','Hpp3l','Hpp4l'], help='Analysis to plot')
    parser.add_argument('channel', type=str, choices=['WZ','Hpp3l','Hpp4l','FakeRate'], help='Channel in analysis')
    parser.add_argument('period', type=int, choices=[7,8,13], help='Energy (TeV)')
    parser.add_argument('-rt','--runTau',action='store_true',help='Run Tau finalStates (not implemented)')
    parser.add_argument('-ub','--unblind',action='store_false',help='Unblind signal channel')
    parser.add_argument('-c','--cut',type=str,default='select.passTight',help='Cut to be applied to plots (default = "select.passTight").')
    args = parser.parse_args(argv)

    return args


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    if args.period == 7:
        print "7 TeV not implemented"

    # loose no iso
    # e: loose CBID
    # m: isLooseMuon

    # loose w/ iso
    # e: loose CBID and iso<0.2
    # m: isLooseMuon and iso<0.2

    # tight
    # e: medium CBID and iso<0.15
    # m: isTightMuon and iso<0.12

    sync(args.analysis,args.channel,args.period,runTau=args.runTau,blind=args.unblind,cut=args.cut)

    return 0


if __name__ == "__main__":
    main()
