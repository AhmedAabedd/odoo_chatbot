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
            
            if (vals.get('model') == 'discuss.channel' 
                and vals.get('res_id')
                and not self._is_processing):
                
                channel = self.env['discuss.channel'].browse(vals.get('res_id'))
                
                if channel.exists():
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
        """
        Call Google Gemini with your API key
        """

        if not user_message or not user_message.strip():
            print("⚠️ Empty message received, skipping Gemini call")
            return "I received an empty message. What would you like to ask?"
        
        print(f"🤔 Calling Gemini with: {user_message}")
        
        # Your API key - replace with your actual key
        API_KEY = ""
        
        try:
            # Initialize Gemini client
            client = genai.Client(api_key=API_KEY)  # [citation:5]
            
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
            odoobot = self.env['res.partner'].browse(2)
            channel.message_post(
                body=ai_response,
                message_type='comment',
                author_id=odoobot.id,
                subtype_xmlid='mail.mt_comment'
            )
            print("✅ AI response posted")
            
        finally:
            self.__class__._is_processing = False