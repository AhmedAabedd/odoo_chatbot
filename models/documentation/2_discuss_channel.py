from odoo import models, fields


class DiscussChannel(models.Model):
    _name = 'discuss.channel'


    """
        THE CHAT ROOM
        This represents a conversation space where multiple people can exchange messages.
    """
    
    name = fields.Char()  # Channel name (e.g., "General", "Support")
    
    channel_type = fields.Selection([
        ('chat', 'Chat'),
        ('channel', 'Channel'),
        ('group', 'Group')],
        string='Channel Type', required=True, default='channel', readonly=True, help="Chat is private and unique between 2 persons." \
            "Group is private among invited persons. Channel can be freely joined (depending on its configuration).")
    
    # Who is in this channel
    channel_member_ids = fields.One2many('discuss.channel.member', 'channel_id')
    
    # What messages are in this channel
    message_ids = fields.One2many('mail.message', 'res_id', 
                                  domain=[('model', '=', 'discuss.channel')])
    
    # Additional settings
    description = fields.Text()
    image = fields.Binary()