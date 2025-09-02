import asyncio
import json
import discord
import random
import sqlite3
import datetime
from discord.ext import commands
import datetime
import pytz

# Kết nối và tạo bảng trong SQLite
# conn = sqlite3.connect('economy.db', isolation_level=None)
# conn.execute('pragma journal_mode=wal')
# cursor = conn.cursor()

def load_random_chance():
    with open('ve.json', 'r') as f:
        data = json.load(f)
        return data.get('random_chance', 0.3)  # Default to 0.3 if not found

random_chance = load_random_chance()

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222 or ctx.author.id == 1307765539896033312 or ctx.author.id == 928879945000833095 or ctx.author.id == 962627128204075039
    return commands.check(predicate)

conn = sqlite3.connect('economy.db')
cursor = conn.cursor()

# Tạo bảng ve_database nếu chưa tồn tại
cursor.execute('''CREATE TABLE IF NOT EXISTS ve_database (
                  id INTEGER PRIMARY KEY,
                  num_gold_tickets_available INTEGER DEFAULT 3385,
                  num_diamond_tickets_available INTEGER DEFAULT 55,
                  quantity_tickets INTEGER DEFAULT 0,
                  tong_tickets INTEGER DEFAULT 0,
                  daily_keo INTEGER DEFAULT 0,
                  daily_bonus1 INTEGER DEFAULT 0,
                  daily_bonus2 INTEGER DEFAULT 0,
                  daily_bonus3 INTEGER DEFAULT 0,
                  daily_bonus4 INTEGER DEFAULT 0,
                  daily_nglieu1 INTEGER DEFAULT 0,
                  daily_nglieu2 INTEGER DEFAULT 0,
                  daily_nglieu3 INTEGER DEFAULT 0,
                  daily_nglieu4 INTEGER DEFAULT 0
               )''')
conn.commit()

# Cập nhật bảng ve_database chỉ khi chưa có dữ liệu
cursor.execute('INSERT OR IGNORE INTO ve_database (id, num_gold_tickets_available, num_diamond_tickets_available) VALUES (?, ?, ?)',
               (1, 3385, 55))
conn.commit()

def is_registered(user_id):  # Hàm kiểm tra xem người dùng đã được đăng ký hay chưa
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

vevang = "<:vevang:1192461054131847260>"
vekc = "<:vekc:1146756758665175040>"

trungvekc = [20, 40, 55, 70, 80, 100, 120, 140, 155, 170, 190, 210, 230, 250, 270, 290, 300, 320, 350, 360, 380, 390, 420, 440, 460, 480, 490, 500, 520, 540, 560,580, 600, 620, 640, 660, 680, 700, 720, 740, 760, 780, 800, 820, 840, 860, 880, 900, 920, 940, 960, 980, 1000]

class Ve(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.allowed_channel_id = 993153068378116127

    @commands.Cog.listener()
    async def on_message(self, message):
        global user_last_ticket_received
        
        if message.author.bot or message.channel.id != self.allowed_channel_id:
            return
        if not is_registered(message.author.id):
            return
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        now_vietnam = datetime.datetime.now(timezone)

        if now_vietnam.hour == 14 and now_vietnam.minute == 0:
            cursor.execute('UPDATE ve_database SET quantity_tickets = 0')
            conn.commit()
            cursor.execute('UPDATE users SET daily_tickets = 0')
            conn.commit()

        if random.random() < random_chance:
            user_id = message.author.id
            trung_ve = tao_lenh_tang_ve(user_id)
            if trung_ve == "Vé vàng":
                await message.add_reaction(vevang)
            elif trung_ve == "Vé kim cương":
                await message.add_reaction(vekc)
                
    @commands.command(aliases=["TILE", "Tile"])
    @is_guild_owner_or_bot_owner()
    async def tile(self, ctx, chance: float):
        if 0 <= chance <= 1:
            global random_chance
            random_chance = chance
            with open('ve.json', 'r') as f:
                data = json.load(f)
            data['random_chance'] = chance
            with open('ve.json', 'w') as f:
                json.dump(data, f, indent=4)
            await ctx.send(f"Đã cập nhật random_chance thành {chance}")
        else:
            await ctx.send("Giá trị chance phải từ 0 đến 1")
    

def tao_lenh_tang_ve(user_id):
    cursor.execute(
        'SELECT num_gold_tickets_available, num_diamond_tickets_available, quantity_tickets, tong_tickets FROM ve_database')
    ve_data = cursor.fetchone()

    if ve_data:
        num_gold_tickets_available, num_diamond_tickets_available, quantity_tickets, tong_tickets = ve_data
        # Kiểm tra nếu daily_tickets của người dùng đã đạt đến 2, thì không cho họ nhận thêm vé
        cursor.execute(
            'SELECT daily_tickets, kimcuong FROM users WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()
        danh_sach_3_ve_ngay = [1021383533178134620, 1110815562910670890]
        danh_sach_cam_user_id = [1043086185557393429, 758208203019517972, 893690187501166613, 1173834427667861616, 988714712961286144, 1019284062294253659, 840058737191288832, 852692490468458566]
        if user_data and (user_id in danh_sach_3_ve_ngay) and user_data[0] >= 4:
            return None
        elif user_id in danh_sach_cam_user_id:
            return None
        elif user_data and user_data[0] >= 3:
            return None

        if random.random() < 0.1 and num_gold_tickets_available > 0 and quantity_tickets < 50:
            new_num_gold_tickets = num_gold_tickets_available - 1
            new_quantity_tickets = quantity_tickets + 1
            new_tong_tickets = tong_tickets + 1
            cursor.execute('UPDATE ve_database SET num_gold_tickets_available = ?, quantity_tickets = ?, tong_tickets = ?',
                           (new_num_gold_tickets, new_quantity_tickets, new_tong_tickets,))
            cursor.execute(
                'UPDATE users SET num_gold_tickets = num_gold_tickets + 1, daily_tickets = daily_tickets + 1, kimcuong = kimcuong +1 WHERE user_id = ?', (user_id,))
            conn.commit()
            return "Vé vàng"
        # Kiểm tra nếu tong_tickets đạt một trong các giá trị đã nêu, thì vé tiếp theo là vekc
        elif tong_tickets in trungvekc and num_diamond_tickets_available > 0 and quantity_tickets < 50:
            new_num_diamond_tickets = num_diamond_tickets_available - 1
            new_quantity_tickets = quantity_tickets + 1  # Thêm 1 vào quantity_tickets
            new_tong_tickets = tong_tickets + 1  # Thêm 1 vào tong_tickets
            cursor.execute('UPDATE ve_database SET num_diamond_tickets_available = ?, quantity_tickets = ?, tong_tickets = ?',
                           (new_num_diamond_tickets, new_quantity_tickets, new_tong_tickets,))
            cursor.execute(
                'UPDATE users SET num_diamond_tickets = num_diamond_tickets + 1, daily_tickets = daily_tickets + 1, kimcuong = kimcuong + 1 WHERE user_id = ?', (user_id,))
            conn.commit()
            return "Vé kim cương"
    else:
        return None