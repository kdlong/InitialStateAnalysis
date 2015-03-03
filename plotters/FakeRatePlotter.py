'''
A cut flow plotter class.

Author: Devin N. Taylor, UW-Madison
'''

from PlotterBase import PlotterBase
from array import array
import ROOT
import math

ROOT.gStyle.SetPalette(1)

class FakeRatePlotter(PlotterBase):
    def __init__(self,analysis,**kwargs):
        PlotterBase.__init__(self,analysis,**kwargs)

    def getNumEntries(self,selection,sample,**kwargs):
        '''Return the lumi scaled number of entries passing a given cut.'''
        doError = kwargs.pop('doError',False)
        totalVal = 0
        totalErr2 = 0
        if sample in self.sampleMergeDict:
            for s in self.sampleMergeDict[sample]:
                tree = self.samples[s]['file'].Get(self.analysis)
                val = tree.GetEntries(selection)
                err = val ** 0.5
                if 'data' not in s: 
                    lumi = self.samples[s]['lumi']
                    val = val * self.intLumi/lumi
                    err = err * self.intLumi/lumi
                totalVal += val
                totalErr2 += err*err
        else:
            tree = self.samples[sample]['file'].Get(self.analysis)
            val = tree.GetEntries(selection)
            err = val ** 0.5
            if 'data' not in sample:
                lumi = self.samples[sample]['lumi']
                val = val * self.intLumi/lumi
                err = err * self.intLumi/lumi
            totalVal += val
            totalErr2 += err*err
        totalErr = totalErr2 ** 0.5
        if doError: return totalVal, totalErr
        return totalVal

    def getFakeRate(self,passSelection, failSelection, ptBins, etaBins, ptVar, etaVar, savename):
        '''Get 2d histogram of fakerates'''
        fakeHist = ROOT.TH2F(savename,'',len(ptBins)-1,array('d',ptBins),len(etaBins)-1,array('d',etaBins))
        for p in range(len(ptBins)-1):
            for e in range(len(etaBins)-1):
                kinCut = '%s>%f && %s<%f && abs(%s)>%f && abs(%s)<%f' %\
                         (ptVar, ptBins[p], ptVar, ptBins[p+1], etaVar, etaBins[e], etaVar, etaBins[e+1])
                numCut = '%s && %s' % (kinCut, passSelection)
                denomCut = '%s && %s' % (kinCut, failSelection)
                #num = self.getNumEntries(numCut,*self.data)
                #denom = self.getNumEntries(denomCut,*self.data)
                num = 0
                denom = 0
                for sample in self.backgrounds:
                    num += self.getNumEntries(numCut, sample)
                    denom += self.getNumEntries(denomCut, sample)
                fakerate = float(num)/denom
                fakeHist.Fill(ptBins[p],etaBins[e],fakerate)
        return fakeHist

    def plotFakeRate(self, passSelection, failSelection, savename, **kwargs):
        '''A function to calculate and plot the fake rate for a given selection.
           kwargs accepts:
               cut         string           applied with all selections
               ptBins      list (float)     list of pt bin edges for fakerate
               etaBins     list (float)     list of eta bin edges for fakerate
               ptVar       string           probe pt variable
               etaVar      string           probe eta variable
               logy        bool             set logy plot
               logx        bool             set logx plot
               lumitext    int              location of lumitext (from CMS_lumi)
               isprelim    bool             The plot is CMS preliminary'''
        cut = kwargs.pop('cut', '1')
        logy = kwargs.pop('logy', 0)
        logx = kwargs.pop('logx', 0)
        lumitext = kwargs.pop('lumitext', 11)
        isprelim = kwargs.pop('isprelim', 1)
        ptBins = kwargs.pop('ptBins', [10,15,20,25,30,35,40,50])
        etaBins = kwargs.pop('etaBins', [0,1,1.479,2,2.5])
        ptVar = kwargs.pop('ptVar','f1.Pt1')
        etaVar = kwargs.pop('etaVar','f1.Eta1')
        xaxis = kwargs.pop('xaxis','p_{T} (GeV)')
        yaxis = kwargs.pop('yaxis','#eta')
        for key, value in kwargs.iteritems():
            print "Unrecognized parameter '" + key + "' = " + str(value)

        self.canvas.SetLogy(logy)
        self.canvas.SetLogx(logx)
        self.canvas.SetRightMargin(0.14)

        # calculate fake rate
        fakeRateHist = self.getFakeRate(passSelection,failSelection,ptBins,etaBins,ptVar,etaVar,savename)
        fakeRateHist.GetXaxis().SetTitle(xaxis)
        fakeRateHist.GetYaxis().SetTitle(yaxis)
        fakeRateHist.GetYaxis().SetTitleOffset(1.)
        fakeRateHist.SetTitle('')
        fakeRateHist.GetZaxis().SetRangeUser(0,1)
        self.savefile.WriteTObject(fakeRateHist)

        # plot fakerate
        fakeRateHist.Draw('colz text')

        # draw cms lumi
        #self.setStyle(lumitext,plotdata,plotratio,isprelim)
        #self.canvas.cd()
        #self.canvas.Update()
        #self.canvas.RedrawAxis()
        #frame = self.canvas.GetFrame()
        #frame.Draw()

        # save everything
        self.canvas.cd()
        self.save(savename)

