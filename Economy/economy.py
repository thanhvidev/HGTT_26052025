import asyncio
import time
import typing
import discord
import random
import sqlite3
from datetime import datetime, timedelta
from discord.ui import View, Button

from discord.ext import commands, tasks
from Commands.Mod.list_emoji import list_emoji

# Kết nối và tạo bảng trong SQLite
conn = sqlite3.connect('economy.db')
cursor = conn.cursor()

# Tạo bảng để lưu danh sách các server mà bot đã tham gia
cursor.execute('''CREATE TABLE IF NOT EXISTS servers (
                  server_id INTEGER PRIMARY KEY,
                  joined_at INTEGER
               )''')

# Tạo bảng users mặc định (cho tương thích ngược)
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                  id INTEGER PRIMARY KEY,
                  user_id INTEGER,
                  balance INTEGER,
                  captcha_attempts INTEGER DEFAULT 0,
                  is_locked INTEGER DEFAULT 0,
                  last_daily INTEGER DEFAULT 0,
                  purchased_items TEXT DEFAULT '',
                  marry TEXT DEFAULT '',
                  num_gold_tickets INTEGER DEFAULT 0,
                  num_diamond_tickets INTEGER DEFAULT 0,
                  open_items TEXT DEFAULT '',
                  daily_tickets INTEGER DEFAULT 0,
                  daily_streak INTEGER DEFAULT 0,
                  total_tickets INTEGER DEFAULT 0,
                  vietlottery_tickets INTEGER DEFAULT 0,
                  vietlottery_numbers TEXT DEFAULT '',
                  kimcuong INTEGER DEFAULT 0,
                  pray INTEGER DEFAULT 0,
                  love_marry INTEGER DEFAULT 0,
                  response TEXT DEFAULT '',
                  reaction TEXT DEFAULT '',
                  love_items TEXT DEFAULT '',
                  coin_kc INTEGER DEFAULT 0,
                  last_voice TEXT DEFAULT NULL,
                  kho_ca TEXT DEFAULT '',
                  kho_moi TEXT DEFAULT '',
                  kho_can TEXT DEFAULT '',
                  exp_fish INTEGER DEFAULT 0,
               	  quest_time INTEGER DEFAULT 0,
                  quest_mess INTEGER DEFAULT 0,
                  quest_image INTEGER DEFAULT 0,               
                  quest TEXT DEFAULT '',
                  quest_done INTEGER DEFAULT 0,
                  quest_time_start INTEGER DEFAULT 0,
                  streak_toan INTEGER DEFAULT 0,
                  setup_marry1 TEXT DEFAULT '',
                  setup_marry2 TEXT DEFAULT '',
                  xu_hlw INTEGER DEFAULT 0,
                  xu_love INTEGER DEFAULT 0,
                  bxh_love INTEGER DEFAULT 0,
                  pray_so INTEGER DEFAULT 0,
                  pray_time INTEGER DEFAULT NULL,
                  work_so INTEGER DEFAULT 0, 
                  work_time INTEGER DEFAULT NULL,    
                  love_so INTEGER DEFAULT 0,    
                  love_time INTEGER DEFAULT NULL        
               )''')
conn.commit()

# Danh sách các cột cần đồng bộ giữa các server
SYNC_COLUMNS = [
    "user_id", "balance", "marry", "pray", "love_marry", 
    "setup_marry1", "setup_marry2", "streak_toan", 
    "pray_so", "pray_time", "work_so", "work_time", 
    "love_so", "love_time"
]

def get_server_table_name(server_id):
    """Trả về tên bảng cho server cụ thể"""
    return f"users_{server_id}"

def create_server_table(server_id):
    """Tạo bảng cho server mới"""
    table_name = get_server_table_name(server_id)
    
    # Kiểm tra xem bảng đã tồn tại chưa
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    if cursor.fetchone() is None:
        # Tạo bảng mới cho server
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {table_name} (
                      id INTEGER PRIMARY KEY,
                      user_id INTEGER,
                      balance INTEGER,
                      captcha_attempts INTEGER DEFAULT 0,
                      is_locked INTEGER DEFAULT 0,
                      last_daily INTEGER DEFAULT 0,
                      purchased_items TEXT DEFAULT '',
                      marry TEXT DEFAULT '',
                      num_gold_tickets INTEGER DEFAULT 0,
                      num_diamond_tickets INTEGER DEFAULT 0,
                      open_items TEXT DEFAULT '',
                      daily_tickets INTEGER DEFAULT 0,
                      daily_streak INTEGER DEFAULT 0,
                      total_tickets INTEGER DEFAULT 0,
                      vietlottery_tickets INTEGER DEFAULT 0,
                      vietlottery_numbers TEXT DEFAULT '',
                      kimcuong INTEGER DEFAULT 0,
                      pray INTEGER DEFAULT 0,
                      love_marry INTEGER DEFAULT 0,
                      response TEXT DEFAULT '',
                      reaction TEXT DEFAULT '',
                      love_items TEXT DEFAULT '',
                      coin_kc INTEGER DEFAULT 0,
                      last_voice TEXT DEFAULT NULL,
                      kho_ca TEXT DEFAULT '',
                      kho_moi TEXT DEFAULT '',
                      kho_can TEXT DEFAULT '',
                      exp_fish INTEGER DEFAULT 0,
                      quest_time INTEGER DEFAULT 0,
                      quest_mess INTEGER DEFAULT 0,
                      quest_image INTEGER DEFAULT 0,               
                      quest TEXT DEFAULT '',
                      quest_done INTEGER DEFAULT 0,
                      quest_time_start INTEGER DEFAULT 0,
                      streak_toan INTEGER DEFAULT 0,
                      setup_marry1 TEXT DEFAULT '',
                      setup_marry2 TEXT DEFAULT '',
                      xu_hlw INTEGER DEFAULT 0,
                      xu_love INTEGER DEFAULT 0,
                      bxh_love INTEGER DEFAULT 0,
                      pray_so INTEGER DEFAULT 0,
                      pray_time INTEGER DEFAULT NULL,
                      work_so INTEGER DEFAULT 0, 
                      work_time INTEGER DEFAULT NULL,    
                      love_so INTEGER DEFAULT 0,    
                      love_time INTEGER DEFAULT NULL        
                   )''')
        
        # Thêm server vào danh sách servers
        cursor.execute("INSERT OR IGNORE INTO servers (server_id, joined_at) VALUES (?, ?)", 
                      (server_id, int(time.time())))
        conn.commit()
        
        # Sao chép dữ liệu từ bảng users gốc (nếu có) cho các cột đồng bộ
        cursor.execute("SELECT * FROM users")
        users_data = cursor.fetchall()
        
        if users_data:
            # Lấy tên các cột từ bảng users
            cursor.execute("PRAGMA table_info(users)")
            columns_info = cursor.fetchall()
            column_names = [column[1] for column in columns_info]
            
            for user_row in users_data:
                # Tạo dictionary ánh xạ tên cột với giá trị
                user_data = dict(zip(column_names, user_row))
                
                # Chỉ lấy các cột cần đồng bộ
                sync_data = {col: user_data[col] for col in SYNC_COLUMNS if col in user_data}
                
                # Tạo câu lệnh INSERT
                columns = ", ".join(sync_data.keys())
                placeholders = ", ".join(["?" for _ in sync_data])
                values = tuple(sync_data.values())
                
                cursor.execute(f"INSERT OR IGNORE INTO {table_name} ({columns}) VALUES ({placeholders})", values)
        
        conn.commit()
        return True
    return False

