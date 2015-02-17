InitialStateAnalysis
======================

The Initial State Analysis (ISA) framework uses ntuples produced with the 
<a href="https://github.com/uwcms/FinalStateAnalysis">FinalStateAnalysis</a> framework.
This framework constructs user defined initial states from final state objects and stores
interesting variables in an output ntuple for further selection.

Installation
------------

Setup FSA in a recent CMSSW release (being certain to install python modules in recipe).
The FSA dependency is for convenience. The python dependencies can also be isntalled via
[recipe/setup.sh](recipe/setup.sh).

```
cd recipe
./setup.sh
```

However, the lepton scalefactors from 2012 data are currently only in FSA, so the relevant parts
of [analyzers/AnalyzerBase.py](analyzers/AnalyzerBase.py) must be commented out for CMSSW independent
running.

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

Limits can be run via [mklimits.py](mklimits.py). This requires a CMSSW_6_1_1 release.

```
TODO
```
