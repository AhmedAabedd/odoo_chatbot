from odoo import models, fields, api

class MailMessage(models.Model):
    _inherit = 'mail.message'



    flag_variable = 0
    
    @api.model_create_multi
    def create(self, vals_list):

        for vals in vals_list:

            print("\n" + "="*60)
            print("📨 NEW MESSAGE DETECTED")
            print("="*60)
            
            # === CORE INFO (Always available) ===
            print(f"📝 Message ID: {vals.get('id', 'Not assigned yet')}")
            print(f"💬 Body: {vals.get('body', 'No body')}")
            print(f"📎 Model: {vals.get('model', 'No model')}")
            print(f"🔢 Record ID: {vals.get('res_id', 'No res_id')}")
            print(f"🔖 Message Type: {vals.get('message_type', 'No type')}")
            
            # === AUTHOR INFO (Always useful) ===
            author_id = vals.get('author_id')
            if author_id:
                author = self.env['res.partner'].browse(author_id)
                print(f"👤 Author: {author.name} (ID: {author_id})")
                print(f"📧 Author Email: {author.email}")
            
            # === CHANNEL INFO (Only for channel messages) ===
            if vals.get('model') == 'discuss.channel' and vals.get('res_id'):
                channel = self.env['discuss.channel'].browse(vals.get('res_id'))
                print(f"💬 Channel: {channel.name} (ID: {channel.id})")
                print(f"🏷️ Channel Type: {channel.channel_type}")

                # 🔥 CRITICAL: Check if this channel has a chatbot script
                if channel.chatbot_script_id :
                    print(f"🤖 Chatbot: {channel.chatbot_script_id.name}")
                else:
                    print("👤 No chatbot - normal human conversation")
            
            # === OPTIONAL INFO (Only if present) ===
            
            # Parent message (if it's a reply)
            if vals.get('parent_id'):
                parent = self.env['mail.message'].browse(vals.get('parent_id'))
                print(f"↩️ Replying to: {parent.id} - {parent.body[:50]}...")
            
            # Attachments (if any)
            attachment_ids = vals.get('attachment_ids')
            if attachment_ids:
                if isinstance(attachment_ids, list):
                    print(f"📎 Attachments: {attachment_ids}")
                elif isinstance(attachment_ids, tuple) and len(attachment_ids) > 1:
                    print(f"📎 Attachments: {attachment_ids[1]}")
            
            # Partner visibility (if specified)
            partner_ids = vals.get('partner_ids')
            if partner_ids:
                if isinstance(partner_ids, list):
                    print(f"👥 Visible to partners: {partner_ids}")
            
            print("="*60 + "\n")
            
            # Send reply logic
            if vals.get('model') == 'discuss.channel' and vals.get('res_id'):
                channel = self.env['discuss.channel'].browse(vals.get('res_id'))
                if channel.exists() and MailMessage.flag_variable == 0:
                    MailMessage.flag_variable = 1
                    print("🤖 SENDING AUTO-REPLY...")

                    # Get Odoobot partner
                    odoobot = self.env['res.partner'].browse(2)
                    
                    channel.message_post(
                        body="Test reply",
                        message_type='comment',
                        author_id=odoobot.id,  # Set author to Odoobot
                        email_from=odoobot.email  # Optional: set email
                    )

                    print("✅ AUTO-REPLY SENT")
            print("="*60 + "\n")

        return super().create(vals_list)