def get_all_server_tables():
    """Lấy danh sách tất cả các bảng server"""
    cursor.execute("SELECT server_id FROM servers")
    servers = cursor.fetchall()
    return [get_server_table_name(server[0]) for server in servers]

def is_registered(user_id, server_id=None):
    """Kiểm tra xem người dùng đã được đăng ký trong server cụ thể hay chưa"""
    if server_id:
        table_name = get_server_table_name(server_id)
        # Kiểm tra xem bảng có tồn tại không
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if cursor.fetchone() is None:
            create_server_table(server_id)
            
        cursor.execute(f"SELECT * FROM {table_name} WHERE user_id = ?", (user_id,))
        return cursor.fetchone() is not None
    else:
        # Kiểm tra trong bảng users gốc (cho tương thích ngược)
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone() is not None

def get_formatted_balance(user_id, server_id=None):
    """Lấy số tiền hiện có của người dùng (đã định dạng)"""
    balance = get_balance(user_id, server_id)
    if balance is not None:
        # Định dạng số tiền có dấu phẩy
        formatted_balance = "{:,}".format(balance)
        return formatted_balance
    return None

def get_balance(user_id, server_id=None):
    """Lấy số tiền hiện có của người dùng"""
    if server_id:
        table_name = get_server_table_name(server_id)
        # Kiểm tra xem bảng có tồn tại không
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if cursor.fetchone() is None:
            create_server_table(server_id)
            
        cursor.execute(f"SELECT balance FROM {table_name} WHERE user_id = ?", (user_id,))
        balance = cursor.fetchone()
        if balance:
            return balance[0]
        return None
    else:
        # Lấy từ bảng users gốc (cho tương thích ngược)
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        balance = cursor.fetchone()
        if balance:
            return balance[0]
        return None

