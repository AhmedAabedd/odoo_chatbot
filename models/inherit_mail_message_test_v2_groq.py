from odoo import models, api, fields
from openai import OpenAI
from odoo.tools import html2plaintext

class MailMessage(models.Model):
    _inherit = 'mail.message'

    _is_processing = False
    
    @api.model_create_multi
    def create(self, vals_list):

        records = super().create(vals_list)

        for message in records:
            print("\n" + "="*60)
            print("📨 USER MESSAGE:", message.body)
            print("🗣️ AUTHOR:", message.author_id.name)
            print("="*60)

            # Only process messages in livechat sessions
            if (message.model == 'discuss.channel' 
                and message.res_id
                and not self._is_processing):
                
                channel = self.env['discuss.channel'].browse(message.res_id)

                members = channel.channel_member_ids
                for member in members:
                    print(f"Member: {member.partner_id.name} (ID: {member.partner_id.id})")

                partner_ids = members.mapped('partner_id.id')

                if message.author_id.id not in partner_ids:
                    continue


                # IMPORTANT: Only process if:
                # 1. Channel exists
                # 2. It's a livechat channel
                # 3. It has an active chatbot step
                # 4. That chatbot belongs to "ChatGPT"
                
                # Check if this session has our ChatGPT chatbot
                if (channel.exists() 
                    and channel.channel_type == 'livechat'
                    and channel.chatbot_script_id):
                    
                    # Get the chatbot script
                    chatbot_script = channel.chatbot_script_id
                    
                    # Check if it's our ChatGPT chatbot
                    if chatbot_script.title == "ChatGPT":

                        chatgpt_script = chatbot_script

                        raw_body = message.body or ''
                        user_message = html2plaintext(raw_body).strip()
                        
                        if not user_message:
                            print("⚠️ Empty message after stripping HTML")
                            continue

                        # ✅ ADD CHECK HERE: Is this message from ChatGPT itself?
                        chatgpt_partner_id = chatgpt_script.operator_partner_id.id
                            
                        # If message author is ChatGPT, skip
                        if message.author_id.id == chatgpt_partner_id:
                            print("⏭️ Message is from ChatGPT itself, skipping...")
                            continue
                        
                        # ✅ Get conversation history (last 10 messages)
                        conversation_history = self._get_channel_history(channel, chatgpt_partner_id, limit=10)
                        
                        # Call ChatGPT directly
                        ai_response = self._call_llm(user_message, conversation_history)
                        
                        # Post response
                        self._post_ai_response(channel, ai_response)
        
        return records

    
    def _get_channel_history(self, channel, bot_partner_id, limit=10):
        """
        Get the last N messages from the channel, alternating between user and bot
        Returns a list of messages formatted for the LLM
        """
        # Get last N messages from this channel, ordered by date
        messages = self.search([
            ('model', '=', 'discuss.channel'),
            ('res_id', '=', channel.id),
        ], order='date asc', limit=limit)  # asc = oldest first for proper conversation flow
        
        history = []
        for msg in messages:
            # Skip empty messages
            if not msg.body:
                continue
                
            # Clean the message body (remove HTML)
            clean_body = html2plaintext(msg.body).strip()
            if not clean_body:
                continue
            
            # Determine role: 'user' if author is not the bot, 'assistant' if it's the bot
            if msg.author_id.id == bot_partner_id:
                role = "assistant"
            else:
                role = "user"
            
            history.append({
                "role": role,
                "content": clean_body
            })
        
        print(f"📜 Loaded {len(history)} previous messages")
        return history
    
    def _call_llm(self, user_message, conversation_history):

        """
        Call ChatGPT with conversation history
        """

        # Your existing method - unchanged
        if not user_message or not user_message.strip():
            print("⚠️ Empty message received, skipping ChatGPT call")
            return "I received an empty message. What would you like to ask?"
        
        print(f"🤔 Calling ChatGPT with: {user_message}")
        print(f"📚 Using {len(conversation_history)} messages for context")
        
        API_KEY = ""

        # Prepare messages with history
        messages = [
            {"role": "system", "content": "You are a helpful assistant for Odoo 18 ERP. Be concise and friendly."},
        ]

        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
            print(f"📚 Added {len(conversation_history)} previous messages for context")

        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        try:
            client = OpenAI(
                api_key=API_KEY,
                base_url="https://api.groq.com/openai/v1"
            )
            response = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=messages,
                temperature=0.7
            )
            ai_reply = response.choices[0].message.content
            print(f"✅ ChatGPT response: {ai_reply[:50]}...")
            return ai_reply
            
        except Exception as e:
            print(f"❌ ChatGPT error: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _post_ai_response(self, channel, ai_response):
        """Post the AI response back to the channel"""
        self.__class__._is_processing = True
        
        try:
            chatgpt_script = self.env['chatbot.script'].search([('title', '=', 'ChatGPT')], limit=1)

            if not chatgpt_script:
                print("❌ ChatGPT chatbot script not found!")
                return
            
            # Get the chatbot's partner ID from the script
            chatbot_partner_id = chatgpt_script.operator_partner_id.id
            
            if not chatbot_partner_id:
                print("❌ ChatGPT chatbot has no operator partner!")
                return

            print(f"🤖 Posting as ChatGPT chatbot (partner ID: {chatbot_partner_id})")
        
            # Post the message as the chatbot
            channel.message_post(
                body=ai_response,
                message_type='comment',
                author_id=chatbot_partner_id,
                subtype_xmlid='mail.mt_comment'
            )
            print("✅ AI response posted as ChatGPT chatbot")
            
        finally:
            self.__class__._is_processing = False
