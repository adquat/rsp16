from datetime import date

from odoo import api, fields, models
from odoo.tools import date_utils
from odoo.tools.misc import xlsxwriter
from odoo.modules.module import get_module_resource

import io
import json
import base64

class ResPartner(models.Model):
    _inherit = 'res.partner'

    date_birth_partner = fields.Date('Date de Naissance')

class ProjectProject(models.Model):
    _name = 'project.project'
    _inherit = ['mail.thread.phone', 'project.project']
    def _phone_get_number_fields(self):
        """ This method returns the fields to use to find the number to use to
        send an SMS on a record. """
        return ['phone_partner']

## Infos client: Onglet fiche client
    name_partner = fields.Char(string="Nom Client", related='partner_id.name')
    birth_partner = fields.Date(string="Date de Naissance", related='partner_id.date_birth_partner')
    street = fields.Char(related='partner_id.street')
    street2 = fields.Char(related='partner_id.street2')
    zip = fields.Char(change_default=True, related='partner_id.zip')
    city = fields.Char(related='partner_id.city')
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]", related='partner_id.state_id')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', related='partner_id.country_id')
    country_code = fields.Char(related='country_id.code', string="Country Code")
    phone_partner = fields.Char(string="Téléphone", related="partner_id.phone")
    mail_partner = fields.Char(string="Adresse Mail", related="partner_id.email")
    time = fields.Char("Temps de Route")
    parrainage = fields.Many2one('res.partner', string="Parrainage")

    @api.onchange('partner_id')
    def _onchange_address(self):
        if self.partner_id:
            if not self.street:
                self.street = self.partner_id.street
            if not self.street2:
                self.street2 = self.partner_id.street2
            if not self.city:
                self.city = self.partner_id.city
            if not self.zip:
                self.zip = self.partner_id.zip
            if not self.state_id:
                self.state_id = self.partner_id.state_id.id

## Infos dossier: Onglet fiche client
    existing_power = fields.Float("Puissance existance")
    rv_or_auto = fields.Selection([
        ('rv', 'RV'),
        ('auto', 'AUTO')
    ], string="RV ou AUTO")
    crae = fields.Char("N°CRAE")
    bta = fields.Char('N°BTA')
    msb = fields.Char('Numéro de série MSB')

## Fichier à joindre + infos complémentaires: Ongmet fiche client
    devis_and_chq = fields.Many2many('ir.attachment', 'ir_attachment_devis_chq', string='Devis + chèque')
    cgv = fields.Many2many('ir.attachment', 'ir_attachment_cdv', string='CGV Paraphées')
    taxes_foncieres = fields.Many2many('ir.attachment', 'ir_attachment_taxes_foncieres', string='Taxes Foncières')
    fact_elec = fields.Many2many('ir.attachment', 'ir_attachment_fact_elec', string='Facture électricité')
    mandat_mairie = fields.Many2many('ir.attachment', 'ir_attachment_mandat_mairie', string='Mandat Mairie')
    mandat_enedis = fields.Many2many('ir.attachment', 'ir_attachment_mandat_enedis', string='Mandat Enedis')
    mandat_OA = fields.Many2many('ir.attachment', 'ir_attachment_mandat_oa', string='Mandat OA')
    date_recepisse = fields.Date('Date récépissé mairie')
    abf = fields.Boolean('ABF', default=False)
    domofinance = fields.Boolean('Domofinance', default=False)
    dossier_complet = fields.Boolean('Dossier Complet', default=False, compute="_compute_dossier_complet", readonly=True)

    @api.onchange('name_partner', 'birth_partner', 'address_partner', 'phone_partner', 'mail_partner', 'time', 'parrainage',
    'existing_power', 'rv_or_auto', 'crae', 'bta', 'msb', 'dossier_complet', 'gestion_surplus', 'amount_ht', 'date_signature',
    'power_choose', 'user_id', 'tech_ids')
    def onchange_stage_id(self):
        for project in self:
            if project.name_partner and project.birth_partner and project.street and project.city and project.zip and project.phone_partner and project.mail_partner and project.time and project.rv_or_auto and project.dossier_complet and project.gestion_surplus and project.amount_ht and project.date_signature and project.power_choose and project.user_id and project.tech_ids and project.stage_id.id == 1:
                if project.gestion_surplus == 'msb' and project.existing_power and project.crae and project.bta and project.msb:
                    project.stage_id = self.env.ref('project.project_project_stage_1').id
                elif project.gestion_surplus == 'msb' and not project.existing_power and project.msb:
                    project.stage_id = self.env.ref('project.project_project_stage_1').id
                elif project.gestion_surplus != 'msb' and project.existing_power and project.crae and project.bta:
                    project.stage_id = self.env.ref('project.project_project_stage_1').id
                elif project.gestion_surplus != 'msb' and not project.existing_power:
                    project.stage_id = self.env.ref('project.project_project_stage_1').id
                else:
                    pass
            else:
                pass

    @api.depends('devis_and_chq', 'cgv', 'taxes_foncieres', 'fact_elec', 'mandat_mairie', 'mandat_OA', 'gestion_surplus', 'mandat_enedis')
    def _compute_dossier_complet(self):
        for project in self:
            if project.gestion_surplus == 'oa' and project.devis_and_chq and project.taxes_foncieres and project.cgv and project.fact_elec and project.mandat_mairie and project.mandat_OA and project.mandat_enedis:
                project.dossier_complet = True
            elif project.gestion_surplus != 'oa' and project.devis_and_chq and project.taxes_foncieres and project.cgv and project.fact_elec and project.mandat_mairie and project.mandat_enedis:
                project.dossier_complet = True
            else:
                project.dossier_complet = False



