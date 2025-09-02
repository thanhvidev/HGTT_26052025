import sqlite3
import discord
from discord.ext import commands
import json
from discord.ui import Select, View

def is_allowed_channel_check():
    async def predicate(ctx):
        allowed_channel_ids = [1147355133622108262, 1090897131486842990,
                               1026627301573677147, 1035183712582766673]  # Danh sách ID của các kênh cho phép
        if ctx.channel.id not in allowed_channel_ids:
            await ctx.send("Hãy dùng lệnh `bxh` ở các kênh `<#1147355133622108262>` `<#1090897131486842990>` `<#1026627301573677147>` `<#1035183712582766673>`")
            return False
        return True
    return commands.check(predicate)


conn = sqlite3.connect('economy.db')
cursor = conn.cursor()

vevang = "<:vevang:1192461054131847260>"
tienhatgiong = "<:timcoin:1192458078294122526>"
pray = "<:chaptay:1271360778812919841>"
line = "<a:line:1181341865786740796>"
saocaunguyen = "<:luhuong:1271360787088146504>"
capdoi = "<:capdoi:1272139761532014654>"
nhan_love = '<a:nhan_love:1339523828161708105>'
marry = "<a:hgtt_tim:1096818657864200324>"
fishcoin = "<:fishcoin:1213027788672737300>"
canthu = "<:cauca:1213249056311083148>"
exp = "<a:exp:1214433497528401920>"
mamcay = "<a:diemtaiche:1211410013868789850>"
bot = "<:bxh:1272143014688456726>"
toptop = "<:toptop:1272506399745642496>"
diemlove = "<a:emoji_50:1273622387358957618>"
xulove = "<a:xu_love_2025:1339490786840150087>"

class Bxh(commands.Cog):
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

    @commands.hybrid_command(alises=['TOP', 'Top'], description="Bảng xếp hạng")
    async def top(self, ctx):
        if await self.check_command_disabled(ctx):
            return
          
        embed = discord.Embed(title=f"", description=f"# {toptop} **XEM BẢNG XẾP HẠNG** {toptop}\n{bot} **Hello {ctx.author.mention}, dưới đây là danh mục các bảng xếp hạng trong sv. Mời bạn xem qua nhé!**", color=discord.Color.from_rgb(255, 255, 255))
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211199649667616768/1272512313706020936/5622698.png") 
        user_id = ctx.author.id  
        bxh = BxhSelectMenu(enable_buttons=user_id)
        view = BxhView(bxh)
        await ctx.send(embed=embed, view=view)

