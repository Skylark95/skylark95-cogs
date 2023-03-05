from discord import Message
from redbot.core import Config, checks, commands
import openai
import re

class ChatGPT(commands.Cog):
    """Send messages to ChatGPT"""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=359554929893)
        default_global = {
            "openai_api_key": None,
            "model": "gpt-3.5-turbo"
        }
        self.config.register_global(**default_global)
    
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        ctx: commands.Context = await self.bot.get_context(message)
        text = message.clean_content
        to_strip = f"(?m)^(<@!?{self.bot.user.id}>)"
        is_mention = re.search(to_strip, message.content)
        is_reply = False
        if message.reference and message.reference.resolved:
            author = getattr(message.reference.resolved, "author")
            if author is not None:
                is_reply = message.reference.resolved.author.id == self.bot.user.id and ctx.me in message.mentions
        if is_mention or is_reply:
            await self.do_chatgpt(ctx)

    @commands.command(aliases=['chat'])
    async def chatgpt(self, ctx: commands.Context, *, message: str):
        """Send a message to ChatGPT"""
        reply = await self.do_chatgpt(ctx, message)

    async def do_chatgpt(self, ctx: commands.Context, message: str = None):
        await ctx.trigger_typing()
        openai_api_key = await self.config.openai_api_key()
        if openai_api_key == None:
            await ctx.send("ChatGPT api key not set.")
            return
        model = await self.config.model()
        if model == None:
            await ctx.send("ChatGPT model not set.")
            return
        messages = []
        await self.build_messages(ctx, messages, ctx.message, message)
        print(messages)
        reply = await self.call_api(
            model=model,
            api_key=openai_api_key,
            messages=messages
        )
        await ctx.send(
            content=reply,
            reference=ctx.message
        )

    async def build_messages(self, ctx: commands.Context, messages: list[Message], message: Message, messageText: str = None):
        role = "assistant" if message.author.id == self.bot.user.id else "user"
        content = messageText if messageText else message.clean_content
        to_strip = f"(?m)^(<@!?{self.bot.user.id}>)"
        is_mention = re.search(to_strip, message.content)
        if is_mention:
            content = content[len(ctx.me.display_name) + 2 :]
        if role == "user" and content.startswith('chat '):
            content = content[5:]
        messages.insert(0, {"role": role, "content": content })
        if message.reference and message.reference.resolved:
            await self.build_messages(ctx, messages, message.reference.resolved)

    async def call_api(self, messages, model: str, api_key: str):
        openai.api_key = api_key
        try: 
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages
            )
            reply = response['choices'][0]['message']['content']
            if not reply:
                return "The message from ChatGPT was empty."
            else:
                return reply
        except openai.error.APIError as e:
            return f"OpenAI API returned an API Error: {e}"
        except openai.error.APIConnectionError as e:
            return f"Failed to connect to OpenAI API: {e}"
        except openai.error.RateLimitError as e:
            return f"OpenAI API request exceeded rate limit: {e}"
        except openai.error.AuthenticationError as e:
            return f"OpenAI API returned an Authentication Error: {e}"

    @commands.command()
    @checks.is_owner()
    async def setchatgptkey(self, ctx: commands.Context, api_key: str):
        """Set the api key for ChatGPT"""
        await self.config.openai_api_key.set(api_key)
        await ctx.send("ChatGPT api key set.")
