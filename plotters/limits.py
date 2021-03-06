'''
Class for plotting limits.
'''

import sys
import os
import errno
import numpy as np
import CMS_lumi, tdrstyle
from plotUtils import _3L_MASSES, _4L_MASSES, python_mkdir

sys.argv.append('-b')
import ROOT
sys.argv.pop()

ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(ROOT.kTRUE)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")
tdrstyle.setTDRStyle()

def save(savename,saveDir,canvas):
    '''Save the limits into root file and images.'''
    #for type in ['png', 'pdf', 'eps']:
    for type in ['png']:
        name = "%s/%s/%s.%s" % (saveDir, type, savename, type)
        python_mkdir(os.path.dirname(name))
        canvas.Print(name)
    #canvas.SetName(savename)
    #savefile.WriteTObject(self.canvas)
    #canvas.Clear()

def plot_limits(analysis, period, savename, **kwargs):
    '''Plot limits and get exclusion limits'''
    datacardBaseDir = kwargs.pop('datacardBaseDir','datacards')
    limitDataBaseDir = kwargs.pop('limitDataBaseDir','limitData')
    saveDir = kwargs.pop('saveDir','plots/limits')
    blind = kwargs.pop('blind',True)
    bp = kwargs.pop('branchingPoint','')
    
    datacardDir = '%s/%s_%itev' % (datacardBaseDir, analysis, period)
    if bp: datacardDir += '/%s' % bp
    limitDataDir = '%s/%s_%itev' % (limitDataBaseDir, analysis, period)
    if bp: limitDataDir += '/%s' % bp

    masses = _3L_MASSES if analysis == 'Hpp3l' else _4L_MASSES
    if period==13: masses = [500]
    quartiles = np.empty((6, len(masses)), dtype=float)

    for j, mass in enumerate(masses):
        fname = os.path.join(limitDataDir, "higgsCombineTest.Asymptotic.mH%i.root" % mass)
        file = ROOT.TFile(fname,"READ")
        tree = file.Get("limit")
        if not tree: continue
        for i, row in enumerate(tree):
            quartiles[i,j] = row.limit

    n = len(masses)
    twoSigma = ROOT.TGraph(2*n)
    oneSigma = ROOT.TGraph(2*n)
    expected  = ROOT.TGraph(n)
    if not blind: observed  = ROOT.TGraph(n)
    for i, mass in enumerate(masses):
        twoSigma.SetPoint(i,masses[i],quartiles[4][i])
        twoSigma.SetPoint(n+i,masses[n-i-1],quartiles[0][n-i-1])
        oneSigma.SetPoint(i,masses[i],quartiles[3][i])
        oneSigma.SetPoint(n+i,masses[n-i-1],quartiles[1][n-i-1])
        expected.SetPoint(i,masses[i],quartiles[2][i])
        if not blind: observed.SetPoint(i,masses[i],quartiles[5][i])
    twoSigma.SetFillColor(ROOT.EColor.kYellow)
    twoSigma.SetLineColor(ROOT.EColor.kYellow)
    twoSigma.SetMarkerStyle(0)
    oneSigma.SetFillColor(ROOT.EColor.kSpring)
    oneSigma.SetLineColor(ROOT.EColor.kSpring)
    oneSigma.SetMarkerStyle(0)
    expected.SetLineStyle(7)
    expected.SetMarkerStyle(0)
    expected.SetFillStyle(0)
    if not blind:
        observed.SetMarkerStyle(0)
        observed.SetFillStyle(0)
    
    canvas = ROOT.TCanvas('c%s'%bp,'c%s'%bp,50,50,800,600)
    canvas.SetFillColor(0)
    canvas.SetBorderMode(0)
    canvas.SetFrameFillStyle(0)
    canvas.SetFrameBorderMode(0)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.04)
    canvas.SetTopMargin(0.08)
    canvas.SetBottomMargin(0.12)
    canvas.SetLogy(1)

    expected.GetXaxis().SetLimits(masses[0],masses[-1])
    expected.GetXaxis().SetTitle('#Phi^{++} Mass (GeV)')
    expected.GetYaxis().SetTitle('95% CLs Upper Limit on #sigma/#sigma_{SM}')
    expected.GetYaxis().SetTitleOffset(1.)
    expected.GetYaxis().SetTitleSize(0.05)

    twoSigma.Draw('f')
    oneSigma.Draw('f')
    expected.Draw()
    if not blind: observed.Draw()

    ratiounity = ROOT.TLine(expected.GetXaxis().GetXmin(),1,expected.GetXaxis().GetXmax(),1)
    ratiounity.Draw()

    legend = ROOT.TLegend(0.65,0.2,0.90,0.4)
    legend.SetFillColor(0)
    if not blind: legend.AddEntry(observed, 'Observed')
    legend.AddEntry(expected, 'Expected')
    legend.AddEntry(twoSigma, 'Expected 2#sigma', 'F')
    legend.AddEntry(oneSigma, 'Expected 1#sigma', 'F')

    legend.Draw('same')

    lumiperiod = 2 if period == 8 else 4
    CMS_lumi.wrtieExtraText = True
    CMS_lumi.extraText = "Preliminary" if not blind else "Simulation Preliminary"
    CMS_lumi.lumi_7TeV = "%0.1f fb^{-1}" % (4.9)
    CMS_lumi.lumi_8TeV = "%0.1f fb^{-1}" % (19.7)
    CMS_lumi.lumi_13TeV = "%0.1f fb^{-1}" % (25.0)
    CMS_lumi.CMS_lumi(canvas,lumiperiod,11)

    save(savename,saveDir,canvas)

    y = 0
    for x in range(masses[0],masses[-1]):
        y = expected.Eval(x)
        if y > 1: break

    print "Expected Limit: %i GeV" % x

