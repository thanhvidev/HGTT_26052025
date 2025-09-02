import asyncio
import discord
import sqlite3
import random
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from Commands.Mod.list_emoji import list_emoji

import pytz

# conn = sqlite3.connect('economy.db', check_same_thread=False)
# cursor = conn.cursor()
# Kết nối và tạo bảng trong SQLite
conn = sqlite3.connect('economy.db', isolation_level=None)
cursor = conn.cursor()
conn.execute('pragma journal_mode=wal')

def is_registered(user_id):
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone() is not None

def is_guild_owner_or_bot_owner():
    async def predicate(ctx):
        return ctx.author == ctx.guild.owner or ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222 or ctx.author.id == 1307765539896033312 or ctx.author.id == 928879945000833095 or ctx.author.id == 1242425610303836251
    return commands.check(predicate)

def is_daily_channel():
    async def predicate(ctx):
        allowed_channel_ids = [1147355133622108262, 1026627301573677147, 1035183712582766673, 1090897131486842990, 1213122881802997770]
        if ctx.channel.id not in allowed_channel_ids:
            await ctx.send(f"{dauxdo} **Dùng lệnh** **`zquest`** [__**ở đây**__](<https://discord.com/channels/832579380634451969/1147355133622108262>)")
            return False
        return True
    return commands.check(predicate)

def is_staff():
    async def predicate(ctx):
        guild_owner = ctx.author == ctx.guild.owner
        bot_owner = ctx.author.id == 573768344960892928 or ctx.author.id == 1006945140901937222
        specific_role = any(role.id == 1113463122515214427 for role in ctx.author.roles)
        return guild_owner or bot_owner or specific_role
    return commands.check(predicate)

def format_number(num):  
    if num >= 1000:  
        return f"{num // 1000}k"  
    return str(num) 

quest = "<:scroll:1245071210157576252>"
tienhatgiong = "<:timcoin:1192458078294122526>"
tickxanh = "<a:quest_done:1362252595544064286>"
lich = "<:quest_so:1362252580868194304>"
bongden = "<a:den_quest:1295397844152488006>"
cham = "<:muiten_quest:1362254110383931493>"
cham1 = "<:muiten_quest:1362254110383931493>"
dauxdo = "<a:hgtt_check:1246910030444495008>"
benphai = "<:phai_quest:1314667889525129286>"

