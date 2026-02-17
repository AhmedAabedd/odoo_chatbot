from odoo import models, fields




class DiscussChannelMember(models.Model):
    _name = 'discuss.channel.member'

    """
        THE BRIDGE BETWEEN USERS AND CHANNELS
        This is a pivot table (many2many relationship) that tracks each user's presence in a channel.
    """

    
    channel_id = fields.Many2one('discuss.channel', required=True)
    partner_id = fields.Many2one('res.partner', required=True)  # The user
    
    # Read status tracking - THIS IS WHAT CAUSED YOUR ERROR!
    fetched_message_id = fields.Many2one('mail.message')  # Last message fetched
    seen_message_id = fields.Many2one('mail.message')     # Last message actually read
    last_seen_dt = fields.Datetime()  # When they last viewed
    
    # Custom notifications
    is_pinned = fields.Boolean(default=True)  # Whether channel appears in their list
    custom_notification = fields.Selection([...])


    """
    This is crucial: When a new message arrives in a channel,
                     Odoo must update the fetched_message_id for ALL members of that channel.
                     If multiple messages arrive simultaneously (like your auto-reply + original message),
                     you get the "concurrent update" error you saw.
    """