## Champ hors onglet
    gestion_surplus = fields.Selection([
        ('oa', 'OA'),
        ('msb', 'MSB'),
        ('other', 'Autres')
    ], string="Gestion Surplus")
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    amount_ht = fields.Monetary("Montant HT", group_operator="sum")
    amount_commission = fields.Monetary("Montant Commission", group_operator="sum")
    date_signature = fields.Date("Date Signature Commande")
    power_choose = fields.Float("Puissance Choisie")
    date_vt = fields.Datetime("Date et heure VT")
    date_mairie = fields.Date("Date accord mairie")
    date_install = fields.Date("Date d'installation")
    #techs_name = fields.Char("Nom des techs")
    tech_ids = fields.Many2many('hr.employee', string="Techniciens")
    date_mise_service_enedis = fields.Date('Date de mise en service Enedis')

    @api.onchange('amount_ht')
    def _onchange_amount_commission(self):
        if self.amount_ht:
            self.amount_commission = self.amount_ht * 0.1

## fichier et infos onglet VT
    tech_id = fields.Many2one('hr.employee', string='Technicien')
    file_to_join = fields.Many2many('ir.attachment', 'ir_attachment_file_join', string='Fichiers à joindre')
    pic_to_join = fields.Many2many('ir.attachment', 'ir_attachment_pic_join', string='Photos à joindre')

    @api.onchange('tech_id', 'file_to_join', 'pic_to_join', 'date_vt')
    def _on_change_stage_id_vt(self):
        for project in self:
            if project.date_vt:
                if project.file_to_join and project.pic_to_join and project.tech_id and project.stage_id.id == self.env.ref('project.project_project_stage_2').id:
                    project.stage_id = self.env.ref('project.project_project_stage_3').id
                else:
                    project.stage_id = self.env.ref('project.project_project_stage_2').id
            else:
                pass

