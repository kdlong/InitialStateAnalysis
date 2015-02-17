'''
Lepton ID's available in ISA

Author: Devin N. Taylor, UW-Madison
'''

import sys

sys.argv.append('b')
import ROOT as rt
sys.argv.pop()


def lep_id(rtrow, period, *lep, **kwargs):
    control = kwargs.get('control', False)
    tight = kwargs.get('tight', False)
    wzloose = kwargs.get('wzloose', False)
    wzloosenoiso = kwargs.get('wzloosenoiso', False)
    wztight = kwargs.get('wztight', False)
    wztightnoiso = kwargs.get('wztightnoiso', False)
    cbid = kwargs.get('cbid','')
    mva = kwargs.get('mva','')

    if cbid or mva:
        for l in lep:
            if l[0]=='e':
                if not elec_id_cbid_mva(rtrow,l,period,cbid,mva): return False
            if l[0]=='m':
                if not muon_id_tight(rtrow,l,period): return False
            if l[0]=='t':
                if not tau_id(rtrow,l,period): return False
        return True
            

    if tight:
        elec_method = 'elec_id_tight'
        muon_method = 'muon_id_tight'
        tau_method  = 'tau_id'
    elif wzloose:
        elec_method = 'elec_WZ_loose'
        muon_method = 'muon_WZ_loose'
        tau_method  = 'tau_id_loose'
    elif wzloosenoiso:
        elec_method = 'elec_WZ_loose'
        muon_method = 'muon_WZ_loose_noiso'
        tau_method  = 'tau_id_loose'
    elif wztight:
        elec_method = 'elec_WZ_tight'
        muon_method = 'muon_WZ_tight'
        tau_method  = 'tau_id'
    elif wztightnoiso:
        elec_method = 'elec_WZ_tight_noiso'
        muon_method = 'muon_WZ_tight_noiso'
        tau_method  = 'tau_id'
    else:
        elec_method = 'elec_id'
        muon_method = 'muon_id'
        tau_method  = 'tau_id'

    for l in lep:
        if l[0]=='e': method = elec_method
        if l[0]=='m': method = muon_method
        if l[0]=='t': method = tau_method
        if not eval('%s(rtrow,l,period)'%method): return False

    return True

def elec_id_cbid_mva(rtrow,l,period,cbid,mva):
    if mva=='NonTrig':
        if not _elec_mva_nontriggering(rtrow, l, period): return False
    if mva=='Trig':
        if not _elec_mva_triggering(rtrow, l, period): return False
    if cbid=='Veto':
        if not getattr(rtrow, '%sCBIDVeto' % l): return False
    if cbid=='Loose':
        if not getattr(rtrow, '%sCBIDLoose' % l): return False
    if cbid=='Medium':
        if not getattr(rtrow, '%sCBIDMedium' % l): return False
    if cbid=='Tight':
        if not getattr(rtrow, '%sCBIDTight' % l): return False
    return True

def tau_id(rtrow, l, period):
    antiElec = getattr(rtrow, "%sAntiElectronTight" % l)
    antiMuon = getattr(rtrow, "%sAntiMuon3Tight" % l)
    id3Hits  = getattr(rtrow, "%sTightIso3Hits" %l)
    return all([antiElec, antiMuon, id3Hits])

def tau_id_loose(rtrow, l, period):
    antiElec = getattr(rtrow, "%sAntiElectronLoose" % l)
    antiMuon = getattr(rtrow, "%sAntiMuon3Loose" % l)
    id3Hits  = getattr(rtrow, "%sLooseIso3Hits" %l)
    return all([antiElec, antiMuon, id3Hits])

def muon_id(rtrow, l, period):
    dz = abs(getattr(rtrow, "%sPVDZ" % l)) < 1.0
    dxy = abs(getattr(rtrow, "%sPVDXY" % l)) < 0.5

    ip3d = "%sIP3DSig" %l if period == "13" else "%sIP3DS" %l

    sip = getattr(rtrow, ip3d) < 4.0

    mu_type = getattr(rtrow, "%sIsTracker" % l) or getattr(rtrow, "%sIsGlobal" % l)

    return all([dz, dxy, sip, mu_type])

def muon_id_tight(rtrow, l, period):
    return getattr(rtrow, '%sPFIDTight' %l)

def elec_id(rtrow, l, period):
    dz = abs(getattr(rtrow, "%sPVDZ" % l)) < 1.0
    dxy = abs(getattr(rtrow, "%sPVDXY" % l)) < 0.5

    ip3d = "%sIP3DSig" %l if period == "13" else "%sIP3DS" %l

    sip = getattr(rtrow, ip3d) < 4.0

    nhit = getattr(rtrow, "%sMissingHits" % l) <= 1

    mva = _elec_mva_nontriggering(rtrow, l, period)
    #cbid = getattr(rtrow, "%sCBIDLoose_25ns" %l) > 0.5

    return all([dz, dxy, sip, nhit, mva])

