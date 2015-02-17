#!/usr/bin/env python

from plotters.Plotter import Plotter
from plotters.ShapePlotter import ShapePlotter
from plotters.CutFlowPlotter import CutFlowPlotter
from plotters.plotUtils import *
import argparse
import itertools
import sys

ZMASS = 91.1876

def plotKinematicsMethod(plotMethod,variables,savename,cuts,**kwargs):
    savedir = kwargs.pop('savedir','')
    if savedir: savedir += '/'
    if type(variables) is not list: variables = [variables]
    for var, c in zip(variables, cuts):
        plotMethod(var+'.Pt',[50,0,250],savedir+var+savename+'Pt',cut=c,yaxis='Events/5.0 GeV/c^{2}',xaxis='p_{T} (GeV/c)',legendpos=43,**kwargs)
        plotMethod(var+'.Eta',[30,-3.0,3.0],savedir+var+savename+'Eta',cut=c,yaxis='Events',xaxis='#eta',legendpos=43,**kwargs)
        plotMethod(var+'.Phi',[30,-3.14159,3.14159],savedir+var+savename+'Phi',cut=c,yaxis='Events',xaxis='#phi',legendpos=43,**kwargs)


def plotDistributions(plotMethod,myCut,nl,isControl,**kwargs):
    savedir = kwargs.pop('savedir','')
    if savedir: savedir += '/'
    plotMethod('h1.mass',[24,0,600],savedir+'hppMass',yaxis='Events/25.0 GeV/c^{2}',xaxis='M(l^{+}l^{+}) (GeV/c^{2})',lumitext=33,logy=int(not isControl),cut=myCut,**kwargs)
    plotMethod('h1.mass',[24,0,600],savedir+'hppMass_mod',yaxis='Events/25.0 GeV/c^{2}',xaxis='M(l^{+}l^{+}) (GeV/c^{2})',lumitext=33,legendpos=41,logy=0,cut=myCut,**kwargs)
    plotMethod('h1.dPhi',[32,0,3.2],savedir+'hppDphi',yaxis='Events/0.1 rad',xaxis='#Delta#phi(l^{+}l^{+}) (rad)',legendpos=41,lumitext=33,logy=0,cut=myCut,**kwargs)
    plotMethod('%il.sT'%nl,[40,0,1000],savedir+'sT',yaxis='Events/25.0 GeV/c^{2}',xaxis='S_{T} (GeV/c^{2})',lumitext=33,logy=int(not isControl),cut=myCut,**kwargs)
    plotMethod('%il.sT'%nl,[50,0,500],savedir+'sT_zoom',yaxis='Events/10.0 GeV/c^{2}',xaxis='S_{T} (GeV/c^{2})',lumitext=33,logy=int(not isControl),cut=myCut,**kwargs)
    plotMethod('%il.jetVeto20'%nl,[8,0,8],savedir+'numJets20',yaxis='Events',xaxis='Number of Jets (p_{T}>20 GeV)',lumitext=33,logy=0,cut=myCut,**kwargs)
    plotMethod('%il.jetVeto30'%nl,[8,0,8],savedir+'numJets30',yaxis='Events',xaxis='Number of Jets (p_{T}>30 GeV)',lumitext=33,logy=0,cut=myCut,**kwargs)
    plotMethod('%il.jetVeto40'%nl,[8,0,8],savedir+'numJets40',yaxis='Events',xaxis='Number of Jets (p_{T}>40 GeV)',lumitext=33,logy=0,cut=myCut,**kwargs)
    plotMethod('%il.muonVeto5'%nl,[8,0,8],savedir+'muonVeto5',yaxis='Events',xaxis='Muon Veto (p_{T}>5 GeV)',lumitext=33,logy=0,cut=myCut,**kwargs)
    plotMethod('%il.muonVeto10Loose'%nl,[8,0,8],savedir+'muonVeto10',yaxis='Events',xaxis='Muon Veto (p_{T}>10 GeV)',lumitext=33,logy=0,cut=myCut,**kwargs)
    plotMethod('%il.muonVeto15'%nl,[8,0,8],savedir+'muonVeto15',yaxis='Events',xaxis='Muon Veto (p_{T}>15 GeV)',lumitext=33,logy=0,cut=myCut,**kwargs)
    plotMethod('%il.elecVeto10'%nl,[8,0,8],savedir+'elecVeto10',yaxis='Events',xaxis='Electron Veto (p_{T}>10 GeV)',lumitext=33,logy=0,cut=myCut,**kwargs)
    plotMethod('%il.met'%nl,[40,0,200],savedir+'met',yaxis='Events/5.0 GeV',xaxis='E_{T}^{miss} (GeV)',lumitext=33,logy=int(not isControl),cut=myCut,**kwargs)
    plotMethod('z1.mass',[42,70,112],savedir+'z1Mass',yaxis='Events/1.0 GeV',xaxis='M(l^{+}l^{-}) (Z1) (GeV)',legendpos=43,logy=0,cut=myCut,**kwargs)
    plotMethod('z1.mass',[7,80.5,101.5],savedir+'z1Mass_wideBin',yaxis='Events/3.0 GeV',xaxis='M(l^{+}l^{-}) (Z1) (GeV)',legendpos=43,logy=0,cut=myCut,**kwargs)
    plotMethod('z1.mass',[80,0,240],savedir+'z1Mass_fullWindow',yaxis='Events/3.0 GeV',xaxis='M(l^{+}l^{-}) (Z1) (GeV)',legendpos=43,logy=0,cut=myCut,**kwargs)
    plotMethod('z1.mass',[80,0,240],savedir+'z1Mass_fullWindow_log',yaxis='Events/3.0 GeV',xaxis='M(l^{+}l^{-}) (Z1) (GeV)',legendpos=43,logy=1,cut=myCut,**kwargs)
    plotMethod('z1.Pt1',[40,0,200],savedir+'z1LeadingLeptonPt',yaxis='Events/5.0 GeV',xaxis='p_{T}^{Z1 Leading Lepton} (GeV)',legendpos=43,logy=0,cut=myCut,**kwargs)
    if nl==4:
        plotMethod('z2.mass',[42,70,112],savedir+'z2Mass',yaxis='Events/1.0 GeV',xaxis='M(l^{+}l^{-}) (Z2) (GeV)',legendpos=43,logy=0,cut=myCut,**kwargs)
        plotMethod('z2.mass',[7,80.5,101.5],savedir+'z2Mass_wideBin',yaxis='Events/3.0 GeV',xaxis='M(l^{+}l^{-}) (Z2) (GeV)',legendpos=43,logy=0,cut=myCut,**kwargs)
        plotMethod('z2.mass',[80,0,240],savedir+'z2Mass_fullWindow',yaxis='Events/3.0 GeV',xaxis='M(l^{+}l^{-}) (Z2) (GeV)',legendpos=43,logy=0,cut=myCut,**kwargs)
        plotMethod('z2.mass',[80,0,240],savedir+'z2Mass_fullWindow_log',yaxis='Events/3.0 GeV',xaxis='M(l^{+}l^{-}) (Z2) (GeV)',legendpos=43,logy=1,cut=myCut,**kwargs)
        plotMethod('z2.Pt1',[40,0,200],savedir+'z2LeadingLeptonPt',yaxis='Events/5.0 GeV',xaxis='p_{T}^{Z2 Leading Lepton} (GeV)',legendpos=43,logy=0,cut=myCut,**kwargs)
    if nl==3:
        plotMethod('w1.Pt1',[40,0,200],savedir+'w1LeptonPt',yaxis='Events/5.0 GeV',xaxis='p_{T}^{W Lepton} (GeV)',legendpos=43,logy=0,cut=myCut,**kwargs)
        plotMethod('w1.mass',[40,0,200],savedir+'w1Mass',yaxis='Events/5.0 GeV',xaxis='M_{T}^{W} (GeV)',legendpos=43,logy=0,cut=myCut,**kwargs)
        plotMethod('w1.dPhi',[32,0,3.2],savedir+'w1dPhi',yaxis='Events/0.1 rad',xaxis='#Delta#phi(W lepton, E_{T}^{miss}) (rad)',legendpos=43,logy=0,cut=myCut,**kwargs)
    plotMethod('event.nvtx',[50,0,50],savedir+'puVertices',yaxis='Events',xaxis='Number PU Vertices',legendpos=43,logy=0,cut=myCut,**kwargs)


