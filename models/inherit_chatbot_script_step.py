from odoo import models, fields, api




class ChatbotScriptStep(models.Model):
    _inherit = 'chatbot.script.step'



    def _is_last_step(self, discuss_channel=False):
        """
        Override to prevent ChatGPT chatbot from ending.
        """
        # Get the script (use sudo if needed to access title)
        script = self.sudo().chatbot_script_id

        # 🟢 CHECK: Is this ChatGPT?
        is_chatgpt = script and script.title == "ChatGPT"

        print("\n" + ":"*60)
        print("🤖 CHATBOT STEP CHECK")
        print(f"🤖 Step {self.id} - ChatGPT: {is_chatgpt}")
        print("\n" + ":"*60)

        
        # If this is your ChatGPT script, never end
        if is_chatgpt:
            return False
        
        #For all other scripts, use normal logic
        return super()._is_last_step(discuss_channel)
        
