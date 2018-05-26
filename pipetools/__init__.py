from pipetools.utils import foreach

__version__ = VERSION = 0, 3, 2
__versionstr__ = VERSION > foreach(str) | '.'.join

from pipetools.main import pipe, X, maybe, xpartial
from pipetools.utils import *

# prevent namespace pollution
import pipetools.compat
for symbol in dir(pipetools.compat):
    if globals().get(symbol) is getattr(pipetools.compat, symbol):
        globals().pop(symbol)