## fichiers et infos onglet Mairie
    done = fields.Boolean('Faite / Pas Faite')
    sending_date_mairie = fields.Date('Date d\'envoi mairie')
    mairie_answer = fields.Selection([
        ('yes', 'Accord'),
        ('no', 'Refus')
    ], string="Réponse mairie")
    mairie_answer_to_join = fields.Many2many('ir.attachment', 'ir_attachment_mairie_answer', string='Accord/Refus à importer')
    recepisse_to_join = fields.Many2many('ir.attachment', 'ir_attachment_recepisse', string='Récépissé fichier')
    other_attachments_to_join = fields.Many2many('ir.attachment', 'ir_attachment_other', string='Pièces complémentaires')
    abf_to_join = fields.Many2many('ir.attachment', 'ir_attachment_abf', string='ABF')
    rsp_to_join = fields.Many2many('ir.attachment', 'ir_attachment_rsp', string='Décharge RSP')

    @api.onchange('sending_date_mairie')
    def _onchange_done(self):
        for project in self:
            if project.sending_date_mairie:
                project.done = True
                project.stage_id = self.env.ref('project.project_project_stage_4').id
            else:
                project.done = False

    @api.onchange('mairie_answer', 'mairie_answer_to_join', 'rsp_to_join')
    def _onchange_stage_id_mairie(self):
        for project in self:
            if ((project.mairie_answer == 'yes' and project.mairie_answer_to_join) or project.rsp_to_join) and project.stage_id.id == self.env.ref('project.project_project_stage_4').id:
                project.stage_id = self.env.ref('project.project_project_stage_5').id
            else:
                pass
    def action_fsm_navigate(self):
        if not self.partner_id.partner_latitude and not self.partner_id.partner_longitude:
            self.partner_id.geo_localize()
        url = "https://www.google.com/maps/dir/?api=1&destination=%s,%s" % (self.partner_id.partner_latitude, self.partner_id.partner_longitude)
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new'
        }

    @api.depends('partner_id')
    def _compute_has_complete_partner_address(self):
        for project in self:
            project.has_complete_partner_address = project.partner_id.city and project.partner_id.country_id

##Fichiers et infos onglet Pose
    return_caution = fields.Boolean('Retour chq Caution', default=False)
    aft = fields.Many2many('ir.attachment', 'ir_attachment_aft', string='AFT')
    picture = fields.Many2many('ir.attachment', 'ir_attachment_picture', string='Photos')
    calepinage_emphase = fields.Many2many('ir.attachment', 'ir_attachment_calepinage', string='Calepinage Emphase')
    implantation_emphase = fields.Many2many('ir.attachment', 'ir_attachment_implantation', string='Implantation Emphase')
    quotation_alaska = fields.Many2many('ir.attachment', 'ir_attachment_quot_alaska', string='Devis Alaska')
    invoice_alaska = fields.Many2many('ir.attachment', 'ir_attachment_inv_alaska', string='Facture alaska')
    invoice_finalRsp = fields.Many2many('ir.attachment', 'ir_attachment_inv_rsp', string='Facture final RSP client')
    all_file_is_good = fields.Boolean(default=False)
    has_complete_partner_address = fields.Boolean(compute='_compute_has_complete_partner_address')

    @api.onchange('aft', 'picture', 'calepinage_emphase', 'implantation_emphase', 'quotation_alaska', 'invoice_alaska', 'invoice_finalRsp')
    def _onchange_all_file_good(self):
        for project in self:
            if project.aft and project.picture and project.calepinage_emphase and project.implantation_emphase and project.quotation_alaska and project.invoice_alaska and project.invoice_finalRsp:
                project.all_file_is_good = True
            else:
                pass

    @api.onchange('date_install')
    def _onchange_stage_id(self):
        for project in self:
            if project.date_install and project.stage_id.id == self.env.ref('project.project_project_stage_5').id:
                project.stage_id = self.env.ref('project.project_project_stage_6').id
            else:
                pass

    def finish_pose(self):
        self.stage_id = self.env.ref('project.project_project_stage_8').id

    def create_fdi(self):
        self.env['fdi.object'].create({
            'project_id': self.id,
        })
        self.stage_id = self.env.ref('project.project_project_stage_7').id

