from odoo import models, fields



class ImLivechatChatSession(models.Model):
    _name = 'im_livechat.chat.session'

    """
        INDIVIDUAL WEBSITE CHAT SESSIONS
        Each time a visitor starts a chat on your website, a session is created.
    """


    
    channel_id = fields.Many2one('im_livechat.channel')
    anonymous_partner_id = fields.Many2one('res.partner')  # The visitor
    operator_id = fields.Many2one('res.users')  # Staff member handling it
    
    # Messages in this session are in mail.message with model='im_livechat.chat.session'
    message_ids = fields.One2many('mail.message', 'res_id',
                                  domain=[('model', '=', 'im_livechat.chat.session')])
    
    state = fields.Selection([
        ('pending', 'Waiting'),
        ('open', 'In Progress'),
        ('closed', 'Closed')
    ])