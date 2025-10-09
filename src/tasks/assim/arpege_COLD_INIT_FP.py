# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import, unicode_literals, division

import vortex
from vortex import toolbox
from vortex.layout.nodes import Driver, Family, LoopFamily

from .cold_init.fp_init import Fp_init


def setup(t, **kw):
    return Driver(tag='drv', ticket=t, options=kw, nodes=[
        Family(tag='default_compilation_flavour', ticket=t, nodes=[
            Family(tag='arpege', ticket=t, nodes=[
                Family(tag='cold_init', ticket=t, nodes=[
                    Fp_init(tag='fp_init', ticket=t, **kw),
                    ], **kw),
                ], **kw),
            ], **kw),
        ],
    )

