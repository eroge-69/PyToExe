import discord
import asyncio
import tkinter as tk
from tkinter import messagebox, StringVar
import threading
import aiohttp
import json
import requests
import re
import time
import base64

class DiscordServerCopier:
    def __init__(self):
        self.token = None
        self.source_guild_id = None
        self.target_guild_id = None
        self.headers = None
        self.setup_gui()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("AdapteShop Sunucu Kopyalama")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#4c44c7") 

        title_label = tk.Label(self.root, text="AdapteShop", font=("Arial", 36, "bold"), bg="#4c44c7", fg="#FFFFFF")
        title_label.pack(pady=(20, 0))

        source_label = tk.Label(self.root, text="Daha Fazlası İçin: discord.gg/adapteshop", font=("Arial", 10), bg="#4c44c7", fg="#FFFFFF")
        source_label.pack(pady=(0, 20))

        token_frame = tk.Frame(self.root, bg="#4c44c7")
        token_frame.pack(pady=10)
        
        token_label = tk.Label(token_frame, text="Discord Kullanıcı Token:", bg="#4c44c7", fg="#FFFFFF")
        token_label.pack(side=tk.LEFT, padx=5)
        
        self.token_var = StringVar()
        token_entry = tk.Entry(token_frame, textvariable=self.token_var, width=40, show="*")
        token_entry.pack(side=tk.LEFT)

        source_frame = tk.Frame(self.root, bg="#4c44c7")
        source_frame.pack(pady=10)
        
        source_label = tk.Label(source_frame, text="Kopyalanacak Sunucu ID:", bg="#4c44c7", fg="#FFFFFF")
        source_label.pack(side=tk.LEFT, padx=5)
        
        self.source_var = StringVar()
        source_entry = tk.Entry(source_frame, textvariable=self.source_var, width=25)
        source_entry.pack(side=tk.LEFT)

        target_frame = tk.Frame(self.root, bg="#4c44c7")
        target_frame.pack(pady=10)
        
        target_label = tk.Label(target_frame, text="Yapıştırılacak Sunucu ID:", bg="#4c44c7", fg="#FFFFFF")
        target_label.pack(side=tk.LEFT, padx=5)
        
        self.target_var = StringVar()
        target_entry = tk.Entry(target_frame, textvariable=self.target_var, width=25)
        target_entry.pack(side=tk.LEFT)

        self.status_var = StringVar()
        self.status_var.set("Hazır")
        status_label = tk.Label(self.root, textvariable=self.status_var, bg="#4c44c7", fg="#43B581")
        status_label.pack(pady=10)

        self.progress_var = StringVar()
        self.progress_var.set("")
        progress_label = tk.Label(self.root, textvariable=self.progress_var, bg="#4c44c7", fg="#FFFFFF")
        progress_label.pack(pady=5)

        start_button = tk.Button(
            self.root, 
            text="Kopyalamayı Başlat", 
            command=self.start_copying,
            bg="#7289DA",
            fg="#FFFFFF",
            relief=tk.FLAT,
            padx=10,
            pady=5
        )
        start_button.pack(pady=20)

        self.root.mainloop()        

    def start_copying(self):
        self.token = self.token_var.get()
        try:
            self.source_guild_id = self.source_var.get()
            self.target_guild_id = self.target_var.get()
        except ValueError:
            messagebox.showerror("Hata", "Sunucu ID'leri sayı olmalıdır!")
            return
        
        if not self.token or not self.source_guild_id or not self.target_guild_id:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
            return
        
        self.headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9007 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36"
        }
        
        try:
            response = requests.get("https://discord.com/api/v9/users/@me", headers=self.headers)
            if response.status_code != 200:
                messagebox.showerror("Hata", "Geçersiz token! Lütfen doğru token girdiğinizden emin olun.")
                return
            
            user_data = response.json()
            self.status_var.set(f"{user_data.get('username', '')}#{user_data.get('discriminator', '')} olarak giriş yapıldı!")
        except Exception as e:
            messagebox.showerror("Hata", f"Token kontrolü sırasında hata: {str(e)}")
            return
        
        try:
            response = requests.get(f"https://discord.com/api/v9/guilds/{self.source_guild_id}", headers=self.headers)
            if response.status_code != 200:
                messagebox.showerror("Hata", "Kaynak sunucu bulunamadı veya erişim yetkiniz yok!")
                return
            source_guild_name = response.json()["name"]
            
            response = requests.get(f"https://discord.com/api/v9/guilds/{self.target_guild_id}", headers=self.headers)
            if response.status_code != 200:
                messagebox.showerror("Hata", "Hedef sunucu bulunamadı veya erişim yetkiniz yok!")
                return
            target_guild_name = response.json()["name"]
            
            self.status_var.set(f"Kopyalama başladı: {source_guild_name} → {target_guild_name}")
        except Exception as e:
            messagebox.showerror("Hata", f"Sunucu kontrolü sırasında hata: {str(e)}")
            return

        threading.Thread(target=self.run_copier, daemon=True).start()

    def run_copier(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.copy_server())

    async def copy_server(self):
        try:
            async with aiohttp.ClientSession() as session:
                # Önce hedef sunucudaki everyone rolünün ID'sini alalım
                self.root.after(0, lambda: self.progress_var.set("Hedef sunucudaki roller kontrol ediliyor..."))
                target_everyone_id = await self.get_everyone_role_id(session)
                
                self.root.after(0, lambda: self.progress_var.set("Roller alınıyor..."))
                roles = await self.get_roles(session)

                self.root.after(0, lambda: self.progress_var.set("Hedef sunucudaki roller temizleniyor..."))
                await self.delete_roles(session)
                
                self.root.after(0, lambda: self.progress_var.set("Roller oluşturuluyor..."))
                role_mapping = await self.create_roles(session, roles)
                
                # Kaynak sunucudaki everyone rolünü target_everyone_id ile eşleştirelim
                source_everyone_id = await self.get_everyone_role_id(session, is_source=True)
                if source_everyone_id and target_everyone_id:
                    role_mapping[source_everyone_id] = {"id": target_everyone_id}
                
                self.root.after(0, lambda: self.progress_var.set("Kanallar alınıyor..."))
                channels = await self.get_channels(session)
                
                self.root.after(0, lambda: self.progress_var.set("Hedef sunucudaki kanallar temizleniyor..."))
                await self.delete_channels(session)
                
                self.root.after(0, lambda: self.progress_var.set("Kategoriler oluşturuluyor..."))
                category_mapping = await self.create_categories(session, channels, role_mapping)
                
                self.root.after(0, lambda: self.progress_var.set("Kanallar oluşturuluyor..."))
                await self.create_channels(session, channels, category_mapping, role_mapping)
                
                self.root.after(0, lambda: self.progress_var.set("Emojiler alınıyor..."))
                emojis = await self.get_emojis(session)
                
                self.root.after(0, lambda: self.progress_var.set("Hedef sunucudaki emojiler temizleniyor..."))
                await self.delete_emojis(session)
                
                self.root.after(0, lambda: self.progress_var.set("Emojiler oluşturuluyor..."))
                await self.create_emojis(session, emojis)
                
                self.root.after(0, lambda: self.status_var.set("Kopyalama tamamlandı!"))
                self.root.after(0, lambda: self.progress_var.set(""))
                
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Hata: {str(e)}"))

    async def get_everyone_role_id(self, session, is_source=False):
        guild_id = self.source_guild_id if is_source else self.target_guild_id
        async with session.get(
            f"https://discord.com/api/v9/guilds/{guild_id}/roles",
            headers=self.headers
        ) as response:
            if response.status == 200:
                roles = await response.json()
                for role in roles:
                    if role['name'] == '@everyone':
                        return role['id']
            return None

    async def get_roles(self, session):
        async with session.get(
            f"https://discord.com/api/v9/guilds/{self.source_guild_id}/roles",
            headers=self.headers
        ) as response:
            if response.status == 200:
                roles = await response.json()
                return sorted([r for r in roles if r['name'] != '@everyone'], key=lambda r: r['position'], reverse=True)
            else:
                error = await response.text()
                raise Exception(f"Rolleri alma hatası: {error}")

    async def delete_roles(self, session):
        async with session.get(
            f"https://discord.com/api/v9/guilds/{self.target_guild_id}/roles",
            headers=self.headers
        ) as response:
            if response.status == 200:
                roles = await response.json()
                for role in roles:
                    if role['name'] != '@everyone':
                        self.root.after(0, lambda r=role: self.progress_var.set(f"Rol siliniyor: {r['name']}"))
                        try:
                            async with session.delete(
                                f"https://discord.com/api/v9/guilds/{self.target_guild_id}/roles/{role['id']}",
                                headers=self.headers
                            ) as del_response:
                                await asyncio.sleep(0.5)
                                if del_response.status not in [200, 204]:
                                    self.root.after(0, lambda r=role: self.progress_var.set(f"Rol silinemedi: {r['name']}"))
                        except:
                            pass
            else:
                error = await response.text()
                raise Exception(f"Rolleri silme hatası: {error}")

    async def create_roles(self, session, roles):
        role_mapping = {}
        for role in roles:
            self.root.after(0, lambda r=role: self.progress_var.set(f"Rol oluşturuluyor: {r['name']}"))
            try:
                color = role.get('color', 0)
                
                role_data = {
                    "name": role["name"],
                    "permissions": role["permissions"],
                    "color": color,
                    "hoist": role["hoist"],
                    "mentionable": role["mentionable"]
                }
                
                async with session.post(
                    f"https://discord.com/api/v9/guilds/{self.target_guild_id}/roles",
                    headers=self.headers,
                    json=role_data
                ) as response:
                    if response.status == 200:
                        new_role = await response.json()
                        role_mapping[role["id"]] = new_role
                        await asyncio.sleep(0.5)
                    else:
                        self.root.after(0, lambda r=role: self.progress_var.set(f"Rol oluşturulamadı: {r['name']}"))
            except Exception as e:
                self.root.after(0, lambda r=role, err=e: self.progress_var.set(f"Rol oluşturma hatası {r['name']}: {str(err)}"))
        return role_mapping

    async def get_channels(self, session):
        async with session.get(
            f"https://discord.com/api/v9/guilds/{self.source_guild_id}/channels",
            headers=self.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Kanalları alma hatası: {error}")

    async def delete_channels(self, session):
        async with session.get(
            f"https://discord.com/api/v9/guilds/{self.target_guild_id}/channels",
            headers=self.headers
        ) as response:
            if response.status == 200:
                channels = await response.json()
                for channel in channels:
                    self.root.after(0, lambda c=channel: self.progress_var.set(f"Kanal siliniyor: {c['name']}"))
                    try:
                        async with session.delete(
                            f"https://discord.com/api/v9/channels/{channel['id']}",
                            headers=self.headers
                        ) as del_response:
                            await asyncio.sleep(0.5)
                            if del_response.status not in [200, 204]:
                                self.root.after(0, lambda c=channel: self.progress_var.set(f"Kanal silinemedi: {c['name']}"))
                    except:
                        pass
            else:
                error = await response.text()
                raise Exception(f"Kanalları silme hatası: {error}")

    async def create_categories(self, session, channels, role_mapping):
        category_mapping = {}
        categories = [c for c in channels if c['type'] == 4]  # 4 = category
        
        for category in categories:
            self.root.after(0, lambda c=category: self.progress_var.set(f"Kategori oluşturuluyor: {c['name']}"))
            try:
                permission_overwrites = self.convert_overwrites(category.get('permission_overwrites', []), role_mapping)
                
                category_data = {
                    "name": category["name"],
                    "type": 4,
                    "permission_overwrites": permission_overwrites,
                    "position": category.get("position", 0)
                }
                
                async with session.post(
                    f"https://discord.com/api/v9/guilds/{self.target_guild_id}/channels",
                    headers=self.headers,
                    json=category_data
                ) as response:
                    if response.status == 201:
                        new_category = await response.json()
                        category_mapping[category["id"]] = new_category
                        await asyncio.sleep(0.5)
                    else:
                        error = await response.text()
                        self.root.after(0, lambda c=category, e=error: self.progress_var.set(f"Kategori oluşturulamadı {c['name']}: {e}"))
            except Exception as e:
                self.root.after(0, lambda c=category, err=e: self.progress_var.set(f"Kategori oluşturma hatası {c['name']}: {str(err)}"))
        
        return category_mapping

    async def create_channels(self, session, channels, category_mapping, role_mapping):
        # Discord izin bayrakları için sabitler
        # https://discord.com/developers/docs/topics/permissions
        SEND_MESSAGES = 0x00000800
        VIEW_CHANNEL = 0x00000400
        ATTACH_FILES = 0x00008000
        EMBED_LINKS = 0x00004000
        READ_MESSAGE_HISTORY = 0x00010000
        USE_EXTERNAL_EMOJIS = 0x00040000
        ADD_REACTIONS = 0x00000040
        CONNECT = 0x00100000
        SPEAK = 0x00200000
        
        # Kanal tiplerine göre filtreleme
        channel_types = {
            0: "Metin",            # Text Channel
            2: "Ses",              # Voice Channel
            5: "Duyuru",           # Announcement Channel 
            15: "Forum",           # Forum Channel
            10: "Duyuru Thread",   # Announcement Thread
            11: "Genel Thread",    # Public Thread
            12: "Özel Thread"      # Private Thread
        }
        
        # Kategori olmayan kanallar
        non_category_channels = [c for c in channels if c['type'] != 4]
        
        for channel in non_category_channels:
            channel_type = channel_types.get(channel['type'], f"Bilinmeyen ({channel['type']})")
            self.root.after(0, lambda c=channel, t=channel_type: self.progress_var.set(f"{t} kanalı oluşturuluyor: {c['name']}"))
            
            try:
                # Özel izin ayarlarını kopyalama
                permission_overwrites = self.convert_overwrites(channel.get('permission_overwrites', []), role_mapping)
                
                # Temel kanal verisi
                channel_data = {
                    "name": channel["name"],
                    "type": channel["type"],
                    "position": channel.get("position", 0),
                    "permission_overwrites": permission_overwrites,
                    "parent_id": category_mapping.get(channel.get("parent_id", ""), {}).get("id", None)
                }
                
                # Kanal tipine göre ek ayarlar
                if channel['type'] == 0:  # Metin kanalı
                    channel_data.update({
                        "topic": channel.get("topic", ""),
                        "nsfw": channel.get("nsfw", False),
                        "rate_limit_per_user": channel.get("rate_limit_per_user", 0),
                        "default_auto_archive_duration": channel.get("default_auto_archive_duration", 60)
                    })
                    
                elif channel['type'] == 2:  # Ses kanalı
                    channel_data.update({
                        "bitrate": channel.get("bitrate", 64000),
                        "user_limit": channel.get("user_limit", 0),
                        "rtc_region": channel.get("rtc_region", None),
                        "video_quality_mode": channel.get("video_quality_mode", 1)
                    })
                    
                elif channel['type'] == 5:  # Duyuru kanalı
                    channel_data.update({
                        "topic": channel.get("topic", ""),
                        "nsfw": channel.get("nsfw", False),
                        "rate_limit_per_user": channel.get("rate_limit_per_user", 0),
                        "default_auto_archive_duration": channel.get("default_auto_archive_duration", 60)
                    })
                    
                elif channel['type'] == 15:  # Forum kanalı
                    channel_data.update({
                        "topic": channel.get("topic", ""),
                        "nsfw": channel.get("nsfw", False),
                        "rate_limit_per_user": channel.get("rate_limit_per_user", 0),
                        "default_auto_archive_duration": channel.get("default_auto_archive_duration", 60),
                        "default_thread_rate_limit_per_user": channel.get("default_thread_rate_limit_per_user", 0),
                    })
                    
                    # Forum özel alanları (sadece varsa ekle)
                    if channel.get("default_reaction_emoji"):
                        channel_data["default_reaction_emoji"] = channel["default_reaction_emoji"]
                    
                    if channel.get("available_tags"):
                        channel_data["available_tags"] = channel["available_tags"]
                    
                    if channel.get("default_sort_order") is not None:
                        channel_data["default_sort_order"] = channel["default_sort_order"]
                    
                    if channel.get("default_forum_layout") is not None:
                        channel_data["default_forum_layout"] = channel["default_forum_layout"]
                
                # Null veya boş değerleri kaldır
                channel_data = {k: v for k, v in channel_data.items() if v is not None}
                if "rtc_region" in channel_data and channel_data["rtc_region"] is None:
                    channel_data.pop("rtc_region")
                
                # Kanal oluşturma isteği
                async with session.post(
                    f"https://discord.com/api/v9/guilds/{self.target_guild_id}/channels",
                    headers=self.headers,
                    json=channel_data
                ) as response:
                    if response.status == 201:
                        await asyncio.sleep(0.5)
                    else:
                        error = await response.text()
                        self.root.after(0, lambda c=channel, t=channel_type, e=error: self.progress_var.set(f"{t} kanalı oluşturulamadı {c['name']}: {e}"))
            except Exception as e:
                self.root.after(0, lambda c=channel, t=channel_type, err=e: self.progress_var.set(f"{t} kanalı oluşturma hatası {c['name']}: {str(err)}"))

    def convert_overwrites(self, overwrites, role_mapping):
        """İzinleri dönüştürür ve @everyone izinlerini de dahil eder"""
        new_overwrites = []
        
        for overwrite in overwrites:
            overwrite_type = overwrite.get('type', 0)
            overwrite_id = overwrite.get('id')
            
            # Rol izinleri
            if overwrite_type == 0 and overwrite_id in role_mapping:
                new_overwrite = {
                    "id": role_mapping[overwrite_id]['id'],
                    "type": 0,
                    "allow": str(overwrite.get('allow', "0")),
                    "deny": str(overwrite.get('deny', "0"))
                }
                new_overwrites.append(new_overwrite)
            
            # @everyone rolü için özel işlem
            elif overwrite_type == 0 and overwrite_id not in role_mapping:
                # everyone rolü ise ve eşleşme yoksa
                if overwrite_id in role_mapping:
                    new_overwrite = {
                        "id": role_mapping[overwrite_id]['id'],
                        "type": 0,
                        "allow": str(overwrite.get('allow', "0")),
                        "deny": str(overwrite.get('deny', "0"))
                    }
                    new_overwrites.append(new_overwrite)
            
            # Kullanıcı izinleri şimdilik atlanıyor
            # Kullanıcı izinlerini de eklemek isterseniz burada 
            # hedef sunucudaki kullanıcıları da kontrol etmek gerekir
        
        return new_overwrites

    async def get_emojis(self, session):
        async with session.get(
            f"https://discord.com/api/v9/guilds/{self.source_guild_id}/emojis",
            headers=self.headers
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error = await response.text()
                raise Exception(f"Emojileri alma hatası: {error}")

    async def delete_emojis(self, session):
        async with session.get(
            f"https://discord.com/api/v9/guilds/{self.target_guild_id}/emojis",
            headers=self.headers
        ) as response:
            if response.status == 200:
                emojis = await response.json()
                for emoji in emojis:
                    self.root.after(0, lambda e=emoji: self.progress_var.set(f"Emoji siliniyor: {e['name']}"))
                    try:
                        async with session.delete(
                            f"https://discord.com/api/v9/guilds/{self.target_guild_id}/emojis/{emoji['id']}",
                            headers=self.headers
                        ) as del_response:
                            await asyncio.sleep(0.5)
                            if del_response.status not in [200, 204]:
                                self.root.after(0, lambda e=emoji: self.progress_var.set(f"Emoji silinemedi: {e['name']}"))
                    except:
                        pass
            else:
                error = await response.text()
                raise Exception(f"Emojileri silme hatası: {error}")

    async def create_emojis(self, session, emojis):
        for emoji in emojis:
            self.root.after(0, lambda e=emoji: self.progress_var.set(f"Emoji oluşturuluyor: {e['name']}"))
            try:
                emoji_id = emoji['id']
                emoji_animated = emoji.get('animated', False)
                emoji_format = 'gif' if emoji_animated else 'png'
                emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.{emoji_format}"
                
                async with session.get(emoji_url) as img_response:
                    if img_response.status == 200:
                        emoji_data = await img_response.read()
                        emoji_base64 = base64.b64encode(emoji_data).decode('utf-8')
                        
                        data = {
                            "name": emoji["name"],
                            "image": f"data:image/{emoji_format};base64,{emoji_base64}"
                        }
                        
                        async with session.post(
                            f"https://discord.com/api/v9/guilds/{self.target_guild_id}/emojis",
                            headers=self.headers,
                            json=data
                        ) as emoji_response:
                            await asyncio.sleep(0.7) 
                            if emoji_response.status != 201:
                                error = await emoji_response.text()
                                self.root.after(0, lambda e=emoji, err=error: self.progress_var.set(f"Emoji oluşturulamadı {e['name']}: {err}"))
                    else:
                        self.root.after(0, lambda e=emoji: self.progress_var.set(f"Emoji indirilemedi: {e['name']}"))
            except Exception as e:
                self.root.after(0, lambda e=emoji, err=e: self.progress_var.set(f"Emoji oluşturma hatası {e['name']}: {str(err)}"))

if __name__ == "__main__":
    DiscordServerCopier()