def plotRegion(analysis,region,runPeriod,**kwargs):
    '''A function to simplify plotting multiple regions and run periods.'''
    blind = kwargs.pop('blind',True)
    mass = kwargs.pop('mass',500)
    runTau = kwargs.pop('runTau',False)
    plotChannels = kwargs.pop('plotChannels',False)
    plotJetBins = kwargs.pop('plotJetBins',False)
    plotOverlay = kwargs.pop('plotOverlay',False)
    plotShapes = kwargs.pop('plotShapes',False)
    plotCutFlow = kwargs.pop('plotCutFlow',False)
    for key, value in kwargs.iteritems():
        print "Unrecognized parameter '" + key + "' = " + str(value)
        return 0

    print "MKPLOTS:%s:%s:%iTeV: Mass: %i" % (analysis,region,runPeriod,mass)
    isControl = analysis != region
    nl = int(analysis[0])
    ntuples = 'ntuples%s_%stev_%s' % (analysis,runPeriod,region)
    saves = '%s_%s_%sTeV' % (analysis,region,runPeriod)
    sigMap = getSigMap(nl,mass)
    intLumiMap = getIntLumiMap()
    regionBackground = {
        'WZ' : ['T','TT', 'TTV', 'Z', 'VVV', 'ZZ','WZ'],
        'QCD': ['T','TT', 'TTV', 'Z', 'VVV', 'ZZ','WZ'],
        'ZZ' : ['T','TT','WZ','ZZ'],
        'TT' : ['Z', 'DB', 'TTV', 'T', 'TT'],
        'TTW': ['T','TT', 'Z', 'VVV', 'DB', 'TTZ', 'TTW'],
        'TTZ': ['T','TT', 'Z', 'VVV', 'DB', 'TTW', 'TTZ'],
        'Z'  : ['T','TT','WW','WZ','ZZ','Z'],
        'Zfr': ['T','TT','WW','WZ','ZZ','Z'],
        #'3l' : ['T','TT', 'TTZ','TTW', 'Z','ZZZ','WWZ','WWW','ZZ','WZ'],
        '3l' : ['T','TT', 'TTV','Z','VVV','DB'],
        '4l' : ['TT','Z','DB']
    }
    if runPeriod==13:
        regionBackground = {
            'WZ' : ['T','TT', 'TTV', 'Z', 'ZZ','WZ'],
            'QCD': ['T','TT', 'TTV', 'W', 'Z', 'ZZ','WZ'],
            'ZZ' : ['T','TT','WZ','ZZ'],
            'TT' : ['W', 'Z', 'DB', 'TTV', 'T', 'TT'],
            'TTW': ['T','TT', 'Z', 'DB', 'TTZ', 'TTW'],
            'TTZ': ['T','TT', 'Z', 'DB', 'TTW', 'TTZ'],
            'Z'  : ['T','TT','WW','WZ','ZZ','W','Z'],
            'Zfr': ['T','TT','WW','WZ','ZZ','W','Z'],
            #'3l' : ['T','TT','TTZ','TTW','Z','ZZ','WZ'],
            '3l' : ['T', 'TT', 'TTV','Z','DB'],
            '4l' : ['T', 'TT', 'Z', 'TTV','DB']
        }

    channels, leptons = getChannels(nl,runTau=runTau)
    myCut = 'select.passTight'
    if region == 'TT': myCut += '&&%il.jetVeto30>1'%nl
    print 'MKPLOTS:%s:%s:%iTeV: Cuts to be applied: %s' % (analysis, region, runPeriod, myCut)
    dataplot = (isControl or not blind) and runPeriod in [7,8]

    # now, setup the plotter
    plotter = Plotter(region,ntupleDir=ntuples,saveDir=saves,period=runPeriod)
    plotter.initializeBackgroundSamples([sigMap[runPeriod][x] for x in regionBackground[region]+['Sig']])
    if dataplot: plotter.initializeDataSamples([sigMap[runPeriod]['data']])
    plotter.setIntLumi(intLumiMap[runPeriod])
    plotMode = 'plotMCDataRatio' if dataplot else 'plotMC'
    plotMethod = getattr(plotter,plotMode)
    # now, plot
    print "MKPLOTS:%s:%s:%iTeV: Plotting discriminating variables" % (analysis,region, runPeriod)
    plotDistributions(plotMethod,myCut,nl,isControl)
    if plotJetBins:
        for jet in range(3):
            print "MKPLOTS:%s:%s:%iTeV: Plotting discriminating variables %i jet" % (analysis, region, runPeriod, jet)
            plotDistributions(plotMethod,myCut+'&&%il.jetVeto30==%i'%(nl,jet),nl,isControl,savedir='%ijet'%jet)
    print "MKPLOTS:%s:%s:%iTeV: Plotting kinematics" % (analysis, region, runPeriod)
    plotKinematicsMethod(plotMethod,leptons,'Lepton',[myCut]*nl,logy=0)
    plotKinematicsMethod(plotMethod,leptons,'Electron',['%sFlv=="e"&&%s' %(x,myCut) for x in leptons],logy=0)
    plotKinematicsMethod(plotMethod,leptons,'Muon',['%sFlv=="m"&&%s' %(x,myCut) for x in leptons],logy=0)
    # each channel
    if plotChannels:
        print "MKPLOTS:%s:%s:%iTeV: Plotting individual channels" % (analysis, region, runPeriod)
        for channel in channels:
            print "MKPLOTS:%s:%s:%iTeV: Channel %s" % (analysis, region, runPeriod, channel)
            plotDistributions(plotMethod,myCut+'&&channel=="%s"'%channel,nl,isControl,savedir=channel)
            if plotJetBins:
                for jet in range(3):
                    print "MKPLOTS:%s:%s:%iTeV: Channel %s %i jet" %(analysis,region, runPeriod, channel, jet)
                    plotDistributions(plotMethod,myCut+'&&channel=="%s"&&%il.jetVeto30==%i'%(channel,nl,jet),nl,isControl,savedir=channel+'/%ijet'%jet)

    # setup signal overlay plots
    if plotOverlay:
        plotter = Plotter(region,ntupleDir=ntuples,saveDir=saves,period=runPeriod,rootName='plots_overlay')
        plotter.initializeBackgroundSamples([sigMap[runPeriod][x] for x in regionBackground[region]])
        plotter.initializeSignalSamples([sigMap[runPeriod]['Sig']])
        if dataplot: plotter.initializeDataSamples([sigMap[runPeriod]['data']])
        plotter.setIntLumi(intLumiMap[runPeriod])
        plotMode = 'plotMCDataSignalRatio' if dataplot else 'plotMCSignalRatio'
        plotMethod = getattr(plotter,plotMode)
        # plot the signal overlay
        print "MKPLOTS:%s:%s:%iTeV: Plotting signal overlay discriminating variables" % (analysis, region, runPeriod)
        plotDistributions(plotMethod,myCut,nl,isControl,savedir='overlay',signalscale=100)
        print "MKPLOTS:%s:%s:%iTeV: Plotting signal overlay kinematics" % (analysis, region, runPeriod)
        plotKinematicsMethod(plotMethod,leptons,'Lepton',[myCut]*nl,signalscale=1000,savedir='overlay',logy=1)
        plotKinematicsMethod(plotMethod,leptons,'Electron',['%sFlv=="e"&&%s' %(x,myCut) for x in leptons],signalscale=100,savedir='overlay',logy=1)
        plotKinematicsMethod(plotMethod,leptons,'Muon',['%sFlv=="m"&&%s' %(x,myCut) for x in leptons],signalscale=100,savedir='overlay',logy=1)

    # plot shapes
    if plotShapes:
        print "MKPLOTS:%s:%s:%iTeV: Plotting shapes" % (analysis, region, runPeriod)
        plotter = ShapePlotter(region,ntupleDir=ntuples,saveDir=saves,period=runPeriod,rootName='plots_shapes')
        plotter.initializeBackgroundSamples([sigMap[runPeriod][x] for x in regionBackground[region]])
        plotter.initializeSignalSamples([sigMap[runPeriod]['Sig']])
        if dataplot: plotter.initializeDataSamples([sigMap[runPeriod]['data']])
        plotter.setIntLumi(intLumiMap[runPeriod])
        plotter.plotMC('z1.mass',['channel=="mmm"','channel=="emm"'],[42,70,112],'zMass_mc_mm',yaxis='Normalized',xaxis='M(l^{+}l^{-}) (GeV)',logy=0,cut=myCut,cutNames=['mmm','emm'])
        if dataplot: plotter.plotData('z1.mass',['channel=="mmm"','channel=="emm"'],[42,70,112],'zMass_data_mm',yaxis='Normalized',xaxis='M(l^{+}l^{-}) (GeV)',logy=0,cut=myCut,cutNames=['mmm','emm'])
        plotter.plotMC('z1.mass',['channel=="eee"','channel=="eme"'],[42,70,112],'zMass_mc_ee',yaxis='Normalized',xaxis='M(l^{+}l^{-}) (GeV)',logy=0,cut=myCut,cutNames=['eee','eme'])
        if dataplot: plotter.plotData('z1.mass',['channel=="eee"','channel=="eme"'],[42,70,112],'zMass_data_ee',yaxis='Normalized',xaxis='M(l^{+}l^{-}) (GeV)',logy=0,cut=myCut,cutNames=['eee','eme'])

    # plot cut flows
    #if isControl: return
    print "MKPLOTS:%s:%s:%iTeV: Plotting cut flow" % (analysis, region, runPeriod)
    cutFlowMap = {}
    cutFlowMap[region] = defineCutFlowMap(region,channels,mass)
    print cutFlowMap

    if region in ['3l','4l']:
        plotter = Plotter(region,ntupleDir=ntuples,saveDir=saves,period=runPeriod,rootName='plots_cutFlowSelections')
        plotter.initializeBackgroundSamples([sigMap[runPeriod][x] for x in regionBackground[region]+['Sig']])
        if dataplot: plotter.initializeDataSamples([sigMap[runPeriod]['data']])
        plotter.setIntLumi(intLumiMap[runPeriod])
        plotMode = 'plotMCDataRatio' if dataplot else 'plotMC'
        plotMethod = getattr(plotter,plotMode)
        if plotCutFlow:
            for i in range(len(cutFlowMap[region]['cuts'])):
                print 'MKPLOTS:%s:%s:%iTeV: Plotting cut flow selections %s' % (analysis, region, runPeriod, cutFlowMap[region]['labels_simple'][i])
                thisCut = '&&'.join(cutFlowMap[region]['cuts'][:i+1])
                plotDistributions(plotMethod,'%s&%s'%(myCut,thisCut),nl,isControl,savedir='cutflow/%s'%cutFlowMap[region]['labels_simple'][i])
    plotter = CutFlowPlotter(region,ntupleDir=ntuples,saveDir=saves,period=runPeriod,rootName='plots_cutflow')
    plotter.initializeBackgroundSamples([sigMap[runPeriod][x] for x in regionBackground[region]])
    plotter.initializeSignalSamples([sigMap[runPeriod]['Sig']])
    if dataplot: plotter.initializeDataSamples([sigMap[runPeriod]['data']])
    plotter.setIntLumi(intLumiMap[runPeriod])
    plotMode = 'plotCutFlowMCDataSignal' if dataplot else 'plotCutFlowMCSignal'
    plotMethod = getattr(plotter,plotMode)
    plotMethod([x+'&&'+myCut for x in cutFlowMap[region]['cuts']],'cutFlow',labels=cutFlowMap[region]['labels'],lumitext=33)
    if region=='3l':
        plotter.plotCutFlowMCDataSignal(cutFlowMap[region]['preselection'],'cutFlow_preselection',labels=cutFlowMap[region]['preselection'],legendpos=43,isprecf=True)
    if plotChannels:
        for channel in channels:
            print "MKPLOTS:%s:%s:%iTeV: Plotting cut flow  %s" % (analysis, region, runPeriod, channel)
            plotMethod(['%s&&channel=="%s"&&%s' %(x,channel,myCut) for x in cutFlowMap[region]['cuts']],'cutFlow'+channel,labels=cutFlowMap[region]['labels'],lumitext=33)
    # setup individual channel cuts on same plot
    plotChannelStrings, plotChannelCuts = getChannelStringsCuts(region,channels)
    plotMode = 'plotCutFlowMCData' if dataplot else 'plotCutFlowMC'
    plotMethod = getattr(plotter,plotMode)
    plotMethod([myCut]+['%s&&%s' %(x,myCut) for x in plotChannelCuts],'individualChannels',labels=['Total']+plotChannelStrings,nosum=True,lumitext=33,logy=0)
    if region in ['3l','4l']:
        plotter = CutFlowPlotter(region,ntupleDir=ntuples,saveDir=saves,period=runPeriod,rootName='plots_cutflowSelectionsChannels')
        plotter.initializeBackgroundSamples([sigMap[runPeriod][x] for x in regionBackground[region]+['Sig']])
        if dataplot: plotter.initializeDataSamples([sigMap[runPeriod]['data']])
        plotter.setIntLumi(intLumiMap[runPeriod])
        plotMode = 'plotCutFlowMCData' if dataplot else 'plotCutFlowMC'
        plotMethod = getattr(plotter,plotMode)
        for i in range(len(cutFlowMap[region]['cuts'])):
            thisCut = '&&'.join(cutFlowMap[region]['cuts'][:i+1])
            plotMethod(['%s&&%s'%(myCut,thisCut)]+['%s&&%s&&%s' %(x,myCut,thisCut) for x in plotChannelCuts],'cutflow/%s/individualChannels'%cutFlowMap[region]['labels_simple'][i],labels=['Total']+plotChannelStrings,nosum=True,lumitext=33,logy=0)