class BxhSelectMenu(discord.ui.Select):
    def __init__(self, enable_buttons):
        self.enable_buttons = enable_buttons
        options = [
            discord.SelectOption(label='BXH Valentine', emoji=nhan_love, value='valentine'),
            discord.SelectOption(label='BXH Vé Vàng',
                                 emoji=vevang, value='vevang'),
            discord.SelectOption(
                label='BXH Tiền', emoji=tienhatgiong, value='tienhatgiong'),
            # discord.SelectOption(
            #     label='BXH Xu Cá', emoji=fishcoin, value='xuca'),
            # discord.SelectOption(label='BXH Cần Thủ',
            #                      emoji=canthu, value='canthu'),
            # discord.SelectOption(label='BXH Tái Chế',
            #                      emoji=mamcay, value='taiche'),
            discord.SelectOption(label='BXH Cầu Nguyện',
                                 emoji=pray, value='caunguyen'),
            discord.SelectOption(label='BXH Cặp Đôi',
                                 emoji=capdoi, value='thanmat'),
        ]
        super().__init__(placeholder='Chọn BXH', options=options)

    async def interaction_check(self, interaction: discord.Interaction) ->  bool:
        if interaction.user.id == self.enable_buttons:
            return True
        else:
            await interaction.response.send_message("BXH này do người khác mở", ephemeral=True)
            return False

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == 'valentine':  
            cursor.execute("SELECT * FROM users ORDER BY bxh_love DESC, marry DESC")  
            result = cursor.fetchall()  
            current_user_id = str(interaction.user.id)  
            current_user_data = [  
                row for row in result if str(row[1]) == current_user_id  
            ]  

            if not current_user_data:  
                await interaction.response.send_message("Lỗi")  
                return  

            rankings = {}  
            current_user_marry_data = current_user_data[0][7]
            current_user_tickets = current_user_data[0][39]    
        
            mention1_current, mention2_current = None, None  

            if current_user_marry_data:  # Kiểm tra xem có dữ liệu marry hay không  
                current_user_mentions = current_user_marry_data.split(" đã kết hôn với ")  
                if len(current_user_mentions) == 2:  
                    mention1_current = current_user_mentions[0].strip()  
                    mention2_current = current_user_mentions[1].split(" bằng")[0].strip()  

            rank = 1  
            embed = discord.Embed(  
                title=f"",  
                description=f"# {xulove} 𝑩𝑿𝑯 𝑺𝑲 𝑽𝑨𝑳𝑬𝑵𝑻𝑰𝑵𝑬 {xulove}",  
                color=discord.Color.from_rgb(255, 122, 228)  
            )  

            processed_pairs = set()  # Tạo một set để theo dõi các cặp đã xử lý  

            for row in result:  # Duyệt qua tất cả cặp đôi để tính thứ hạng
                marry_data = row[7]  
                mentions = marry_data.split(" đã kết hôn với ")  
                if len(mentions) == 2:  
                    mention1 = mentions[0].strip()  
                    mention2 = mentions[1].split(" bằng")[0].strip()  

                    sorted_mentions = tuple(sorted([mention1, mention2]))  

                    if sorted_mentions not in processed_pairs:  
                        processed_pairs.add(sorted_mentions)
        
                        rankings[sorted_mentions] = rank  

                        if rank <= 10:  # Chỉ thêm vào embed cho top 10
                            embed.add_field(  
                                name=f"",  
                                value=f"**{rank}**. {mention1} **và** {mention2} : **`{row[39]}`** {nhan_love}",  
                                inline=False  
                            )  
                        rank += 1 

            current_rank = 0
            if mention1_current and mention2_current:  
                sorted_current_mentions = tuple(sorted([mention1_current, mention2_current]))  
                if sorted_current_mentions in rankings:  
                    current_rank = rankings[sorted_current_mentions]
                else:
                    current_rank = rank  # Nếu không trong top 10, xếp họ ở vị trí hiện tại của rank

            embed.set_footer(text=f"Bạn đang ở vị trí: {current_rank} | Điểm: {current_user_tickets}")  

            await interaction.response.edit_message(embed=embed)
        
        elif self.values[0] == 'vevang':
            cursor.execute("SELECT * FROM users ORDER BY kimcuong DESC")
            result = cursor.fetchall()

            current_user_id = str(interaction.user.id)
            current_rank = [
                i + 1 for i, row in enumerate(result) if str(row[1]) == current_user_id]

            current_user_tickets = [row[16]
                                    for row in result if str(row[1]) == current_user_id]
            current_user_tickets = current_user_tickets[0] if current_user_tickets else 0

            embed = discord.Embed(title="", description=f"# {vevang} BXH VÉ {vevang}", color=discord.Color.from_rgb(255, 246, 143))
            embed.set_footer(text=f"Bạn đang ở vị trí: {current_rank[0]} | : {current_user_tickets}")
            for i, row in enumerate(result[:10], 1):
                embed.add_field(
                    name=f"", value=f"**{i}.** <@{row[1]}> : **`{row[16]}`** {vevang}", inline=False)
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == 'tienhatgiong':
            cursor.execute("SELECT * FROM users ORDER BY balance DESC")
            result = cursor.fetchall()

            current_user_id = str(interaction.user.id)
            current_rank = [
                i + 1 for i, row in enumerate(result) if str(row[1]) == current_user_id]

            current_user_tickets = [row[2]
                                    for row in result if str(row[1]) == current_user_id]
            current_user_tickets = current_user_tickets[0] if current_user_tickets else 0

            embed = discord.Embed(title=f"", description=f"# {tienhatgiong} BXH RICHKID {tienhatgiong}", color=discord.Color.from_rgb(242, 205, 255))
            embed.set_footer(text=f"Bạn đang ở vị trí: {current_rank[0]} | : {current_user_tickets}")
            for i, row in enumerate(result[:10], 1):
                formatted_balance = "{:,}".format(row[2])
                embed.add_field(name=f"", value=f"**{i}.** <@{row[1]}> : **`{formatted_balance}`** {tienhatgiong}", inline=False)
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == 'caunguyen':
            cursor.execute("SELECT * FROM users ORDER BY pray DESC")
            result = cursor.fetchall()

            current_user_id = str(interaction.user.id)
            current_rank = [
                i + 1 for i, row in enumerate(result) if str(row[1]) == current_user_id]

            current_user_tickets = [row[17]
                                    for row in result if str(row[1]) == current_user_id]
            current_user_tickets = current_user_tickets[0] if current_user_tickets else 0

            embed = discord.Embed(title=f"", description=f"# {pray} BXH CẦU NGUYỆN {pray}", color=discord.Color.from_rgb(255, 255, 255))
            embed.set_footer(text=f"Bạn đang ở vị trí: {current_rank[0]} | : {current_user_tickets}")
            for i, row in enumerate(result[:10], 1):
                embed.add_field(
                    name=f"", value=f"**{i}.** <@{row[1]}> : **`{row[17]}`** {saocaunguyen}", inline=False)
            await interaction.response.edit_message(embed=embed)

        elif self.values[0] == 'thanmat':  
            cursor.execute("SELECT * FROM users ORDER BY love_marry DESC, marry DESC")  
            result = cursor.fetchall()  
            current_user_id = str(interaction.user.id)  
            current_user_data = [  
                row for row in result if str(row[1]) == current_user_id  
            ]  

            if not current_user_data:  
                await interaction.response.send_message("Lỗi")  
                return  

            rankings = {}  
            current_user_marry_data = current_user_data[0][7]
            current_user_tickets = current_user_data[0][18]    
        
            mention1_current, mention2_current = None, None  

            if current_user_marry_data:  # Kiểm tra xem có dữ liệu marry hay không  
                current_user_mentions = current_user_marry_data.split(" đã kết hôn với ")  
                if len(current_user_mentions) == 2:  
                    mention1_current = current_user_mentions[0].strip()  
                    mention2_current = current_user_mentions[1].split(" bằng")[0].strip()  

            rank = 1  
            embed = discord.Embed(  
                title=f"",  
                description=f"# {capdoi} BXH CẶP ĐÔI {capdoi}",  
                color=discord.Color.from_rgb(255, 255, 255)  
            )  

            processed_pairs = set()  # Tạo một set để theo dõi các cặp đã xử lý  

            for row in result:  # Duyệt qua tất cả cặp đôi để tính thứ hạng
                marry_data = row[7]  
                mentions = marry_data.split(" đã kết hôn với ")  
                if len(mentions) == 2:  
                    mention1 = mentions[0].strip()  
                    mention2 = mentions[1].split(" bằng")[0].strip()  

                    sorted_mentions = tuple(sorted([mention1, mention2]))  

                    if sorted_mentions not in processed_pairs:  
                        processed_pairs.add(sorted_mentions)
        
                        rankings[sorted_mentions] = rank  

                        if rank <= 10:  # Chỉ thêm vào embed cho top 10
                            embed.add_field(  
                                name=f"",  
                                value=f"**{rank}**. {mention1} **và** {mention2} : **`{row[18]}`** {diemlove}",  
                                inline=False  
                            )  
                        rank += 1 

            current_rank = 0
            if mention1_current and mention2_current:  
                sorted_current_mentions = tuple(sorted([mention1_current, mention2_current]))  
                if sorted_current_mentions in rankings:  
                    current_rank = rankings[sorted_current_mentions]
                else:
                    current_rank = rank  # Nếu không trong top 10, xếp họ ở vị trí hiện tại của rank

            embed.set_footer(text=f"Bạn đang ở vị trí: {current_rank} | Điểm: {current_user_tickets}")  

            await interaction.response.edit_message(embed=embed)

        # elif self.values[0] == 'xuca':
        #     cursor.execute("SELECT * FROM users ORDER BY coin_kc DESC")
        #     result = cursor.fetchall()

        #     current_user_id = str(interaction.user.id)
        #     current_rank = [i + 1 for i, row in enumerate(result) if str(row[1]) == current_user_id]

        #     current_user_tickets = [row[22]for row in result if str(row[1]) == current_user_id]
        #     current_user_tickets = current_user_tickets[0] if current_user_tickets else 0

        #     embed = discord.Embed(title=f"{fishcoin} BẢNG XẾP HẠNG XU CÁ {fishcoin}", color=discord.Color.from_rgb(0, 255, 255))
        #     embed.add_field(name="", value=f"{line}{line}{line}{line}{line}{line}{line}{line}", inline=False)
        #     embed.set_footer(text=f"Bạn đang ở vị trí: {current_rank[0]} | Số xu cá: {current_user_tickets}")
        #     for i, row in enumerate(result[:10], 1):
        #         embed.add_field(
        #             name=f"", value=f"**{i}.** <@{row[1]}> : **`{row[22]}`** {fishcoin}", inline=False)
        #     embed.add_field(name="", value=f"{line}{line}{line}{line}{line}{line}{line}{line}", inline=False)
        #     await interaction.response.edit_message(embed=embed)
        # elif self.values[0] == 'canthu':
        #     cursor.execute("SELECT * FROM users ORDER BY exp_fish DESC")
        #     result = cursor.fetchall()

        #     current_user_id = str(interaction.user.id)
        #     current_rank = [
        #         i + 1 for i, row in enumerate(result) if str(row[1]) == current_user_id]

        #     current_user_tickets = [row[27]
        #                             for row in result if str(row[1]) == current_user_id]
        #     current_user_tickets = current_user_tickets[0] if current_user_tickets else 0

        #     embed = discord.Embed(title=f"{exp} BẢNG XẾP HẠNG CẦN THỦ {exp}", color=discord.Color.from_rgb(255, 255, 255))
        #     embed.add_field(name="", value=f"{line}{line}{line}{line}{line}{line}{line}{line}", inline=False)
        #     embed.set_footer(text=f"Bạn đang ở vị trí: {current_rank[0]} | Số cá: {current_user_tickets}")
        #     for i, row in enumerate(result[:10], 1):
        #         embed.add_field(
        #             name=f"", value=f"**{i}.** <@{row[1]}> : **`{row[27]}`** {exp}", inline=False)
        #     embed.add_field(name="", value=f"{line}{line}{line}{line}{line}{line}{line}{line}", inline=False)
        #     await interaction.response.edit_message(embed=embed)
        # elif self.values[0] == 'taiche':
        #     cursor.execute(
        #         "SELECT user_id, kho_ca FROM users ORDER BY exp_fish DESC LIMIT 10")
        #     results = cursor.fetchall()
        #     top_users = []
        #     for result in results:
        #         user_id, kho_ca_json = result
        #         kho_ca = json.loads(kho_ca_json) if kho_ca_json else []
        #         mamcay_quantity = next(
        #             (item.get('quantity', 0) for item in kho_ca if item.get('name') == 'mamcay'), 0)
        #         user = {
        #             "user_id": user_id,
        #             "mamcay_quantity": mamcay_quantity
        #         }
        #         top_users.append(user)

        #     # Sắp xếp danh sách top_users theo quantity của mamcay giảm dần
        #     top_users.sort(key=lambda x: x['mamcay_quantity'], reverse=True)

        #     embed = discord.Embed(title=f"{mamcay} BẢNG XẾP HẠNG TÁI CHẾ {mamcay}", color=discord.Color.from_rgb(255, 255, 255))
        #     embed.add_field(name="", value=f"{line}{line}{line}{line}{line}{line}{line}{line}", inline=False)
        #     for i, user in enumerate(top_users, start=1):
        #         member = interaction.guild.get_member(user['user_id'])
        #         if member:
        #             username = f"<@{user['user_id']}>"
        #         else:
        #             username = f"<@{user['user_id']}>"
        #         embed.add_field(
        #             name="", value=f"**{i}.** {username}: {user['mamcay_quantity']} {mamcay}", inline=False)
        #     embed.add_field(name="", value=f"{line}{line}{line}{line}{line}{line}{line}{line}", inline=False)
        #     await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.send_message("Lỗi")


class BxhView(discord.ui.View):
    def __init__(self, BxhSelectMenu: discord.ui.Select):
        super().__init__(timeout=180)
        self.add_item(BxhSelectMenu)
