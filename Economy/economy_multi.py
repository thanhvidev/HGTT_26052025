import asyncio
import random
from datetime import datetime
import typing
import discord
from discord.ext import commands, tasks
from discord.ui import View, Button

from Commands.Mod.list_emoji import list_emoji
from services.economy_repo import (
    ensure_guild,
    is_registered,
    register_user,
    get_balance,
    add_balance,
    transfer,
    get_user_field,
    set_user_field,
    inc_user_fields,
)

saocaunguyen = "<a:sao2:1193346135138508810>"
tickxanh = "<:hgtt_dung:1186838952544575538>"
tickdo = "<:hgtt_sai:1186839020974657657>"
cash = "<:cash:1191596352422019084>"
fishcoin = "<:fishcoin:1213027788672737300>"
tienhatgiong = "<:timcoin:1192458078294122526>"
caunguyen = "<a:emoji_pray:1367337789481422858>"
caunguyen2 = "<:luhuong:1271360787088146504>"
vevang = "<:vevang:1192461054131847260>"
vekc = "<:vekc:1146756758665175040>"
bank = '<:bankhong_2025:1339490810768527420>'
dungset = '<a:dung1:1340173892681072743>'
saiset = '<a:sai1:1340173872535703562>'


def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id in (
            573768344960892928, 1006945140901937222, 1307765539896033312, 928879945000833095
        )
    return commands.check(predicate)


