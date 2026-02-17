from odoo import models, fields

class MailMessage(models.Model):
    _name = 'mail.message'

    """
    THE HEART OF ALL COMMUNICATION
    This is the most important model you're already working with. Every single message in Odoo is stored here.
        Key insight:
            mail.message is a polymorphic model - it can attach to ANY record in Odoo using the (model, res_id) pair.
            That's why you see messages in CRM opportunities, project tasks, AND chat channels.
    """
    
    # What the message says
    body = fields.Html()  # The actual content
    subject = fields.Char()  # Optional subject line
    date = fields.Datetime()  # When it was sent
    
    # Who sent it
    author_id = fields.Many2one('res.partner', string="Author")  # The sender
    email_from = fields.Char()  # Email address if from email
    
    # Where it belongs
    model = fields.Char()  # Which model this message is attached to (e.g., 'discuss.channel', 'crm.lead')
    res_id = fields.Integer()  # The ID of that record
    
    # Context
    parent_id = fields.Many2one('mail.message')  # If it's a reply to another message
    subtype_id = fields.Many2one('mail.message.subtype')  # What kind of message (comment, note, etc.)
    
    # Who can see it
    partner_ids = fields.Many2many('res.partner')  # Recipients/visible to these partners
    
    # Attachments
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'mail.message')])