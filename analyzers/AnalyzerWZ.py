#!/usr/bin/env python
'''
The WZ analyzer.
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
        self.initial_states = ['z','w'] # in order of leptons returned in choose_objects
        self.object_definitions = {
            'w': ['em','n'],
            'z': ['em','em'],
        }
        self.cutflow_labels = ['Trigger','Fiducial','Tight ID','Isolation','3l Mass','Z Selection','W Selection']
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

    ##########################
    ### Defin preselection ###
    ##########################
    def preselection(self,rtrow):
        cuts = CutSequence()
        cuts.add(self.trigger)
        cuts.add(self.fiducial)
        cuts.add(self.ID_tight)
        cuts.add(self.isolation)
        cuts.add(self.mass3l)
        cuts.add(self.zSelection)
        cuts.add(self.wSelection)
        return cuts

    def trigger(self, rtrow):
        triggers = ["mu17ele8isoPass", "mu8ele17isoPass",
                    "doubleETightPass", "tripleEPass",
                    "doubleMuPass", "doubleMuTrkPass"]

        if self.period == '13':
            triggers = ['muEPass', 'doubleMuPass',
                        'doubleEPass', 'tripleEPass']

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

    def ID_tight(self, rtrow):
        return self.ID(rtrow,'wztightnoiso',*self.objects)

    def isolation(self, rtrow):
        for l in self.objects:
            if l[0] == 'e':
                isotype = "RelPFIsoRho"
                isocut = 0.15
            if l[0] == 'm':
                isotype = "RelPFIsoDBDefault"
                isocut = 0.12
            if l[0] == 't': continue # no iso cut on tau
            if getattr(rtrow, '%s%s' %(l,isotype)) > isocut: return False

        return True

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
    parser.add_argument('in_sample', type=str)
    parser.add_argument('out_file', type=str)
    parser.add_argument('period', type=str)

    args = parser.parse_args(argv)
    return args


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    analyzer = AnalyzerWZ(args.in_sample,args.out_file,args.period)
    with analyzer as thisAnalyzer:
        thisAnalyzer.analyze()

    return 0


if __name__ == "__main__":
    status = main()
    sys.exit(status)
