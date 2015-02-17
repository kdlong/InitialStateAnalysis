#!/usr/bin/env python
'''
The doubly charged higgs associated production analyzer.

Author: Devin N. Taylor, UW-Madison
'''

from AnalyzerBase import *

class AnalyzerHpp4l(AnalyzerBase):
    '''
    The primary analyzer for the doubly charged higgs associated production channel.

    Objects:
        two doubly charged higgs
        h1: H++ = 2 same sign leptons (not necessarily same flavor)
        h2: H-- = "
    Minimization function:
        abs(Mass(++)-Mass(--))
    Selection:
        Trigger: double lepton
        Fiducial
        Trig threshold
        ID: muon tight, cbid tight mva trig
        Isolation: 0.15 (0.12) elec (muon)
        QCD suppression: M(ll) > 12
    '''

    def __init__(self, sample_location, out_file, period, **kwargs):
        runTau = kwargs.pop('runTau',False)
        self.channel = 'Hpp4l'
        self.final_states = ['eeee','eeem','eemm','emmm','mmmm'] # no tau
        if runTau: self.final_states = ['eeee','eeem','eeet','eemm','eemt','eett','emmm','emmt','emtt','ettt',\
                                        'mmmm','mmmt','mmtt','mttt','tttt']
        self.initial_states = ['h1','h2']
        self.object_definitions = {
            'h1': ['em','em'],
            'h2': ['em','em'],
        }
        if runTau:
            self.object_definitions['h1'] = ['emt', 'emt']
            self.object_definitions['h2'] = ['emt', 'emt']
        self.cutflow_labels = ['Trigger','Fiducial','Trigger Threshold','ID','Isolation','QCD Suppression']
        super(AnalyzerHpp4l, self).__init__(sample_location, out_file, period)

    ###############################
    ### Define Object selection ###
    ###############################
    def choose_objects(self, rtrow):
        '''
        Select candidate objects
        '''
        cands = []
        for l in permutations(self.objects):
            if lep_order(l[0], l[1]) or lep_order(l[2], l[3]):
                continue

            SS1 = getattr(rtrow, "%s_%s_SS" % (l[0], l[1])) > 0 # select same sign
            mass1 = getattr(rtrow, "%s_%s_Mass" % (l[0], l[1])) # select mass
            SS2 = getattr(rtrow, "%s_%s_SS" % (l[2], l[3])) > 0 # select same sign
            mass2 = getattr(rtrow, "%s_%s_Mass" % (l[2], l[3])) # select mass
            OS = getattr(rtrow, "%sCharge" % l[0]) != getattr(rtrow, "%sCharge" % l[2]) # select opposite sign
            massdiff = abs(mass1-mass2)

            if SS1 and SS2 and OS:
                cands.append([massdiff,list(l)]) # minimization is by mass diff

        if not len(cands): return 0

        cands.sort(key=lambda x: x[0])
        massdiff, leps = cands[0]

        return ([massdiff], leps)

    ###########################
    ### Define preselection ###
    ###########################
    def preselection(self,rtrow):
        cuts = CutSequence()
        cuts.add(self.trigger)
        cuts.add(self.fiducial)
        cuts.add(self.trigger_threshold)
        cuts.add(self.ID_tight_noiso)
        cuts.add(self.isolation)
        cuts.add(self.qcd_rejection)
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

    def ID_tight_noiso(self, rtrow):
        return self.ID(rtrow,cbid='Tight',mva='Trig',*self.objects)

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

    def trigger_threshold(self, rtrow):
        pts = [getattr(rtrow, "%sPt" % l) for l in self.objects]
        pts.sort(reverse=True)
        return pts[0] > 20.0 and pts[1] > 10.0

    def qcd_rejection(self, rtrow):
        qcd_pass = [getattr(rtrow, "%s_%s_Mass" % (l[0], l[1])) > 12.0
                    for l in combinations(self.objects, 2)]
        return all(qcd_pass)

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

    analyzer = AnalyzerHpp3l(args.in_sample,args.out_file,args.period)
    with analyzer as thisAnalyzer:
        thisAnalyzer.analyze()

    return 0


if __name__ == "__main__":
    status = main()
    sys.exit(status)
