#!/usr/bin/env python
'''
The WZ analyzer.

Author: Devin N. Taylor, UW-Madison
'''

from AnalyzerBase import *

class AnalyzerWZ(AnalyzerBase):
    '''
    An implementation of the AnalyzerBase class for use in WZ analysis.

    Objects:
        z: 2 leptons same flavor opposite sign
        w: 1 lepton and met
    Minimization function:
        Z mass difference
    Selection:
        Trigger: double lepton triggers
        Fiducial cut
        Lepton id: tight muon, cbid medium electron + triggering MVA
        Isolation: 0.12 (0.15) for muon (electron) with deltabeta (rho) corrections
        Invariant mass > 100. GeV
        Z selection: within 20. GeV of Z mass, leading lepton pt > 20.
        W selection: met > 30. lepton pt > 20.
    '''

    def __init__(self, sample_location, out_file, period):
        self.channel = 'WZ'
        self.final_states = ['eee','eem','emm','mmm']
        self.initial_states = ['z1','w1'] # in order of leptons returned in choose_objects
        self.object_definitions = {
            'w1': ['em','n'],
            'z1': ['em','em'],
        }
        self.cutflow_labels = ['Trigger','Fiducial','ID','3l Mass','Z Selection','W Selection']
        self.alternateIds, self.alternateIdMap = self.defineAlternateIds()
        super(AnalyzerWZ, self).__init__(sample_location, out_file, period)

    ###############################
    ### Define Object selection ###
    ###############################
    def choose_objects(self, rtrow):
        '''
        Select leptons that best fit the WZ selection.
        The first two leptons are the Z and the third is the W.
        We select combinatorics by closest to zmass.
        '''
        cands = []
        for l in permutations(self.objects):
            if lep_order(l[0], l[1]):
                continue

            OS1 = getattr(rtrow, "%s_%s_SS" % (l[0], l[1])) < 0.5 # select opposite sign
            mass = getattr(rtrow, "%s_%s_Mass" % (l[0], l[1]))
            massdiff = abs(ZMASS-mass)

            if OS1 and l[0][0]==l[1][0]:
                cands.append((massdiff, list(l)))

        if not len(cands): return 0

        # Sort by mass difference
        cands.sort(key=lambda x: x[0])
        massdiff, leps = cands[0]

        return ([massdiff], leps)

    # overide good_to_store
    # will store via veto
    @staticmethod
    def good_to_store(rtrow, cand1, cand2):
        '''
        Veto on 4th lepton
        '''
        return (rtrow.eVetoMVAIsoVtx + rtrow.muVetoPt5IsoIdVtx == 0)

    def defineAlternateIds(self):
        elecIds = ['Veto', 'Loose', 'Medium', 'Tight', 'Trig', 'NonTrig', 'ZZLoose', 'ZZTight']
        muonIds = ['Loose', 'Tight', 'ZZLoose', 'ZZTight']
        elecIsos = [0.5, 0.2, 0.15]
        muonIsos = [0.4, 0.2, 0.12]
        idList = []
        idMap = {}
        for id in elecIds:
            for iso in elecIsos:
                idName = 'elec%s%0.2f' % (id, iso)
                idName = idName.replace('.','p')
                idList += [idName]
                idMap[idName] = {
                    'idDef' : {
                        'e': id
                    },
                    'isoCut' : {
                        'e': iso
                    }
                }
        for id in muonIds:
            for iso in muonIsos:
                idName = 'muon%s%0.2f' % (id, iso)
                idName = idName.replace('.','p')
                idList += [idName]
                idMap[idName] = {
                    'idDef' : {
                        'm': id
                    },
                    'isoCut' : {
                        'm': iso
                    }
                }
        return idList, idMap
                

    ###########################
    ### Define preselection ###
    ###########################
    def preselection(self,rtrow):
        cuts = CutSequence()
        cuts.add(self.trigger)
        cuts.add(self.fiducial)
        cuts.add(self.passAnyId)
        #cuts.add(self.ID_loose)
        #cuts.add(self.mass3l)
        #cuts.add(self.zSelection)
        #cuts.add(self.wSelection)
        return cuts

    def selection(self,rtrow):
        cuts = CutSequence()
        cuts.add(self.trigger)
        cuts.add(self.fiducial)
        cuts.add(self.ID_tight)
        cuts.add(self.mass3l)
        cuts.add(self.zSelection)
        cuts.add(self.wSelection)
        return cuts

    def getIdArgs(self,type):
        kwargs = {}
        if type=='Tight':
            kwargs['idDef'] = {
                'e':'Medium',
                'm':'Tight',
                't':'Medium'
            }
            kwargs['isoCut'] = {
                'e':0.15,
                'm':0.12
            }
        if type=='Loose':
            kwargs['idDef'] = {
                'e':'Loose',
                'm':'Loose',
                't':'Loose'
            }
            kwargs['isoCut'] = {
                'e':0.2,
                'm':0.2
            }
        if type=='Veto':
            kwargs['idDef'] = {
                'e':'Veto',
                'm':'Loose',
                't':'Loose'
            }
            kwargs['isoCut'] = {
                'e':0.4,
                'm':0.4
            }
        if type in self.alternateIds:
            kwargs = self.alternateIdMap[type]
        return kwargs

    def trigger(self, rtrow):
        triggers = ["mu17ele8isoPass", "mu8ele17isoPass",
                    "doubleETightPass", "doubleMuPass", "doubleMuTrkPass"]

        if self.period == '13':
            triggers = ['muEPass', 'doubleMuPass', 'doubleEPass']

        for t in triggers:
            if getattr(rtrow,t)>0:
                return True
        return False

    def fiducial(self, rtrow):
        for l in self.objects:
            if l[0]=='e':
                ptcut = 10.0
                etacut = 2.5
            if l[0]=='m':
                ptcut = 10.0
                etacut = 2.4
            if l[0]=='t':
                ptcut = 20.0
                etacut = 2.3
            if getattr(rtrow, '%sPt' % l) < ptcut:
                return False
            if getattr(rtrow, '%sAbsEta' % l) > etacut:
                return False
        return True

    def passAnyId(self,rtrow):
        '''Check to make sure the leptons pass at least 1 ID'''
        passCheck = {'e': False, 'm': False}
        for altId in self.alternateIds:
           if passCheck[altId[0]]: continue
           if self.ID(rtrow,*self.objects,**self.getIdArgs(altId)): passCheck[altId[0]] = True
        return passCheck['e'] and passCheck['m']

    def ID_veto(self, rtrow):
        return self.ID(rtrow,*self.objects,**self.getIdArgs('Veto'))

    def ID_loose(self, rtrow):
        return self.ID(rtrow,*self.objects,**self.getIdArgs('Loose'))

    def ID_tight(self, rtrow):
        return self.ID(rtrow,*self.objects,**self.getIdArgs('Tight'))

    def mass3l(self,rtrow):
        return rtrow.Mass > 100.

    def zSelection(self,rtrow):
        leps = self.objects
        if not leps: return False
        m1 = getattr(rtrow,'%s_%s_Mass' % (leps[0], leps[1])) if not lep_order(leps[0], leps[1]) else\
             getattr(rtrow,'%s_%s_Mass' % (leps[1], leps[0]))
        l0Pt = getattr(rtrow,'%sPt' %leps[0])
        return abs(m1-ZMASS)<20. and l0Pt>20.

    def wSelection(self,rtrow):
        leps = self.objects
        if not leps: return False
        if getattr(rtrow, '%sPt' %leps[2])<20.: return False
        if rtrow.pfMetEt < 30.: return False
        for l in leps[:2]:
            dr = getattr(rtrow, '%s_%s_DR' %(l,leps[2])) if not lep_order(l,leps[2]) else\
                 getattr(rtrow, '%s_%s_DR' %(leps[2],l))
            if dr < 0.1: return False
        return True

##########################
###### Command line ######
##########################
def parse_command_line(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('analyzer', type=str)
    parser.add_argument('in_sample', type=str)
    parser.add_argument('out_file', type=str)
    parser.add_argument('period', type=str)

    args = parser.parse_args(argv)
    return args


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    if args.analyzer == 'WZ': analyzer = AnalyzerWZ(args.in_sample,args.out_file,args.period)
    with analyzer as thisAnalyzer:
        thisAnalyzer.analyze()

    return 0


if __name__ == "__main__":
    status = main()
    sys.exit(status)
