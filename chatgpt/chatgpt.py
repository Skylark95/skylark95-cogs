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
            "model": "gpt-3.5-turbo",
            "max_tokens": 400,
            "mention": True,
            "reply": True,
        }
        self.config.register_global(**default_global)

    async def openai_api_key(self):
        openai_keys = await self.bot.get_shared_api_tokens("openai")
        openai_api_key = openai_keys.get("api_key")
        if openai_api_key is None:
            # Migrate key from config if exists
            openai_api_key = await self.config.openai_api_key()
            if openai_api_key is not None:
                await self.bot.set_shared_api_tokens("openai", api_key=openai_api_key)
                await self.config.openai_api_key.set(None)
        return openai_api_key
    
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        config_mention = await self.config.mention()
        config_reply = await self.config.reply()
        if not config_mention and not config_reply:
            return

        ctx: commands.Context = await self.bot.get_context(message)
        to_strip = f"(?m)^(<@!?{self.bot.user.id}>)"
        is_mention = config_mention and re.search(to_strip, message.content)
        is_reply = False
        if config_reply and message.reference and message.reference.resolved:
            author = getattr(message.reference.resolved, "author")
            if author is not None:
                is_reply = message.reference.resolved.author.id == self.bot.user.id and ctx.me in message.mentions
        if is_mention or is_reply:
            await self.do_chatgpt(ctx)

    @commands.command(aliases=['chat'])
    async def chatgpt(self, ctx: commands.Context, *, message: str):
        """Send a message to ChatGPT."""
        await self.do_chatgpt(ctx, message)

    async def do_chatgpt(self, ctx: commands.Context, message: str = None):
        await ctx.typing()
        openai_api_key = await self.openai_api_key()
        if openai_api_key == None:
            prefix = ctx.prefix if ctx.prefix else "[p]"
            await ctx.send(f"OpenAI API key not set. Use `{prefix}set api openai api_key <value>`.\nAn API key may be acquired from: https://platform.openai.com/account/api-keys.")
            return
        model = await self.config.model()
        if model == None:
            await ctx.send("ChatGPT model not set.")
            return
        max_tokens = await self.config.max_tokens()
        if max_tokens == None:
            await ctx.send("ChatGPT max_tokens not set.")
            return
        messages = []
        await self.build_messages(ctx, messages, ctx.message, message)
        reply = await self.call_api(
            model=model,
            api_key=openai_api_key,
            messages=messages,
            max_tokens=max_tokens
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

    async def call_api(self, messages, model: str, api_key: str, max_tokens: int):
        openai.api_key = api_key
        try: 
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens
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
    async def getchatgptmodel(self, ctx: commands.Context):
        """Get the model for ChatGPT.
        
        Defaults to `gpt-3.5-turbo` See https://platform.openai.com/docs/models/gpt-3-5 for a list of models."""
        model = await self.config.model()
        await ctx.send(f"ChatGPT model set to `{model}`")

    @commands.command()
    @checks.is_owner()
    async def setchatgptmodel(self, ctx: commands.Context, model: str):
        """Set the model for ChatGPT.
        
        Defaults to `gpt-3.5-turbo` See https://platform.openai.com/docs/models/gpt-3-5 for a list of models."""
        await self.config.model.set(model)
        await ctx.send("ChatGPT model set.")

    @commands.command()
    @checks.is_owner()
    async def getchatgpttokens(self, ctx: commands.Context):
        """Get the maximum number of tokens for ChatGPT to generate.
        
        Defaults to `400` See https://platform.openai.com/tokenizer for more details."""
        model = await self.config.max_tokens()
        await ctx.send(f"ChatGPT maximum number of tokens set to `{model}`")

    @commands.command()
    @checks.is_owner()
    async def setchatgpttokens(self, ctx: commands.Context, number: str):
        """Set the maximum number of tokens for ChatGPT to generate.
        
        Defaults to `400` See https://platform.openai.com/tokenizer for more details."""
        try:
            await self.config.max_tokens.set(int(number))
            await ctx.send("ChatGPT maximum number of tokens set.")
        except ValueError:
            await ctx.send("Invalid numeric value for maximum number of tokens.")

    @commands.command()
    @checks.is_owner()
    async def togglechatgptmention(self, ctx: commands.Context):
        """Toggle messages to ChatGPT on mention.
        
        Defaults to `True`."""
        mention = not await self.config.mention()
        await self.config.mention.set(mention)
        if mention:
            await ctx.send("Enabled sending messages to ChatGPT on bot mention.")
        else:
            await ctx.send("Disabled sending messages to ChatGPT on bot mention.")

    @commands.command()
    @checks.is_owner()
    async def togglechatgptreply(self, ctx: commands.Context):
        """Toggle messages to ChatGPT on reply.
        
        Defaults to `True`."""
        reply = not await self.config.reply()
        await self.config.reply.set(reply)
        if reply:
            await ctx.send("Enabled sending messages to ChatGPT on bot reply.")
        else:
            await ctx.send("Disabled sending messages to ChatGPT on bot reply.")
