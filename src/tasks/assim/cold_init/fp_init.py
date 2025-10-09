# -*- coding: utf-8 -*-

import footprints.util
from footprints import FPDict, FPList

import vortex
from vortex import toolbox
from vortex.layout.nodes import Task, Driver
import davai
from davai.vtx.tasks.mixins import DavaiIALTaskMixin, IncludesTaskMixin
from davai.vtx.hooks.namelists import hook_gnam


class Fp_init(Task, DavaiIALTaskMixin, IncludesTaskMixin):

    @property
    def experts(self):
        """Redefinition as property because of runtime/conf-determined values."""
        return [FPDict({'expert':'fields_in_file', 'kind':'boundary'}),
                FPDict({'kind':'norms', 'hide_equal_norms':self.conf.hide_equal_norms})
                ] + davai.vtx.util.default_experts()

    def process(self):
        self._wrapped_init()
        self._notify_start_inputs()

        # 0./ Promises
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._wrapped_promise(**self._promised_listing())
            self._wrapped_promise(**self._promised_expertise())
            #-------------------------------------------------------------------------------

        # 1.1.0/ Reference resources, to be compared to:
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._wrapped_input(**self._reference_continuity_expertise())
            self._wrapped_input(**self._reference_continuity_listing())

        # 1.1.1/ Static Resources:
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._load_usual_tools()  # LFI tools, ecCodes defs, ...
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Initial Clim',
                format         = 'fa',
                genv           = self.conf.appenv_global,
                geometry       = self.conf.source_geometry,
                kind           = 'clim_model',
                local          = 'Const.Clim.m[month]',
                month          = [self.conf.rundate.month, self.conf.rundate.month + 1],
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Target Clim',
                format         = 'fa',
                genv           = self.conf.davaienv,
                geometry       = self.conf.geometry,
                kind           = 'clim_model',
                local          = 'const.clim.[geometry::area::upper].m[month]',
                model          = 'arpege',
                month          = [self.conf.rundate.month, self.conf.rundate.month +1],
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'RrtmConst',
                format         = 'unknown',
                genv           = self.conf.appenv,
                kind           = 'rrtm',
                local          = 'rrtm.const.tgz',
            )
            #-------------------------------------------------------------------------------

        # 1.1.2/ Static Resources (namelist(s) & config):
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Namelist',
                intent         = 'inout',
                kind           = 'namelist',
                local          = 'fort.4',
                source         = 'namelisth2l149',
                path           = f'namelist/arpege/4dvarfr/namelisth2l149',
                ref            = self.conf.gitenv_ref,
                repo           = self.conf.gitenv_repo,
            )
            #-------------------------------------------------------------------------------

        # 1.1.3/ Static Resources (executables):
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            #-------------------------------------------------------------------------------
            tbx = self.flow_executable()
            #-------------------------------------------------------------------------------

        # 1.2/ Initial Flow Resources: theoretically flow-resources, but statically stored in input_shelf
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._wrapped_input(
                role           = 'Model State',
                block          = '4dupd2',
                experiment     = self.conf.xpid_init,
                format         = 'fa',
                kind           = 'analysis',
                filling        = 'atm',
                geometry       = self.conf.source_geometry,
                local          = 'ICMSHCEXPINIT',
                vapp           = self.conf.source_vapp,
                vconf          = self.conf.source_vconf,
            )
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
                crash_witness  = True,
                drhookprof     = self.conf.drhook_profiling,
                engine         = 'parallel',
                kind           = 'l2h',
                outdirectories = self.conf.geometry,
            )
            print(self.ticket.prompt, 'tbalgo =', tbalgo)
            print()
            self.component_runner(tbalgo, tbx)
            #-------------------------------------------------------------------------------
            self.run_expertise()
            #-------------------------------------------------------------------------------

        # 2.3/ Flow Resources: produced by this task and possibly used by a subsequent flow-dependant task
        if 'backup' in self.steps:
            self._wrapped_output(
                role           = 'Analysis',
                block          = self.output_block(),
                experiment     = self.conf.xpid,
                format         = 'fa',
                geometry       = self.conf.geometry,
                kind           = 'analysis',
                local          = 'PFFPOS000+0000',
                namespace      = 'vortex.multi.fr',
            )
            #-------------------------------------------------------------------------------

        # 3.0.1/ Davai expertise:
        if 'late-backup' in self.steps or 'backup' in self.steps:
            self._wrapped_output(**self._output_expertise())
            self._wrapped_output(**self._output_comparison_expertise())
            #-------------------------------------------------------------------------------

        # 3.0.2/ Other output resources of possible interest:
        if 'late-backup' in self.steps or 'backup' in self.steps:
            self._wrapped_output(**self._output_listing())
            self._wrapped_output(**self._output_stdeo())
            self._wrapped_output(**self._output_drhook_profiles())
            #-------------------------------------------------------------------------------

