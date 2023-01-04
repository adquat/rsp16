# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class FdiSavWizard(models.TransientModel):
    _name = "project.fdi.sav.wizard"
    _description = "Assistant de création"

    project_id = fields.Many2one('project.project', string='Projet', required=True)
    type = fields.Selection([('fdi', 'FDI'), ('sav', 'SAV'), ('pose', 'Pose')], required=True)
    date = fields.Datetime('Date prévue')
    date_start = fields.Date('Date Début')
    date_end = fields.Date('Date fin')
    #FDI
    cause = fields.Char('Cause interruption')
    #SAV
    type_sav = fields.Selection([
        ('1', 'Toiture'),
        ('2', 'Elec'),
        ('3', 'Autre')
    ], string="Type de SAV")
    other_type_sav = fields.Char('Autre type de SAV')

    def validate(self):
        self.ensure_one()
        if self.type == 'fdi':
            self.env['fdi.object'].create({
                'project_id': self.project_id.id,
                'date': self.date,
                'cause': self.cause,
                'state':'planif',
            })
            self.project_id.stage_id = self.env.ref('adquat_rsp.project_project_stage_fdi').id
        elif self.type == 'sav':
            self.env['sav.object'].create({
                'project_id': self.project_id.id,
                'date': self.date,
                'type_sav': self.type_sav,
                'other_type_sav': self.other_type_sav,
                'state': 'planif',
            })
            self.project_id.stage_id = self.env.ref('adquat_rsp.project_project_stage_sav').id
        else:
            self.env['project.pose'].create({
                'project_id': self.project_id.id,
                'date_start_install': self.date_start,
                'date_end_install': self.date_end,
            })
            self.project_id.stage_id = self.env.ref('adquat_rsp.project_project_stage_pose_planned').id

        return True