def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [
            1147355133622108262, 1152710848284991549, 1079170812709458031, 1207593935359320084,
            1215331218124574740, 1215331281878130738, 1051454917702848562, 1210296290026455140,
            1210417888272318525, 1256198177246285825, 1050649044160094218, 1091208904920281098,
            1238177759289806878, 1243264114483138600, 1251418765665505310, 1243440233685712906,
            1237810926913323110, 1247072223861280768, 1270031327999164548, 1022533822031601766,
            1065348266193063979, 1027622168181350400, 1072536912562241546, 1045395054954565652
        ]
        return ctx.channel.id not in allowed_channel_ids
    return commands.check(predicate)


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.confirm_threshold_choices = [3, 4, 5, 6, 7]
        self.checkpoint_loop.start()

    async def check_command_disabled(self, ctx):
        guild_id = str(ctx.guild.id)
        command_name = ctx.command.name.lower()
        toggle = self.client.get_cog('Toggle')
        if toggle and guild_id in toggle.toggles:
            if command_name in toggle.toggles[guild_id]:
                if ctx.channel.id in toggle.toggles[guild_id][command_name]:
                    await ctx.send(f"Lệnh `{command_name}` đã bị tắt ở kênh này.")
                    return True
        return False

    @commands.command(aliases=["dangky", "dangki", "dk", "DK", "Dk"], description="Đăng ký tài khoản", help="Đăng ký tài khoản")
    async def register(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        user_id = ctx.author.id
        gid = ctx.guild.id
        await ensure_guild(gid)
        if await is_registered(gid, user_id):
            await ctx.send(f"{ctx.author.mention}, bạn đã đăng ký tài khoản rồi!")
            return
        await register_user(gid, user_id, 200_000)
        await set_user_field(gid, user_id, "captcha_attempts", 0)
        await ctx.send(f"<:users:1181400074127945799> | {ctx.author.display_name} đăng kí tài khoản thành công, bạn được tặng __**200k**__ {tienhatgiong}")

    @commands.command(aliases=["CASH", "Cash"], description="xem có bao nhiêu vé")
    async def cash(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        gid = ctx.guild.id
        uid = ctx.author.id
        if not await is_registered(gid, uid):
            await ctx.send(f"{ctx.author.mention} bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        bal = await get_balance(gid, uid) or 0
        num_gold_tickets = await get_user_field(gid, uid, "num_gold_tickets") or 0
        num_diamond_tickets = await get_user_field(gid, uid, "num_diamond_tickets") or 0
        xu_ev = await get_user_field(gid, uid, "xu_hlw") or 0
        if num_diamond_tickets == 0:
            await ctx.send(f"{list_emoji.card} | {ctx.author.display_name} đang có {num_gold_tickets} {vevang}, __**{bal:,}**__ {tienhatgiong} và __**{xu_ev}**__ {list_emoji.xu_event}")
        else:
            await ctx.send(f"{list_emoji.card} | {ctx.author.display_name} đang có {num_gold_tickets} {vevang} {num_diamond_tickets} {vekc}, __**{bal:,}**__ {tienhatgiong} và __**{xu_ev}**__ {list_emoji.xu_event}")

    @commands.command(aliases=["GIVE", "Give"], description="gửi tiền cho mọi người")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def give(self, ctx, receiver: discord.User, amount: int):
        if await self.check_command_disabled(ctx):
            return
        if receiver.bot:
            await ctx.send("Không gửi tiền cho bot.")
            return
        if ctx.author.id == receiver.id:
            await ctx.send("Tự ẻ tự ăn hả???")
            return
        gid = ctx.guild.id
        uid = ctx.author.id
        rid = receiver.id
        if not (await is_registered(gid, uid) and await is_registered(gid, rid)):
            await ctx.send("Bạn hoặc người nhận chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        bal = await get_balance(gid, uid) or 0
        if amount <= 0:
            await ctx.send("Số tiền không hợp lệ")
            return
        if bal < amount:
            await ctx.send("Làm gì còn đủ tiền mà gửi!")
            return

        # Xác nhận bằng reaction
        embed = discord.Embed(color=discord.Color.from_rgb(238, 130, 238))
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
        embed.set_author(name="Xác nhận chuyển tiền", icon_url=avatar_url)
        embed.add_field(name="", value=f"- {ctx.author.mention} sẽ gửi {cash} {receiver.mention}:", inline=False)
        embed.add_field(name="", value=f"``` {amount:,} pinkcoin```", inline=False)
        embed.timestamp = datetime.utcnow()
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(tickxanh)
        await msg.add_reaction(tickdo)

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in [tickxanh, tickdo]

        try:
            reaction, _ = await self.client.wait_for('reaction_add', timeout=180.0, check=check)
        except asyncio.TimeoutError:
            embed.color = discord.Color.from_rgb(0, 0, 0)
            embed.description = "Hết thời gian. Giao dịch đã bị huỷ bỏ."
            await msg.edit(embed=embed)
            await asyncio.sleep(5)
            await msg.delete()
            return

        if str(reaction.emoji) == tickxanh:
            ok, _m = await transfer(gid, uid, rid, amount)
            await msg.delete()
            await ctx.send(f"{bank} {ctx.author.mention} đã gửi __**{amount:,}**__ {tienhatgiong} đến {receiver.mention}.")

    @commands.command(aliases=["PRAY", "Pray"], description="Cầu nguyện")
    @commands.cooldown(1, 900, commands.BucketType.user)
    @is_allowed_channel_check()
    async def pray(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        gid = ctx.guild.id
        uid = ctx.author.id
        counter = await get_user_field(gid, uid, "pray_so") or 0
        threshold = await get_user_field(gid, uid, "pray_time")
        if threshold is None:
            threshold = random.choice(self.confirm_threshold_choices)
            await set_user_field(gid, uid, "pray_time", threshold)
        if counter + 1 > threshold:
            confirmed = False
            view = View(timeout=30)
            button = Button(label="Xác nhận cầu nguyện", style=discord.ButtonStyle.green)
            view.add_item(button)

            async def confirm_cb(interaction: discord.Interaction):
                nonlocal confirmed
                if interaction.user.id != uid:
                    return await interaction.response.send_message("Chỉ người thực hiện lệnh mới có thể xác nhận.", ephemeral=True)
                confirmed = True
                await interaction.response.defer()
                await inc_user_fields(gid, uid, {"pray": 1})
                await set_user_field(gid, uid, "pray_so", 0)
                await set_user_field(gid, uid, "pray_time", random.choice(self.confirm_threshold_choices))
                count = await get_user_field(gid, uid, "pray") or 0
                await interaction.message.delete()
                await interaction.followup.send(f"{caunguyen} | **{ctx.author.display_name}** thành tâm sám hối thắp được __**{count}**__ nén nhang! {caunguyen2}")
                view.stop()

            button.callback = confirm_cb
            prompt = await ctx.send(view=view)
            await view.wait()
            if not confirmed:
                await prompt.delete()
        else:
            await inc_user_fields(gid, uid, {"pray": 1, "pray_so": 1})
            count = await get_user_field(gid, uid, "pray") or 0
            await ctx.send(f"{caunguyen} | **{ctx.author.display_name}** thành tâm sám hối thắp được __**{count}**__ nén nhang! {caunguyen2}")

    @pray.error
    async def pray_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            mins, secs = divmod(int(error.retry_after), 60)
            msg = await ctx.send(f"<:hgtt_chamthan:1179452469017858129> | Vui lòng đợi {mins}m{secs}s trước khi cầu nguyện tiếp.")
            await asyncio.sleep(2)
            await msg.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @commands.command(aliases=["WORK", "Work"], description="Làm việc")
    @commands.cooldown(1, 300, commands.BucketType.user)
    @is_allowed_channel_check()
    async def work(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        gid = ctx.guild.id
        uid = ctx.author.id
        counter = await get_user_field(gid, uid, "work_so") or 0
        threshold = await get_user_field(gid, uid, "work_time")
        if threshold is None:
            threshold = random.choice(self.confirm_threshold_choices)
            await set_user_field(gid, uid, "work_time", threshold)
        if counter + 1 > threshold:
            confirmed = False
            view = View(timeout=30)
            button = Button(label="Xác nhận làm việc", style=discord.ButtonStyle.primary)
            view.add_item(button)

            async def confirm_callback(interaction: discord.Interaction):
                nonlocal confirmed
                if interaction.user.id != uid:
                    return await interaction.response.send_message("Chỉ chủ lệnh mới xác nhận được.", ephemeral=True)
                confirmed = True
                await interaction.response.defer()
                earnings = random.randint(1000, 5000)
                await inc_user_fields(gid, uid, {"balance": earnings})
                embed = discord.Embed(color=discord.Color.green())
                embed.description = f"**<:hgtt_dung:1186838952544575538> {ctx.author.mention} đi làm được trả** __**{earnings:,}**__ {tienhatgiong}"
                await interaction.followup.send(embed=embed)
                await set_user_field(gid, uid, "work_so", 0)
                await set_user_field(gid, uid, "work_time", random.choice(self.confirm_threshold_choices))
                await interaction.message.delete()
                view.stop()

            button.callback = confirm_callback
            prompt = await ctx.send(view=view)
            await view.wait()
            if not confirmed:
                await prompt.delete()
        else:
            earnings = random.randint(1000, 5000)
            await inc_user_fields(gid, uid, {"balance": earnings})
            ws = counter + 1
            await set_user_field(gid, uid, "work_so", ws)
            await ctx.send(f"**<:hgtt_dung:1186838952544575538> {ctx.author.mention} đi làm được trả** __**{earnings:,}**__ {tienhatgiong}")

    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            mins, secs = divmod(int(error.retry_after), 60)
            msg = await ctx.send(f"<:hgtt_chamthan:1179452469017858129> | Vui lòng đợi {mins}m{secs}s trước khi làm việc tiếp.")
            await asyncio.sleep(2)
            await msg.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

    @tasks.loop(hours=4)
    async def checkpoint_loop(self):
        pass

    @checkpoint_loop.before_loop
    async def before_checkpoint(self):
        await self.client.wait_until_ready()