def plotTest():
    print 'Running test plot'
    myCut = 'select.passWZ'
    sigMap = getSigMap(3,500)
    plotter = Plotter('3l',ntupleDir='ntuples3l_8tev',saveDir='test',period=8)
    plotter.initializeBackgroundSamples([sigMap[8][x] for x in ['T','TT','Z','WW','ZZ','WZ','Sig']])
    plotter.initializeDataSamples([sigMap[8]['data']])
    plotter.setIntLumi(19700)
    plotter.plotMCData('h1.mass',[20,0,500],'hppMass',yaxis='Events/25.0 GeV/c^{2}',xaxis='M(l^{+}l^{+}) (GeV/c^{2})',lumitext=33,logy=0,cut=myCut)
    plotter.plotMCDataRatio('h1.mass',[20,0,500],'hppMass_ratio',yaxis='Events/25.0 GeV/c^{2}',xaxis='M(l^{+}l^{+}) (GeV/c^{2})',lumitext=33,logy=0,cut=myCut)

    plotter = Plotter('3l',ntupleDir='ntuples3l_8tev',saveDir='test',period=8,rootName='plots_overlay')
    plotter.initializeBackgroundSamples([sigMap[8][x] for x in ['T','TT','Z','WW','ZZ','WZ']])
    plotter.initializeSignalSamples([sigMap[8]['Sig']])
    plotter.initializeDataSamples([sigMap[8]['data']])
    plotter.setIntLumi(19700)
    plotter.plotMCDataSignal('h1.mass',[20,0,500],'hppMass_overlay',yaxis='Events/25.0 GeV/c^{2}',xaxis='M(l^{+}l^{+}) (GeV/c^{2})',lumitext=33,logy=1,cut=myCut,signalscale=100)
    plotter.plotMCDataSignalRatio('h1.mass',[20,0,500],'hppMass_overlay_ratio',yaxis='Events/25.0 GeV/c^{2}',xaxis='M(l^{+}l^{+}) (GeV/c^{2})',lumitext=33,logy=1,cut=myCut,signalscale=100)

    plotter = ShapePlotter('3l',ntupleDir='ntuples3l_8tev',saveDir='test',period=8,rootName='plots_shapes')
    plotter.initializeBackgroundSamples([sigMap[8][x] for x in ['T','TT','Z','WW','ZZ','WZ']])
    plotter.initializeSignalSamples([sigMap[8]['Sig']])
    plotter.initializeDataSamples([sigMap[8]['data']])
    plotter.setIntLumi(19700)
    plotter.plotMC('z1.mass',['channel=="mmm"','channel=="emm"','channel=="eme"','channel=="eee"'],[42,70,112],'zMass_mc',yaxis='Normalized',xaxis='M(l^{+}l^{-}) (GeV)',logy=0,cut=myCut,cutNames=['mmm','emm','eme','eee'])

    mass = 500
    cutFlowMap = {
        '3l' : {
             'cuts' : ['1',\
                       '3l.sT>1.1*%f+60.' %mass,\
                       'fabs(z1.mass-%f)>80.' %ZMASS,\
                       'h1.dPhi<%f/600.+1.95' %mass,\
                       'h1.mass>0.9*%f & h1.mass<1.1*%f' %(mass,mass)],
             'labels' : ['Preselection','s_{T}','Z Veto','#Delta#phi','Mass window']
        },
    }
    plotter = CutFlowPlotter('3l',ntupleDir='ntuples3l_8tev',saveDir='test',period=8,rootName='plots_cutflow')
    plotter.initializeBackgroundSamples([sigMap[8][x] for x in ['T','TT','Z','DB']])
    plotter.initializeSignalSamples([sigMap[8]['Sig']])
    plotter.initializeDataSamples([sigMap[8]['data']])
    plotter.setIntLumi(19700)
    plotter.plotCutFlowMCSignal([x+'&&'+myCut for x in cutFlowMap['3l']['cuts']],'cutFlow',labels=cutFlowMap['3l']['labels'],lumitext=33)

