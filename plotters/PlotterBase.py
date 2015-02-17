'''
Base plotting class using ntuples produced in the DblHAnalysis framework.
This class requires the definition of luminosity files claculated with lumiCalcy2.py, a cross section file,
and a data styles file for each mc sample. The xsecs should be defined in a dictionary found in xsec.py. 
The data styles should be defined in a disctionary in dataStyles.py. 

Author: Devin N. Taylor, UW-Madison
'''

import sys
import os
import errno
import glob
import ROOT
import json
import math
from array import array

from xsec import xsecs
from dataStyles import dataStyles
import CMS_lumi, tdrstyle
from plotUtils import *

ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")
tdrstyle.setTDRStyle()

class PlotterBase(object):
    '''A Base plotting class to be used with flat histograms.'''
    def __init__(self,analysis,**kwargs):
        '''Initialize the plotter (optionally make the plots blinded).'''
        # get kwargs
        saveDir = kwargs.pop('saveDir','')
        ntupleDir = kwargs.pop('ntupleDir','ntuples')
        period = kwargs.pop('period',13)
        blind = kwargs.pop('blind',False)
        rootName = kwargs.pop('rootName','plots')
        for key, value in kwargs.iteritems():
            print "Unrecognized parameter '" + key + "' = " + str(value)
        # first, setup our canvas
        W = 800
        H = 600
        T = 0.08
        B = 0.12
        L = 0.12
        R = 0.04
        self.canvas = ROOT.TCanvas("c1","c1",50,50,W,H)
        self.canvas.SetFillColor(0)
        self.canvas.SetBorderMode(0)
        self.canvas.SetFrameFillStyle(0)
        self.canvas.SetFrameBorderMode(0)
        self.canvas.SetLeftMargin( L )
        self.canvas.SetRightMargin( R )
        self.canvas.SetTopMargin( T )
        self.canvas.SetBottomMargin( B )
        self.canvas.SetTickx(0)
        self.canvas.SetTicky(0)
        self.H = H
        self.W = W
        self.T = T
        self.B = B
        self.L = L
        self.R = R
        # now, setup plotter conditions (some to be initalized later)
        self.backgroundInitialized = False
        self.background = []
        self.dataInitialized = False
        self.data = []
        self.signalInitialized = False
        self.signal = []
        self.analysis = analysis
        self.blind = blind
        self.sqrts=period
        # worry about this later
        self.plot7TeV = self.sqrts==7
        self.plot8TeV = self.sqrts==8
        self.plot13TeV = self.sqrts==13
        self.xsecs = xsecs[self.sqrts]
        self.dataStyles = dataStyles
        self.ntupleDir = ntupleDir
        if saveDir=='': saveDir = self.analysis
        self.plotDir = 'plots/'+saveDir
        python_mkdir(self.plotDir)
        python_mkdir(self.plotDir+'/png')
        #python_mkdir(self.plotDir+'/pdf')
        #python_mkdir(self.plotDir+'/eps')
        self.savefile = ROOT.TFile(self.plotDir+"/"+rootName+".root","recreate")
        self.samples = {}
        self.intLumi = 25000. # just a default 25 fb-1 for plotting without data
        self.sampleMergeDict = {}
        # 13 TeV sample aliases
        self.sampleMergeDict['SingleTop'] = ['TBarToLeptons_s-channel-CSA14_Tune4C_13TeV-aMCatNLO-tauola',\
            'TBarToLeptons_t-channel_Tune4C_CSA14_13TeV-aMCatNLO-tauola',\
            'TToLeptons_s-channel-CSA14_Tune4C_13TeV-aMCatNLO-tauola',\
            'TToLeptons_t-channel-CSA14_Tune4C_13TeV-aMCatNLO-tauola',\
            'T_tW-channel-DR_Tune4C_13TeV-CSA14-powheg-tauola',\
            'Tbar_tW-channel-DR_Tune4C_13TeV-CSA14-powheg-tauola']
        self.sampleMergeDict['Diboson'] = ['WZJetsTo3LNu_Tune4C_13TeV-madgraph-tauola',\
            'ZZTo4L_Tune4C_13TeV-powheg-pythia8']
        self.sampleMergeDict['WZJets'] = ['WZJetsTo3LNu_Tune4C_13TeV-madgraph-tauola']
        self.sampleMergeDict['ZZJets'] = ['ZZTo4L_Tune4C_13TeV-powheg-pythia8']
        self.sampleMergeDict['TTJets'] = ['TTJets_MSDecaysCKM_central_Tune4C_13TeV-madgraph-tauola']
        self.sampleMergeDict['ZJets'] = ['DYJetsToLL_M-50_13TeV-madgraph-pythia8']
        self.sampleMergeDict['WJets'] = ['WJetsToLNu_13TeV-madgraph-pythia8-tauola']
        self.sampleMergeDict['TTVJets'] = ['TTWJets_Tune4C_13TeV-madgraph-tauola',\
            'TTZJets_Tune4C_13TeV-madgraph-tauola']
        # 8 TeV sample aliases
        if period==8:
            self.sampleMergeDict['WWJets'] = ['WWJetsTo2L2Nu_TuneZ2star_8TeV-madgraph-tauola']
            self.sampleMergeDict['WZJets'] = ['WZJetsTo2L2Q_TuneZ2star_8TeV-madgraph-tauola',\
                'WZJetsTo3LNu_TuneZ2_8TeV-madgraph-tauola']
            self.sampleMergeDict['Diboson'] = ['WWJetsTo2L2Nu_TuneZ2star_8TeV-madgraph-tauola',\
                'WZJetsTo2L2Q_TuneZ2star_8TeV-madgraph-tauola', 'WZJetsTo3LNu_TuneZ2_8TeV-madgraph-tauola',\
                'ZZJetsTo4L_TuneZ2star_8TeV-madgraph-tauola']
            self.sampleMergeDict['ZZJets'] = ['ZZJetsTo4L_TuneZ2star_8TeV-madgraph-tauola']
            self.sampleMergeDict['SingleTop'] = ['T_s-channel_TuneZ2star_8TeV-powheg-tauola',\
                'T_t-channel_TuneZ2star_8TeV-powheg-tauola', 'T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola',\
                'Tbar_s-channel_TuneZ2star_8TeV-powheg-tauola', 'Tbar_t-channel_TuneZ2star_8TeV-powheg-tauola',\
                'Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola']
            self.sampleMergeDict['TTJets'] = ['TTJetsFullLepMGDecays', 'TTJetsSemiLepMGDecays']
            self.sampleMergeDict['ZJets'] = ['Z1jets_M50', 'Z2jets_M50_S10', 'Z3jets_M50',\
                'Z4jets_M50']
            #self.sampleMergeDict['ZJets'] = ['DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball']
            self.sampleMergeDict['data'] = ['data_Run2012A', 'data_Run2012B', 'data_Run2012C',\
                'data_Run2012D']
            self.sampleMergeDict['TTVJets'] = ['TTZJets', 'TTWJets', 'TTWWJets', 'TTGJets']
            self.sampleMergeDict['VVVJets'] = ['ZZZNoGstarJets', 'WWZNoGstarJets', 'WWWJets']

    def reset(self):
        '''Reset the plotter class'''
        print "Resetting the PlotterBase class"
        self.backgroundInitialized = False
        self.backgrounds = []
        self.dataInitialized = False
        self.data = []
        self.signalInitialized = False
        self.signal = []
        self.samples = {}
        self.intLumi = 25000.
        self.resetCanvas()

    def resetCanvas(self):
        '''Reset canvas after changes'''
        self.canvas.SetCanvasSize(self.W,self.H)
        #self.canvas.SetFillColor(0)
        #self.canvas.SetBorderMode(0)
        #self.canvas.SetFrameFillStyle(0)
        #self.canvas.SetFrameBorderMode(0)
        self.canvas.SetLeftMargin( self.L )
        self.canvas.SetRightMargin( self.R )
        self.canvas.SetTopMargin( self.T )
        self.canvas.SetBottomMargin( self.B )
        self.canvas.SetTickx(0)
        self.canvas.SetTicky(0)
        

    def initializeBackgroundSamples(self,sampleList):
        '''Initialize the background samples.'''
        self.backgrounds = sampleList
        self.initializeSamples(sampleList)
        self.backgroundInitialized = True

    def initializeDataSamples(self,sampleList):
        '''Initialize the data samples.'''
        self.data = sampleList
        self.initializeSamples(sampleList)
        self.dataInitialized = True
        self.calculateIntLumi()

    def initializeSignalSamples(self,sampleList):
        '''Initialize the signal samples.'''
        self.signal = sampleList
        self.initializeSamples(sampleList)
        self.signalInitialized = True

    def initializeSamplesHelper(self,sample):
        '''initialize single sample'''
        self.samples[sample] = {} 
        file = self.ntupleDir+'/%s.root' % sample
        self.samples[sample]['file'] = ROOT.TFile(file)
        if 'data' in sample:
            lumifile = self.ntupleDir+'/%s.lumicalc.sum' % sample
            #lumi = open(lumifile)
            #self.samples[sample]['lumi'] = lumi.readline()
            #lumi.close()
        else:
            cutflowHist = self.samples[sample]['file'].Get('cutflow')
            n_evts = cutflowHist.GetBinContent(1)
            sample_xsec = self.xsecs[sample]
            self.samples[sample]['lumi'] = float(n_evts)/sample_xsec

    def initializeSamples(self,sampleList):
        '''Initialize a list of samples to the sample dictionary.'''
        for sample in sampleList:
            if sample in self.sampleMergeDict:
                for s in self.sampleMergeDict[sample]:
                    self.initializeSamplesHelper(s)
            else:
                self.initializeSamplesHelper(sample)

    def calculateIntLumi(self):
        '''Calculate the integrated luminosity to scale the Monte Carlo'''
        if not self.dataInitialized: 
            print "No data initialized, default to 25 fb-1"
            self.intLumi = 25000.
            return
        #intLumi = 0.
        #for sample in self.data:
        #    # here only add samples for this channel
        #    intLumi += self.samples[sample]['lumi']
        #self.intLumi = intLumi
        self.intLumi = 25000.

    def setIntLumi(self,intLumi):
        '''Set the integrated luminosity to scale MC to'''
        self.intLumi = intLumi

    # TODO: Not right, check later
    def getOverflowUnderflow(self,hist):
        '''Get the plot with overflow and underflow bins'''
        nx = hist.GetNbinsX()+1
        xbins = [0]*(nx+1)
        for i in range(nx):
            xbins[i]=hist.GetBinLowEdge(i+1)
        xbins[nx]=xbins[nx-1]+hist.GetBinWidth(nx)
        tempName = hist.GetName()+'OU'
        htmp = ROOT.TH1F(tempName, hist.GetTitle(), nx, array('d',xbins))
        for i in range(nx):
            htmp.Fill(htmp.GetBinCenter(i), hist.GetBinContent(i))
        htmp.Fill(hist.GetBinLowEdge(1)-1, hist.GetBinContent(0))
        htmp.SetEntries(hist.GetEntries())
        return htmp

    def getSingleVarHist(self,tree,sample,variable,binning,cut):
        '''Single variable, single sample hist'''
        if 'data' not in sample: lumi = self.samples[sample]['lumi']
        if len(binning) == 3: # standard drawing
            drawString = "%s>>h%s%s(%s)" % (variable, sample, variable, ", ".join(str(x) for x in binning))
        else: # we will need to rebin
            drawString = "%s>>h%s%s()" % (variable, sample, variable)
        if not cut: cut = '1'
        if 'data' not in sample and self.sqrts != 13: # TODO: dont forget to remove when we have data!
            tree.Draw(drawString,'(event.pu_weight*event.lep_scale)*('+cut+')','goff')
            #tree.Draw(drawString,'event.pu_weight*('+cut+')','goff')
            #tree.Draw(drawString,'event.lep_scale*('+cut+')','goff')
            #tree.Draw(drawString,cut,'goff')
        else:
            tree.Draw(drawString,cut,'goff')
        if not ROOT.gDirectory.Get("h%s%s" %(sample, variable)):
            #print "%s has no events" % sample
            return 0
        hist = ROOT.gDirectory.Get("h%s%s" %(sample, variable)).Clone("hmod%s%s"%(sample,variable))
        if len(binning) != 3: # variable binning (list of bin edges
            hist.Rebin(len(binning)-1,"hnew%s%s" %(sample,variable),array('d',binning))
            hist = ROOT.gDirectory.Get("hnew%s%s" %(sample,variable)).Clone("hnewmod%s%s"%(sample,variable))
        if False: hist = self.getOverflowUnderflow(hist)
        if 'data' not in sample: # if it is mc, scale to intLumi
            hist.Scale(self.intLumi/lumi)
        return hist

    def getHist(self, sample, variables, binning, cut, noFormat=False):
        '''Return a histogram of a given variable from the given dataset with a cut'''
        hists = ROOT.TList()
        for v in range(len(variables)):
            if sample in self.sampleMergeDict:
                for s in self.sampleMergeDict[sample]:
                    tree = self.samples[s]['file'].Get(self.analysis)
                    if len(variables) != len(cut):
                        hist = self.getSingleVarHist(tree,s,variables[v],binning,cut)
                    else:
                        hist = self.getSingleVarHist(tree,s,variables[v],binning,cut[v])
                    if hist:
                        hists.Add(hist)
            else:
                tree = self.samples[sample]['file'].Get(self.analysis)
                if len(variables) != len(cut):
                    hist = self.getSingleVarHist(tree,sample,variables[v],binning,cut)
                else:
                    hist = self.getSingleVarHist(tree,sample,variables[v],binning,cut[v])
                if hist:
                    hists.Add(hist)
        if hists.IsEmpty():
            return 0
        hist = hists[0].Clone("hmerged%s%s" % (sample, variables[0]))
        hist.Reset()
        hist.Merge(hists)
        # set styles
        if not noFormat: hist.SetTitle(self.dataStyles[sample]['name'])
        if sample in self.data: return hist
        if not noFormat:
            hist.SetFillColor(self.dataStyles[sample]['fillcolor'])
            hist.SetLineColor(self.dataStyles[sample]['linecolor'])
            hist.SetFillStyle(self.dataStyles[sample]['fillstyle'])
        return hist

    def getData(self, variables, binning, cut, noFormat=False):
        '''Return a histogram of data for the given variable'''
        hists = ROOT.TList()
        for sample in self.data:
            hist = self.getHist(sample, variables, binning, cut, noFormat)
            hists.Add(hist)
        hist = hists[0].Clone("hdata%s" % variables[0])
        hist.Reset()
        hist.Merge(hists)
        return hist

    def getMCStack(self, variables, binning, cut):
        '''Return a stack of MC histograms'''
        mcstack = ROOT.THStack('hs%s' % variables[0],'mc stack')
        for sample in self.backgrounds:
            hist = self.getHist(sample, variables, binning, cut)
            if not hist: continue
            mcstack.Add(hist)
        return mcstack

    def get_stat_err(self, hist):
        '''Create statistical errorbars froma histogram'''
        staterr = hist.Clone("staterr")
        staterr.Sumw2()
        staterr.SetFillColor(ROOT.EColor.kGray+3)
        staterr.SetLineColor(ROOT.EColor.kGray+3)
        staterr.SetLineWidth(0)
        staterr.SetMarkerSize(0)
        staterr.SetFillStyle(3013)
        return staterr

    def get_ratio(self, num, denom, label):
        '''Return a ratio histogram'''
        ratio = num.Clone(label)
        ratio.Sumw2()
        ratio.SetMarkerSize(0.8)
        ratio.Divide(num, denom, 1., 1., "")
        return ratio

    def get_ratio_stat_err(self, hist):
        '''Return a statistical error bars for a ratio plot'''
        ratiostaterr = hist.Clone("ratiostaterr")
        ratiostaterr.Sumw2()
        ratiostaterr.SetStats(0)
        ratiostaterr.SetTitle("")
        ratiostaterr.GetYaxis().SetTitle("Data/MC")
        ratiostaterr.SetMaximum(2.)
        ratiostaterr.SetMinimum(0)
        ratiostaterr.SetMarkerSize(0)
        ratiostaterr.SetFillColor(ROOT.EColor.kGray+3)
        ratiostaterr.SetFillStyle(3013)
        ratiostaterr.GetXaxis().SetLabelSize(0.19)
        ratiostaterr.GetXaxis().SetTitleSize(0.21)
        ratiostaterr.GetXaxis().SetTitleOffset(1.0)
        ratiostaterr.GetYaxis().SetLabelSize(0.19)
        ratiostaterr.GetYaxis().SetTitleSize(0.21)
        ratiostaterr.GetYaxis().SetTitleOffset(0.27)
        ratiostaterr.GetYaxis().SetNdivisions(503)

        # bin by bin errors
        for i in range(hist.GetNbinsX()+2):
            ratiostaterr.SetBinContent(i, 1.0)
            if hist.GetBinContent(i)>1e-6:  # not empty
                binerror = hist.GetBinError(i) / hist.GetBinContent(i)
                ratiostaterr.SetBinError(i, binerror)
            else:
                ratiostaterr.SetBinError(i, 999.)

        return ratiostaterr

    def setStyle(self,position=11,plotdata=True,plotratio=False,preliminary=True):
        '''Set style for plots based on the CMS TDR style guidelines.
           https://twiki.cern.ch/twiki/bin/view/CMS/Internal/PubGuidelines#Figures_and_tables
           https://ghm.web.cern.ch/ghm/plots/'''
        # set period (used in CMS_lumi)
        # period : sqrts
        # 1 : 7, 2 : 8, 3 : 7+8, 4 : 13, ... 7 : 7+8+13
        self.period = 1*self.plot7TeV + 2*self.plot8TeV + 4*self.plot13TeV
        CMS_lumi.wrtieExtraText = preliminary
        CMS_lumi.extraText = "Preliminary" if plotdata else "Simulation Preliminary"
        #CMS_lumi.extraText = "Preliminary"
        CMS_lumi.lumi_7TeV = "%0.1f fb^{-1}" % (float(self.intLumi)/1000.)
        CMS_lumi.lumi_8TeV = "%0.1f fb^{-1}" % (float(self.intLumi)/1000.)
        CMS_lumi.lumi_13TeV = "%0.1f fb^{-1}" % (float(self.intLumi)/1000.)
        CMS_lumi.CMS_lumi(self.plotpad if plotratio else self.canvas,self.period,position)

    def drawLegend(self,plotdata,plotsignal,plotratio,legendpos):
        '''Plot a legend using the new PUB COMM recommendations.'''
        # initialize latex for labels and legend
        latex = ROOT.TLatex()
        # setup number of things to include in legend
        n_ = len(self.backgrounds)
        if plotdata: n_ += 1
        if plotsignal: n_ += len(self.signal)
        # create legend position
        if legendpos % 10 == 1: # on the left
            x1_l = 0.45
        elif legendpos % 10 == 2: # in the middle
            x1_l = 0.70
        else: # default (on right)
            x1_l = 0.95
        dx_l = 0.3
        x0_l = x1_l-dx_l
        if legendpos//10 == 1: # bottom
            y1_l = 0.35
        elif legendpos//10 == 2: # middle
            y1_l = 0.59
        elif legendpos//10 == 4: # very top (in line with CMS label)
            y1_l = 0.91
        else: # default, top, just below CMS label
            y1_l = 0.77
        if plotratio: y1_l *= 0.95
        dy_l = 0.045*n_ # number of things in legend
        #if plotratio: dy_l *= 0.85
        y0_l = y1_l-dy_l
        legend = ROOT.TPad("legend_0","legend_0",x0_l,y0_l,x1_l,y1_l)
        legend.Draw()
        # now setup the position of the boxes in the legend
        legend.cd()
        ar_l = dy_l/dx_l
        gap_ = 1./(n_+1)
        bwx_ = 0.12
        bwy_ = gap_/1.5
        x_l = [1.2*bwx_]
        y_l = [1-gap_]
        ex_l = [0]
        ey_l = [0.04/ar_l]
        x_l = array("d",x_l)
        ex_l = array("d",ex_l)
        y_l = array("d",y_l)
        ey_l = array("d",ey_l)
        latex.SetTextFont(42)
        latex.SetTextAngle(0)
        latex.SetTextColor(ROOT.EColor.kBlack)    
        latex.SetTextSize(0.7/n_) 
        #latex.SetTextSize(0.25) 
        latex.SetTextAlign(12) 
        # plot data label
        if plotdata:
            gr_l =  ROOT.TGraphErrors(1, x_l, y_l, ex_l, ey_l)
            ROOT.gStyle.SetEndErrorSize(0)
            gr_l.SetMarkerStyle(20)
            gr_l.SetMarkerSize(0.9)
            gr_l.Draw("0P")
            xx_ = x_l[0]
            yy_ = y_l[0]
            latex.DrawLatex(xx_+1.*bwx_,yy_,"Data")
        # plot mc labels
        allMC = self.backgrounds + self.signal if plotsignal else self.backgrounds
        box_ = ROOT.TBox()
        for s in range(len(allMC)):
            xx_ = x_l[0]
            yy_ = y_l[0]
            yy_ -= gap_*(s+1) if plotdata else gap_*s
            box_.SetFillColor( self.dataStyles[allMC[s]]['fillcolor'] )
            if allMC[s] in self.signal:
                box_.SetFillStyle( 0 )
            else:
                box_.SetFillStyle( self.dataStyles[allMC[s]]['fillstyle'] )
            box_.DrawBox( xx_-bwx_/2, yy_-bwy_/2, xx_+bwx_/2, yy_+bwy_/2 )
            box_.SetLineStyle( ROOT.kSolid )
            if allMC[s] in self.signal:
                box_.SetLineWidth( 2 )
            else:
                box_.SetLineWidth( 1 )
            box_.SetLineColor( self.dataStyles[allMC[s]]['linecolor'] )
            box_.SetFillStyle( 0 )
            box_.DrawBox( xx_-bwx_/2, yy_-bwy_/2, xx_+bwx_/2, yy_+bwy_/2 )
            latex.DrawLatex(xx_+1.*bwx_,yy_,self.dataStyles[allMC[s]]['name'])
        self.canvas.Update()

    def save(self, savename):
        '''Save the canvas in multiple formats.'''
        #for type in ['png', 'pdf', 'eps']:
        for type in ['png']:
            name = "%s/%s/%s.%s" % (self.plotDir, type, savename, type)
            python_mkdir(os.path.dirname(name))
            self.canvas.Print(name)
        self.canvas.SetName(savename)
        self.savefile.WriteTObject(self.canvas)
        self.canvas.Clear()

