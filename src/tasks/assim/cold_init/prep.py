# -*- coding: utf-8 -*-

from footprints import FPDict

import vortex
from vortex import toolbox
from vortex.layout.nodes import Task

import davai
from davai.vtx.tasks.mixins import DavaiIALTaskMixin, IncludesTaskMixin
from davai.vtx.hooks.namelists import hook_gnam


class Prep(Task, DavaiIALTaskMixin, IncludesTaskMixin):

    experts = [FPDict({'expert':'fields_in_file', 'kind':'initial_condition'}),]
    _flow_input_task_tag = 'pgd'

    def process(self):
        self._wrapped_init()
        self._notify_start_inputs()

        # 0./ Promises
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._wrapped_promise(**self._promised_expertise())
            #-------------------------------------------------------------------------------

        # 1.1.0/ Reference resources, to be compared to:
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._wrapped_input(**self._reference_continuity_expertise())
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Reference',  # Surface output IC
                block          = self.output_block(),
                experiment     = self.conf.ref_xpid,
                filling        = 'surf',
                fatal          = False,
                format         = 'fa',
                kind           = 'ic',
                local          = 'ref.PREP1_interpolated.[format]',
                model          = 'surfex',
                vconf          = self.conf.ref_vconf,
            )
            #-------------------------------------------------------------------------------

        # 1.1.1/ Static Resources:
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._load_usual_tools()  # LFI tools, ecCodes defs, ...
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'CoverParams',
                format         = 'foo',
                genv           = self.conf.commonenv,
                kind           = 'coverparams',
                local          = 'ecoclimap_covers_param.tgz',
                source         = 'ecoclimap',
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Initial Clim',  # PGD
                format         = 'fa',
                #genv           = self.conf.init_pgd_genv,
                #geometry       = self.conf.source_geometry,
                remote         = "/scratch/work/suzat/pgd_arpege.t1798.06.fa",
                kind           = 'pgdfa',
                local          = 'PGD1.[format]',
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Surface Initial Conditions',
                block          = 'surfan',
                experiment     = self.conf.xpid_init,
                format         = 'fa',
                geometry       = self.conf.source_geometry,
                kind           = 'analysis',
                filling        = 'surf',
                local          = 'PREP1.[format]',
                model          = 'surfex',
                vapp           = self.conf.source_vapp,
                vconf          = self.conf.source_vconf,
            )
            #-------------------------------------------------------------------------------

        # 1.1.2/ Static Resources (namelist(s) & config):
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._wrapped_input(
                role           = 'Namelist',
                # FIXME: update PGD so as to be able to have gelato seaice scheme ?
                #flo halo 0 cause problem in t1798 to 149
                hook_halo      = (hook_gnam, {'NAM_PREP_SURF_ATM':{'NHALO_PREP':10}, }),
                intent         = 'inout',
                kind           = 'namelist',
                local          = 'OPTIONS.nam',
                path           = f'namelist/{self.conf.suite_vapp}/{self.conf.source_vconf}/{self.conf.prep_namelist}',
                ref            = self.conf.gitenv_ref,
                repo           = self.conf.gitenv_repo,
            )
            #-------------------------------------------------------------------------------

        # 1.1.3/ Static Resources (executables):
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            #-------------------------------------------------------------------------------
            tbx = self.flow_executable(
                kind           = 'prep',
                local          = 'PREP.X',
            )
            #-------------------------------------------------------------------------------

        # 1.2/ Flow Resources (initial): theoretically flow-resources, but statically stored in input_shelf
        if 'fetch' in self.steps:
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Target Clim',  # PGD
                block          = self.input_block(),
                experiment     = self.conf.xpid,
                format         = 'fa',
                geometry       = self.conf.geometry,
                kind           = 'pgdfa',
                local          = 'PGD.[format]',
            )

        self._notify_inputs_done()
        # 2.2/ Compute step
        if 'compute' in self.steps:
            self._notify_start_compute()
            self.sh.title('Toolbox algo = tbalgo')
            tbalgo = toolbox.algo(
                crash_witness  = True,
                drhookprof     = self.conf.drhook_profiling,
                engine         = 'blind',
                kind           = 'prep',
                underlyingformat = 'fa',
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
                role           = 'Target Surface Conditions',
                block          = self.output_block(),
                experiment     = self.conf.xpid,
                filling        = 'surf',
                format         = 'fa',
                kind           = 'ic',
                local          = 'PREP1_interpolated.[format]',
                model          = 'surfex',
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
            #-------------------------------------------------------------------------------
