'''
Lepton ID's available in ISA

Author: Devin N. Taylor, UW-Madison
'''

import sys

sys.argv.append('b')
import ROOT as rt
sys.argv.pop()


def lep_id(rtrow, period, *lep, **kwargs):
    idType = kwargs.get('idType','')

    if idType:
        for l in lep:
            if l[0]=='e': lep_method = 'elec_id'
            if l[0]=='m': lep_method = 'muon_id'
            if l[0]=='t': lep_method = 'tau_id'
            if not eval('%s(rtrow,l,period,idType)'%lep_method): return False
        
    return True

def elec_id(rtrow, l, period, idType):
    if idType=='NonTrig':
        if not _elec_mva_nontriggering(rtrow, l, period): return False
    if idType=='Trig':
        if not _elec_mva_triggering(rtrow, l, period): return False
    if idType=='Veto':
        if not getattr(rtrow, '%sCBIDVeto' % l): return False
    if idType=='Loose':
        if not getattr(rtrow, '%sCBIDLoose' % l): return False
    if idType=='Medium':
        if not getattr(rtrow, '%sCBIDMedium' % l): return False
    if idType=='Tight':
        if not getattr(rtrow, '%sCBIDTight' % l): return False
    return True

def muon_id(rtrow, l, period, idType):
    if idType=='Tight':
        if not getattr(rtrow,'%sPFIDTight'%l): return False
    if idType=='Loose':
        if not getattr(rtrow,'%sPFIDLoose'%l): return False
    return True

# TODO, define Tight and Loose IDs
def tau_id(rtrow, l, period, idType):
    antiElec = getattr(rtrow, "%sAntiElectronTight" % l)
    antiMuon = getattr(rtrow, "%sAntiMuon3Tight" % l)
    id3Hits  = getattr(rtrow, "%sVTightIsoMVA3NewDMLT" %l)
    decayFind = getattr(rtrow, "%sDecayFinding" %l)
    return all([antiElec, antiMuon, id3Hits, decayFind])


def _elec_mva_nontriggering(rtrow, l, period):
    pt = getattr(rtrow, "%sPt" % l)
    eta = abs(getattr(rtrow, "%sSCEta" % l))
    mvastr = "%sMVANonTrigID" %l if period == '13' else "%sMVANonTrig" %l
    mva = getattr(rtrow, mvastr)

    if 5.0 < pt < 10.0:
        return (eta < 0.8 and mva > 0.47) or (0.8 < eta < 1.479 and mva > 0.004) or (1.479 < eta and mva > 0.295)

    elif 10.0 < pt:
        return (eta < 0.8 and mva > -0.34) or (0.8 < eta < 1.479 and mva > -0.65) or (1.479 < eta and mva > 0.6)

    else:
        return False

def _elec_mva_triggering(rtrow, l, period):
    pt = getattr(rtrow, "%sPt" % l)
    eta = abs(getattr(rtrow, "%sSCEta" % l))
    mvastr = "%sMVATrigID" %l if period == '13' else "%sMVATrig" %l
    mva = getattr(rtrow, mvastr)

    if 10.0 < pt < 20.0:
        return (eta < 0.8 and mva > 0.00) or (0.8 < eta < 1.479 and mva > 0.10) or (1.479 < eta and mva > 0.62)

    elif 20.0 < pt:
        return (eta < 0.8 and mva > 0.94) or (0.8 < eta < 1.479 and mva > 0.85) or (1.479 < eta and mva > 0.92)

    else:
        return False
