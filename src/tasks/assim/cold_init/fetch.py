# -*- coding: utf-8 -*-

import footprints.util
from footprints import FPDict, FPList

import vortex
from vortex import toolbox
from vortex.layout.nodes import Task, Driver
import davai
from davai.vtx.tasks.mixins import DavaiIALTaskMixin, IncludesTaskMixin
from davai.vtx.hooks.namelists import hook_gnam
import common

class Fetch(Task, DavaiIALTaskMixin, IncludesTaskMixin):

    @property
    def experts(self):
        """Redefinition as property because of runtime/conf-determined values."""
        return [FPDict({'expert':'fields_in_file', 'kind':'boundary'}),
                FPDict({'kind':'norms', 'hide_equal_norms':self.conf.hide_equal_norms})
                ] + davai.vtx.util.default_experts()

    def process(self):
        self._wrapped_init()
        self._notify_start_inputs()


        obstype = self.conf.get('obstype', None)
        # 1.1.1/ Static Resources:
        if 'early-fetch' in self.steps or 'fetch' in self.steps:
            self._load_usual_tools()  # LFI tools, ecCodes defs, ...
            #-------------------------------------------------------------------------------
            tbmap = self._wrapped_input(
                role           = 'Obsmap',
                block          = 'observations',
                experiment     = self.conf.source_obs[0],
                vapp           = self.conf.source_obs[1],
                vconf          = self.conf.source_obs[2],
                format         = 'ascii',
                kind           = 'obsmap',
                local          = 'bator_map',
                # if obstype is not specified (in conf or loop), get all obstypes from Bator Map:
                only           = FPSet([obstype]) if obstype else None,
                discard        = FPSet([self.conf.discard_obstype]) if 'discard_obstype' in self.conf else None,
                scope          = self.conf.obsmap_scope,
                stage          = 'extract',
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Observations',
                block          = 'observations',
                experiment     = self.conf.source_obs[0],
                vapp           = self.conf.source_obs[1],
                vconf          = self.conf.source_obs[2],
                fatal          = False,
                format         = '[helper:getfmt]',
                helper         = tbmap[0].contents,
                kind           = 'observations',
                local          = '[actualfmt].[part]',
                part           = tbmap[0].contents.dataset(),
                stage          = 'extract',
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'Varbc',
                block          = '4dupd2',
                experiment     = self.conf.source_obs[0],
                vapp           = self.conf.source_obs[1],
                vconf          = self.conf.source_obs[2],
                format         = 'ascii',
                intent         = 'inout',
                kind           = 'varbc',
                local          = 'varbc',
                stage          = 'traj',
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'BackgroundStdError',
                block          = 'sigmab',
                geometry       = 'globalupd224',
                date           = '{}/-{}'.format(self.conf.rundate, self.conf.cyclestep),
                experiment     = self.conf.source_obs[0],
                vapp           = self.conf.source_obs[1],
                vconf          = self.conf.source_obs[2],
                hook_split     = 'common.util.usepygram.split_errgrib_on_shortname',
                format         = 'grib',
                kind           = 'bgstderr',
                local          = 'sigma_b',
                stage          = 'scr',
                term           = self.conf.cyclestep,
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'BackgroundStdError',
                block          = 'covb',
                geometry       = 'globalupd224',
                date           = '{}/-{}'.format(self.conf.rundate, self.conf.cyclestep),
                experiment     = self.conf.source_ensemble[0],
                vapp           = self.conf.source_ensemble[1],
                vconf          = self.conf.source_ensemble[2],
                hook_split     = 'common.util.usepygram.split_errgrib_on_shortname',
                format         = 'grib',
                kind           = 'bgstderr',
                local          = 'errgrib_[geometry:truncation]_',
                stage          = 'vor',
                term           = '3',
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'BlacklistGlobal',
                block          = 'observations',
                experiment     = self.conf.source_obs[0],
                vapp           = self.conf.source_obs[1],
                vconf          = self.conf.source_obs[2],
                format         = 'ascii',
                kind           = 'blacklist',
                local          = 'LISTE_NOIRE_DIAP',
                scope          = 'global',
            )
            #-------------------------------------------------------------------------------
            self._wrapped_input(
                role           = 'BlacklistLocal',
                block          = 'observations',
                experiment     = self.conf.source_obs[0],
                vapp           = self.conf.source_obs[1],
                vconf          = self.conf.source_obs[2],
                format         = 'ascii',
                kind           = 'blacklist',
                local          = 'LISTE_LOC',
                scope          = 'local',
            )
            #-------------------------------------------------------------------------------



        if 'late-backup' in self.steps:
            tbmapout = self._wrapped_output(
                role           = 'Obsmap',
                block          = 'obsraw',
                experiment     = [self.conf.xpid,self.conf.update_shelf],
                format         = 'ascii',
                kind           = 'obsmap',
                local          = 'bator_map',
                scope          = self.conf.obsmap_scope,
                only           = FPSet([obstype]) if obstype else None,
                discard        = FPSet([self.conf.discard_obstype]) if 'discard_obstype' in self.conf else None,
                stage          = 'extract',
                namespace      = 'vortex.multi.fr',
                vapp           = self.conf.shelves_vapp,
                vconf          = self.conf.shelves_vconf,
            )
            #-------------------------------------------------------------------------------
            self._wrapped_output(
                role           = 'ObservationsODB',
                block          = 'obsraw',
                experiment     = [self.conf.xpid,self.conf.update_shelf],
                format         = '[helper:getfmt]',
                helper         = tbmapout[0].contents,
                kind           = 'observations',
                local          = '[actualfmt].[part]',
                part           = tbmapout[0].contents.dataset(),
                stage          = 'extract',
                namespace      = 'vortex.multi.fr',
                vapp           = self.conf.shelves_vapp,
                vconf          = self.conf.shelves_vconf,
            )
            #-------------------------------------------------------------------------------
            self._wrapped_output(
                role           = 'Varbc',
                block          = '4dupd2',
                experiment     = [self.conf.xpid,self.conf.update_shelf],
                format         = 'ascii',
                intent         = 'inout',
                kind           = 'varbc',
                local          = 'varbc',
                stage          = 'traj',
                namespace      = 'vortex.multi.fr',
                vapp           = self.conf.shelves_vapp,
                vconf          = self.conf.shelves_vconf,
            )
            #-------------------------------------------------------------------------------
            self._wrapped_output(
                role           = 'BackgroundStdError',
                block          = 'sigmab',
                experiment     = [self.conf.xpid,self.conf.update_shelf],
                date           = '{}/-{}'.format(self.conf.rundate, self.conf.cyclestep),
                geometry       = 'globalupd224',
                format         = 'grib',
                kind           = 'bgstderr',
                local          = 'sigma_b[variable]',
                variable       = 'u,v,t,q,r,lnsp,gh,btmp,vo',
                stage          = 'scr',
                term           = self.conf.cyclestep,
                namespace      = 'vortex.multi.fr',
                vapp           = self.conf.shelves_vapp,
                vconf          = self.conf.shelves_vconf,
            )
            #-------------------------------------------------------------------------------
            self._wrapped_output(
                role           = 'BackgroundStdError',
                block          = 'covb',
                geometry       = 'globalupd224',
                date           = '{}/-{}'.format(self.conf.rundate, self.conf.cyclestep),
                experiment     = [self.conf.xpid,self.conf.update_shelf],
                format         = 'grib',
                kind           = 'bgstdrenorm',
                local          = 'errgrib_[geometry:truncation]_[variable]',
                variable       = 'vo,ucdv,uctp,ucln,q',
                stage          = 'vor',
                term           = '3',
                namespace      = 'vortex.multi.fr',
                vapp           = self.conf.shelves_vapp,
                vconf          = self.conf.shelves_vconf,
            )
            #-------------------------------------------------------------------------------
            self._wrapped_output(
                role           = 'BlacklistGlobal',
                block          = 'obsraw',
                experiment     = [self.conf.xpid,self.conf.update_shelf],
                format         = 'ascii',
                kind           = 'blacklist',
                local          = 'LISTE_NOIRE_DIAP',
                scope          = 'global',
                vapp           = self.conf.shelves_vapp,
                vconf          = self.conf.shelves_vconf,
            )
            #-------------------------------------------------------------------------------
            self._wrapped_output(
                role           = 'BlacklistLocal',
                block          = 'obsraw',
                experiment     = [self.conf.xpid,self.conf.update_shelf],
                format         = 'ascii',
                kind           = 'blacklist',
                local          = 'LISTE_LOC',
                scope          = 'local',
                vapp           = self.conf.shelves_vapp,
                vconf          = self.conf.shelves_vconf,
            )
            #-------------------------------------------------------------------------------

