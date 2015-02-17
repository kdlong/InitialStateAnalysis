InitialStateAnalysis Analyzers
==============================

Running analyzers
-----------------

Analyzers can be run from the [run.py](../run.py) script. Alternatively one can run over a single analyzer
here:

```
./AnalyzerWZ.py /path/to/sample/directory/ output.root 13
```

Creating new analyzers
----------------------

New analyzers should be created from the [AnalyzerTemplate.py](AnalyzerTemplate.py):

```
cp AnalyzerTemplate.py AnalyzerNEW.py
```

From here, you must add the following necessary objects and functions:

* `self.channel`
* `self.final_states`
* `self.initial_states`
* `self.object_definitions`
* `self.cutflow_labels` (optional)
* `choose_objects(self,rtrow)`
* `preselection(self,rtrow)`

Look at [AnalyzerWZ.py](AnalyzerWZ.py) for an example.

After adding a new Analyzer, be certain to update [run.py](../run.py) to make the new analyzer accessible.