def sync_user_data(user_id, column, value):
    """Đồng bộ dữ liệu người dùng giữa các server cho các cột được chỉ định"""
    if column in SYNC_COLUMNS:
        # Cập nhật trong bảng users gốc
        cursor.execute(f"UPDATE users SET {column} = ? WHERE user_id = ?", (value, user_id))
        
        # Cập nhật trong tất cả các bảng server
        for table_name in get_all_server_tables():
            cursor.execute(f"SELECT user_id FROM {table_name} WHERE user_id = ?", (user_id,))
            if cursor.fetchone():  # Chỉ cập nhật nếu người dùng đã tồn tại trong bảng
                cursor.execute(f"UPDATE {table_name} SET {column} = ? WHERE user_id = ?", (value, user_id))
        
        conn.commit()

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222 or ctx.author.id == 1307765539896033312 or ctx.author.id == 928879945000833095
    return commands.check(predicate)

def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [1147355133622108262, 1152710848284991549, 1079170812709458031, 1207593935359320084, 1215331218124574740,1215331281878130738, 1051454917702848562, 1210296290026455140, 1210417888272318525, 1256198177246285825, 1050649044160094218, 1091208904920281098, 1238177759289806878, 1243264114483138600, 1251418765665505310, 1243440233685712906, 1237810926913323110, 1247072223861280768, 1270031327999164548, 1022533822031601766, 1065348266193063979, 1027622168181350400, 1072536912562241546, 1045395054954565652]
        if ctx.channel.id in allowed_channel_ids:
            return False
        return True
    return commands.check(predicate)

