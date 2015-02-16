import ROOT as rt
from array import array

def buildNtuple(object_definitions,channelName):
    '''
    A function to build an initial state ntuple for AnalyzerBase.py
    '''

    finalStateObjects = 'emtjgn'
    structureDict = {}
    structOrder = []

    # define common root classes
    rt.gROOT.ProcessLine(
    "struct structEvent_t {\
       Int_t   evt;\
       Int_t   run;\
       Int_t   lumi;\
       Int_t   nvtx;\
       Float_t lep_scale;\
       Float_t pu_weight;\
    };");
    eventStruct = rt.structEvent_t()
    structureDict['event'] = [eventStruct, eventStruct,'evt/I:run:lumi:nvtx:lep_scale/F:pu_weight']
    structOrder += ['event']

    rt.gROOT.ProcessLine(
    "struct structChannel_t {\
       Char_t  channel[9];\
    };");
    channelStruct = rt.structChannel_t()
    structureDict['channel'] = [channelStruct, rt.AddressOf(channelStruct,'channel'),'channel/C']
    structOrder += ['channel']

    rt.gROOT.ProcessLine(
    "struct structFinalState_t {\
       Float_t mass;\
       Float_t sT;\
       Float_t met;\
       Float_t metPhi;\
       Int_t   jetVeto20;\
       Int_t   jetVeto30;\
       Int_t   jetVeto40;\
       Int_t   bjetVeto20;\
       Int_t   bjetVeto30;\
       Int_t   muonVeto5;\
       Int_t   muonVeto10Loose;\
       Int_t   muonVeto15;\
       Int_t   elecVeto10;\
    };");
    finalStateStruct = rt.structFinalState_t()
    structureDict['finalstate'] = [finalStateStruct, finalStateStruct,'mass/F:sT:met:metPhi:jetVeto20/I:jetVeto30:jetVeto40:bjetVeto20:bjetVeto30:muonVeto5:muonVeto10Loose:muonVeto15:elecVeto10']
    structOrder += ['finalstate']

    rt.gROOT.ProcessLine(
    "struct structObject_t {\
       Float_t Pt;\
       Float_t Eta;\
       Float_t Phi;\
       Float_t Iso;\
       Int_t   Chg;\
    };");
    rt.gROOT.ProcessLine(
    "struct structObjChar_t {\
       Char_t  Flv[2];\
    };");
    lepCount = 0
    jetCount = 0
    phoCount = 0
    for key,val in object_definitions.iteritems():
        for obj in val:
            if obj=='n': continue
            else:
                objStruct = rt.structObject_t()
                flvStruct = rt.structObjChar_t()
                if obj in 'emt': 
                    charName = 'l'
                    lepCount += 1
                    objCount = lepCount
                if obj == 'j':
                    charName = 'j'
                    jetCount += 1
                    objCount = jetCount
                if obj == 'g':
                    charName = 'g'
                    phoCount += 1
                    objCount = phoCount
                structureDict['%s%i' % (charName, objCount)] = [objStruct, objStruct, 'Pt/F:Eta:Phi:Iso:Chg/I']
                structureDict['%s%iFlv' % (charName, objCount)] = [flvStruct, rt.AddressOf(flvStruct,'Flv'),'Flv/C']
                structOrder += ['%s%i' % (charName, objCount)]
                structOrder += ['%s%iFlv' % (charName, objCount)]

    # define objects for each initial state
    for key,val in object_definitions.iteritems():
        strForBranch = ""
        strToProcess = "struct struct%s_t {" % key.upper()
        strForBranch += "mass/F:sT:dPhi:"
        strToProcess += "\
            Float_t mass;\
            Float_t sT;\
            Float_t dPhi;"
        objCount = 0
        for obj in val:
            if obj == 'n':
                strForBranch += "met:metPhi:"
                strToProcess += "\
                    Float_t met;\
                    Float_t metPhi;"
            else:
                objCount += 1
                strForBranch += "Pt%i:Eta%i:Phi%i:" % (objCount, objCount, objCount)
                strToProcess += "\
                    Float_t Pt%i;\
                    Float_t Eta%i;\
                    Float_t Phi%i;" % (objCount, objCount, objCount)
        objCount = 0
        for obj in val:
            if obj == 'n': continue
            else:
                objCount += 1
                strForBranch += "Chg%i/I:" % objCount if objCount == 1 else "Chg%i:" % objCount
                strToProcess += "\
                    Int_t   Chg%i;" % objCount
        strForBranch = strForBranch[:-1] # remove trailing :
        strToProcess += "\
            };"
        rt.gROOT.ProcessLine(strToProcess)
        initialStruct = getattr(rt,"struct%s_t" % key.upper())()
        structureDict[key] = [initialStruct, initialStruct, strForBranch]
        structOrder += [key]

    rt.gROOT.ProcessLine(
    "struct structInitialChar_t {\
       Char_t  Flv[3];\
    };");
    for key in object_definitions:
        initialFlvStruct = rt.structInitialChar_t()
        structureDict['%sFlv' % key] = [initialFlvStruct,rt.AddressOf(initialFlvStruct,'Flv'),'Flv/C']
        structOrder += ['%sFlv' % key]

    # now create the tree
    tree = rt.TTree(channelName,channelName)
    allBranches = {}
    for key in structOrder:
        val = structureDict[key]
        tree.Branch(key,val[1],val[2])
        allBranches[key] = val[0]

    return (tree, allBranches)

    