## Infos FDI
    date_fdi = fields.Datetime('Date FDI', compute="_compute_date_fdi")
    fdi_ids = fields.One2many('fdi.object', 'project_id')

    @api.depends('fdi_ids')
    def _compute_date_fdi(self):
        for project in self:
            last_fdi = project.fdi_ids[-1] if project.fdi_ids else False
            if last_fdi and last_fdi.date and last_fdi.state == 'planif':
                project.date_fdi = last_fdi.date
            else:
                project.date_fdi = False

    @api.onchange('date_fdi')
    def _onchange_date_fdi(self):
        if self.date_fdi:
            template = self.env.ref('adquat_rsp.mail_auto_end_install')
            mail_body = template.body_html.split('<t t-out="object.partner_id.name"/>')
            mail_body = self.partner_id.name.join(mail_body)
            mail_body = mail_body.split('<t t-out="object.date_fdi" style="text-align: center;"/>')
            mail_body = self.date_fdi.strftime('%d/%m/%Y à %Hh%M').join(mail_body)

            mail = self.env['mail.compose.message'].create({
                'partner_ids': self.partner_id.ids,
                'subject': template.subject,
                'body': mail_body,
                'composition_mode': 'comment',
                'subtype_id': 1,
                'model': 'project.project',
                'res_id': self.ids[0],
                'template_id': template.id
            })
            mail.action_send_mail()


## Infos SAV
    sav_ids = fields.One2many('sav.object', 'project_id')
    date_sav = fields.Datetime('Date SAV', compute="_compute_date_sav")

    @api.depends('sav_ids')
    def _compute_date_sav(self):
        for project in self:
            last_sav = project.sav_ids[-1] if project.sav_ids else False
            if last_sav and last_sav.date and last_sav.state == 'planif':
                project.date_sav = last_sav.date
            else:
                project.date_sav = False

    @api.onchange('date_sav')
    def _onchange_date_sav(self):
        if self.date_sav:
            template = self.env.ref('adquat_rsp.mail_auto_sav')
            mail_body = template.body_html.split('<t t-out="object.partner_id.name"/>')
            mail_body = self.partner_id.name.join(mail_body)
            mail_body = mail_body.split("""<t t-out="object.date_sav.strftime('%d/%m/%Y à %Hh%M')" style="text-align: center;"/>""")
            mail_body = self.date_sav.strftime('%d/%m/%Y à %Hh%M').join(mail_body)

            mail = self.env['mail.compose.message'].create({
                'partner_ids': self.partner_id.ids,
                'subject': template.subject,
                'body': mail_body,
                'subtype_id': 1,
                'composition_mode': 'comment',
                'model': 'project.project',
                'res_id': self.ids[0],
                'template_id': template.id
            })
            mail.action_send_mail()

