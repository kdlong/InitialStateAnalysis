#!/usr/bin/env python
import ROOT

ZMASS = 91.1876

def fillPlot(plot,passCut,mass,cut):
    sigPass = 1
    sigTotal = 1
    bgPass = 1
    bgTotal = 1
    p = sigPass/sigTotal
    f = bgPass/bgTotal
    plot.SetBinContent(mass,cut,p/f)

def optimizeSelections(analysis):
    nl = 3 if analysis=='Hpp3l' else 4

    hNumTaus = range(3)
    
    masses = [500]
    
    myCut = 'select.passTight'
    
    hmassWindow = range(100)
    zmassWindow = range(100)
    dPhiCut = [x*3.14159/20. for x in range(20)]
    metCut = range(60)
    stCut = [x*10 for x in range(150)]
    
    tauFlavor = {
        0: ['ee','em','mm'],
        1: ['et','mt'],
        2: ['tt']
    }
    
    plots = {}
    
    for nTaus in hNumTaus:
        h1Select = '('+'&&'.join(['h1Flv==%s' %x for x in tauFlavor[nTaus]]) + ')'
        h2Select = '('+'&&'.join(['h2Flv==%s' %x for x in tauFlavor[nTaus]]) + ')'
        for mass in masses:
            # optimize hmass window
            plots['h1mass_%i'%nTaus] = ROOT.TH2F('h1mass_%i'%nTaus,'h1mass_%i; H^{#pm#pm} Mass Hypothesis (GeV/c^{2}); |m(l^{#pm}l^{#pm})-Mass hypothesis|< (GeV/c^{2})'%nTaus,40,175,1025,100,0,100)
            for cut in hmassWindow:
                passCut = '%s&&fabs(h1.mass-%f)<%f&&%s' % (myCut, mass, cut, h1Select)
                fillPlot(plots['h1mass_%i'%nTaus],passCut,mass,cut)
            if nl==4:
                plots['h2mass_%i'%nTaus] = ROOT.TH2F('h2mass_%i'%nTaus,'h2mass_%i; H^{#pm#pm} Mass Hypothesis (GeV/c^{2}); |m(l^{#pm}l^{#pm})-Mass hypothesis|<  (GeV/c^{2})'%nTaus,40,175,1025,100,0,100)
                for cut in hmassWindow:
                    passCut = '%s&&fabs(h2.mass-%f)<%f&&%s' % (myCut, mass, cut, h2Select)
                    fillPlot(plots['h2mass_%i'%nTaus],passCut,mass,cut)
            # optimize zmass veto
            plots['z1mass_%i'%nTaus] = ROOT.TH2F('z1mass_%i'%nTaus,'z1mass_%i; H^{#pm#pm} Mass Hypothesis (GeV/c^{2}); |m(l^{#pm}l^{#mp})-m_{Z}|>  (GeV/c^{2})'%nTaus,40,175,1025,100,0,100)
            for cut in zmassWindow:
                passCut = '%s&&fabs(z1.mass-%f)>%f&&%s' % (myCut, ZMASS, cut, h1Select)
                if nl==4: passCut += '&&' + h2Select
                fillPlot(plots['z1mass_%i'%nTaus],passCut,mass,cut)
            if nl==4:
                plots['z2mass_%i'%nTaus] = ROOT.TH2F('z2mass_%i'%nTaus,'z2mass_%i; H^{#pm#pm} Mass Hypothesis (GeV/c^{2}); |m(l^{#pm}l^{#mp})-m_{Z}|>  (GeV/c^{2})'%nTaus,40,175,1025,100,0,100)
                for cut in zmassWindow:
                    passCut = '%s&&fabs(z2.mass-%f)>%f&&%s&&%s' % (myCut, ZMASS, cut, h1Select, h2Select)
                    fillPlot(plots['z2mass_%i'%nTaus],passCut,mass,cut)
            # optimize dPhi selection
            plots['dPhi1_%i'%nTaus] = ROOT.TH2F('dPhi1_%i'%nTaus,'dPhi1_%i; H^{#pm#pm} Mass Hypothesis (GeV/c^{2}); |#Delta#phi(l^{#pm}l^{#pm})|<'%nTaus,40,175,1025,20,0,3.14159)
            for cut in dPhiCut:
                passCut = '%s&&fabs(h1.dPhi)<%f&&%s' % (myCut, cut, h1Select)
                if nl==4: passCut += '&&' + h2Select
                fillPlot(plots['dPhi1_%i'%nTaus],passCut,mass,cut)
            if nl==4:
                plots['dPhi2_%i'%nTaus] = ROOT.TH2F('dPhi2_%i'%nTaus,'dPhi2_%i; H^{#pm#pm} Mass Hypothesis (GeV/c^{2}); |#Delta#phi(l^{#pm}l^{#pm})|<'%nTaus,40,175,1025,20,0,3.14159)
                for cut in dPhiCut:
                     passCut = '%s&&fabs(h2.dPhi)<%f&&%s&&%s' % (myCut, cut, h1Select, h2Select)
                     fillPlot(plots['dPhi2_%i'%nTaus],passCut,mass,cut)
            # optimize met selection
            plots['met_%i'%nTaus] = ROOT.TH2F('met_%i'%nTaus,'met_%i; H^{#pm#pm} Mass Hypothesis (GeV/c^{2}); E_{T}^{miss}> (GeV/c^{2})'%nTaus,40,175,1025,60,0,60)
            for cut in metCut:
                passCut = '%s&&finalstate.met>%f&&%s' % (myCut, cut, h1Select)
                if nl==4: passCut += '&&' + h2Select
                fillPlot(plots['met_%i'%nTaus],passCut,mass,cut)
            # optimize st cut
            plots['st_%i'%nTaus] = ROOT.TH2F('st_%i'%nTaus,'st_%i; H^{#pm#pm} Mass Hypothesis (GeV/c^{2}); s_{T}> (GeV/c^{2})'%nTaus,40,175,1025,150,0,1500)
            for cut in stCut:
                passCut = '%s&&finalstate.sT>%f&&%s' % (myCut, cut, h1Select)
                if nl==4: passCut += '&&' + h2Select
                fillPlot(plots['st_%i'%nTaus],passCut,mass,cut)

    canvas = ROOT.TCanvas('cMoneyPlot','cMoneyPlot',50,50,800,600)
    canvas.SetFillColor(0)
    canvas.SetBorderMode(0)
    canvas.SetFrameFillStyle(0)
    canvas.SetFrameBorderMode(0)
    canvas.SetLeftMargin(0.12)
    canvas.SetRightMargin(0.04)
    canvas.SetTopMargin(0.08)
    canvas.SetBottomMargin(0.12)

    for keys in plots:
        savedir = 'plots/%s_optimization_13TeV/png' % analysis
        savename = '%s/%s_%s.png' % (savedir, analysis, keys)
        

optimizeSelections('Hpp3l')
optimizeSelections('Hpp4l')