def parse_command_line(argv):
    parser = argparse.ArgumentParser(description="Plot a given region and period")

    parser.add_argument('analysis', type=str, choices=['4l','3l'], help='Analysis to plot')
    parser.add_argument('region', type=str, choices=['4l','ZZ','TT','3l','WZ','Z','TTW','TTZ'], help='Plot region')
    parser.add_argument('period', type=int, choices=[7,8,13], help='Energy (TeV)')
    parser.add_argument('-pc','--plotChannels',action='store_true',help='Plot individual channels')
    parser.add_argument('-pj','--plotJetBins',action='store_true',help='Plot jet bins')
    parser.add_argument('-po','--plotOverlay',action='store_true',help='Plot overlay')
    parser.add_argument('-ps','--plotShapes',action='store_true',help='Plot shapes')
    parser.add_argument('-pcf','--plotCutFlow',action='store_true',help='Plot cutflow distributions')
    parser.add_argument('-rt','--runTau',action='store_true',help='Run Tau channels (not implemented)')
    parser.add_argument('-ub','--unblind',action='store_false',help='Unblind signal region')
    parser.add_argument('-m','--mass',nargs='?',type=int,const=500,default=500)
    parser.add_argument('-am','--allMasses',action='store_true',help='Run over all masses')
    parser.add_argument('-ac','--allControls',action='store_true',help='Run over all controls for a given analysis (3l, 4l)')
    args = parser.parse_args(argv)

    return args


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    if argv[0] == 'test':
        plotTest()
        return 0

    args = parse_command_line(argv)

    massLists = {
        13 : {
            '3l' : [500],
            '4l' : [500]
        }, 
        8 : {
            '3l' : [170, 200, 250, 300, 350, 400, 450, 500, 600, 700],
            '4l' : [110, 130, 150, 170, 200, 250, 300, 350, 400, 450, 500, 600, 700]
        }
    }

    controlList = {
        '3l' : ['3l', 'WZ', 'TT', 'Z', 'TTW', 'TTZ'], #'QCD', 'Zfr'],
        '4l' : ['4l', 'ZZ', 'TT']
    }

    if args.period == 7:
        print "7 TeV not implemented"
    elif args.allMasses:
        for m in massLists[args.period][args.region]:
            plotRegion(args.analysis,args.region,args.period,plotChannels=args.plotChannels,runTau=args.runTau,blind=args.unblind,mass=m,plotJetBins=args.plotJetBins,plotOveraly=args.plotOverlay,plotShapes=args.plotShapes,plotCutFlow=args.plotCutFlow)
    elif args.allControls:
        for control in controlList[args.region]:
            plotRegion(args.analysis,control,args.period,plotChannels=args.plotChannels,runTau=args.runTau,blind=args.unblind,mass=args.mass,plotJetBins=args.plotJetBins,plotOverlay=args.plotOverlay,plotShapes=args.plotShapes,plotCutFlow=args.plotCutFlow)
    else:
        plotRegion(args.analysis,args.region,args.period,plotChannels=args.plotChannels,runTau=args.runTau,blind=args.unblind,mass=args.mass,plotJetBins=args.plotJetBins,plotOverlay=args.plotOverlay,plotShapes=args.plotShapes,plotCutFlow=args.plotCutFlow)

    return 0


if __name__ == "__main__":
    main()