## Infos Enedis et Consuel: Onglet mise en servcie
    # Enedis
    numb_pdr = fields.Char('Créat° Numéro PDR')
    consuel_transmitted_enedis = fields.Boolean('Consuel transmis à Enedis', default=False)
    synthese = fields.Many2many('ir.attachment', 'ir_attachment_synthese_enedis', string='Synthèse')
    enedis_done = fields.Boolean('Enedis Fait?')

    @api.onchange('numb_pdr', 'synthese')
    def _onchange_enedis_done(self):
        if self.numb_pdr and self.synthese:
            self.enedis_done = True
            template = self.env.ref('adquat_rsp.mail_auto_synthese_enedis')
            mail_body = template.body_html.split('<t t-out="object.partner_id.name"/>')
            mail_body = self.partner_id.name.join(mail_body)

            mail = self.env['mail.compose.message'].create({
                'partner_ids': [self.partner_id.id],
                'subject': template.subject,
                'body': mail_body,
                'subtype_id': 1,
                'composition_mode': 'comment',
                'model': 'project.project',
                'res_id': self.ids[0],
                'attachment_ids': self.synthese.ids,
                'template_id': template.id
            })
            mail.action_send_mail()
        else:
            self.enedis_done = False

    def finish_project(self):
        self.stage_id = self.env.ref('project.project_project_stage_10').id

    def create_sav(self):
        self.env['sav.object'].create({
            'project_id': self.id,
        })
        self.stage_id = self.env.ref('project.project_project_stage_9').id

    # Consuel
    shipping_number = fields.Char('Numéro d\'envoi')
    type_of_visit = fields.Selection([
        ('1', 'AUDIT'),
        ('2', 'CONSUEL')
    ], string="Type de Visite")
    intended_date = fields.Date('Date prévue')
    date_contre_visite = fields.Date('Date contre-visite')
    date_attestation = fields.Date('Date attestation visée')
    pdf_consuel = fields.Many2many('ir.attachment', 'ir_attachment_pdf_consuel', string='PDF du Consuel')
    fileTech_and_schema = fields.Many2many('ir.attachment', 'ir_attachment_filetech', string='Doss Tech + Schéma')
    consuel_done = fields.Boolean('Consuel Fait?')

    #MSB
    contrat_mylight = fields.Boolean('Contrat MyLight', default=False)

    @api.onchange('contrat_mylight')
    def _onchange_contrat_mylight(self):
        if self.contrat_mylight:
            template = self.env.ref('adquat_rsp.mail_auto_end_install_souscription_mylight')
            mail_body = template.body_html.split('<t t-out="object.partner_id.name"/>')
            mail_body = self.partner_id.name.join(mail_body)

            mail = self.env['mail.compose.message'].create({
                'partner_ids': [self.partner_id.id],
                'subject': template.subject,
                'body': mail_body,
                'subtype_id': 1,
                'composition_mode': 'comment',
                'model': 'project.project',
                'res_id': self.ids[0],
                'template_id': template.id
            })
            mail.action_send_mail()

    @api.onchange('shipping_number', 'fileTech_and_schema')
    def _onchange_consuel_done(self):
        if self.shipping_number and self.fileTech_and_schema:
            self.consuel_done = True
            if self.gestion_surplus == 'msb':
                template = self.env.ref('adquat_rsp.mail_auto_envoi_consuel_if_msb')
                mail_body = template.body_html.split('<t t-out="object.partner_id.name"/>')
                mail_body = self.partner_id.name.join(mail_body)

                mail = self.env['mail.compose.message'].create({
                    'partner_ids': [self.partner_id.id],
                    'subject': template.subject,
                    'body': mail_body,
                    'subtype_id': 1,
                    'composition_mode': 'comment',
                    'attachment_ids': self.pdf_consuel.ids,
                    'model': 'project.project',
                    'res_id': self.ids[0],
                    'template_id': template.id
                })
                mail.action_send_mail()
            elif self.gestion_surplus == 'oa':
                template = self.env.ref('adquat_rsp.mail_auto_envoi_consuel_if_oa')
                mail_body = template.body_html.split('<t t-out="object.partner_id.name"/>')
                mail_body = self.partner_id.name.join(mail_body)

                mail = self.env['mail.compose.message'].create({
                    'partner_ids': [self.partner_id.id],
                    'subject': template.subject,
                    'body': mail_body,
                    'subtype_id': 1,
                    'composition_mode': 'comment',
                    'model': 'project.project',
                    'res_id': self.ids[0],
                    'template_id': template.id
                })
                mail.action_send_mail()
        else:
            self.consuel_done = False

    nb_quotation_validate = fields.Integer('Devis validés', default=0)
    nb_vt_to_planif = fields.Integer('VT à planifier', default=0)
    nb_pose_to_planif = fields.Integer('Pose à planifier', default=0)
    nb_pose_planif = fields.Integer('Pose Finies', default=0)
    nb_sav_finish = fields.Integer('SAV finis', default=0)
    nb_sav_to_planif = fields.Integer('SAV à planifier', default=0)
    nb_fdi_to_planif = fields.Integer('FDI à planifier', default=0)
    nb_fdi_finish = fields.Integer('FDI finies', default=0)
    nb_project_finish = fields.Integer('Dossiers clôturés', default=0)
    xls_vt_file = fields.Binary(string="VT XLS")
    xls_vt_filename = fields.Char()

    # def excel_vt(self):
    #     data = {}
    #     return {'type': 'ir.actions.report', 'report_type': 'XLSX',
    #             'data': {'model': 'project.project', 'output_format': 'XLSX',
    #                      'options': json.dumps(data, default=date_utils.json_default),
    #                      'report_name': 'Visite Technique %s %s' % (self.partner_id.name, self.name), }, }
    # def test_xlsx_success(self):
    #     xlsx_file_path = get_module_resource('adquat_rsp', 'static/excel', 'document_vt.xlsx')
    #     file_content = open(xlsx_file_path, 'rb').read()
    #     import_wizard = self.env['base_import.import'].create({
    #         'res_model': 'base_import.tests.models.preview',
    #         'file': file_content,
    #         'file_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    #     })
    #
    #     result = import_wizard.parse_preview({
    #         'has_headers': True,
    #     })
    #     import pdb; pdb.set_trace()

    def action_generate_xls(self):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Exemption Details')
        style_highlight = workbook.add_format({'bold': True, 'pattern': 1, 'bg_color': '#E0E0E0', 'align': 'center'})
        style_normal = workbook.add_format({'align': 'center'})
        row = 0
        workbook.close()
        xlsx_data = output.getvalue()
        #self.xls_file = base64.encodebytes(xlsx_data)
        document_vt = self.env['ir.attachment'].search([('name', '=', 'document_vt')],limit=1)

        xlsxwriter.Workbook()
        #ENREGISTRER EN PJ
        if document_vt:
            self.xls_vt_file = document_vt.datas

        self.xls_vt_filename = 'Visite Technique %s %s.xlsx' % (self.partner_id.name, self.name)