class Quest(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.voice_times = {}
        self.update_quest_time.start()
        # self.check_quests.start()
        self.quest_reset.start()

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
    async def on_message(self, message):
        user_id = message.author.id
        if not is_registered(user_id):
            return
        cursor.execute("SELECT quest, quest_mess, quest_image FROM users WHERE user_id = ?", (user_id,))
        quest_data = cursor.fetchone()
        if quest_data:
            quest, quest_mess, quest_image = quest_data
            if quest:
                quest_dict = eval(quest)
                # quest_dict = eval(quest_data[0]) 
                if message.channel.id in {quest_dict.get('message_image', 0)}: 
                    if message.attachments: 
                        if all(att.content_type and att.content_type.startswith("image/") for att in message.attachments):  
                            cursor.execute("UPDATE users SET quest_image = 1 WHERE user_id = ?", (user_id,))
                            conn.commit()
                        else:
                            return  
                    else:
                        return 
                elif message.channel.id in {quest_dict.get('message_channel', 0)}:
                    if quest_data and quest_data[0]:
                        cursor.execute("UPDATE users SET quest_mess = quest_mess + 1 WHERE user_id = ?", (user_id,))
                        conn.commit()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        user_id = member.id
        if not is_registered(user_id):
            return
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(timezone)
        cursor.execute("SELECT quest FROM users WHERE user_id = ?", (user_id,))
        existing_quest = cursor.fetchone()
        if existing_quest and existing_quest[0]:
            if before.channel is None and after.channel is not None:
                self.voice_times[user_id] = now
            elif before.channel is not None and after.channel is None:
                if user_id in self.voice_times:
                    join_time = self.voice_times.pop(user_id)
                    if not before.self_deaf:
                        time_spent = round((now - join_time).total_seconds() / 3600, 2)
                        cursor.execute("UPDATE users SET quest_time = quest_time + ? WHERE user_id = ?", (time_spent, user_id))
                        conn.commit()

    @tasks.loop(minutes=1)
    async def update_quest_time(self):
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(timezone)
        for user_id in list(self.voice_times):
            cursor.execute("SELECT quest FROM users WHERE user_id = ?", (user_id,))
            existing_quest = cursor.fetchone()
            if existing_quest and existing_quest[0]:  # Kiểm tra xem cột "quest" có dữ liệu hay không
                join_time = self.voice_times[user_id]
                time_spent = round((now - join_time).total_seconds() / 3600, 2)  
                cursor.execute("SELECT quest_time FROM users WHERE user_id = ?", (user_id,))
                existing_time = cursor.fetchone()
                if existing_time:
                    new_time = round(existing_time[0] + time_spent, 2)
                    cursor.execute("UPDATE users SET quest_time = ? WHERE user_id = ?", (new_time, user_id))
                    conn.commit()
                # Cập nhật lại thời gian bắt đầu
                self.voice_times[user_id] = now

    @update_quest_time.before_loop
    async def before_update_quest_time(self):
        await self.client.wait_until_ready()

    @commands.command(aliases=["Q", "q"], description="Nhiệm vụ hàng ngày")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_daily_channel()
    async def quest(self, ctx):
        if await self.check_command_disabled(ctx):
            return
        guild = ctx.guild  
        user_id = ctx.author.id
        cursor.execute("SELECT quest, quest_time, quest_mess, quest_image, quest_time_start FROM users WHERE user_id = ?", (user_id,))
        quest_data = cursor.fetchone()
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(timezone)
        reset_time = datetime(now.year, now.month, now.day, 15, 0) + timedelta(days=1)
        if quest_data:
            quest, quest_time, quest_mess, quest_image, quest_time_start = quest_data
            if quest_time_start:
                quest_time_start = datetime.strptime(quest_time_start, "%Y-%m-%d %H:%M:%S")

            if quest:
                quest_dict = eval(quest)
                is_time_completed = quest_time >= quest_dict.get('voice_time', 0)
                is_mess_completed = quest_mess >= quest_dict.get('messages', 0)
                is_image_completed = quest_image >= quest_dict.get('image', 0)
                
                embed = discord.Embed(title="", color=discord.Color.from_rgb(100,166,236))
                if ctx.author.avatar:
                    avatar_url = ctx.author.avatar.url
                else:
                    avatar_url = "https://cdn.discordapp.com/embed/avatars/0.png"
                embed.set_author(name=f"Nhiệm vụ hàng ngày", icon_url=avatar_url)
                embed.add_field(
                    name="", 
                    value=f"{lich} **Chat** __**{quest_dict.get('messages', 0)} tin**__ tại [__**sảnh chat**__](<https://discord.com/channels/832579380634451969/{quest_dict.get('message_channel', 0)}>)\n {cham} Tiến độ: **{quest_mess}/{quest_dict.get('messages', 0)}**\n {cham1} Phần thưởng: **{format_number(quest_dict.get('balance_mess', 0))} {tienhatgiong} + {quest_dict.get('mess_noel', 0)} {list_emoji.xu_event}**" if not is_mess_completed else f"{lich} **Chat** __**{quest_dict.get('messages', 0)} tin**__ tại [__**sảnh chat**__](<https://discord.com/channels/832579380634451969/{quest_dict.get('message_channel', 0)}>)\n {cham} Tiến độ: {tickxanh}\n {cham1} Phần thưởng: **{format_number(quest_dict.get('balance_mess', 0))} {tienhatgiong} + {quest_dict.get('mess_noel', 0)} {list_emoji.xu_event}**",
                    inline=False
                )
                embed.add_field(
                    name="",
                    value=f"{lich} **Treo voice** __**{quest_dict.get('voice_time', 0)}h**__\n {cham} Tiến độ: **{quest_time}/{quest_dict.get('voice_time', 0)}**\n {cham1} Phần thưởng: **{format_number(quest_dict.get('balance_voice', 0))} {tienhatgiong} + {quest_dict.get('voice_noel', 0)} {list_emoji.xu_event}**" if not is_time_completed else f"{lich} **Treo voice** __**{quest_dict.get('voice_time', 0)}h**__\n {cham} Tiến độ: {tickxanh} \n {cham1} Phần thưởng: **{format_number(quest_dict.get('balance_voice', 0))} {tienhatgiong} + {quest_dict.get('voice_noel', 0)} {list_emoji.xu_event}**",
                    inline=False
                )
                if quest_dict.get('message_image', 0) == 1052625475769471127:
                    embed.add_field(
                        name="",
                        value=f"{lich} **Gửi một ảnh meme vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1052625475769471127>)"if not is_image_completed else f"{lich} **Gửi một ảnh meme vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1052625475769471127>) {tickxanh}",
                        inline=False
                    )
                elif quest_dict.get('message_image', 0) == 1021646306567016498:
                    embed.add_field(
                        name="",
                        value=f"{lich} **Gửi một ảnh đồ ăn vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1021646306567016498>)"if not is_image_completed else f"{lich} **Gửi một ảnh đồ ăn vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1021646306567016498>) {tickxanh}",
                        inline=False)
                    
                embed.add_field(name="", value=f"-# {benphai}Voice nhớ out ra vào lại, kh tắt loa\n-# {benphai}Hoàn thành cả ba + 1 {list_emoji.xu_event}", inline=False)
                icon_url = guild.icon.url if guild.icon else None
                embed.set_footer(text="Nhiệm vụ làm mới vào 14h hằng ngày", icon_url=icon_url)
                await self.check_quests()
                await ctx.send(embed=embed)
            else:
                self.create_new_quest(user_id, ctx)
        else:
            self.create_new_quest(user_id, ctx)

    @quest.error
    async def quest_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = divmod(int(error.retry_after), 60)  # Chia cho 60 để có phút và giây
            formatted_time = f"{remaining_time[0]}m{remaining_time[1]}s"
            message = await ctx.send(f"{dauxdo} | Vui lòng đợi thêm `{formatted_time}` để có thể sử dụng lệnh này!!")
            await asyncio.sleep(2)
            await message.delete()
            await ctx.message.delete()
        elif isinstance(error, commands.CheckFailure):
            pass
        else:
            raise error


    async def check_quests(self):  
        # Lấy danh sách người dùng và nhiệm vụ
        cursor.execute("SELECT user_id, quest, quest_time, quest_mess, quest_image, quest_done, balance FROM users")  
        users = cursor.fetchall()  

        for user in users:  
            user_id, quest_data, quest_time, quest_mess, quest_image, quest_done, balance = user  

            if quest_data:  
                try:
                    # Chuyển đổi dữ liệu nhiệm vụ từ chuỗi sang dictionary
                    quest_dict = eval(quest_data)  
                except Exception as e:
                    print(f"Lỗi khi phân tích dữ liệu nhiệm vụ: {e}")
                    continue
                
                # Kiểm tra điều kiện hoàn thành từng nhiệm vụ
                is_time_completed = quest_time >= quest_dict.get('voice_time', 0)  
                is_mess_completed = quest_mess >= quest_dict.get('messages', 0)  
                is_image_completed = quest_image >= quest_dict.get('image', 0)  
                
                balance_reward = quest_dict.get('balance_voice', 0) + quest_dict.get('balance_mess', 0)
                event_reward = quest_dict.get('voice_noel', 0) + quest_dict.get('mess_noel', 0) + quest_dict.get('img_xu', 0)
                # Kiểm tra nếu quest_done == 0 (chưa hoàn thành nhiệm vụ nào)
                if quest_done == 0:
                    if is_time_completed and is_mess_completed and is_image_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 8 WHERE user_id = ?",   
                                        (balance_reward, event_reward + 1, user_id))  
                        conn.commit()
                    elif is_time_completed and is_mess_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 5 WHERE user_id = ?",   
                                        (quest_dict.get('balance_voice', 0) + quest_dict.get('balance_mess', 0), 
                                        quest_dict.get('voice_noel', 0) + quest_dict.get('mess_noel', 0), user_id))  
                        conn.commit()
                    elif is_time_completed and is_image_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 6 WHERE user_id = ?",   
                                        (quest_dict.get('balance_voice', 0), 
                                        quest_dict.get('voice_noel', 0) + quest_dict.get('img_xu', 0), user_id))  
                        conn.commit()
                    elif is_mess_completed and is_image_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 7 WHERE user_id = ?",   
                                        (quest_dict.get('balance_mess', 0), 
                                        quest_dict.get('mess_noel', 0) + quest_dict.get('img_xu', 0), user_id))  
                        conn.commit()
                    elif is_time_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 1 WHERE user_id = ?",   
                                        (quest_dict.get('balance_voice', 0), quest_dict.get('voice_noel', 0), user_id))  
                        conn.commit()
                    elif is_mess_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 2 WHERE user_id = ?",   
                                        (quest_dict.get('balance_mess', 0), quest_dict.get('mess_noel', 0), user_id))  
                        conn.commit()
                    elif is_image_completed:
                        cursor.execute("UPDATE users SET xu_hlw = xu_hlw + ?, quest_done = 3 WHERE user_id = ?",   
                                        (quest_dict.get('img_xu', 0), user_id))  
                        conn.commit()

                # Kiểm tra nếu quest_done == 1 (đã hoàn thành nhiệm vụ time)
                elif quest_done == 1:
                    if is_mess_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 5 WHERE user_id = ?",   
                                        (quest_dict.get('balance_mess', 0), quest_dict.get('mess_noel', 0), user_id))  
                        conn.commit()
                    elif is_image_completed:
                        cursor.execute("UPDATE users SET xu_hlw = xu_hlw + ?, quest_done = 6 WHERE user_id = ?",   
                                        (quest_dict.get('img_xu', 0), user_id))  
                        conn.commit()

                # Kiểm tra nếu quest_done == 2 (đã hoàn thành nhiệm vụ message)
                elif quest_done == 2:
                    if is_image_completed:
                        cursor.execute("UPDATE users SET xu_hlw = xu_hlw + ?, quest_done = 7 WHERE user_id = ?",   
                                        (quest_dict.get('img_xu', 0), user_id))  
                        conn.commit()
                    elif is_time_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 5 WHERE user_id = ?",   
                                        (quest_dict.get('balance_voice', 0), quest_dict.get('voice_noel', 0), user_id))  
                        conn.commit()

                # Kiểm tra nếu quest_done == 3 (đã hoàn thành nhiệm vụ image)
                elif quest_done == 3:
                    if is_time_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 6 WHERE user_id = ?",   
                                        (quest_dict.get('balance_voice', 0), quest_dict.get('voice_noel', 0), user_id))  
                        conn.commit()
                    elif is_mess_completed:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 7 WHERE user_id = ?",   
                                        (quest_dict.get('balance_mess', 0), quest_dict.get('mess_noel', 0), user_id))  
                        conn.commit()
        
                # Kiểm tra nếu tất cả các điều kiện hoàn thành và quest_done < 7
                if is_time_completed and is_mess_completed and is_image_completed and quest_done < 8:
                    if quest_done == 5:
                        cursor.execute("UPDATE users SET xu_hlw = xu_hlw + ?, quest_done = 8 WHERE user_id = ?", (quest_dict.get('img_xu', 0) + 1, user_id))  
                        conn.commit()
                    elif quest_done == 6:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 8 WHERE user_id = ?", (quest_dict.get('balance_mess', 0), quest_dict.get('mess_noel', 0) + 1, user_id))  
                        conn.commit()
                    elif quest_done == 7:
                        cursor.execute("UPDATE users SET balance = balance + ?, xu_hlw = xu_hlw + ?, quest_done = 8 WHERE user_id = ?", (quest_dict.get('balance_voice', 0), quest_dict.get('voice_noel', 0) + 1, user_id))  
                        conn.commit()

    # @check_quests.before_loop
    # async def before_check_quests(self):
    #     await self.client.wait_until_ready()

    def create_new_quest(self, user_id, ctx):
        guild = ctx.guild  
        voice_time = random.choice([1, 2, 3])  
        if voice_time == 1:  
            voice_xu = 5000
            voice_noel = 2  
        elif voice_time == 2:  
            voice_xu = 10000  
            voice_noel = 3
        elif voice_time == 3:   
            voice_xu = 15000  
            voice_noel = 5

        message_channel = 993153068378116127    
        if message_channel == 993153068378116127:  
            messages = random.choice([50, 80, 120])
        else: 
            return  

        if messages == 50:  
            message_xu = 5000
            mess_xu = 2  
        elif messages == 80:  
            message_xu = 10000
            mess_xu = 3
        elif messages == 120:
            message_xu = 15000
            mess_xu = 5

        # Khởi tạo giá trị mặc định cho image
        image = 0  
        img_xu = 0 
        message_channel_image = [1052625475769471127, 1021646306567016498]
        message_image = random.choice(message_channel_image) 

        if message_image == 1052625475769471127:
            image = 1 
            img_xu = 1 
        elif message_image == 1021646306567016498:
            image = 1 
            img_xu = 1

        balance_voice = voice_xu  
        balance_mess = message_xu

        quest_data = {
            'voice_time': voice_time,
            'balance_voice': balance_voice,
            'voice_noel': voice_noel,
            'messages': messages,
            'message_channel': message_channel,
            'balance_mess': balance_mess,
            'mess_noel': mess_xu,
            'image': image,
            'message_image': message_image,
            'img_xu': img_xu
        }

        cursor.execute("UPDATE users SET quest = ? WHERE user_id = ?", (str(quest_data), user_id))
        conn.commit()

        embed = discord.Embed(title="", color=discord.Color.from_rgb(100,166,236))
        avatar_url = ctx.author.avatar.url if ctx.author.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
        embed.set_author(name=f"Nhiệm vụ hàng ngày", icon_url=avatar_url)

        embed.add_field(
            name="",
            value=f"{lich} **Chat** __**{messages} tin**__ tại [__**sảnh chat**__](<https://discord.com/channels/832579380634451969/993153068378116127>)\n {cham} Tiến độ: **0/{messages}**\n {cham1} Phần thưởng: **{format_number(balance_mess)} {tienhatgiong} + {mess_xu} {list_emoji.xu_event}**",
            inline=False
        )
        embed.add_field(
            name="",
            value=f"{lich} **Treo voice** __**{voice_time}h**__\n {cham} Tiến độ: **0/{voice_time}**\n {cham1} Phần thưởng: **{format_number(balance_voice)} {tienhatgiong} + {voice_noel} {list_emoji.xu_event}**",
            inline=False
        )
        if message_image == 1052625475769471127:
            embed.add_field(
                name="",
                value=f"{lich} **Gửi một ảnh meme vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1052625475769471127>)",
                inline=False
            )
        elif message_image == 1021646306567016498:
            embed.add_field(
                name="",
                value=f"{lich} **Gửi một ảnh đồ ăn vào** [__**đây**__](<https://discord.com/channels/832579380634451969/1021646306567016498>)",
                inline=False
            )
        embed.add_field(name="", value=f"-# {benphai}Voice nhớ out ra vào lại, kh tắt loa\n-# {benphai}Hoàn thành cả ba + 1 {list_emoji.xu_event}", inline=False)
        icon_url = guild.icon.url if guild.icon else None
        embed.set_footer(text="Nhiệm vụ làm mới vào 14h hằng ngày", icon_url=icon_url)

        asyncio.run_coroutine_threadsafe(ctx.send(embed=embed), self.client.loop)


    def cog_unload(self):
        self.quest_reset.cancel()

    @tasks.loop(minutes=1)
    async def quest_reset(self):
        timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        now = datetime.now(timezone)
        if now.hour == 14 and now.minute == 0: 
            cursor.execute("UPDATE users SET quest = '', quest_time = 0, quest_mess = 0, quest_image = 0, quest_time_start = '', quest_done = 0")
            conn.commit()

    @quest_reset.before_loop
    async def before_quest_reset(self):
        await self.client.wait_until_ready()

    @commands.command(aliases=["RSQUEST", "Rsquest"], description="reset quest")
    @commands.cooldown(1, 2, commands.BucketType.user)
    @is_guild_owner_or_bot_owner()
    async def rsquest(self, ctx):
        cursor.execute("UPDATE users SET quest = '', quest_time = 0, quest_mess = 0, quest_image = 0, quest_time_start = '', quest_done = 0")
        conn.commit()
        await ctx.send("Đã reset quest của tất cả người dùng")

    # async def notify_completion(self, user_id, reward, quest_type, goal):
    #     channel = self.client.get_channel(NOTIFY_CHANNEL_ID)
    #     if channel:
    #         user_obj = await self.client.fetch_user(user_id)
    #         if user_obj:
    #             user_name = user_obj.name
    #             if quest_type == "voice":
    #                 await channel.send(f"**{user_name}** đã hoàn thành nhiệm vụ treo voice __**{goal}**__ giờ! và nhận được {reward} {tienhatgiong}")
    #             elif quest_type == "messages":
    #                 await channel.send(f"**{user_name}** đã hoàn thành nhiệm vụ chat __**{goal}**__ tin nhắn và nhận được {reward} {tienhatgiong}")
