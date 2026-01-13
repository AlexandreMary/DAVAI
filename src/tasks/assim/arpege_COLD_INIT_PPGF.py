# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, unicode_literals, division

import vortex
from vortex import toolbox
from vortex.layout.nodes import Driver, Family, LoopFamily

from .cold_init.make_global_domain import MakeGlobalDomain
from .cold_init.pgd import PGD
from .cold_init.prep import Prep
from .cold_init.guess import Guess
from .cold_init.fetch import Fetch


def setup(t, **kw):
    return Driver(tag='drv', ticket=t, options=kw, nodes=[
        Family(tag='default_compilation_flavour', ticket=t, nodes=[
            Family(tag='arpege', ticket=t, nodes=[
                Family(tag='cold_init', ticket=t, nodes=[
                    MakeGlobalDomain(tag='MakeGlobalDomain', ticket=t, **kw),
                    PGD(tag='pgd', ticket=t, **kw),
                    Prep(tag='prep', ticket=t, **kw),
                    Guess(tag='guess', ticket=t, **kw),
                    Fetch(tag='fetch', ticket=t, **kw),
                    ], **kw),
                ], **kw),
            ], **kw),
        ],
    )

