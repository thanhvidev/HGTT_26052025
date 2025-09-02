import discord
from discord.ext import commands
import json
import config
import typing


class Prefix(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def check_command_disabled(self, ctx):  
        guild_id = str(ctx.guild.id)  
        command_name = ctx.command.name.lower()  
        if guild_id in self.client.get_cog('Toggle').toggles:  
            if command_name in self.client.get_cog('Toggle').toggles[guild_id]:  
                if ctx.channel.id in self.client.get_cog('Toggle').toggles[guild_id][command_name]:  
                    await ctx.send(f"Lệnh `{command_name}` đã bị tắt ở kênh này.")  
                    return True  
        return False 

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        # Đổi tiền tố thành danh sách chứa cả chữ thường và chữ hoa
        prefixes[str(guild.id)] = ['z', 'Z']
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        prefixes.pop(str(guild.id))
        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)

    @commands.hybrid_command(aliases=["setpre", "sprefix", "setprefix"], description="thay đổi tiền tố lệnh")
    async def set_prefix(self, ctx, *, prefix: str):
        if await self.check_command_disabled(ctx):
            return
        if not ctx.author.guild_permissions.administrator:
            return None
        else:
            with open('prefixes.json', 'r') as f:
                prefixes = json.load(f)
            # Chuyển đổi tiền tố thành danh sách chứa cả chữ thường và chữ hoa
            prefixes[str(ctx.guild.id)] = [prefix.lower(), prefix.upper()]
            with open('prefixes.json', 'w') as f:
                json.dump(prefixes, f, indent=4)
            embed = discord.Embed(
                description=f"Prefix đã được thay đổi thành: `{prefix}`", color=discord.Color.from_rgb(242, 205, 255))
            await ctx.send(embed=embed)

    @commands.hybrid_command(name='prefix', description='xem tiền tố lệnh')
    async def prefix(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        # Mặc định là danh sách chứa cả chữ thường và chữ hoa
        prefix = prefixes.get(str(ctx.guild.id), ['z', 'Z'])
        embed = discord.Embed(
            description=f"Tiền tố lệnh hiện tại là: `{prefix[0]}` (hoặc `{prefix[1]}`)", color=discord.Color.from_rgb(242, 205, 255))
        await ctx.send(embed=embed)

    async def get_prefix(self, bot, message):
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)
        # Mặc định là danh sách chứa cả chữ thường và chữ hoa
        prefix = prefixes.get(str(message.guild.id), ['z', 'Z'])
        return commands.when_mentioned_or(*prefix)(bot, message)
