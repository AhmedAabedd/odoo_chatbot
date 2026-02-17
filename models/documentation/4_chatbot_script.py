from odoo import models, fields



class ChatbotScript(models.Model):
    _name = 'chatbot.script'

    """
        THE AUTOMATED RESPONSE ENGINE
        This is Odoo's built-in chatbot system (different from your custom AI).
    """


    
    title = fields.Char()
    trigger_type = fields.Selection([
        ('keyword', 'Keyword Match'),
        ('visit', 'Page Visit'),
        ('time', 'Time on Site')
    ])
    
    # The conversation flow
    script_step_ids = fields.One2many('chatbot.script.step', 'script_id')
    
    # When to use it
    channel_id = fields.Many2one('im_livechat.channel')  # Which livechat channel
    country_ids = fields.Many2many('res.country')  # Geographic targeting