def elec_id_tight(rtrow, l, period):
    dz = abs(getattr(rtrow, "%sPVDZ" % l)) < 0.1
    dxy = abs(getattr(rtrow, "%sPVDXY" % l)) < 0.02

    mva = _elec_mva_triggering(rtrow, l, period)

    nhit = getattr(rtrow, "%sMissingHits" % l) == 0

    convVeto = not getattr(rtrow, "%sHasConversion" % l)

    return all([dz, dxy, nhit, convVeto, mva])

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

def elec_WZ_loose(rtrow, l, period):
    pt = getattr(rtrow, "%sPt" % l)
    eta = abs(getattr(rtrow, "%sEta" % l))
    sceta = abs(getattr(rtrow, "%sSCEta" % l))
    sieie = getattr(rtrow, "%sSigmaIEtaIEta" % l)
    dphi = getattr(rtrow, "%sdeltaPhiSuperClusterTrackAtVtx" %l)
    deta = getattr(rtrow, "%sdeltaEtaSuperClusterTrackAtVtx" %l)
    hoe = getattr(rtrow, "%sHadronicOverEM" %l)
    eiso = getattr(rtrow, "%sEcalIsoDR03" %l)
    hiso = getattr(rtrow, "%sHcalIsoDR03" %l)
    tiso = getattr(rtrow, "%sTrkIsoDR03" %l)
    conv = getattr(rtrow, "%sHasConversion" %l)
    misshits = getattr(rtrow, "%sMissingHits" %l)

    passid = True
    if pt < 10: passid = False
    if eta > 2.5: passid = False
    if sceta < 1.479:
        if sieie > 0.01: passid = False # 0.01 for WZ
        if dphi > 0.15: passid = False
        if deta > 0.007: passid = False
        if hoe > 0.12: passid = False # 0.12 for WZ
        if max(eiso-1,0)/pt > 0.2: passid = False
    if sceta >= 1.479:
        if sieie > 0.03: passid = False # 0.03 for WZ
        if dphi > 0.1: passid = False
        if deta > 0.009: passid = False
        if hoe > 0.1: passid = False
        if eiso/pt > 0.2: passid = False
    if tiso/pt > 0.2: passid = False
    if hiso/pt > 0.2: passid = False
    #if eiso/pt > 0.2: passid = False # differnt for WZ
    if conv: passid = False
    if misshits: passid = False

    return passid

def elec_WZ_tight_noiso(rtrow, l, period):
    d0 = getattr(rtrow, "%sPVDXY" %l)
    dz = getattr(rtrow, "%sPVDZ" %l)
    mva = _elec_mva_triggering(rtrow, l, period)

    if period=='13':
        cbid = getattr(rtrow, '%sCBIDTight' % l)
        return cbid and d0<0.02 and dz<0.1 and mva

    wzloose = elec_WZ_loose(rtrow, l, period)

    return d0 < 0.02 and dz < 0.1 and wzloose and mva

def elec_WZ_tight(rtrow, l, period):
    wztightNoIso = elec_WZ_tight_noiso(rtrow, l, period)
    reliso = getattr(rtrow, "%sRelPFIsoRho" %l)

    return reliso < 0.15 and wztightNoIso 

def muon_WZ_loose_noiso(rtrow, l, period):
    pt = getattr(rtrow, "%sPt" % l)
    eta = abs(getattr(rtrow, "%sEta" % l))
    d0 = getattr(rtrow, "%sPVDXY" %l)
    dz = getattr(rtrow, "%sPVDZ" %l)
    tightid = getattr(rtrow, '%sPFIDTight' %l)

    passid = True
    if pt < 10: passid = False
    if eta > 2.4: passid = False
    #if d0 > 0.2: passid = False
    #if dz > 0.1: passid = False
    if not tightid: passid = False

    return passid


def muon_WZ_loose(rtrow, l, period):
    looseNoIso = muon_WZ_loose_noiso(rtrow,l,period)
    reliso = getattr(rtrow, "%sRelPFIsoDBDefault" %l)

    passid = looseNoIso
    if reliso > 0.2: passid = False
    
    return passid

def muon_WZ_tight_noiso(rtrow, l, period):
    looseid = muon_WZ_loose_noiso(rtrow, l, period)
    d0 = getattr(rtrow, "%sPVDXY" %l)
    pt = getattr(rtrow, "%sPt" % l)
    eta = abs(getattr(rtrow, "%sEta" % l))

    passid = looseid
    #if pt<20 and d0>0.01: passid = False
    #if pt>=20 and d0>0.02: passid = False

    return passid

def muon_WZ_tight(rtrow, l, period):
    tightNoIso = muon_WZ_tight_noiso(rtrow, l, period)
    reliso = getattr(rtrow, "%sRelPFIsoDBDefault" %l)

    passid = tightNoIso
    if reliso > 0.12: passid = False

    return passid