class Fdi(models.Model):
    _name = 'fdi.object'

    state = fields.Selection([
        ('a_planif', 'À programmer'),
        ('planif', 'Programmée'),
        ('finish', 'Terminée'),
        ('no', 'Interrompu')
    ], string="État", default="a_planif")
    project_id = fields.Many2one('project.project', string='Projet')
    aft_fdi = fields.Many2many('ir.attachment', 'ir_attachment_aft_fdi', string='AFT')
    date = fields.Datetime('Date')
    pictures_fdi = fields.Many2many('ir.attachment', 'ir_attachment_pictures_fdi', string='Photos')

    @api.onchange('date')
    def _on_change_state(self):
        if self.date:
            self.state = 'planif'

    def yes_finish(self):
        self.project_id.stage_id = self.env.ref('project.project_project_stage_8').id
        self.state = 'finish'

    def no_finish(self):
        self.state = 'no'
        self.create({
            'project_id': self.project_id.id
        })

class Sav(models.Model):
    _name = 'sav.object'

    project_id = fields.Many2one('project.project')
    type_sav = fields.Selection([
        ('1', 'Toiture'),
        ('2', 'Elec'),
        ('3', 'Autre')
    ], string="Type de SAV")

    other_type_sav = fields.Char('Autre type de SAV')
    date = fields.Datetime('Date')
    return_picture = fields.Many2many('ir.attachment', 'ir_attachment_return_pic_sav', string='Retour Photo')
    sheet_intervention = fields.Many2many('ir.attachment', 'ir_attachment_sheet_inter_sav', string='Feuille d\'intervention')
    picture_sav = fields.Many2many('ir.attachment', 'ir_attachment_picture_sav', string='Photos SAV')
    state = fields.Selection([
        ('a_planif', 'À programmer'),
        ('planif', 'Programmée'),
        ('finish', 'Terminée'),
        ('no', 'Interrompu')
    ], string="État", default="a_planif")

    @api.onchange('date')
    def _on_change_state(self):
        if self.date:
            self.state = 'planif'

    def mise_en_service(self):
        self.state = 'finish'
        self.project_id.stage_id = self.env.ref('project.project_project_stage_8').id

    def close_project(self):
        self.state = 'finish'
        self.project_id.stage_id = self.env.ref('project.project_project_stage_10').id

    def no_finish_sav(self):
        self.state = 'no'
        self.create({
            'project_id': self.project_id.id
        })

