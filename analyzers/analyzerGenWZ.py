#!/bin/env python
import os
import sys
from itertools import combinations
import argparse
from ntuples import *
from GenEvent import *

sys.argv.append('-b')
import ROOT
sys.argv.pop()

ZMASS = 91.1876

class Cut(object):
    def __init__(self, function, name):
        self.function = function
        self.name = name
    def evaluate(self, rtrow):
        return self.function(rtrow) 

class CutSequence(object):
    '''
    A class for defining cut orders for preselection.
    '''
    def __init__(self):
        self.cut_sequence = []

    def add(self, cut_function):
        self.cut_sequence.append(fun)

    def evaluate(self, rtrow):
        cut_history = OrderedDict()
        for cut in enumerate(self.cut_sequence):
            cut_history.extend({cut.getName() : cut.evaluate(rtrow)})
        return cut_history

    def getCuts(self):
        return self.cut_sequence()

    def addSequence(self, sequence):
        for cut in sequence.getCuts():
            self.cut_sequence.append(cut)

class CutTracker(object):
    def __init__(self, preselection, selection):
        self.preselection = preselection
        self.selection = selection 
        #self.allCuts = preselection.deep
class AnalyzerGenWZ(object):
    def __init__(self, root_file_name):
        self.root_file = rtFile = ROOT.TFile(root_file_name)
        self.event = GenEvent()
    def fiducial(self):
        keep = []
        ptCut = 10
        eEta = 2.5
        mEta = 2.4
        for lepton in self.event.getLeptons():
            etaCut = eEta if abs(lepton.getPdgID()) == 11 else mEta 
            if lepton.Pt() < ptCut:
                continue
            if lepton.Eta() > etaCut:
                continue
            keep.append(lepton)
        
        self.leptons = keep
        return len(self.leptons) > 2
    def mass3l(self): 
        print "3l Mass is %f" % self.event.get3lMass()
        return self.event.get3lMass() > 100
    def Zselection(self):
        Zcand = self.event.getZcand()
        print "Z Mass is %f" % Zcand.M()
        return abs(Zcand.M() - ZMASS) < 20 
    def Wselection(self):
        return self.event.getMET() > 30 and self.event.getWLepton().Pt() > 20
    def trigger(self):
        leptons = self.event.getLeptons()
        foundEPt12 = False
        foundMuPt8 = False

        for lepton in leptons:
            if abs(lepton.getPdgID()) == 11:
                # Double E
                if lepton.Pt() > 23 and foundEPt12:
                    return True
                # EMu
                elif lepton.Pt() > 23 and foundMuPt8:
                    return True
                elif lepton.Pt() > 12:
                    foundEPt12 = True
            elif abs(lepton.getPdgID()) == 13:
                # Double Mu
                if lepton.Pt() > 17 and foundMuPt8:
                    return True
                # EMu
                elif lepton.Pt() > 23 and foundEPt12:
                    return True
                elif lepton.Pt() > 8:
                    foundMuPt8 = True
        return False

    def store_event(self, branches):
        ntupleEntry = {}
        for i, lepton in enumerate(self.leptons):
            if i > 3:
                break
            pdgid = lepton.getPdgID()
            obj = "e" if abs(pdgid) == 11 else "m"
            ntupleEntry["l%i.Pt" % (i+1)] = lepton.Pt()
            ntupleEntry["l%i.Eta" % (i+1)] = lepton.Eta()
            ntupleEntry["l%i.Phi" % (i+1)] = lepton.Phi()
            ntupleEntry["l%i.Chg" % (i+1)] = -1 if pdgid < 0 else 1
            ntupleEntry["l%iFlv.Flv" % (i+1)] = obj  

        for key,val in ntupleEntry.iteritems():
            branch, var = key.split('.')
            setattr(branches[branch],var,val)
    def analyze(self):
        tree = self.root_file.Get("demo/Ntuple")

    #    outfile = ROOT.TFile("genWZ.root", 'recreate')
    #    final_states = ['eee','eem','emm','mmm']
    #    initial_states = ['z1','w1'] # in order of leptons returned in choose_objects
    #    object_definitions = {
    #        'w1': ['em','n'],
    #        'z1': ['em','em'],
    #    }
    #    ntuple, branches = buildNtuple(object_definitions,initial_states,'WZ',final_states)

        numEvents = tree.GetEntries()
        passed = { 'gen' : 0, 'trig' : 0, '3l' : 0 , 'Z' : 0, 'W' : 0 }
        for row in range(numEvents):
            self.event.reset()
            tree.GetEntry(row)
            for i, pdgid in enumerate(tree.pdgId):
                if abs(pdgid) in [11, 13]:
                    self.event.foundLepton(pdgid,
                        tree.pt[i],
                        tree.eta[i],
                        tree.phi[i],
                        tree.mass[i])
                if abs(pdgid) in [12, 14, 16]:
                    self.event.foundMET(tree.pt[i],
                        tree.eta[i],
                        tree.phi[i],
                        tree.mass[i])
            self.event.Print()
            if self.fiducial():
                passed['gen'] += 1
            if self.fiducial():
                passed['trig'] += 1
            else:
                continue
            if self.mass3l():
                passed['3l'] += 1
            else:
                continue
            if self.Zselection():
                passed['Z'] += 1
            else:
                continue
            if self.Wselection():
                passed['W'] += 1
            #event.store_event(branches)

        print "%i passed the fiducial cuts" % passed['gen']
        print "%i passed the trigger cuts" % passed['trig']
        print "%i passed the 3l mass cut" % passed['3l']
        print "%i passed the Z mass cut" % passed['Z']
        print "%i passed the W mass cut" % passed['W']
    #    outfile.Write()
    #    outfile.Close()

def main():
    root_file_name = 'ntuplesWZ_13tev_WZ/WZgenNtuple.root'
    analyzer = AnalyzerGenWZ(root_file_name)
    analyzer.analyze()

if __name__ == "__main__":
    status = main()
    sys.exit(status)
