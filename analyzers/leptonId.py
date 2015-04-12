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
    if idType=='ZZLoose':
        if not _elec_zz_loose(rtrow,l,period): return False
    if idType=='ZZTight':
        if not _elec_zz_tight(rtrow,l,period): return False
    return True

def muon_id(rtrow, l, period, idType):
    if idType=='Tight':
        if not getattr(rtrow,'%sPFIDTight'%l): return False
    if idType=='Loose':
        if not getattr(rtrow,'%sPFIDLoose'%l): return False
    if idType=='ZZLoose':
        if not _muon_zz_loose(rtrow,l,period): return False
    if idType=='ZZTight':
        if not _muon_zz_tight(rtrow,l,period): return False
    return True

def tau_id(rtrow, l, period, idType):
    if not getattr(rtrow, "%sDecayModeFinding" %l): return False  # really should be old DM, but not available in PHYS14 right now, all miniAOD pass
    if not getattr(rtrow, "%sAgainstElectronMediumMVA5" % l): return False
    if not getattr(rtrow, "%sAgainstMuonTight3" % l): return False
    if idType=='Loose':
        if not getattr(rtrow, "%sByLooseCombinedIsolationDeltaBetaCorr3Hits" %l): return False
    if idType=='Medium':
        if not getattr(rtrow, "%sByMediumCombinedIsolationDeltaBetaCorr3Hits" %l): return False
    if idType=='Tight':
        if not getattr(rtrow, "%sByTightCombinedIsolationDeltaBetaCorr3Hits" %l):return False
    return True



def _muon_zz_loose(rtrow, l, period):
    if getattr(rtrow, "%sPt" % l) < 5: return False
    if abs(getattr(rtrow, "%sEta" % l)) > 2.4: return False
    if abs(getattr(rtrow, '%sPVDZ' % l)) > 1.: return False
    if abs(getattr(rtrow, '%sPVDXY' % l)) > 0.5:return False
    isGlobal = getattr(rtrow, '%sIsGlobal' % l)
    isTracker = getattr(rtrow, '%sIsTracker' % l)
    matchedStations = getattr(rtrow, '%sMatchedStations' % l)
    return isGlobal or isTracker or matchedStations>0

def _muon_zz_tight(rtrow, l, period):
    if not _muon_zz_loose(rtrow,l,period): return False
    return getattr(rtrow,'%sIsPFMuon' %l)

def _elec_zz_loose(rtrow, l, period):
    if getattr(rtrow, "%sPt" % l) < 7: return False
    if abs(getattr(rtrow, "%sEta" % l)) > 2.5: return False
    if abs(getattr(rtrow, '%sPVDZ' % l)) > 1.: return False
    if abs(getattr(rtrow, '%sPVDXY' % l)) > 0.5:return False
    if getattr(rtrow,'%sMissingHits'%l) > 1: return False
    return True

def _elec_zz_tight(rtrow, l, period):
    if not _elec_zz_loose(rtrow,l,period): return False
    return _elec_mva_nontriggering_zz(rtrow,l,period)

def _elec_mva_nontriggering_zz(rtrow, l, period):
    pt = getattr(rtrow, "%sPt" % l)
    eta = abs(getattr(rtrow, "%sSCEta" % l))
    mva = getattr(rtrow, "%sMVANonTrigID" % l)

    if 5.0 < pt < 10.0:
        return (eta < 0.8 and mva > -0.202) or (0.8 < eta < 1.479 and mva > -0.444) or (1.479 < eta and mva > 0.264)
    elif 10.0 < pt:
        return (eta < 0.8 and mva > -0.110) or (0.8 < eta < 1.479 and mva > -0.284) or (1.479 < eta and mva > -0.212)
    else:
        return False

def _elec_mva_nontriggering(rtrow, l, period):
    pt = getattr(rtrow, "%sPt" % l)
    eta = abs(getattr(rtrow, "%sSCEta" % l))
    mva = getattr(rtrow, "%sMVANonTrigID" % l)

    if 5.0 < pt < 10.0:
        return (eta < 0.8 and mva > 0.47) or (0.8 < eta < 1.479 and mva > 0.004) or (1.479 < eta and mva > 0.295)

    elif 10.0 < pt:
        return (eta < 0.8 and mva > -0.34) or (0.8 < eta < 1.479 and mva > -0.65) or (1.479 < eta and mva > 0.6)

    else:
        return False

def _elec_mva_triggering(rtrow, l, period):
    pt = getattr(rtrow, "%sPt" % l)
    eta = abs(getattr(rtrow, "%sSCEta" % l))
    mva = getattr(rtrow, "%sMVATrigID" % l)

    if 10.0 < pt < 20.0:
        return (eta < 0.8 and mva > 0.00) or (0.8 < eta < 1.479 and mva > 0.10) or (1.479 < eta and mva > 0.62)

    elif 20.0 < pt:
        return (eta < 0.8 and mva > 0.94) or (0.8 < eta < 1.479 and mva > 0.85) or (1.479 < eta and mva > 0.92)

    else:
        return False
