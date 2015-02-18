PlottingUtils
=============
A comprehensize plotting framework for use with ntuples output from ISA. The style of the plots match
the latest recommendations from the [CMS Publication Committee](https://ghm.web.cern.ch/ghm/plots/).
The primary plotter,  [PlotterBase.py](PlotterBase.py), accesses information about the cross section
([xsec.py](xsec.py)) and plot styles ([tdrstyle.py](tdrstyle.py), [CMS_lumi.py](CMS_lumi.py), and [dataStyles.py](dataStyles.py)). Convenient access methods are available via [Plotter.py](Plotter.py).
In addition, other useful plots can be made with [CutFlowPlotter.py](CutFlowPlotter.py), [FakeRatePlotter.py](FakeRatePlotter.py), and [ShapePlotter.py](ShapePlotter.py).

Limits can be plotted separately with [limits.py](limits.py).
