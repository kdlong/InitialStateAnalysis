#from __future__ import absolute_import

import sys
import os
import glob
import logging
import numpy as np
import ROOT

from .datacard import Datacard
import plotters.xsec as xsec
from plotters.FakeRatePlotter import FakeRatePlotter
from plotters.plotUtils import _3L_MASSES, _4L_MASSES, ZMASS, getChannels, getSigMap, getIntLumiMap

ROOT.gROOT.SetBatch(ROOT.kTRUE)

class Limits(object):

    def __init__(self, analysis, period, base_selections, ntuple_dir, out_dir,
                 channels=[], lumi=25.0, blinded=True, bgMode='mc'):
        self.base_selections = base_selections
        self.analysis = analysis
        self.period = period
        self.out_dir = out_dir
        self.ntuple_dir = ntuple_dir
        self.sample_groups = {}
        self.lumi = lumi
        self.blinded = blinded
        self.sytematic_list = []
        self.datacard = Datacard(self.analysis)
        self.channels = channels
        self.xsecs = xsec.xsecs[period]
        self.bgMode = bgMode

        self.log = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

        os.system("mkdir -p %s" % self.out_dir)

    def getPlotter(self,analysis,runPeriod,mass,runTau,plotName,doFakes):
        nl = 3 if analysis=='Hpp3l' or analysis=='WZ' else 4
        ntuples = 'ntuples%s_%itev_%s' % (analysis,runPeriod,analysis)
        saves = '%s_%s_%iTeV' % (analysis,analysis,runPeriod)
        sigMap = getSigMap(nl,mass)
        intLumiMap = getIntLumiMap()
        regionBackground = {
            'Hpp3l' : ['T','TT', 'TTV','Z','VVV','DB'],
            'Hpp4l' : ['T','TT', 'TTV','Z','VVV','DB']
        }
        if runPeriod==13: regionBackground['Hpp3l'] = ['T','TT', 'TTV','Z','DB']
        if runPeriod==13: regionBackground['Hpp4l'] = ['T','TT', 'TTV','Z','DB']
        channels, leptons = getChannels(nl,runTau=runTau)
    
        plotter = FakeRatePlotter(analysis,ntupleDir=ntuples,saveDir=saves,period=runPeriod,rootName=plotName)
        if not doFakes: plotter.initializeBackgroundSamples([sigMap[runPeriod][x] for x in regionBackground[analysis]])
        if runPeriod==8: plotter.initializeDataSamples([sigMap[runPeriod]['data']])
        plotter.setIntLumi(intLumiMap[runPeriod])
    
        return plotter


    def add_group(self, group_name, *sample_names, **kwargs):
        samples = []
        for name in sample_names:
            samples += glob.glob("%s/%s.root" % (self.ntuple_dir, name))

        is_data = kwargs.get('isData', False)
        is_sig = kwargs.get('isSignal', False)
        scale = kwargs.get('scale', 1.0)

        self.sample_groups[group_name] = {
            'sample_names': [os.path.splitext(os.path.basename(x))[0]
                             for x in samples],
            'scale': scale,
            'isSig': is_sig,
            'isData': is_data}

    def add_systematics(self, syst_name, syst_type, **kwargs):
        self.datacard.add_syst(syst_name, syst_type, **kwargs)

    def get_var_weights(self, sample, var, cut, scale):
        file = self.ntuple_dir+'/%s.root' % sample
        tfile = ROOT.TFile(file)
        cutflowHist = tfile.Get('cutflow')
        n_evts = cutflowHist.GetBinContent(1)
        sample_xsec = self.xsecs[sample]
        samplelumi = float(n_evts)/sample_xsec
        lumiscale = self.lumi/samplelumi
        val = 0
        tree = tfile.Get(self.analysis)
        tree.Draw('event.pu_weight>>h%s()'%sample,'event.lep_scale*(%s)' %cut,'goff')
        if not ROOT.gDirectory.Get("h%s" %sample): return [0,0]
        hist = ROOT.gDirectory.Get("h%s" %sample).Clone("hnew%s" %sample)
        hist.Sumw2()
        val = hist.Integral()
        err = 0
        for i in range(hist.GetNbinsX()):
            err += hist.GetBinError(i)
        val = val * scale * lumiscale
        err = err * scale * lumiscale
        #print "val: %f" % val
        #print "err: %f" % err
        #if val < err: return err
        return [val, err]

    def gen_card(self, file_name, **kwargs):
        mass = kwargs.pop('mass',500)
        cuts = kwargs.pop('cuts','1')
        period = kwargs.pop('period',13)
        values = []
        weights = []

        var = 'mass'

        if isinstance(cuts, str):
            cut = self.base_selections + '&&' + cuts
            cutMC_data = cut
            cutSig = cut
        else:
            cutMC_data = self.base_selections + '&&(' + '||'.join(cuts) + ')' # full selection for bg and data
            cutSig = [self.base_selections + '&&' + x for x in cuts]          # different selections or signal so it can be scaled
            cuts = '(' + '||'.join(cuts) + ')'

        # setup sideband stuff
        minMass = 12.
        maxMass = 800.
        srCut = '(h1.mass>0.9*%f & h1.mass<1.1*%f & h1.mass>%f & h1.mass<%f)' %(mass,mass,minMass,maxMass)
        sbCut = '((h1.mass<150. & h1.mass>%f) ||  (h1.mass>1.1*%f & h1.mass<%f))' %(minMass,mass,maxMass)
        fullCut = '3l.sT>1.1*%f+60. & fabs(z.mass-%f)>80. & h1.dPhi<%f/600.+1.95' %(mass,ZMASS,mass)
        finalSRCut = 'h1.mass>0.9*%f & h1.mass<1.1*%f' %(mass,mass)
        # TODO: change for 4l

        myCut = '1'

        plotter = self.getPlotter(self.analysis,self.period,mass,False,'plots_limits_temp',False)

        nSBDict = {}
        nSRDict = {}
        for background in plotter.backgrounds:
            nSBDict[background] = plotter.getNumEntries('%s&%s&%s' %(myCut,sbCut,cuts),background,doError=True)
            nSRDict[background] = plotter.getNumEntries('%s&%s&%s' %(myCut,srCut,cuts),background,doError=True)
        nSB = sum([x[0] for x in nSBDict.itervalues()])
        eSB = sum([x[1]*x[1] for x in nSBDict.itervalues()]) ** 0.5
        nSR = sum([x[0] for x in nSRDict.itervalues()])
        eSR = sum([x[1]*x[1] for x in nSRDict.itervalues()]) ** 0.5
        alpha = nSR/nSB if nSB else nSR
        # TODO: Check this
        if period == 13:
            nSBData, eSBData = (0., 0.)
            nSRData, eSRData = (0., 0.)
        else:
            nSBData, eSBData = plotter.getNumEntries('%s&%s&%s&%s' %(myCut,sbCut,fullCut,cuts),*plotter.data,doError=True)
            nSRData, eSRData = plotter.getNumEntries('%s&%s&%s&%s' %(myCut,finalSRCut,fullCut,cuts),*plotter.data,doError=True)
        nBGSR = alpha*(nSBData+1)
        eBGSR = alpha*((nSBData+1) ** 0.5)

        # store values for values card
        sbVal = nBGSR
        sbStatErr = eBGSR
        dataVal = nSRData
        dataStatErr = eSRData
        dataSystErr = 0.0 # TODO
        mcVal = 0.0 # TODO
        mcStatErr = 0.0 # TODO
        pairVal = 0.0 # TODO
        pairStatErr = 0.0 # TODO
        assocVal = 0.0 # TODO
        assocStatErr = 0.0 # TODO

        # if nBGSR < stat uncertainty of MC in SR, nBGSR = stat uncertainty
        if nBGSR < eBGSR: nBGSR = eBGSR
        # print this out just to check
        print "nSBMC: %0.4f" % nSB
        print "eSBMC: %0.4f" % eSB
        print "nSRMC: %0.4f" % nSR
        print "eSRMC: %0.4f" % eSR
        print "alpha: %0.4f" % alpha
        print "nSBDa: %0.4f" % nSBData
        print "eSBDa: %0.4f" % nSBData
        print "nBGSR: %0.4f" % nBGSR
        print "eBGSR: %0.4f" % eBGSR
        #if not self.blinded: print "nSRDa: %0.4f" % nSRData

        # calculate values
        bgMap = {}
        for key in self.sample_groups:
           is_data = self.sample_groups[key]['isData']
           scale = self.sample_groups[key]['scale']
           wgts = []
           if not is_data:
               self.log.info("Processing MC: %s" % key)
               for sample_name in self.sample_groups[key]["sample_names"]:
                   if type(scale) is list:
                       for s,c in zip(scale,cutSig):
                           wgts.append(self.get_var_weights(sample_name,var,c,s))
                   else:
                       wgts.append(self.get_var_weights(sample_name,var,cutMC_data,scale))
               bgMap[key] = [sum([x[0] for x in wgts]), sum([x[1]**2 for x in wgts])**0.5]

        mcVal = 0.
        mcStatErr2 = 0.
        for key, val in bgMap.iteritems():
            if not self.sample_groups[key]['isData'] and not self.sample_groups[key]['isSig'] and key!='bg':
                mcVal += val[0]
                mcStatErr2 += val[1] ** 2
            if self.sample_groups[key]['isSig']:
                assocVal = val[0]
                assocStatErr = val[1]
        mcStatErr = mcStatErr2 ** 0.5

        # here we decide what datacard format we want to output
        if self.bgMode=='sideband':
            for key in self.sample_groups:
                is_data = self.sample_groups[key]['isData']
                if self.sample_groups[key]['isSig']:
                    self.datacard.add_sig(key, bgMap[key][0])
                elif key=='bg': # don't add the mc bg
                    self.datacard.add_bkg(key, nBGSR)
                elif is_data and not self.blinded:
                    self.datacard.set_observed(nSRData)

        if self.bgMode=='mc':
            for key in self.sample_groups:
                is_data = self.sample_groups[key]['isData']
                if not is_data:
                    if self.sample_groups[key]['isSig']:
                        self.datacard.add_sig(key, bgMap[key][0])
                    elif key!='bg': # dont add the sideband bg
                        self.datacard.add_bkg(key, bgMap[key][0])
                elif is_data and not self.blinded:
                    self.datacard.set_observed(nSRData)

        self.log.info("Saving card to file")

        with open("%s/%s" % (self.out_dir, file_name), 'w') as outfile:
            outfile.write(self.datacard.dump())

        # output this to text file to be read later
        # format mcVal:mcStatErr:mcSystErr:sbVal:sbStatErr:sbSystErr:dataVal:dataStatErr:dataSystErr:\
        #        pairVal:pairStatErr:pairSystErr:assocVal:assocStatErr:assocSystErr
        with open(self.out_dir+'/values.txt', 'w') as file:
            outString = '%f:%f' % (mcVal, mcStatErr)
            outString += ':%f:%f' % (sbVal, sbStatErr)
            if not self.blinded:
                outString += ':%f:%f:%f' % (dataVal, dataStatErr, dataSystErr)
            else:
                outString += ':%f:%f:%f' % (0, 0, 0)
            outString += ':%f:%f' % (pairVal, pairStatErr)
            outString += ':%f:%f' % (assocVal, assocStatErr)
            file.write(outString)
