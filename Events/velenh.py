import asyncio
import random
import typing
import discord
import sqlite3
from datetime import datetime, timedelta
from discord.ext import commands, tasks
import json
from discord.ui import Button, View
import pytz
import datetime
from Commands.Mod.list_emoji import list_emoji

conn = sqlite3.connect('economy.db', isolation_level=None)
conn.execute('pragma journal_mode=wal')
cursor = conn.cursor()

# Tạo bảng ve_database nếu chưa tồn tại
cursor.execute('''CREATE TABLE IF NOT EXISTS phan_thuong (
                  id INTEGER PRIMARY KEY,
                  name_phanthuong TEXT NOT NULL,
                  soluong_phanthuong INTEGER NOT NULL,
                  emoji_phanthuong INTEGER NOT NULL
               )''')
conn.commit()


def is_registered(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None


def is_allowed_channel():
    async def predicate(ctx):
        allowed_channel_id = 1147035278465310720
        if ctx.channel.id != allowed_channel_id:
            message = await ctx.reply(f"{dauxdo} **Dùng lệnh** **`zmoqua`** **để mở vé** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147035278465310720>)")
            await asyncio.sleep(10)
            await message.delete()
            await ctx.message.delete()
            return False
        return True
    return commands.check(predicate)


def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [1273768834830041301, 1273769137985818624, 993153068378116127, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770, 1147355133622108262, 1295144686536888340, 1207593935359320084]
        if ctx.channel.id not in allowed_channel_ids:
            await ctx.send(f"{dauxdo} **Dùng lệnh** **`zinv`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147355133622108262>)")
            return False
        return True
    return commands.check(predicate)

def is_marry():
    async def predicate(ctx):
        role_marry = any(role.id == 1339482195907186770 for role in ctx.author.roles)
        return role_marry
    return commands.check(predicate)

def is_daily_channel():
    async def predicate(ctx):
        allowed_channel_id = 1147355133622108262
        if ctx.channel.id != allowed_channel_id:
            await ctx.send(f"{dauxdo} **Dùng lệnh** **`zdaily`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147355133622108262>)")
            return False
        return True
    return commands.check(predicate)

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
    return commands.check(predicate)

def is_staff():
    async def predicate(ctx):
        guild_owner = ctx.author == ctx.guild.owner
        bot_owner = ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
        specific_role = any(
            role.id == 1113463122515214427 for role in ctx.author.roles)
        return guild_owner or bot_owner or specific_role
    return commands.check(predicate)


def get_superscript(n):
    superscripts = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(n).translate(superscripts)

married = "<a:emoji_31:1271993759378440192>"
dauxdo = "<a:hgtt_check:1246910030444495008>"
fishcoin = "<:fishcoin:1213027788672737300>"
emojidung = "<:sushi_thanhcong:1215621188059926538> "
emojisai = "<:hgtt_sai:1186839020974657657>"
noicom = "<:sushi_nau:1215607752005652480>"
dongho = "<a:hgtt_timee:1159077258535907328>"
tickdung = "<:hgtt_dung:1186838952544575538>"
quaxanh = "<:hgtt_quaxanhdatroi:1202482871063805992>"
quatim = "<:hgtt_quatim:1202482829397860382>"
quasua = "<:hgtt_qua:1179397064426278932>"
quataocherry = "<:ticketqua3:1198800796054208593>"
quasushi = "<:ss:1214794754542276648>"
quacam = "<:hgtt_qua:1170591248256618506>"
quahongdong = "<a:hgtt_qua:1180122434746200104>"
cakhoc = "<:khongdutien:1211921509514477568>"
congthuc = "<a:congthuc:1214570098879373343>"
daily_streak1 = "<a:lich_daily:1362248474166427759>"
daily_streak2 = "<:lich:1313829453826359398>"
chamthan = "<:chamthann:1233135104281411757>"
quatienowo = "<:qua:1183804744725168148>"
nhayvang = "<a:dotvang:1215606222942896128>"
nhaysao = "<a:nhaysao:1284496637623926784>"
quatienpink = "<:qua:1242529922870673528>"
ngoisao = "<a:ngoisao:1284490593829130250>"
momo = "<:momo:1180104032208048209>"
time_daily = "<a:dongho_daily:1362251621974802492>"
daily_love = "<a:daily_love:1314586830082932806>"
chamthanvang = "<:chamthanvang:1331908568521248779>"

# Emoji quà
kco = "<:0noel_hgtt_chamthan:1313775980141350954>"
tienvnd = "<:hgtt_tien_vnd:1235115910445142037>"
quatienowo_hong = "<:quadaily_vlt:1339536375392768071>"
nhayxanh = "<a:dotxanh:1215606225492774993>"
nhayhong = "<a:dothong:1215606220367466506>"
nhayvang = "<a:nhayvang1:1331714375370932336>"
nhayhong1 = "<a:nhayhong:1331714335919046657>"
phaohoa = "<a:phaohoatron:1331714384107671642>"
quatienowo = "<:qua_tien:1331708095180701736>"
quathantai = "<:qua_thantai:1331708087714713680>"
quaran = "<:qua_ran:1331708134305304716>"
quahuongduong = "<:qua_huongduong:1331708102579326976>"
quahatde = "<:qua_hatde:1331708108837355560>"
quahoamai = "<:qua_hoamai:1331708126977724539>"
quahoadao = "<:qua_hoadao:1331708119839146045>"
quakco = "<:qua_kco:1331708141917966528>"
quanglieu = "<:qua_nglieu:1331708149240954891>"
meotrasua = "<:meotrasua:1331713432822747166>"

dungset = '<a:dung1:1340173892681072743>'
saiset = '<a:sai1:1340173872535703562>'

# class MoquaView(discord.ui.View):
#     def __init__(self, enable_buttons, phan_thuong, timeout: float = 20.0):
#         super().__init__(timeout=timeout)
#         self.enable_buttons = enable_buttons
#         self.phan_thuong = phan_thuong
#         self.message = None

#     async def interaction_check(self, interaction: discord.Interaction) -> bool:
#         if interaction.user.id == self.enable_buttons:
#             return True
#         else:
#             await interaction.response.send_message("Nút mở quà này của người khác", ephemeral=True)
#             return False

#     async def disable_all_items(self):
#         for item in self.children:
#             item.disabled = True
#         await self.message.edit(view=self)

#     @discord.ui.button(
#         label="Rút lì xì",
#         style=discord.ButtonStyle.green,
#         emoji="<:ga_lixitet:1331667458024669335>",
#         custom_id="rutlixi",
#         disabled=False
#         )
#     async def rutlixi(self, interaction: discord.Interaction, button: discord.ui.Button):
#         await self.disable_all_items()
#         cursor.execute("SELECT balance, xu_hlw FROM users WHERE user_id = ?", (interaction.user.id,))
#         result = cursor.fetchone()
#         balance = result[0]
#         xu_hlw = result[1]

#         phan_thuong = self.phan_thuong
#         if phan_thuong[0] in {1, 2, 3}:
#             embed = discord.Embed(
#                 title=f"{quathantai} **Chúc mừng {interaction.user.mention}, bạn rút lì xì được** **{phan_thuong[1]}** {phan_thuong[3]}",
#                 description="",
#                 color=discord.Color.from_rgb(245, 172, 27),
#             )
#             embed.set_thumbnail(
#                 url="https://cdn.discordapp.com/attachments/1211199649667616768/1331718238522048663/discord_fake_avatar_decorations_1737574867767.gif"
#             )
#             await interaction.response.send_message(embed=embed)
#         elif phan_thuong[0] == 4:   
#             embed = discord.Embed(
#                 title=f"{quathantai} **Chúc mừng {interaction.user.mention}, bạn được tặng 1** **{phan_thuong[1]}** {phan_thuong[3]}",
#                 description="",
#                 color=discord.Color.from_rgb(245, 172, 27),
#             )
#             embed.set_thumbnail(
#                 url="https://cdn.discordapp.com/attachments/1211199649667616768/1330255780900769812/discord_fake_avatar_decorations_1737228068493.gif"
#             )
#             await interaction.response.send_message(embed=embed)
#         elif phan_thuong[0] == 5:
#             embed = discord.Embed(
#                 title=f"{quathantai} **Chúc mừng {interaction.user.mention}, bạn được tặng** **{phan_thuong[1]}** {phan_thuong[3]}",
#                 description="",
#                 color=discord.Color.from_rgb(245, 172, 27),
#             )
#             embed.set_thumbnail(
#                 url="https://cdn.discordapp.com/attachments/1211199649667616768/1330253919334436884/discord_fake_avatar_decorations_1737227063095.gif"
#             )
#             await interaction.response.send_message(embed=embed)
#         elif phan_thuong[0] in {6, 7, 8, 9, 10}:
#             await interaction.response.send_message(
#                 f"{quatienowo} **Chúc mừng {interaction.user.mention}, bạn rút lì xì được** {nhayxanh}**{phan_thuong[1]}**{nhayxanh} {phan_thuong[3]}"
#             )
#         elif phan_thuong[0] == 11:
#             await interaction.response.send_message(
#                 f"{quatienowo} **Chúc mừng {interaction.user.mention}**, **bạn rút lì xì được** {nhayhong}**{phan_thuong[1]}**{nhayhong} {phan_thuong[3]}"
#             )
#         elif phan_thuong[0] == 12:
#             await interaction.response.send_message(
#                 f"{quatienowo} **Chúc mừng {interaction.user.mention}, bạn rút lì xì được** {nhayhong}**{phan_thuong[1]}**{nhayhong} {phan_thuong[3]}"
#             )

class Velenh(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.reset_daily_task.start()
        self.guild = None
        self.vevang = None
        self.vekc = None
        self.dk = None
        self.clock = None
        self.users = None
        self.inv = None
        self.chamthan = None
        self.tangqua = None
        self.quadaily = None
        self.tienhatgiong = None
        self.nauan = None
        self.tickdunghong = None
        self.client.loop.create_task(self.setup())

    async def setup(self):
        await self.init_emojis()
        print("Velenh đã được fetch thành công")

    async def init_emojis(self):
        self.guild = self.client.get_guild(1090136467541590066)
        self.vevang = await self.guild.fetch_emoji(1192461054131847260)
        self.vekc = await self.guild.fetch_emoji(1146756758665175040)
        self.users = await self.guild.fetch_emoji(1181378307548250163)
        self.dk = await self.guild.fetch_emoji(1181400074127945799)
        self.inv = await self.guild.fetch_emoji(1159077258535907328)
        self.clock = await self.guild.fetch_emoji(1159077258535907328)
        self.chamthan = await self.guild.fetch_emoji(1179452469017858129)
        self.tangqua = await self.guild.fetch_emoji(1170709400470687806)
        self.quadaily = await self.guild.fetch_emoji(1179397064426278932)
        self.tienhatgiong = await self.guild.fetch_emoji(1192458078294122526)
        self.nauan = await self.guild.fetch_emoji(1192458078294122526)
        self.tickdunghong = await self.guild.fetch_emoji(1186838952544575538)

    async def check_command_disabled(self, ctx):  
        guild_id = str(ctx.guild.id)  
        command_name = ctx.command.name.lower()  
        if guild_id in self.client.get_cog('Toggle').toggles:  
            if command_name in self.client.get_cog('Toggle').toggles[guild_id]:  
                if ctx.channel.id in self.client.get_cog('Toggle').toggles[guild_id][command_name]:  
                    await ctx.send(f"Lệnh `{command_name}` đã bị tắt ở kênh này.")  
                    return True  
        return False 

    @commands.hybrid_command(aliases=["CHECK", "Check"], description="xem có bao nhiêu vé")
    @is_guild_owner_or_bot_owner()
    async def check(self, ctx):
        if is_registered(ctx.author.id):
            cursor.execute(
                "SELECT num_gold_tickets_available, num_diamond_tickets_available, quantity_tickets FROM ve_database WHERE id = ?", (1,))
            ve_db_result = cursor.fetchone()

            if ve_db_result:
                num_gold_tickets_available = ve_db_result[0]
                num_diamond_tickets_available = ve_db_result[1]
                quantity_tickets = ve_db_result[2]
                soluongconlai = 100 - quantity_tickets
                embed = discord.Embed(
                    title=f"", color=discord.Color.magenta())
                embed.add_field(
                    name="", value=f"Số vé còn lại trong ngày: {soluongconlai} {self.tienhatgiong}", inline=False)
                embed.add_field(
                    name="", value=f"Số vé còn lại trong tháng: {num_gold_tickets_available} {self.vevang} và {num_diamond_tickets_available} {self.vekc}", inline=False)
                await ctx.send(embed=embed, ephemeral=True)
            else:
                return None
        else:
            await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")

    @commands.command(aliases=["VE", "Ve"], description="Tặng vé vàng cho người dùng")
    @is_guild_owner_or_bot_owner()
    async def ve(self, ctx, nguoi_nhan: discord.User, so_luong: int):
        # Kiểm tra xem kênh có ID là 1147035278465310720 hay không
        if ctx.channel.id == 1104362707580375120:
            return None
        else:
            if not is_registered(ctx.author.id):
                await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            else:
                if nguoi_nhan is None or so_luong is None or so_luong < 1:
                    await ctx.send("Vd: ztang `user` `1`")
                    return
                if nguoi_nhan.bot:  # Không cho phép trao đổi với bot
                    await ctx.send("Không thể thực hiện trao đổi với bot.")
                    return
                if ctx.author.id == nguoi_nhan.id:
                    await ctx.send("Không thể tặng vé cho bản thân")
                    return
                # Kiểm tra người dùng chưa đăng ký
                if not is_registered(ctx.author.id):
                    await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
                    return
                cursor.execute(
                    "SELECT num_gold_tickets FROM users WHERE user_id = ?", (ctx.author.id,))
                sender_result = cursor.fetchone()
                if not sender_result:
                    await ctx.send("Không thể tải thông tin vé của bạn.")
                    return
                ve_type = "num_gold_tickets"
                sender_ve = sender_result[0]
                if sender_ve < so_luong:
                    await ctx.send(f"{self.chamthan} Bạn k đủ vé {self.vevang} để tặng. **Chăm chat & voice** trong sv để sở hữu thêm vé nha")
                    return
                cursor.execute("SELECT id, kimcuong, " + ve_type +
                            " FROM users WHERE user_id = ?", (nguoi_nhan.id,))
                receiver_result = cursor.fetchone()
                if not receiver_result:
                    await ctx.send(f"{self.dk} người nhận chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
                    return
                new_sender_ve = sender_ve - so_luong
                new_receiver_ve = receiver_result[2] + so_luong  # Cập nhật cột "num_gold_tickets"
                new_receiver_kimcuong = receiver_result[1] + so_luong  # Thêm vào cột "kimcuong"
                cursor.execute("UPDATE users SET " + ve_type +
                            " = ? WHERE user_id = ?", (new_sender_ve, ctx.author.id))
                cursor.execute("UPDATE users SET " + ve_type + " = ?, kimcuong = ? WHERE id = ?", (new_receiver_ve, new_receiver_kimcuong, receiver_result[0]))
                conn.commit()
                await ctx.send(f"{self.tangqua} **| {ctx.author.mention} đã tặng {nguoi_nhan.mention} {so_luong} {self.vevang}**.")

    # @commands.command(aliases=["MOQUA", "Moqua"], description="Mở vé vàng hoặc kim cương")
    # @commands.cooldown(1, 2, commands.BucketType.user)
    # @is_allowed_channel()
    # async def moqua(self, ctx, loai_ve: str = None):
    #     if await self.check_command_disabled(ctx):
    #         return
    #     if not is_registered(ctx.author.id):
    #         await ctx.send(f"{self.chamthan} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` tại kênh <#1147355133622108262> để đăng kí")
    #     else:
    #         if loai_ve is None:
    #             loai_ve = "vang"
    #         elif loai_ve not in ["vang", "kc"]:
    #             await ctx.send("Vui lòng chỉ mở vé vàng (`vang`) hoặc vé kim cương (`kc`).")
    #             return
    #         if loai_ve == "kc":
    #             min_id = 1
    #             max_id = 5
    #         elif loai_ve == "vang":
    #             min_id = 6
    #             max_id = 28
    #             random_id = random.randint(min_id, max_id)
    #         cursor.execute(
    #             "SELECT * FROM phan_thuong WHERE id >= ? AND id <= ?", (min_id, max_id))
    #         phan_thuong_list = cursor.fetchall()

    #         user_id = ctx.author.id
    #         ve_column = "num_gold_tickets" if loai_ve == "vang" else "num_diamond_tickets"
    #         cursor.execute(
    #             f"SELECT {ve_column} FROM users WHERE user_id = ?", (user_id,))
    #         ve_con_lai = cursor.fetchone()[0]
    #         if ve_con_lai <= 0:
    #             await ctx.send(f"{self.chamthan} Bạn k có vé nào để mở. **Chăm chat & voice**  trong sv để sở hữu thêm vé {self.vevang} nha")
    #             return
    #         phan_thuong_co_the_mo = [
    #             pt for pt in phan_thuong_list if pt[2] > 0]
    #         if not phan_thuong_co_the_mo:
    #             await ctx.send("Không còn phần thưởng nào để mở.")
    #             return
    #         selected_phan_thuong = random.choice(phan_thuong_co_the_mo)
    #         phan_thuong_id = selected_phan_thuong[0]
    #         cursor.execute(
    #             "UPDATE phan_thuong SET soluong_phanthuong = soluong_phanthuong - 1 WHERE id = ?", (phan_thuong_id,))
    #         conn.commit()
    #         await self.trao_thuong(ctx, selected_phan_thuong)
    #         await self.cap_nhat_ve(user_id, loai_ve, selected_phan_thuong)

    # @moqua.error
    # async def moqua_error(self, ctx, error):
    #     if isinstance(error, commands.CommandOnCooldown):
    #         message = await ctx.send(f"{dongho} **| {ctx.author.mention} vui lòng chờ {error.retry_after:.0f} giây trước khi sử dụng lệnh này.**")
    #         await asyncio.sleep(2)
    #         await message.delete()
    #         await ctx.message.delete()
    #     elif isinstance(error, commands.CheckFailure):
    #         pass
    #     else:
    #         raise error

    # async def cap_nhat_ve(self, user_id, loai_ve, phan_thuong):
    #     ve_column = "num_gold_tickets" if loai_ve == "vang" else "num_diamond_tickets"
    #     cursor.execute(
    #         f"UPDATE users SET {ve_column} = {ve_column} - 1 WHERE user_id = ?", (user_id,))
    #     conn.commit()

    #     cursor.execute(
    #         f"SELECT open_items FROM users WHERE user_id = ?", (user_id,))
    #     open_items_data = cursor.fetchone()[0]
    #     open_items_dict = json.loads(
    #         open_items_data) if open_items_data else {}

    #     if phan_thuong[1] in open_items_dict:
    #         open_item = open_items_dict[phan_thuong[1]]
    #         open_item["emoji"] = phan_thuong[3]  # emoji_phanthuong
    #         open_item["so_luong"] += 1
    #     else:
    #         open_item = {
    #             "emoji": phan_thuong[3],  # emoji_phanthuong
    #             "name_phanthuong": phan_thuong[1],
    #             "so_luong": 1
    #         }
    #         open_items_dict[phan_thuong[1]] = open_item

    #     # Sắp xếp lại các mục trong open_items theo emoji_phanthuong
    #     sorted_open_items = dict(
    #         sorted(open_items_dict.items(), key=lambda item: item[1]["emoji"]))

    #     updated_open_items = json.dumps(sorted_open_items)
    #     cursor.execute(
    #         f"UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, user_id))
    #     conn.commit()

    # async def trao_thuong(self, ctx, phan_thuong):
    #     cursor.execute("SELECT balance, xu_hlw FROM users WHERE user_id = ?", (ctx.author.id,))
    #     result = cursor.fetchone()
    #     balance = result[0]
    #     xu_hlw = result[1]

    #     enable_buttons = ctx.author.id
    #     view = MoquaView(enable_buttons, phan_thuong)
        
    #     if phan_thuong[0] in {1, 2, 3, 4}:
    #         message = await ctx.reply(view=view)
    #         view.message = message
    #     if phan_thuong[0] == 5:
    #         # Cập nhật xu_hlw
    #         cursor.execute(
    #             "UPDATE users SET xu_hlw = xu_hlw + 10 WHERE user_id = ?", (ctx.author.id,))
    #         conn.commit()
    #         message = await ctx.reply(view=view)
    #         view.message = message
    #     elif phan_thuong[0] in {6, 7, 8, 9, 10}:
    #         message = await ctx.reply(view=view)
    #         view.message = message
    #     elif phan_thuong[0] == 11:
    #         # Cập nhật balance
    #         cursor.execute(
    #             "UPDATE users SET balance = balance + 100000 WHERE user_id = ?", (ctx.author.id,))
    #         conn.commit()
    #         message = await ctx.reply(view=view)
    #         view.message = message
    #     elif phan_thuong[0] == 12:
    #         # Cập nhật balance
    #         cursor.execute(
    #             "UPDATE users SET balance = balance + 200000 WHERE user_id = ?", (ctx.author.id,))
    #         conn.commit()
    #         message = await ctx.reply(view=view)
    #         view.message = message
    #     elif phan_thuong[0] == 13:
    #         await ctx.send(f"{quakco} **Haha, {ctx.author.mention}, bị mẹ giữ hết tiền lì xì rồi nên không có đồng nào!** {phan_thuong[3]}")
    #     elif phan_thuong[0] == 14:
    #         await ctx.send(f"{quaran} **Chúc {ctx.author.mention}, năm mới phát tài phát lộc, năm con rắn nhiều may mắn nha!** {phan_thuong[3]}")
    #     elif phan_thuong[0] == 15 or phan_thuong[0] == 16 or phan_thuong[0] == 17 or phan_thuong[0] == 23 or phan_thuong[0] == 24:
    #         await ctx.send(f"{quatienowo_hong} **Chúc mừng {ctx.author.mention}, bạn được tặng 1** __**lon {phan_thuong[1]}**__ {phan_thuong[3]}{meotrasua}")
    #     elif phan_thuong[0] == 18:
    #         await ctx.send(f"{quahoamai} **{ctx.author.mention}, hái được 1** __**{phan_thuong[1]}**__ {phan_thuong[3]}{nhayhong1}")
    #     elif phan_thuong[0] == 19:
    #         await ctx.send(f"{quahoadao} **{ctx.author.mention}, hái được 1** __**{phan_thuong[1]}**__ {phan_thuong[3]}{nhayhong1}")   
    #     elif phan_thuong[0] == 20:
    #         await ctx.send(f"{quahuongduong} **{ctx.author.mention}, được tặng 1** __**{phan_thuong[1]}**__ {phan_thuong[3]}{nhayvang}")
    #     elif phan_thuong[0] == 21:
    #         await ctx.send(f"{quahatde} **{ctx.author.mention}, được tặng 1** __**{phan_thuong[1]}**__ {phan_thuong[3]}{nhayvang}")
    #     elif phan_thuong[0] == 22:
    #         await ctx.send(f"{quaran} **Chúc mừng {ctx.author.mention} bạn được tặng 1** __**{phan_thuong[1]}**__ {phan_thuong[3]}{phaohoa}")
    #     elif phan_thuong[0] == 25 or phan_thuong[0] == 26 or phan_thuong[0] == 27 or phan_thuong[0] == 28:
    #         await ctx.send(f"{quanglieu} **{ctx.author.mention} được tặng nguyên liệu là 1** __**{phan_thuong[1]}**__ {phan_thuong[3]} **để làm bánh Tết, bấm lệnh ** [__**`zlambanh`**__](<https://discord.com/channels/832579380634451969/1147355133622108262>) **để xem nhé**")               

    # @commands.command(aliases=["inv", "INV","Inv"], description="Hiển thị danh sách inventory")
    # @is_allowed_channel_check()
    # async def inventory(self, ctx):
    #     if await self.check_command_disabled(ctx):
    #         return
    #     if not is_registered(ctx.author.id):
    #         await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
    #     else:
    #         user_id = ctx.author.id
    #         cursor.execute("SELECT open_items, daily_streak FROM users WHERE user_id = ?", (user_id,))
    #         result = cursor.fetchone()

    #         open_items_data = result[0]
    #         daily_streak = result[1]

    #         open_items_dict = json.loads(open_items_data) if open_items_data else {}

    #         embed = discord.Embed(title=f"",
    #                             color=discord.Color.from_rgb(242, 226, 6))
    #         if ctx.author.avatar:
    #             avatar_url = ctx.author.avatar.url
    #         else:
    #             avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
    #         embed.set_author(name=f"Kho quà của {ctx.author.display_name}", icon_url=avatar_url)

    #         if not open_items_dict:
    #             embed.add_field(
    #                 name=f"", value=f"{chamthan} **Kho trống, chat & voice tại sv để nhận {self.vevang} nha**")
    #         else:
    #             sorted_open_items = dict(
    #                 sorted(open_items_dict.items(), key=lambda item: item[1]["emoji"]))
    #             item_fields = []
    #             items_per_inline = 6  # Số lượng item trong mỗi trường
                # reward_items = {  
                #         1: {"name": "1dua", "emoji": dua},  
                #         2: {"name": "2sung", "emoji": sung},
                #         3: {"name": "3buoi", "emoji": buoi},
                #         4: {"name": "4duahau", "emoji": duahau},
                #         5: {"name": "5nho", "emoji": nho},
                #         6: {"name": "6mangcau", "emoji": mangcau},
                #         7: {"name": "7dudu", "emoji": dudu},
                #         8: {"name": "8xoai", "emoji": xoai},
                #         9: {"name": "9chuoi", "emoji": chuoi},
                #         10: {"name": "10quyt", "emoji": quyt},
                #         11: {"name": "11thanhlong", "emoji": thanhlong},
                #         12: {"name": "12thom", "emoji": thom}
                #     }  
                # excluded_item_names = {reward["name"] for reward in reward_items.values()}

    #             xinchu_items ={
    #                     1: {"name": "1van", "emoji": van},  
    #                     2: {"name": "2su", "emoji": su},
    #                     3: {"name": "3nhu", "emoji": nhu},
    #                     4: {"name": "4y", "emoji": y},
    #                     5: {"name": "5an", "emoji": an},
    #                     6: {"name": "6khang", "emoji": khang},
    #                     7: {"name": "7thinh", "emoji": thinh},
    #                     8: {"name": "8vuong", "emoji": vuong},
    #             }
    #             xinchu_names = {reward["name"] for reward in xinchu_items.values()}

    #             for i, (item_name, item_data) in enumerate(sorted_open_items.items()):
    #                 emoji_str = item_data["emoji"] 
    #                 item_quantity = get_superscript(item_data["so_luong"])  
    #                 if item_name in ["10k", "20k", "50k", "100k", "200k", "500k", "100,000", "200,000","500,000", "1,000,000","2,000,000","20,000"]:  
    #                     if item_name == "20,000":  
    #                         item_name = "20k"  
    #                     elif item_name == "100,000":  
    #                         item_name = "100k"
    #                     elif item_name == "200,000":
    #                         item_name = "200k"  
    #                     elif item_name == "500,000":
    #                         item_name = "500k"
    #                     elif item_name == "1,000,000":  
    #                         item_name = "1M"
    #                     elif item_name == "2,000,000":
    #                         item_name = "2M"
    #                     item_fields.append(f"**{item_name}** {emoji_str} **{item_quantity}**")  
    #                 else:  
    #                     item_fields.append(f"{emoji_str} **{item_quantity}**")  

    #                 if (i + 1) % items_per_inline == 0 or (i + 1) == len(sorted_open_items):  
    #                     embed.add_field(name="",  
    #                                     value="  ".join(item_fields), inline=False)  
    #                     item_fields = []   
                    
    #             embed.add_field(name="",
    #                             value=f"{daily_streak1} **Daily streak:** __**{daily_streak}**__ **ngày**", inline=False)
    #             reward_fields = []
    #             songuqua = 0
    #             soxinchu = 0
    #             for r, (reward_names, reward_datas) in enumerate(sorted_open_items.items()):
    #                 if reward_names not in xinchu_names:
    #                     continue 
    #                 if reward_names == "1van" or reward_names == "2su" or reward_names == "3nhu" or reward_names == "4y" or reward_names == "5an" or reward_names == "6khang" or reward_names == "7thinh" or reward_names == "8vuong":
    #                     soxinchu += 1
    #                 emoji_strss = reward_datas["emoji"]
    #                 reward_quantitys = get_superscript(reward_datas["so_luong"])
    #                 reward_fields.append(f"{emoji_strss}**{reward_quantitys}**") 
    #                 # if (r + 1) % items_per_inline == 0 or (r + 1) == len(sorted_open_items):
    #                 #     embed.add_field(name="",
    #                 #                     value="  ".join(reward_fields), inline=False)
    #                 #     reward_fields = []
    #             for r, (reward_name, reward_data) in enumerate(sorted_open_items.items()):
    #                 if reward_name not in excluded_item_names:
    #                     continue 
    #                 if reward_name == "1dua" or reward_name == "2sung" or reward_name == "3buoi" or reward_name == "4duahau" or reward_name == "5nho" or reward_name == "6mangcau" or reward_name == "7dudu" or reward_name == "8xoai" or reward_name == "9chuoi" or reward_name == "10quyt" or reward_name == "11thanhlong" or reward_name == "12thom":
    #                     songuqua += 1
    #                 emoji_strs = reward_data["emoji"]
    #                 reward_quantity = get_superscript(reward_data["so_luong"])
    #                 reward_fields.append(f"{emoji_strs}**{reward_quantity}**") 
    #                 # if (r + 1) % items_per_inline == 0 or (r + 1) == len(sorted_open_items):
    #                 #     embed.add_field(name="",
    #                 #                     value="  ".join(reward_fields), inline=False)
    #                 #     reward_fields = []                    
    #             if songuqua == 0:
    #                 embed.add_field(name="", value=f"**{duahau} Ngũ quả** __**0/12**__", inline=False)
    #                 embed.add_field(name="", value=f"**{xinchu} Xin chữ** __**0/8**__", inline=False)
    #             else:
    #                 embed.add_field(name="", value=f"**{duahau} Ngũ quả** __**{songuqua}/12**__", inline=False)
    #                 embed.add_field(name="", value=f"**{xinchu} Xin chữ** __**{soxinchu}/8**__", inline=False)
    #         await ctx.send(embed=embed)

    @commands.command(description="Reset các cột trong các bảng dữ liệu")
    @is_guild_owner_or_bot_owner()
    async def rsve(self, ctx):
        # Reset bảng users
        cursor.execute(
            "UPDATE users SET num_gold_tickets = 0, num_diamond_tickets = 0, open_items = '', total_tickets = 0, daily_streak = 0, last_daily = 0, daily_tickets = 0, kimcuong = 0")
        # Reset bảng ve_database
        cursor.execute(
            "UPDATE ve_database SET num_gold_tickets_available = 5550, num_diamond_tickets_available = 60, quantity_tickets = 0, tong_tickets = 0, daily_keo = 0, daily_bonus1 = 0, daily_bonus2 = 0, daily_bonus3 = 0, daily_bonus4 = 0, daily_nglieu1 = 0, daily_nglieu2 = 0, daily_nglieu3 = 0, daily_nglieu4 = 0")
        # Xóa và thêm lại các dòng trong bảng phan_thuong theo danh sách mới
        danh_sach_phan_thuong = [
            ("500,000", 10, 1284735146515365959),  # 1 vé kim cương
            ("1,000,000", 10, 1284735146515365959),  # 2 vé kim cương
            ("2,000,000", 10, 1284735146515365959),  # 3 vé kim cương
            ("rắn tài lộc", 10, 1328666132764426240),  # 4 vé kim cương
            ("10 xu", 20, 1331676365572935741),  # 5 vé kim cương
            ("10k", 30, 1284735146515365959),  # 6
            ("20k", 30, 1284735146515365959),  # 7
            ("50k", 30, 1284735146515365959),  # 8
            ("100k", 50, 1284735146515365959),  # 9
            ("200k", 20, 1284735146515365959),  # 10
            ("100,000", 30, 1192458078294122526),  # 11
            ("200,000", 30, 1192458078294122526),  # 12
            ("mẹ giữ", 25, 1282056711208701962),  # 13
            ("lời chúc", 25, 1329907955033837608),  # 14
            ("7 up", 60, 1328119885791760414),  # 15
            ("mirinda", 50, 1328120461992661042),  # 16
            ("bí đao", 40, 1328120098501693571),  # 17
            ("hoa mai", 490, 1329800833214185567),  # 18 ------ quà bonus
            ("hoa đào", 490, 1330097186154877048),  # 19
            ("hạt hướng dương", 340, 1328139977783246964),  # 20
            ("hạt dẻ", 340, 1328141403729166379),  # 21
            ("gấu bông rắn x carybara", 360, 1329907958628487242),  # 22
            ("coca", 360, 1328119828657082491),  # 23
            ("pepsi", 360, 1328120158291497173),  # 24 
            ("lá chuối", 620, 1328119615108415569),  # 25 ------ quà daily
            ("nếp", 600, 1329908183740846172),  # 26
            ("thịt heo", 590, 1329807171176890492),  # 27
            ("đậu xanh", 590, 1328119595151654954),  # 28
        ]

        # Xóa toàn bộ dữ liệu cũ trong bảng phan_thuong
        cursor.execute("DELETE FROM phan_thuong")

        for phan_thuong in danh_sach_phan_thuong:
            emoji = None
            # Duyệt qua tất cả các server mà bot đang tham gia
            for guild in self.client.guilds:
                emoji = discord.utils.get(guild.emojis, id=phan_thuong[2])
                if emoji:
                    break  # Nếu tìm thấy emoji thì dừng lại

            emoji_str = f"{emoji}" if emoji else ""
            cursor.execute(
                "INSERT OR IGNORE INTO phan_thuong (name_phanthuong, soluong_phanthuong, emoji_phanthuong) VALUES (?, ?, ?)", 
                (phan_thuong[0], phan_thuong[1], emoji_str)
            )
            conn.commit()

        await ctx.send("Đã thực hiện reset các cột trong các bảng dữ liệu.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.id == 1147035278465310720 and any(keyword in message.content.lower() for keyword in ["zve", "ogive", "zsetve"]):
            await asyncio.sleep(10)
            await message.delete()

    def cog_unload(self):
        self.reset_daily_task.cancel()

    @tasks.loop(seconds=60)
    async def reset_daily_task(self):
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.datetime.now(timezone)
        if now.hour == 15 and now.minute == 0:  # Nếu là 15:00 giờ +7
            # Thực hiện lệnh resetdaily
            cursor.execute(
                "UPDATE users SET last_daily = 0, quest = '', quest_mess = 0, quest_time = 0")
            cursor.execute("UPDATE ve_database SET daily_keo = 0, daily_bonus1 = 0, daily_bonus2 = 0, daily_bonus3 = 0, daily_bonus4 = 0, daily_nglieu1 = 0, daily_nglieu2 = 0, daily_nglieu3 = 0, daily_nglieu4 = 0")
            conn.commit()
            channel = self.client.get_channel(1147355133622108262)
            await channel.send(f"# ĐÃ RESET DAILY THÀNH CÔNG!!!")

    @reset_daily_task.before_loop
    async def before_reset_daily_task(self):
        await self.client.wait_until_ready()

    @commands.command(aliases=["DAILY", "Daily"], description="Điểm danh mỗi ngày")
    @is_marry()
    @is_daily_channel()
    async def daily(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        if not is_registered(ctx.author.id):
            await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        user_id = ctx.author.id
        now = datetime.datetime.utcnow() + timedelta(hours=7)  # Điều chỉnh múi giờ
        cursor.execute(
            "SELECT last_daily, daily_streak FROM users WHERE user_id = ?", (user_id,))
        last_daily, daily_streak = cursor.fetchone()
        cursor.execute(
            "SELECT daily_keo, daily_bonus1, daily_bonus2, daily_bonus3, daily_bonus4, daily_nglieu1, daily_nglieu2, daily_nglieu3, daily_nglieu4 FROM ve_database")
        result = cursor.fetchone()
        daily_keo = result[0]
        daily_bonus1 = result[1]
        daily_bonus2 = result[2]
        daily_bonus3 = result[3]
        daily_bonus4 = result[4]
        daily_nglieu1 = result[5]
        daily_nglieu2 = result[6]
        daily_nglieu3 = result[7]
        daily_nglieu4 = result[8]

        # Tính thời gian còn lại đến reset daily
        reset_time = datetime.datetime(now.year, now.month, now.day,
                                       15, 0) + timedelta(days=1)
        time_left = reset_time - now
        # Định dạng lại thời gian còn lại
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_left_str = f"{hours}h{minutes}m{seconds}s"
        # Lấy lại giá trị của daily_streak sau khi cập nhật
        cursor.execute(
            "SELECT last_daily FROM users WHERE user_id = ?", (user_id,))
        last_daily = cursor.fetchone()[0]
        if last_daily != 0:
            await ctx.send(f"{time_daily} | Bạn đã điểm danh hôm nay rồi! Lượt điểm danh tiếp theo còn: **{time_left_str}**")
            return
        # Cập nhật Daily streak
        cursor.execute(
            "UPDATE users SET daily_streak = daily_streak + 1 WHERE user_id = ?", (user_id,))
        # Cập nhật last_daily
        cursor.execute(
            "UPDATE users SET last_daily = ? WHERE user_id = ?", (now, user_id))
        # Lấy lại giá trị của daily_streak sau khi cập nhật
        cursor.execute(
            "SELECT daily_streak FROM users WHERE user_id = ?", (user_id,))
        daily_streak = cursor.fetchone()[0]
        # Kiểm tra nếu user thuộc các role DONATOR
        donator_roles = [1021383533178134620, 1082887622311022603, 1056244443184906361,
                         1055759097133277204, 1055758414678069308, 1055519421424222208, 1117282898052141188]
        # domdom_roles = [1311874053786566688, 1071865893103075468]
        if any(role.id in donator_roles for role in ctx.author.roles):
            balance_increase = 40000
            coin_kc_increase = 15
            cursor.execute(
                "UPDATE users SET balance = balance + ?, xu_love = xu_love + ? WHERE user_id = ?", (balance_increase, coin_kc_increase, user_id))
        else:
            balance_increase = 20000
            coin_kc_increase = 10
            cursor.execute(
                "UPDATE users SET balance = balance + ?, xu_love = xu_love + ? WHERE user_id = ?", (balance_increase, coin_kc_increase, user_id))
        donator_role_id = None  # ID của role DONATOR nếu người dùng có
        for role in ctx.author.roles:
            if role.id in donator_roles:
                donator_role_id = role.id  # Lưu ID của role DONATOR của người dùng
        if donator_role_id:  # Nếu người dùng có role thuộc danh sách DONATOR
            donator_info = f"- <@&{donator_role_id}>: **20k {self.tienhatgiong} + 5 {list_emoji.xu_event}**"
        else:
            donator_info = f"- <@&{1021383533178134620}>: **20k {self.tienhatgiong} + 5 {list_emoji.xu_event}**"
            
        # if any(role.id in domdom_roles for role in ctx.author.roles):
        #     balance_increase = 50000
        #     noel_coin = 1
        #     cursor.execute(
        #         "UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ? WHERE user_id = ?", (balance_increase, noel_coin, user_id))
        #     domdom_info = f"- <@&{1311874053786566688}>: **50k {self.tienhatgiong} + 1 {list_emoji.xu_event}**"
        # else:
        #     domdom_info = f"- <@&{1311874053786566688}>: **Không có**"
        #nếu người dùng có marry thì cộng thêm tiền
        # cursor.execute("SELECT marry FROM users WHERE user_id = ?", (user_id,))
        # marry = cursor.fetchone()[0]
        # if marry:
        #     cursor.execute(
        #         "UPDATE users SET balance = balance + 20000, xu_hlw = xu_hlw + 1 WHERE user_id = ?", 
        #         (user_id,)
        #     )
        #     conn.commit()
        #     marry_info = f"- {daily_love} | Married: 20k {self.tienhatgiong} + 1 {list_emoji.xu_event}"
        # else:
        #     marry_info = "- 💔 | **single**"

        # Random tỉ lệ 80%
        if random.random() <= 0.9 and daily_keo <= 120 and (daily_bonus1 <=15 or daily_bonus2 <=15 or daily_bonus3 <=15 or daily_bonus4 <=15) and (daily_nglieu1 <= 30 or daily_nglieu2 <= 10 or daily_nglieu3 <= 10 or daily_nglieu4 <= 10):
            min_id = 18
            max_id = 28
            exclude_ids = [25, 26, 27, 28]
            quabiboqua_ids = [18, 19, 20, 21, 22, 23]
            cursor.execute(
                "SELECT * FROM phan_thuong WHERE id >= ? AND id <= ?", (min_id, max_id))
            phan_thuong_list = cursor.fetchall()
            phan_thuong_con_lai = [
                pt for pt in phan_thuong_list if pt[0] not in exclude_ids and pt[2] > 0
            ]
            phan_thuong_nguyen_lieu = [
                pt for pt in phan_thuong_list if pt[0] not in quabiboqua_ids and pt[2] > 0
            ]
            selected_phan_thuong = random.choice(phan_thuong_con_lai)
            selected_nguyen_lieu = random.choice(phan_thuong_nguyen_lieu)

            # if selected_phan_thuong[0] == 28:  # Kiểm tra nếu là item 28
            #     cursor.execute(
            #         "UPDATE users SET coin_kc = coin_kc + 10 WHERE user_id = ?", (user_id,))

            # await self.cap_nhat_ve_daily(user_id, selected_phan_thuong, selected_nguyen_lieu)

            conn.commit()
            embed = discord.Embed(title="",
                                  color=discord.Color.from_rgb(255, 122, 228))

            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"

            embed.set_author(
                name=f"{ctx.author.display_name} daily thành công", icon_url=avatar_url)
            if any(role.id in donator_roles for role in ctx.author.roles):
                embed.add_field(
                    name=f"", value=f"- {daily_streak1} | Daily streak __**{daily_streak}**__\n- {quatienowo_hong} | Quà daily: **20k {self.tienhatgiong} + 10 {list_emoji.xu_event}**\n{donator_info}\n- {time_daily} | Next daily: **`{time_left_str}`**", inline=False)
            else:
                embed.add_field(
                    name=f"", value=f"- {daily_streak1} | Daily streak __**{daily_streak}**__\n- {quatienowo_hong} | Quà daily: **20k {self.tienhatgiong} + 10 {list_emoji.xu_event}**\n{donator_info}\n- {time_daily} | Next daily: **`{time_left_str}`**", inline=False)
            await ctx.send(embed=embed)
            daily_mapping = {  
                14: "daily_bonus1",  
                15: "daily_bonus2",  
                16: "daily_bonus3",  
                17: "daily_bonus4",  
                18: "daily_nglieu1",  
                19: "daily_nglieu2",  
                20: "daily_nglieu3",  
                21: "daily_nglieu4"  
            }  
            column_name = daily_mapping.get(selected_phan_thuong[0])  

            if column_name:  
                cursor.execute(f"UPDATE ve_database SET {column_name} = {column_name} + 1") 
            cursor.execute(
                "UPDATE phan_thuong SET soluong_phanthuong = soluong_phanthuong - 1 WHERE id = ?", (selected_phan_thuong[0],))
            cursor.execute(
                "UPDATE phan_thuong SET soluong_phanthuong = soluong_phanthuong - 1 WHERE id = ?", (selected_nguyen_lieu[0],))
            cursor.execute(
                "UPDATE ve_database SET daily_keo = daily_keo + 1")
            conn.commit()
        else:
            # Không trong 80%, không ra nguyên liệu và phần thưởng, không ghi vào database
            embed = discord.Embed(title="",
                                  color=discord.Color.from_rgb(255, 122, 228))
            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
            embed.set_author(
                name=f"{ctx.author.display_name} daily thành công", icon_url=avatar_url)
            if any(role.id in donator_roles for role in ctx.author.roles):
                embed.add_field(
                    name=f"", value=f"- {daily_streak1} | Daily streak __**{daily_streak}**__\n- {quatienowo_hong} | Quà daily: **20k {self.tienhatgiong} + 10 {list_emoji.xu_event}**\n{donator_info}\n- {time_daily} | Next daily: **`{time_left_str}`**", inline=False)
            else:
                embed.add_field(
                    name=f"", value=f"- {daily_streak1} | Daily streak __**{daily_streak}**__\n- {quatienowo_hong} | Quà daily: **20k {self.tienhatgiong} + 10 {list_emoji.xu_event}**\n{donator_info}\n- {time_daily} | Next daily: **`{time_left_str}`**", inline=False)
            await ctx.send(embed=embed)
            cursor.execute(
                "UPDATE ve_database SET daily_keo = daily_keo + 1")
            conn.commit()
            return

    # async def cap_nhat_ve_daily(self, user_id, phan_thuong, nguyen_lieu):
    #     cursor.execute(
    #         f"SELECT open_items FROM users WHERE user_id = ?", (user_id,))
    #     open_items_data = cursor.fetchone()[0]
    #     open_items_dict = json.loads(
    #         open_items_data) if open_items_data else {}

    #     if phan_thuong[1] in open_items_dict:
    #         open_item = open_items_dict[phan_thuong[1]]
    #         open_item["emoji"] = phan_thuong[3]  # emoji_phanthuong
    #         open_item["so_luong"] += 1
    #     else:
    #         open_item = {
    #             "emoji": phan_thuong[3],  # emoji_phanthuong
    #             "name_phanthuong": phan_thuong[1],
    #             "so_luong": 1
    #         }
    #         open_items_dict[phan_thuong[1]] = open_item

    #     if nguyen_lieu[1] in open_items_dict:
    #         open_item = open_items_dict[nguyen_lieu[1]]
    #         open_item["emoji"] = nguyen_lieu[3]
    #         open_item["so_luong"] += 1
    #     else:
    #         open_item = {
    #             "emoji": nguyen_lieu[3],
    #             "name_phanthuong": nguyen_lieu[1],
    #             "so_luong": 1
    #         }
    #         open_items_dict[nguyen_lieu[1]] = open_item

    #     # Sắp xếp lại các mục trong open_items theo emoji_phanthuong
    #     sorted_open_items = dict(
    #         sorted(open_items_dict.items(), key=lambda item: item[1]["emoji"]))
    #     updated_open_items = json.dumps(sorted_open_items)
    #     cursor.execute(
    #         f"UPDATE users SET open_items = ? WHERE user_id = ?", (updated_open_items, user_id))
    #     conn.commit()
        
    @commands.command(aliases=["RSDAILY", "Rsdaily"], description="set lại số vé hàng ngày")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def rsdaily(self, ctx):
        msg = await ctx.send("Bạn có chắc chắn muốn set lại số vé hàng ngày? ")
        await msg.add_reaction(dungset)
        await msg.add_reaction(saiset)
        
        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in [dungset, saiset]
                and reaction.message.id == msg.id
            )
        
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
            if str(reaction.emoji) == dungset:
                cursor.execute("UPDATE ve_database SET quantity_tickets = 0")
                cursor.execute("UPDATE users SET daily_tickets = 0")
                conn.commit()
                await msg.edit(content="Đã set lại số vé hàng ngày")
            else:
                await msg.edit(content="Lệnh đã bị hủy.")
        except asyncio.TimeoutError:
            await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")

    @commands.command(aliases=["RSDAILYly", "Rsdailyly"], description="set lại số vé hàng ngày")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def rsdailyly(self, ctx):
        msg = await ctx.send("Bạn có chắc chắn muốn set lại daily? ")
        await msg.add_reaction(dungset)
        await msg.add_reaction(saiset)
        
        def check(reaction, user):
            return (
                user == ctx.author
                and str(reaction.emoji) in [dungset, saiset]
                and reaction.message.id == msg.id
            )
        
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
            if str(reaction.emoji) == dungset:
                cursor.execute("UPDATE users SET last_daily = 0")
                conn.commit()
                await msg.edit(content="Đã set lại daily")
            else:
                await msg.edit(content="Lệnh đã bị hủy.")
        except asyncio.TimeoutError:
            await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")

    @commands.command(aliases=["SETTONGVE", "Settongve"], description="set tổng số vé nhận được cho người khác")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def settongve(self, ctx, user: discord.User, so_luong: int):
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
        user_data = cursor.fetchone()
        if user_data is None:
            await ctx.send(f"{self.dk} người nhận chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        cursor.execute("UPDATE users SET kimcuong = kimcuong + ? WHERE user_id = ? ", (so_luong, user.id))
        conn.commit()

    @commands.command(aliases=["SETVE", "Setve"], description="Set số lượng cho cột num_gold_tickets và num_diamond_tickets bảng users")
    @is_guild_owner_or_bot_owner()
    async def setve(self, ctx, user: discord.User, loai_ve: str, so_luong: int):
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user.id,))
        user_data = cursor.fetchone()

        if user_data is None:
            await ctx.send(f"{self.dk} người nhận chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            return
        if loai_ve is None:
            loai_ve = "vang"
        elif loai_ve not in ["vang", "kc"]:
            await ctx.send("Nhập vé vàng (`vang`) hoặc vé kim cương (`kc`).")
            return

        ve_column = "num_gold_tickets" if loai_ve == "vang" else "num_diamond_tickets"
        # Lấy dữ liệu hiện có của cột vé
        cursor.execute(
            f"SELECT {ve_column} FROM users WHERE user_id = ?", (user.id,))
        current_tickets = cursor.fetchone()[0]
        # Tính toán số lượng mới bằng cách cộng với dữ liệu hiện có (hoặc 0 nếu không có dữ liệu)
        new_tickets = so_luong + current_tickets if current_tickets is not None else so_luong
        # Cập nhật cột vé với giá trị mới
        cursor.execute(
            f"UPDATE users SET {ve_column} = ?, kimcuong = kimcuong + ? WHERE user_id = ?", (new_tickets, so_luong, user.id))
        conn.commit()
        # Kiểm tra và xử lý cột num_diamond_tickets_available hoặc num_gold_tickets_available
        if loai_ve == 'vang':
            ve_available_column = "num_gold_tickets_available"
        elif loai_ve == 'kc':
            ve_available_column = "num_diamond_tickets_available"
        cursor.execute(f"SELECT {ve_available_column} FROM ve_database")
        available_tickets = cursor.fetchone()[0]
        cursor.execute(
            'SELECT tong_tickets FROM ve_database')
        ve_data = cursor.fetchone()
        if available_tickets is not None and ve_data:
            tong_tickets = ve_data[0]
            # Trừ đi số lượng vé đã set từ số lượng vé có sẵn
            updated_available_tickets = available_tickets - so_luong
            new_tong_tickets = tong_tickets + so_luong
            # Cập nhật cột vé có sẵn với giá trị mới
            cursor.execute(
                f"UPDATE ve_database SET tong_tickets = ?, {ve_available_column} = ?", (new_tong_tickets, updated_available_tickets,))
            conn.commit()

        if loai_ve == 'vang':
            await ctx.send(f"**HGTT** gửi tặng **{so_luong} vé {self.vevang}** cho {user.mention}.")
        elif loai_ve == 'kc':
            await ctx.send(f"**HGTT** gửi tặng **{so_luong} vé {self.vekc}** cho {user.mention}.")

    @commands.command(aliases=["SEND", "Send"], description="Gửi tin nhắn đến người dùng khả dụng trong database")
    @is_guild_owner_or_bot_owner()
    async def send(self, ctx, member: typing.Optional[discord.Member] = None, *, message):
        cursor.execute("SELECT user_id FROM users")
        user_ids = cursor.fetchall()
        
        # Kiểm tra trường hợp gửi đến tất cả người dùng
        if member is None:
            confirmation_msg = await ctx.send("Bạn có chắc chắn muốn gửi tin nhắn này đến **tất cả người dùng** không?")
        else:
            # Kiểm tra trường hợp gửi đến một người cụ thể
            confirmation_msg = await ctx.send(f"Bạn có chắc chắn muốn gửi tin nhắn này đến {member.mention} không?")
        
        # Thêm reaction emoji để xác nhận
        await confirmation_msg.add_reaction(dungset)
        await confirmation_msg.add_reaction(saiset)
        
        def check(reaction, user):
            return user == ctx.author and reaction.message.id == confirmation_msg.id and str(reaction.emoji) in [dungset, saiset]
        
        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=30.0, check=check)  # Chờ tối đa 30 giây
        except asyncio.TimeoutError:
            await ctx.send("Hết thời gian chờ. Lệnh đã bị hủy.")
            return
        
        # Hủy lệnh nếu người dùng chọn ❌
        if str(reaction.emoji) == saiset:
            await ctx.send("Lệnh đã bị hủy.")
            return

        # Xử lý gửi tin nhắn
        if member is None:
            for user_id in user_ids:
                try:
                    user = await self.client.fetch_user(user_id[0])
                    await user.send(message)
                except discord.Forbidden:
                    pass
            await ctx.send("Đã gửi tin nhắn đến tất cả người dùng trong database.")
        else:
            if member.bot:
                await ctx.send("Không thể gửi tin nhắn đến bot.")
                return
            try:
                await member.send(message)
                await ctx.send(f"Đã gửi tin nhắn đến {member.mention}.")
            except discord.Forbidden:
                await ctx.send(f"Không thể gửi tin nhắn đến {member.mention}. Bạn không có quyền gửi tin nhắn.")