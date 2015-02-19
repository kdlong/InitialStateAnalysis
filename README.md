InitialStateAnalysis
======================

The Initial State Analysis (ISA) framework uses ntuples produced with the 
<a href="https://github.com/uwcms/FinalStateAnalysis">FinalStateAnalysis</a> framework.
This framework constructs user defined initial states from final state objects and stores
interesting variables in an output ntuple for further selection.

Installation
------------

ISA can run independent of CMSSW and only requires python 2.7 (or argparse with python 2.6)
and ROOT. The setup script is unecessary at the moment. To run limits you must create a 
`CMSSW_7_1_5` release. Note: lepton scale factors do have some dependence on FSA. These are
currently disabled.

Analyzing data
--------------
The primary analyzer is accessed via the [run.py](run.py) command. This command has paths to ntuples stored
for convenient access. For example, to run the TT channel of the WZ analysis over all MC samples:

```
# Usage: ./run.py [analysis] [channel] [period] samples (unix wildcards allowed)
./run.py WZ TT 13 W* T* DY* Z*
```

One can also run the analyzer directly via:

```
./analyzers/AnalyzerWZ.py /path/to/sample/directory/ output.root 13
```

Jobs can be submitted to the cluster using the `--submit` option:

```
./run.py --submit --jobName=testSubmit Hpp3l Hpp3l 13 D* T* W* Z* 
```

Plotting
--------

Plotting can be accomplished via the [mkplots.py](mkplots.py) command:

```
# Usage: ./mkplots.py [analysis] [channel] [period] [options]
./mkplots.py Hpp3l Hpp3l 13
```

Limits
------

Limits can be run via [mklimits.py](mklimits.py). This produces datacards able to be read by the 
`HiggsAnalysis/CombinedLimit` module. Documentation and how to setup a release can be found 
<a href="https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideHiggsAnalysisCombinedLimit#For_end_users_that_don_t_need_to">here</a>. 
This requires a `CMSSW_7_1_5` release (or greater in 71X, not 70X or 72X).

The [mklimits.py](mklimits.py) script can produce limits using three different methods: a purely MC driven
method that estimates background from MC samples (default), a data-driven method with a user defined
sideband and signal region, and a fakerate method (requires the fakerate option on the ntuple production, TODO).

```
# Usage: ./mklimits [analysis] [period] [options]
./mklimits.py Hpp4l 13
```

The datacards can then be processed with the [processdatacards.py](processdatacards.py) script:

```
TODO
```

And finally, the limits can be plotted with [plotlimits.py](plotlimits.py):

```
TODO
```
