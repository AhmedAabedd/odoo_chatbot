from odoo import models, fields, api




class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'




    chatbot_script_id = fields.Many2one(related="chatbot_current_step_id.chatbot_script_id")
    
    mail_message_ids = fields.One2many(
        'mail.message', 
        'res_id', 
        domain=[('model', '=', 'discuss.channel')],
        string='Channel Messages'
    )

    
