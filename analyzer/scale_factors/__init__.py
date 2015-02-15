import sys
import os
import glob
#import FinalStateAnalysis.TagAndProbe.MuonPOGCorrections as MuonPOGCorrections
#import FinalStateAnalysis.TagAndProbe.H2TauCorrections as H2TauCorrections

sys.argv.append('-b')
import ROOT as rt
sys.argv.pop()


class LeptonScaleFactors(object):

    def __init__(self):
        path = os.path.join(os.path.dirname(__file__),
                            'CombinedMethod_ScaleFactors_RecoIdIsoSip.root')
        self.e_rtfile = rt.TFile(path, 'READ')
        self.e_hist = self.e_rtfile.Get("h_electronScaleFactor_RecoIdIsoSip")

        path = os.path.join(os.path.dirname(__file__),
                            'MuonScaleFactors_2011_2012.root')
        self.m_rtfile = rt.TFile(path, 'READ')
        self.m_hist = self.m_rtfile.Get("TH2D_ALL_2012")

        #self.muPOGId = MuonPOGCorrections.make_muon_pog_PFTight_2012()
        #self.muPOGIso = MuonPOGCorrections.make_muon_pog_PFRelIsoDB012_2012()

    def scale_factor(self, row, *lep_list, **kwargs):
        tight = kwargs.pop('tight',False)
        out = 1.0
        for l in lep_list:
            lep_type = l[0]

            if lep_type == 'm':
                out *= self.m_tight_scale(row, l) if tight else self.m_scale(row, l)

            elif lep_type == 'e':
                out *= self.e_tight_scale(row, l) if tight else self.e_scale(row, l)
            elif lep_type == 't':
                out *= 1 # TODO

            else:
                raise TypeError("Lepton type %s not recognized" % lep_type)

        return out

    def e_scale(self, row, l):
        pt = getattr(row, "%sPt" % l)
        eta = getattr(row, "%sEta" % l)
        global_bin = self.e_hist.FindBin(pt, eta)
        scl = self.e_hist.GetBinContent(global_bin)

        if scl < 0.1:
            scl = 1.0

        return scl

    def e_tight_scale(self, row, l):
        pt = getattr(row, "%sPt" % l)
        eta = getattr(row, "%sEta" % l)
        #return H2TauCorrections.correct_e_idiso_2012(pt,abs(eta))
        return 1.

    def m_scale(self, row, l):
        pt = getattr(row, "%sPt" % l)
        eta = getattr(row, "%sEta" % l)
        global_bin = self.m_hist.FindBin(pt, eta)
        scl = self.m_hist.GetBinContent(global_bin)

        if scl < 0.1:
            scl = 1.0

        return scl

    def m_tight_scale(self, row, l):
        pt = getattr(row, "%sPt" % l)
        eta = getattr(row, "%sEta" % l)
        #return self.muPOGId(pt,eta) * self.muPOGIso(pt,eta)
        #return H2TauCorrections.correct_mu_idiso_2012(pt,eta)
        return 1.0

    def close(self):
        self.e_rtfile.Close()
        self.m_rtfile.Close()
