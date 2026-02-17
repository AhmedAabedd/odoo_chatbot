from odoo import models, api, fields
from google import genai
from odoo.tools import html2plaintext

class MailMessage(models.Model):
    _inherit = 'mail.message'

    _is_processing = False
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            print("\n" + "="*60)
            print("📨 USER MESSAGE:", vals.get('body'))
            print("="*60)
            
            # Only process messages in livechat sessions
            if (vals.get('model') == 'im_livechat.channel' 
                and vals.get('res_id')
                and not self._is_processing):
                
                channel = self.env['im_livechat.channel'].browse(vals.get('res_id'))

                # IMPORTANT: Only process if:
                # 1. Channel exists
                # 2. It's a livechat channel
                # 3. It has an active chatbot step
                # 4. That chatbot belongs to "Gemini"
                
                # Check if this session has our Gemini chatbot
                if (channel.exists() 
                    and channel.channel_type == 'livechat'
                    and channel.chatbot_current_step_id):
                    
                    # Get the chatbot script from the current step
                    chatbot_script = channel.chatbot_script_id
                    
                    # Check if it's our Gemini chatbot
                    if chatbot_script.title == "Gemini":

                        raw_body = vals.get('body', '')
                        user_message = html2plaintext(raw_body).strip()
                        
                        if not user_message:
                            print("⚠️ Empty message after stripping HTML")
                            continue
                        
                        # Call Gemini directly
                        ai_response = self._call_gemini(user_message)
                        
                        # Post response
                        self._post_ai_response(channel, ai_response)
        
        return super().create(vals_list)
    
    def _call_gemini(self, user_message):
        # Your existing method - unchanged
        if not user_message or not user_message.strip():
            print("⚠️ Empty message received, skipping Gemini call")
            return "I received an empty message. What would you like to ask?"
        
        print(f"🤔 Calling Gemini with: {user_message}")
        
        API_KEY = ""
        
        try:
            client = genai.Client(api_key=API_KEY)
            response = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=user_message
            )
            ai_reply = response.text
            print(f"✅ Gemini response: {ai_reply[:50]}...")
            return ai_reply
            
        except Exception as e:
            print(f"❌ Gemini error: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _post_ai_response(self, channel, ai_response):
        """Post the AI response back to the channel"""
        self.__class__._is_processing = True
        
        try:
            #gemini_script = self.env['chatbot.script'].search([('title', '=', 'Gemini')], limit=1)
            gemini_script = channel.chatbot_script_id

            if not gemini_script:
                print("❌ Gemini chatbot script not found!")
                return
            
            # Get the chatbot's partner ID from the script
            chatbot_partner_id = gemini_script.operator_partner_id.id
            
            if not chatbot_partner_id:
                print("❌ Gemini chatbot has no operator partner!")
                return


            print(f"🤖 Posting as Gemini chatbot (partner ID: {chatbot_partner_id})")
        
            # Post the message as the chatbot
            channel.message_post(
                body=ai_response,
                message_type='comment',
                author_id=chatbot_partner_id,  # Use Gemini's partner ID
                subtype_xmlid='mail.mt_comment'
            )
            print("✅ AI response posted as Gemini chatbot")
            
        finally:
            self.__class__._is_processing = False