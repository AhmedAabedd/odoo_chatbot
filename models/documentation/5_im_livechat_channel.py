from odoo import models, fields



class ImLivechatChannel(models.Model):
    _name = 'im_livechat.channel'

    """
        WEBSITE CHAT CONFIGURATION
        When you test on the website, you're using this.
    """


    
    name = fields.Char()
    user_ids = fields.Many2many('res.users')  # Operators who handle chats
    
    # Rules
    rule_ids = fields.One2many('im_livechat.channel.rule', 'channel_id')
    
    # Optional chatbot
    chatbot_script_id = fields.Many2one('chatbot.script')