saocaunguyen = "<a:sao2:1193346135138508810>"
tickxanh = "<:hgtt_dung:1186838952544575538>"
tickdo = "<:hgtt_sai:1186839020974657657>"
cash = "<:cash:1191596352422019084>"
fishcoin = "<:fishcoin:1213027788672737300>"
tienhatgiong = "<:timcoin:1192458078294122526>"
caunguyen = "<a:emoji_pray:1367337789481422858>"
caunguyen2 = "<:luhuong:1271360787088146504>"
theguitien = "<:cash:1191596352422019084>"
vevang = "<:vevang:1192461054131847260>"
vekc = "<:vekc:1146756758665175040>"
bank = '<:bankhong_2025:1339490810768527420>'
dungset = '<a:dung1:1340173892681072743>'
saiset = '<a:sai1:1340173872535703562>'

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.guild = None
        self.vevang = None
        self.vekc = None
        self.dk = None
        self.users = None
        self.tienhatgiong = None
        self.theguitien = None
        self.caunguyen = None
        self.chamthan = None
        self.tickdunghong = None
        self.confirm_threshold_choices = [3, 4, 5, 6, 7]
        self.checkpoint_loop.start()
        self.client.loop.create_task(self.setup())

    async def check_command_disabled(self, ctx):  
        guild_id = str(ctx.guild.id)  
        command_name = ctx.command.name.lower()  
        if guild_id in self.client.get_cog('Toggle').toggles:  
            if command_name in self.client.get_cog('Toggle').toggles[guild_id]:  
                if ctx.channel.id in self.client.get_cog('Toggle').toggles[guild_id][command_name]:  
                    await ctx.send(f"Lệnh `{command_name}` đã bị tắt ở kênh này.")  
                    return True  
        return False 

    async def setup(self):
        await self.init_emojis()
        print("Economy đã được fetch thành công")

    async def init_emojis(self):
        self.guild = self.client.get_guild(1090136467541590066)
        self.vevang = await self.guild.fetch_emoji(1192461054131847260)
        self.vekc = await self.guild.fetch_emoji(1146756758665175040)
        self.users = await self.guild.fetch_emoji(1181378307548250163)
        self.dk = await self.guild.fetch_emoji(1181400074127945799)
        self.tienhatgiong = await self.guild.fetch_emoji(1192458078294122526)
        self.theguitien = await self.guild.fetch_emoji(1191596352422019084)
        self.caunguyen = await self.guild.fetch_emoji(1191607516484866098)
        self.chamthan = await self.guild.fetch_emoji(1179452469017858129)
        self.tickdunghong = await self.guild.fetch_emoji(1186838952544575538)

    @commands.command(aliases=["dangky", "dangki", "dk", "DK", "Dk"], description="Đăng ký tài khoản", help="Đăng ký tài khoản")
    async def register(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        guild = self.client.get_guild(1090136467541590066)
        users = await guild.fetch_emoji(1181400074127945799)
        user_id = ctx.author.id
        # Kiểm tra xem kênh có ID là 1147035278465310720 hay không
        if ctx.channel.id == 1147035278465310720:
            await ctx.send(f"Hãy dùng lệnh ở kênh khác!")
        else:
            if not is_registered(user_id):
                cursor.execute(
                    "INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
                conn.commit()
                cursor.execute("UPDATE users SET balance = balance + 200000 WHERE user_id = ?", (user_id,))
                conn.commit()
                await ctx.send(f"{users} **| {ctx.author.display_name} đăng kí tài khoản thành công, bạn được tặng** __**200k**__ {tienhatgiong}")
                cursor.execute(
                    "UPDATE users SET captcha_attempts = 0 WHERE user_id = ?", (user_id,))
                conn.commit()
            else:
                await ctx.send(f"{ctx.author.mention}, bạn đã đăng ký tài khoản rồi!")

    @commands.command(aliases=["CASH", "Cash"], description="xem có bao nhiêu vé")
    async def cash(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        # Kiểm tra xem kênh có ID là 1147035278465310720 hay không
        if ctx.channel.id == 1147035278465310720 or ctx.channel.id == 1207593935359320084:
            return None
        else:
            if not is_registered(ctx.author.id):
                await ctx.send(f"{self.dk} **{ctx.author.display_name}**, bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")
            else:
                cursor.execute(
                    "SELECT num_gold_tickets, num_diamond_tickets, balance, coin_kc, xu_hlw FROM users WHERE user_id = ?", (ctx.author.id,))
                user_result = cursor.fetchone()
                if user_result:
                    num_gold_tickets = user_result[0]
                    num_diamond_tickets = user_result[1]
                    balance = user_result[2]
                    coin_kc = user_result[3]
                    xu_ev = user_result[4]
                    # await ctx.send(f"{list_emoji.card} **| {ctx.author.display_name}** **đang có** **{num_gold_tickets} {vevang}**, __**{balance:,}**__ {tienhatgiong} **và** __**{xu_ev}**__ {list_emoji.xu_event}")
                    if num_diamond_tickets == 0:
                        await ctx.send(f"{list_emoji.card} **| {ctx.author.display_name}** **đang có** **{num_gold_tickets} {vevang}**, __**{balance:,}**__ {tienhatgiong} và __**{xu_ev}**__ {list_emoji.xu_event}")
                    else:
                        await ctx.send(f"{list_emoji.card} **| {ctx.author.display_name}** **đang có** **{num_gold_tickets} {vevang}** **{num_diamond_tickets} {vekc}**, __**{balance:,}**__ {tienhatgiong} và __**{xu_ev}**__ {list_emoji.xu_event}")
                else:
                    return None

    @commands.command(aliases=["GIVE", "Give"], description="gửi tiền cho mọi người")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def give(self, ctx, receiver: discord.User, amount: int):
        if await self.check_command_disabled(ctx):
            return
        if ctx.channel.id == 1215331218124574740 or ctx.channel.id == 1215331281878130738:
            return None
        sender_id = ctx.author.id
        receiver_id = receiver.id
        formatted_amount = "{:,}".format(amount)
        if receiver.bot:
            await ctx.send("Không gửi tiền cho bot.")
            return
        if ctx.author.id == receiver.id:
            await ctx.send("Tự ẻ tự ăn hả???")
            return
        if is_registered(sender_id) and is_registered(receiver_id):
            sender_balance = get_balance(sender_id)
            receiver_balance = get_balance(receiver_id)

            if amount <= 0:
                await ctx.send("Về học lại toán lớp 1 dùm.")
                return
            elif sender_balance is not None and sender_balance < amount:
                await ctx.send("Làm gì còn đủ tiền mà gửi!")
                return

            embed = discord.Embed(title="", description=f"", color=discord.Color.from_rgb(238, 130, 238))  # Màu đỏ
            if ctx.author.avatar:
                avatar_url = ctx.author.avatar.url
            else:
                avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"  
            
            embed.set_author(name=f"Xác nhận chuyển tiền", icon_url=avatar_url)
            embed.add_field(name="", value=f"- **{ctx.author.mention} sẽ gửi {cash} {receiver.mention}:**", inline=False)
            embed.add_field(name="", value=f"``` {formatted_amount} pinkcoin```", inline=False)
            embed._timestamp = datetime.utcnow()

            msg = await ctx.send(embed=embed)
            await msg.add_reaction(tickxanh)  
            await msg.add_reaction(tickdo)  

            def check(reaction, user):
                return user == ctx.author and reaction.message == msg and str(reaction.emoji) in [tickxanh, tickdo]

            try:
                reaction, _ = await self.client.wait_for('reaction_add', timeout=180.0, check=check)
            except TimeoutError:
                embed.color = discord.Color.from_rgb(0, 0, 0)
                embed.description = "Hết thời gian. Giao dịch đã bị huỷ bỏ."
                await msg.edit(embed=embed)
                await asyncio.sleep(5)
                await msg.delete()
                return

            if str(reaction.emoji) == tickxanh:
                cursor.execute(
                    "UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, sender_id))
                cursor.execute(
                    "UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, receiver_id))
                conn.commit()
                await msg.delete()  # Xoá tin nhắn gốc
                mgs5 = await ctx.send(f"ㅤ")  
                await mgs5.edit(content=f"{bank} **{ctx.author.mention}** **đã gửi** __**{formatted_amount}**__ {tienhatgiong} **đến** **{receiver.mention}**.")

            # Ghi log vào kênh log
            # log_channel = self.client.get_channel(1275312675848585280)  
            # if log_channel:
            #     sender_new_balance = get_balance(sender_id)  # Lấy số dư sau khi gửi
            #     receiver_new_balance = get_balance(receiver_id)  # Lấy số dư sau khi nhận
                
            #     log_embed = discord.Embed(
            #         title="Giao dịch chuyển tiền",
            #         color=discord.Color.green()
            #     )
            #     log_embed.add_field(name="Người gửi", value=ctx.author.mention, inline=True)
            #     log_embed.add_field(name="Số tiền", value=f"__**{formatted_amount}**__ {tienhatgiong}", inline=True)
            #     log_embed.add_field(name="Người nhận", value=receiver.mention, inline=True)
            #     log_embed.add_field(name=f"Số dư người gửi:", value=f"__**{sender_balance:,}**__ {tienhatgiong}\n__**{sender_new_balance:,}**__ {tienhatgiong}", inline=True)
            #     log_embed.add_field(name=f"Số dư người nhận:", value=f"__**{receiver_balance:,}**__ {tienhatgiong}\n__**{receiver_new_balance:,}**__ {tienhatgiong}", inline=True)
            #     log_embed._timestamp = datetime.utcnow()
                
            #     await log_channel.send(embed=log_embed)

            # else:
            #     embed.color = 0xff0000  # Màu đỏ
            #     embed.description = "Giao dịch đã bị huỷ bỏ."
            #     await msg.edit(embed=embed)
            #     await asyncio.sleep(5)
            #     await msg.delete()
        else:
            await ctx.send("bạn chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")


    @commands.command(aliases=["PRAY", "Pray"], description="Cầu nguyện")
    @commands.cooldown(1, 900, commands.BucketType.user)
    @is_allowed_channel_check()
    async def pray(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        if ctx.channel.id == 1273769291099144222:
            return

        user_id = ctx.author.id
        row = cursor.execute(
            "SELECT pray_so, pray_time FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
        counter, threshold = row if row else (0, None)

        # Khởi tạo threshold nếu chưa có
        if threshold is None:
            threshold = random.choice(self.confirm_threshold_choices)
            cursor.execute(
                "UPDATE users SET pray_time = ? WHERE user_id = ?",
                (threshold, user_id)
            )
            conn.commit()

        # Nếu vượt ngưỡng → cần xác nhận
        if counter + 1 > threshold:
            confirmed = False
            view = View(timeout=30)
            button = Button(label="Xác nhận cầu nguyện", style=discord.ButtonStyle.green)
            view.add_item(button)

            async def confirm_cb(interaction: discord.Interaction):
                nonlocal confirmed
                if interaction.user.id != user_id:
                    return await interaction.response.send_message(
                        "Chỉ người thực hiện lệnh mới có thể xác nhận.", ephemeral=True
                    )
                confirmed = True
                await interaction.response.defer()

                # Thực hiện pray
                cursor.execute(
                    "UPDATE users SET pray = pray + 1, pray_so = 0 WHERE user_id = ?",
                    (user_id,)
                )
                new_th = random.choice(self.confirm_threshold_choices)
                cursor.execute(
                    "UPDATE users SET pray_time = ? WHERE user_id = ?",
                    (new_th, user_id)
                )
                conn.commit()

                count = cursor.execute(
                    "SELECT pray FROM users WHERE user_id = ?", (user_id,)
                ).fetchone()[0]

                # Xóa prompt và gửi kết quả
                await interaction.message.delete()
                await interaction.followup.send(
                    f"{caunguyen} | **{ctx.author.display_name}** thành tâm sám hối thắp được __**{count}**__ nén nhang! {caunguyen2}"
                )
                view.stop()

            button.callback = confirm_cb

            prompt = await ctx.send(
                view=view
            )
            await view.wait()
            if not confirmed:
                await prompt.delete()

        else:
            # Auto pray
            cursor.execute(
                "UPDATE users SET pray = pray + 1, pray_so = pray_so + 1 WHERE user_id = ?",
                (user_id,)
            )
            conn.commit()
            count = cursor.execute(
                "SELECT pray FROM users WHERE user_id = ?", (user_id,)
            ).fetchone()[0]
            await ctx.send(
                f"{caunguyen} | **{ctx.author.display_name}** thành tâm sám hối thắp được __**{count}**__ nén nhang! {caunguyen2}"
            )

    @pray.error
    async def pray_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            mins, secs = divmod(int(error.retry_after), 60)
            msg = await ctx.send(f"{self.chamthan} | Vui lòng đợi {mins}m{secs}s trước khi cầu nguyện tiếp.")
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
        if ctx.channel.id in (1273769291099144222, 993153068378116127):
            return

        user_id = ctx.author.id
        # Lấy số lần auto và ngưỡng xác nhận
        row = cursor.execute(
            "SELECT work_so, work_time FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        counter, threshold = row if row else (0, None)

        # Nếu chưa có ngưỡng, khởi tạo random 3 hoặc 4
        if threshold is None:
            threshold = random.choice(self.confirm_threshold_choices)
            cursor.execute(
                "UPDATE users SET work_time = ? WHERE user_id = ?",
                (threshold, user_id)
            )
            conn.commit()

        # Kiểm tra xem có cần xác nhận hay không
        if counter + 1 > threshold:
            confirmed = False
            view = View(timeout=30)
            button = Button(label="Xác nhận làm việc", style=discord.ButtonStyle.primary)
            view.add_item(button)

            async def confirm_callback(interaction: discord.Interaction):
                nonlocal confirmed
                if interaction.user.id != user_id:
                    return await interaction.response.send_message(
                        "Chỉ chủ lệnh mới xác nhận được.", ephemeral=True
                    )
                confirmed = True
                await interaction.response.defer()

                # Tạo kết quả work
                earnings = random.randint(1000, 5000)
                work_list = [
                    "đi làm đi~ và được bo",
                    "đi ăn xin và được",
                    "đi bán vé số và kiếm được",
                    "đi lụm ve chai và bán được",
                    "đi chém thuê và được trả công",
                    "ăn trộm tiền của",
                    "ăn cắp tiền của mẹ được",
                    "đi phụ hồ và được trả",
                    "làm thuê cột bịch nước mắm được trả công",
                    "làm bảo vệ và được trả công",
                    "đi móc bọc kiếm được",
                    "đi làm tay vịn và được khách bo",
                ]
                result = random.choice(work_list)

                # Xử lý trộm/ăn xin
                if result.startswith("đi ăn xin") or result.startswith("ăn trộm"):
                    victims = cursor.execute(
                        "SELECT user_id, balance FROM users WHERE balance > 10000 AND user_id != ?", (user_id,)
                    ).fetchall()
                    if victims:
                        victim_id, _ = random.choice(victims)
                        cursor.execute(
                            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                            (earnings, user_id)
                        )
                        cursor.execute(
                            "UPDATE users SET balance = balance - ? WHERE user_id = ?",
                            (earnings, victim_id)
                        )
                        conn.commit()
                        embed = discord.Embed(color=discord.Color.green())
                        embed.description = (
                            f"**{self.tickdunghong} {ctx.author.mention} {result} <@{victim_id}>** "
                            f"__**{earnings:,}**__ {tienhatgiong}"
                        )
                        await interaction.followup.send(embed=embed)
                else:
                    cursor.execute(
                        "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                        (earnings, user_id)
                    )
                    conn.commit()
                    embed = discord.Embed(color=discord.Color.green())
                    embed.description = (
                        f"**{self.tickdunghong} {ctx.author.mention} {result}** "
                        f"__**{earnings:,}**__ {tienhatgiong}"
                    )
                    await interaction.followup.send(embed=embed)

                # Reset counter và ngưỡng mới
                cursor.execute(
                    "UPDATE users SET work_so = 0, work_time = ? WHERE user_id = ?",
                    (random.choice(self.confirm_threshold_choices), user_id)
                )
                conn.commit()

                # Xóa prompt và dừng view
                await interaction.message.delete()
                view.stop()

            button.callback = confirm_callback

            # Gửi prompt và chờ
            prompt = await ctx.send(
                view=view
            )
            await view.wait()
            # Nếu timeout mà chưa confirm, xóa prompt
            if not confirmed:
                await prompt.delete()

        else:
            # Auto work path
            earnings = random.randint(1000, 5000)
            work_list = [
                "đi làm đi~ và được bo",
                "đi ăn xin và được",
                "đi bán vé số và kiếm được",
                "đi lụm ve chai và bán được",
                "đi chém thuê và được trả công",
                "ăn trộm tiền của",
                "ăn cắp tiền của mẹ được",
                "đi phụ hồ và được trả",
                "làm thuê cột bịch nước mắm được trả công",
                "làm bảo vệ và được trả công",
                "đi móc bọc kiếm được",
                "đi làm tay vịn và được khách bo",
            ]
            result = random.choice(work_list)

            if result.startswith("đi ăn xin") or result.startswith("ăn trộm"):
                victims = cursor.execute(
                    "SELECT user_id, balance FROM users WHERE balance > 10000 AND user_id != ?", (user_id,)
                ).fetchall()
                if victims:
                    victim_id, _ = random.choice(victims)
                    cursor.execute(
                        "UPDATE users SET balance = balance + ? WHERE user_id = ?", (earnings, user_id)
                    )
                    cursor.execute(
                        "UPDATE users SET balance = balance - ? WHERE user_id = ?", (earnings, victim_id)
                    )
            else:
                cursor.execute(
                    "UPDATE users SET balance = balance + ? WHERE user_id = ?", (earnings, user_id)
                )

            cursor.execute(
                "UPDATE users SET work_so = work_so + 1 WHERE user_id = ?",
                (user_id,)
            )
            conn.commit()

            await ctx.send(
                f"**{self.tickdunghong} {ctx.author.mention} {result}** __**{earnings:,}**__ {tienhatgiong}"
            )

    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            mins, secs = divmod(int(error.retry_after), 60)
            msg = await ctx.send(
                f"{self.chamthan} | Vui lòng đợi {mins}m{secs}s trước khi làm việc tiếp."
            )
            await asyncio.sleep(2)
            await msg.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error

        
    @commands.command(aliases=["zsettien", "set"], description="set tiền cho người khác")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def settien(self, ctx, amount: int, member: typing.Optional[discord.Member] = None):
        formatted_amount = "{:,}".format(amount)
        
        if member is None:
            # Xác nhận cho toàn bộ người dùng
            msg = await ctx.send(f"Bạn có chắc chắn muốn tặng **{formatted_amount}** {tienhatgiong} cho tất cả người dùng?")
            await msg.add_reaction(dungset)
            await msg.add_reaction(saiset)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [dungset, saiset] and reaction.message.id == msg.id

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                if str(reaction.emoji) == dungset:
                    cursor.execute("UPDATE users SET balance = balance + ?", (amount,))
                    conn.commit()
                    await msg.edit(content=f"**HGTT đã tặng** __**{formatted_amount}**__ {tienhatgiong} **cho tất cả người dùng**")
                else:
                    await msg.edit(content="Lệnh đã bị hủy.")
            except asyncio.TimeoutError:
                await ctx.send("Bạn không phản ứng kịp thời, lệnh đã bị hủy.")

        elif is_registered(member.id):
            # Xác nhận cho người dùng cụ thể
            msg = await ctx.send(f"Bạn có chắc chắn muốn tặng **{formatted_amount}** {tienhatgiong} cho {member.display_name}?")
            await msg.add_reaction(dungset)
            await msg.add_reaction(saiset)

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [dungset, saiset] and reaction.message.id == msg.id

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                if str(reaction.emoji) == dungset:
                    cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, member.id))
                    conn.commit()
                    await msg.edit(content=f"**HGTT đã tặng** __**{formatted_amount}**__ {tienhatgiong} **cho {member.display_name}**")
                else:
                    await msg.edit(content="Lệnh đã bị hủy.")
            except asyncio.TimeoutError:
                await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")
        else:
            await ctx.send("Người dùng chưa đăng kí tài khoản. Bấm `zdk` để đăng kí")


    @commands.command(aliases=["RESETTIEN", "rstien"], description="reset tiền cho người khác")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def resettien(self, ctx, member: typing.Optional[discord.Member] = None):
        if member is None:
            # Gửi yêu cầu xác nhận cho toàn bộ người dùng
            msg = await ctx.send("Bạn có chắc chắn muốn reset tiền cho tất cả người dùng?")

            # Đặt emoji phản ứng cho người dùng lựa chọn
            await msg.add_reaction(dungset)
            await msg.add_reaction(saiset)

            # Xác nhận người dùng phản ứng
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in [dungset, saiset] and reaction.message.id == msg.id

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                if str(reaction.emoji) == dungset:
                    cursor.execute("UPDATE users SET balance = 0")
                    conn.commit()
                    await msg.edit(content="Đã reset tiền cho tất cả người dùng.")
                else:
                    await msg.edit(content="Lệnh đã bị hủy.")
            except asyncio.TimeoutError:
                await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")
        elif is_registered(member.id):
            # Lấy số tiền hiện tại của người dùng
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (member.id,))
            result = cursor.fetchone()

            if result:
                current_balance = result[0]
                # Gửi yêu cầu xác nhận cho người dùng cụ thể
                msg = await ctx.send(
                    f"Bạn có chắc chắn muốn reset tiền cho {member.name}? "
                    f"Số tiền hiện tại của họ là: {current_balance} VNĐ. "
                )

                # Đặt emoji phản ứng cho người dùng lựa chọn
                await msg.add_reaction(dungset)
                await msg.add_reaction(saiset)

                # Xác nhận người dùng phản ứng
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in [dungset, saiset] and reaction.message.id == msg.id

                try:
                    reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=check)
                    if str(reaction.emoji) == dungset:
                        cursor.execute("UPDATE users SET balance = 0 WHERE user_id = ?", (member.id,))
                        conn.commit()
                        await msg.edit(content=f"Đã reset tiền cho {member.display_name}.")
                    else:
                        await msg.edit(content="Lệnh đã bị hủy.")
                except asyncio.TimeoutError:
                    await msg.edit(content="Bạn không phản ứng kịp thời, lệnh đã bị hủy.")
            else:
                await msg.edit(content="Không tìm thấy thông tin tài khoản của người dùng.")
        else:
            await ctx.send("Người dùng chưa đăng kí tài khoản.")

    @tasks.loop(hours=2)  # Lặp lại sau mỗi 10 phút
    async def checkpoint_loop(self):
        try:
            cursor.execute('PRAGMA wal_checkpoint(FULL);')
            print("Checkpoint đã được thực hiện tự động!")
        except Exception as e:
            print(f"Có lỗi xảy ra khi thực hiện checkpoint tự động: {e}")

    @commands.command(aliases=["NHAPDL", "nhapdl"], description="cập nhật database")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def nhapdulieu(self, ctx):
        try:
            # Thực hiện checkpoint thủ công
            cursor.execute('PRAGMA wal_checkpoint(FULL);')
            await ctx.send("Cập nhật database thành công!")
        except Exception as e:
            await ctx.send(f"Có lỗi xảy ra: {e}")

    @checkpoint_loop.before_loop
    async def before_checkpoint(self):
        await asyncio.sleep(6000)  # Đợi 10 phút trước khi bắt đầu lặp
        await self.client.wait_until_ready()