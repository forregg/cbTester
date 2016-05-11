from testStrat import TestStrat
from dukascopyEngine import DukascopyEngine

strategyParams = {'pOptimization': False}
engine = DukascopyEngine(['USD/CAD'], '1 Min', TestStrat, strategyParams, True)