import asyncio
import random
import aiohttp
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        guild_owner = ctx.author == ctx.guild.owner
        bot_owner = ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
        specific_role = any(role.id == 1113463122515214427 or role.id == 1069779822768832634 for role in ctx.author.roles)

        return guild_owner or bot_owner or specific_role
    
    return commands.check(predicate)

def is_allowed_channel():
    async def predicate(ctx):
        allowed_channel_ids = [1079990874232070225, 1079170812709458031]  # ID của kênh văn bản cho phép
        if ctx.channel.id not in allowed_channel_ids:
            message = await ctx.send("Lệnh này chỉ dành cho staff, dùng ở kênh <#1079990874232070225>")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
            return False
        return True
    return commands.check(predicate)

demso = "<a:number:1262756536980078684>"
lua = "<a:hgtt_fire:1295137544215986206>"
loa = "<:loa:1157931679374131230>"
chamthan = "<:chamthan:1299231374695464992>"

class Loto(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.voice_client = None  # Lưu trữ thông tin về voice client
        self.used_numbers = set()  # Set để lưu các số đã được sử dụng

    @commands.hybrid_command(name="loto", aliases=["LOTO", "lt", "LT"], description="trò chơi lô tô")
    @is_guild_owner_or_bot_owner()
    @is_allowed_channel()
    async def loto(self, ctx):
        message = await ctx.send(f"# {demso} SỐ GÌ RA, CON MẤY GÌ RA {demso}")
        numbers = random.sample(range(1, 91), 1) 
        while numbers[0] in self.used_numbers:  # Kiểm tra xem số đã được sử dụng chưa
            numbers = random.sample(range(1, 91), 1)  # Nếu đã được sử dụng, chọn lại số mới
        self.used_numbers.add(numbers[0])  # Thêm số đã chọn vào set của các số đã sử dụng
        numbers.sort()
        # Phát âm thanh lô tô cho mỗi số
        for number in numbers:
            audio_file = f'loto_sounds/{number}.mp3' 
            voice_channel = ctx.author.voice.channel
            if voice_channel:
                if self.voice_client and self.voice_client.channel == voice_channel:
                    vc = self.voice_client
                else:
                    vc = await voice_channel.connect()
                    self.voice_client = vc
                vc.play(discord.FFmpegPCMAudio(audio_file))
                while vc.is_playing():
                    await asyncio.sleep(1)
                # await vc.disconnect()
            else:
                await ctx.send("Bạn cần tham gia một kênh thoại trước khi sử dụng lệnh này.")
        await asyncio.sleep(1)
        await ctx.message.delete()
        embed = discord.Embed(title="", description =f"# {loa} Danh sách số đã kêu", color=discord.Color.from_rgb(242, 205, 255))
        numbers_list = sorted(self.used_numbers)
        chunks = [numbers_list[i:i+10] for i in range(0, len(numbers_list), 10)]
        for chunk in chunks:
            embed.add_field(name="", value='**' + ' - '.join(map(str, chunk)) + '**', inline=False)
        embed.add_field(name="", value=f'{chamthan} **Ai kinh nhớ la lên!!!**', inline=False)
        await message.edit(content=f'# {lua} SỐ LÔ TÔ MỚI LÀ : __' + '__, __'.join(map(str, numbers)) + f'__ {lua}', embed=embed)     

    @commands.hybrid_command(name="danhsach", aliases=["DS", "ds"], description="Hiển thị danh sách các số đã kêu")
    @is_guild_owner_or_bot_owner()
    @is_allowed_channel()
    async def danhsach(self, ctx):
        if self.used_numbers:
            embed = discord.Embed(title="", description =f"# {loa} Danh sách số đã kêu", color=discord.Color.from_rgb(242, 205, 255))
            numbers_list = sorted(self.used_numbers)
            chunks = [numbers_list[i:i+10] for i in range(0, len(numbers_list), 10)]
            for chunk in chunks:
                embed.add_field(name="", value='**' + ' - '.join(map(str, chunk)) + '**', inline=False)
            await ctx.send(embed=embed)
        else:
            msg = await ctx.send("Chưa có số nào được kêu.")
            await asyncio.sleep(1)
            await msg.delete()
        await asyncio.sleep(1)
        await ctx.message.delete()

    @commands.hybrid_command(name="resetloto", aliases=["RESETLOTO", "rsloto"], description="Xóa danh sách số đã sử dụng")
    @is_guild_owner_or_bot_owner()
    @is_allowed_channel()
    async def resetloto(self, ctx):
        self.used_numbers.clear()
        msg = await ctx.send("Danh sách số đã sử dụng đã được xóa.")
        await asyncio.sleep(1)  # Đợi 3 giây
        await msg.delete()
        await ctx.message.delete()  # Xoá tin nhắn của người dùng
