# -*- coding: utf-8 -*-

from footprints import FPDict

import vortex
from vortex import toolbox
from vortex.layout.nodes import Task, Family, Driver
from common.util.hooks import update_namelist
import davai

from davai.vtx.tasks.mixins import DavaiIALTaskMixin, IncludesTaskMixin


class MakeGlobalDomain(Task, DavaiIALTaskMixin, IncludesTaskMixin):

    experts = []
    _taskinfo_kind = 'statictaskinfo'


    def process(self):
        self._wrapped_init()
        self._notify_start_inputs()

        # 0./ Promises
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            #self._wrapped_promise(**self._promised_expertise())
            pass
            #-------------------------------------------------------------------------------

        # 1.1.0/ Reference resources, to be compared to:
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
          pass  # not so useful to compare namelist to reference

            #-------------------------------------------------------------------------------

        # 1.1.1/ Static Resources:
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._load_usual_tools()  # LFI tools, ecCodes defs, ...
            #-------------------------------------------------------------------------------

        # 1.1.2/ Static Resources (namelist(s) & config):
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            #-------------------------------------------------------------------------------
            pass

        # 1.1.3/ Static Resources (executables):
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            #-------------------------------------------------------------------------------
            tbx = self.flow_executable(
                kind           = 'rgrid',
                local          = 'RGRID.X',
            )
            #-------------------------------------------------------------------------------

        # 1.2/ Flow Resources (initial): theoretically flow-resources, but statically stored in input_shelf
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            pass
            #-------------------------------------------------------------------------------

        # 2.1/ Flow Resources: produced by another task of the same job
        if 'fetch' in self.steps:
            pass
            #-------------------------------------------------------------------------------

        self._notify_inputs_done()
        # 2.2/ Compute step
        if 'compute' in self.steps:
            self._notify_start_compute()
            self.sh.title('Toolbox algo = tbalgo')
            tbalgo = toolbox.algo(
                engine         = 'parallel',
                format         = '',
                grid           = 'linear',
                geometry        = self.conf.geometry.tag,
                illustration   = False,
                oddity   = 0,
                kind           = 'make_gauss_grid',
                orography_grid = 'linear', # 'linear', 'quadratic' or 'cubic'
                pole = {'pole_lon_in_rad': 0.0, 'pole_sin_lat': 1.0},
                truncation = 149,
                stretching = 1,
            )
            print(self.ticket.prompt, 'tbalgo =', tbalgo)
            print()
            self.component_runner(tbalgo, tbx)
            #-------------------------------------------------------------------------------
            self.run_expertise()
            #-------------------------------------------------------------------------------

        # 2.3/ Flow Resources: produced by this task and possibly used by a subsequent flow-dependant task
        if 'backup' in self.steps:
            #-------------------------------------------------------------------------------
            self._wrapped_output(
              role           = 'Namelist',
              #block          = c2v(e.CLASS),
              block = self.output_block(),
              #experiment     = c2v(e.XPID),
              experiment = self.conf.xpid,
              format         = 'ascii',
              geometry       = '[glob:g]',
              kind           = 'geoblocks',
              local          = '{glob:g:\w+}.namel_{glob:n:\w+}.geoblocks',
              namespace      = self.REF_OUTPUT,
              target         = '[glob:n]',
            )
            #-------------------------------------------------------------------------------

        # 3.0.1/ Davai expertise:
        if 'late-backup' in self.steps or 'backup' in self.steps:
            self._wrapped_output(**self._output_expertise())
            #self._wrapped_output(**self._output_comparison_expertise())
            pass
            #-------------------------------------------------------------------------------

        # 3.0.2/ Other output resources of possible interest:
        if 'late-backup' in self.steps or 'backup' in self.steps:
            #self._wrapped_output(**self._output_listing())
            pass
            #-------------------------------------------------------------------------------

