import discord
import asyncio
from datetime import datetime
import os
import sys

class VexoraCloner:
    def __init__(self):
        self.client = None
        
    def print_banner(self):
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                            VEXORA DISCORD CLONER                            ║
║                       Professional Server Management                         ║
║                              Version 1.0                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def get_credentials(self):
        print("\n" + "="*60)
        print("SUNUCU KLONLAMA SİSTEMİ")
        print("="*60)
        
        print("\nBot token'ınızı giriniz:")
        token = input("Token: ").strip()
        
        print("\nKopyalanacak sunucu ID'sini giriniz:")
        source_id = input("Sunucu ID: ").strip()
        
        print("\nHedef sunucu ID'sini giriniz (içerik silinecek):")
        target_id = input("Sunucu ID: ").strip()
        
        if not all([token, source_id, target_id]):
            self.log("Eksik bilgi girişi tespit edildi", "ERROR")
            return None
            
        try:
            return token, int(source_id), int(target_id)
        except ValueError:
            self.log("Geçersiz sunucu ID formatı", "ERROR")
            return None
            
    def confirm_operation(self):
        print("\n" + "="*60)
        print("UYARI: KRİTİK İŞLEM")
        print("="*60)
        print("Hedef sunucudaki tüm veriler kalıcı olarak silinecektir.")
        print("Bu işlem geri alınamaz.")
        print("Bu aracı yalnızca sahip olduğunuz sunucularda kullanın.")
        
        while True:
            response = input("\nİşlemi onaylıyor musunuz? (evet/hayır): ").lower()
            if response in ['evet', 'e']:
                return True
            elif response in ['hayır', 'h']:
                return False
            print("Lütfen 'evet' veya 'hayır' yazınız.")
                
    def progress_bar(self, current, total, task):
        if total == 0:
            return
        percent = (current / total) * 100
        bar = "█" * int(percent / 2.5) + "░" * (40 - int(percent / 2.5))
        print(f"\r{task}: [{bar}] {percent:.1f}%", end="", flush=True)
        if current == total:
            print()
            
    async def execute_cloning(self, token, source_id, target_id):
        try:
            # Discord.py versiyonuna göre client oluştur
            try:
                # Yeni versiyon (discord.py 1.5+)
                intents = discord.Intents.default()
                intents.guilds = True
                intents.members = True
                self.client = discord.Client(intents=intents)
                self.log("Discord.py yeni versiyon tespit edildi", "INFO")
            except AttributeError:
                # Eski versiyon (discord.py 1.4 ve altı)
                self.client = discord.Client()
                self.log("Discord.py eski versiyon tespit edildi", "INFO")
            
            @self.client.event
            async def on_ready():
                self.log(f"Bot giriş yaptı: {self.client.user}", "INFO")
                
                source = self.client.get_guild(source_id)
                target = self.client.get_guild(target_id)
                
                if not source:
                    self.log(f"Kaynak sunucu bulunamadı: {source_id}", "ERROR")
                    await self.client.close()
                    return
                    
                if not target:
                    self.log(f"Hedef sunucu bulunamadı: {target_id}", "ERROR")
                    await self.client.close()
                    return
                    
                self.log(f"Kaynak: {source.name} | Hedef: {target.name}", "INFO")
                await self.clone_process(source, target)
                await self.client.close()
                
            await self.client.start(token)
            
        except discord.LoginFailure:
            self.log("Token doğrulama başarısız - Token'ı kontrol edin", "ERROR")
        except discord.HTTPException as e:
            self.log(f"HTTP hatası: {str(e)}", "ERROR")
        except Exception as e:
            self.log(f"Sistem hatası: {str(e)}", "ERROR")
            
    async def clone_process(self, source, target):
        try:
            print("\n" + "="*60)
            self.log("Klonlama işlemi başlatıldı", "PROCESS")
            
            # Sunucu ayarları
            await self.clone_settings(source, target)
            await asyncio.sleep(1)  # Rate limit için bekle
            
            # Rol işlemleri
            await self.process_roles(source, target)
            await asyncio.sleep(2)  # Rate limit için bekle
            
            # Kanal işlemleri
            await self.process_channels(source, target)
            await asyncio.sleep(2)  # Rate limit için bekle
            
            # Emoji işlemleri
            if source.emojis:
                await self.process_emojis(source, target)
            
            print("\n" + "="*60)
            self.log("Klonlama işlemi tamamlandı", "SUCCESS")
            print("="*60)
            
        except Exception as e:
            self.log(f"Klonlama hatası: {str(e)}", "ERROR")
            
    async def clone_settings(self, source, target):
        try:
            self.log("Sunucu ayarları kopyalanıyor...", "PROCESS")
            
            # Sunucu adını kopyala
            if source.name != target.name:
                await target.edit(name=source.name)
                self.log(f"Sunucu adı güncellendi: {source.name}", "SUCCESS")
            
            # Sunucu ikonunu kopyala
            if source.icon:
                try:
                    icon_bytes = await source.icon.read()
                    await target.edit(icon=icon_bytes)
                    self.log("Sunucu ikonu kopyalandı", "SUCCESS")
                except Exception as e:
                    self.log(f"İkon kopyalanamadı: {str(e)}", "WARNING")
            
            # Sunucu bannerını kopyala (premium özellik)
            if hasattr(source, 'banner') and source.banner:
                try:
                    banner_bytes = await source.banner.read()
                    await target.edit(banner=banner_bytes)
                    self.log("Sunucu banner'ı kopyalandı", "SUCCESS")
                except Exception as e:
                    self.log(f"Banner kopyalanamadı: {str(e)}", "WARNING")
                    
        except discord.Forbidden:
            self.log("Sunucu ayarları için yetki yetersiz", "ERROR")
        except Exception as e:
            self.log(f"Sunucu ayarları hatası: {str(e)}", "WARNING")
            
    async def process_roles(self, source, target):
        try:
            # Silme işlemi
            roles_to_delete = [r for r in target.roles if r.name != "@everyone" and not r.managed]
            self.log(f"{len(roles_to_delete)} rol silinecek", "INFO")
            
            for i, role in enumerate(roles_to_delete):
                try:
                    await role.delete(reason="Vexora Cloner - rol silme")
                    self.progress_bar(i + 1, len(roles_to_delete), "Roller siliniyor")
                    await asyncio.sleep(0.5)  # Rate limit
                except discord.Forbidden:
                    self.log(f"Rol silme yetkisi yok: {role.name}", "WARNING")
                except Exception as e:
                    self.log(f"Rol silme hatası: {role.name} - {str(e)}", "WARNING")
                    
            if roles_to_delete:
                print()  # Progress bar için yeni satır
                
            # Oluşturma işlemi
            roles_to_create = [r for r in reversed(source.roles) if r.name != "@everyone" and not r.managed]
            self.log(f"{len(roles_to_create)} rol oluşturulacak", "INFO")
            
            for i, role in enumerate(roles_to_create):
                try:
                    await target.create_role(
                        name=role.name, 
                        permissions=role.permissions,
                        colour=role.colour, 
                        hoist=role.hoist, 
                        mentionable=role.mentionable,
                        reason="Vexora Cloner - rol oluşturma"
                    )
                    self.progress_bar(i + 1, len(roles_to_create), "Roller oluşturuluyor")
                    await asyncio.sleep(0.5)  # Rate limit
                except discord.Forbidden:
                    self.log(f"Rol oluşturma yetkisi yok: {role.name}", "WARNING")
                except Exception as e:
                    self.log(f"Rol oluşturma hatası: {role.name} - {str(e)}", "WARNING")
                    
            if roles_to_create:
                print()  # Progress bar için yeni satır
                
            self.log(f"Rol işlemi tamamlandı", "SUCCESS")
            
        except Exception as e:
            self.log(f"Rol işlemi genel hatası: {str(e)}", "ERROR")
        
    async def process_channels(self, source, target):
        try:
            # Kanal silme
            channels_to_delete = list(target.channels)
            self.log(f"{len(channels_to_delete)} kanal silinecek", "INFO")
            
            for i, channel in enumerate(channels_to_delete):
                try:
                    await channel.delete(reason="Vexora Cloner - kanal silme")
                    self.progress_bar(i + 1, len(channels_to_delete), "Kanallar siliniyor")
                    await asyncio.sleep(0.5)  # Rate limit
                except discord.Forbidden:
                    self.log(f"Kanal silme yetkisi yok: {channel.name}", "WARNING")
                except Exception as e:
                    self.log(f"Kanal silme hatası: {channel.name} - {str(e)}", "WARNING")
                    
            if channels_to_delete:
                print()  # Progress bar için yeni satır
                
            # Kategori oluşturma
            categories_created = 0
            for category in source.categories:
                try:
                    # Rol izinlerini kopyala
                    overwrites = {}
                    for target_obj, permissions in category.overwrites.items():
                        if isinstance(target_obj, discord.Role):
                            new_role = discord.utils.get(target.roles, name=target_obj.name)
                            if new_role:
                                overwrites[new_role] = permissions
                    
                    await target.create_category(
                        name=category.name, 
                        overwrites=overwrites,
                        reason="Vexora Cloner - kategori oluşturma"
                    )
                    categories_created += 1
                    await asyncio.sleep(0.5)  # Rate limit
                except discord.Forbidden:
                    self.log(f"Kategori oluşturma yetkisi yok: {category.name}", "WARNING")
                except Exception as e:
                    self.log(f"Kategori oluşturma hatası: {category.name} - {str(e)}", "WARNING")
                    
            self.log(f"{categories_created} kategori oluşturuldu", "INFO")
            
            # Kanal oluşturma
            all_channels = list(source.text_channels) + list(source.voice_channels)
            created = 0
            
            # Metin kanalları
            for channel in source.text_channels:
                try:
                    category = discord.utils.get(target.categories, name=channel.category.name) if channel.category else None
                    
                    # Rol izinlerini kopyala
                    overwrites = {}
                    for target_obj, permissions in channel.overwrites.items():
                        if isinstance(target_obj, discord.Role):
                            new_role = discord.utils.get(target.roles, name=target_obj.name)
                            if new_role:
                                overwrites[new_role] = permissions
                    
                    new_channel = await target.create_text_channel(
                        name=channel.name, 
                        overwrites=overwrites, 
                        topic=channel.topic,
                        slowmode_delay=channel.slowmode_delay,
                        nsfw=channel.nsfw,
                        reason="Vexora Cloner - metin kanalı oluşturma"
                    )
                    
                    if category:
                        await new_channel.edit(category=category)
                        
                    created += 1
                    self.progress_bar(created, len(all_channels), "Kanallar oluşturuluyor")
                    await asyncio.sleep(0.5)  # Rate limit
                    
                except discord.Forbidden:
                    self.log(f"Metin kanalı oluşturma yetkisi yok: {channel.name}", "WARNING")
                except Exception as e:
                    self.log(f"Metin kanalı oluşturma hatası: {channel.name} - {str(e)}", "WARNING")
                    
            # Ses kanalları
            for channel in source.voice_channels:
                try:
                    category = discord.utils.get(target.categories, name=channel.category.name) if channel.category else None
                    
                    # Rol izinlerini kopyala
                    overwrites = {}
                    for target_obj, permissions in channel.overwrites.items():
                        if isinstance(target_obj, discord.Role):
                            new_role = discord.utils.get(target.roles, name=target_obj.name)
                            if new_role:
                                overwrites[new_role] = permissions
                    
                    new_channel = await target.create_voice_channel(
                        name=channel.name, 
                        overwrites=overwrites,
                        bitrate=channel.bitrate,
                        user_limit=channel.user_limit,
                        reason="Vexora Cloner - ses kanalı oluşturma"
                    )
                    
                    if category:
                        await new_channel.edit(category=category)
                        
                    created += 1
                    self.progress_bar(created, len(all_channels), "Kanallar oluşturuluyor")
                    await asyncio.sleep(0.5)  # Rate limit
                    
                except discord.Forbidden:
                    self.log(f"Ses kanalı oluşturma yetkisi yok: {channel.name}", "WARNING")
                except Exception as e:
                    self.log(f"Ses kanalı oluşturma hatası: {channel.name} - {str(e)}", "WARNING")
                    
            if all_channels:
                print()  # Progress bar için yeni satır
                
            self.log(f"{created} kanal oluşturuldu", "SUCCESS")
            
        except Exception as e:
            self.log(f"Kanal işlemi genel hatası: {str(e)}", "ERROR")
        
    async def process_emojis(self, source, target):
        try:
            # Emoji silme
            existing_emojis = list(target.emojis)
            for emoji in existing_emojis:
                try:
                    await emoji.delete(reason="Vexora Cloner - emoji silme")
                    await asyncio.sleep(0.5)  # Rate limit
                except Exception as e:
                    self.log(f"Emoji silme hatası: {emoji.name} - {str(e)}", "WARNING")
                    
            # Emoji oluşturma
            created = 0
            total_emojis = len(source.emojis)
            
            for i, emoji in enumerate(source.emojis):
                try:
                    emoji_bytes = await emoji.read()
                    await target.create_custom_emoji(
                        name=emoji.name, 
                        image=emoji_bytes,
                        reason="Vexora Cloner - emoji oluşturma"
                    )
                    created += 1
                    self.progress_bar(i + 1, total_emojis, "Emojiler kopyalanıyor")
                    await asyncio.sleep(1)  # Emoji için daha uzun bekleme
                except discord.Forbidden:
                    self.log(f"Emoji oluşturma yetkisi yok: {emoji.name}", "WARNING")
                except discord.HTTPException as e:
                    if "Maximum number of emojis reached" in str(e):
                        self.log("Emoji limiti doldu", "WARNING")
                        break
                    else:
                        self.log(f"Emoji oluşturma hatası: {emoji.name} - {str(e)}", "WARNING")
                except Exception as e:
                    self.log(f"Emoji işlemi hatası: {emoji.name} - {str(e)}", "WARNING")
                    
            if total_emojis > 0:
                print()  # Progress bar için yeni satır
                
            self.log(f"{created} emoji kopyalandı", "SUCCESS")
            
        except Exception as e:
            self.log(f"Emoji işlemi genel hatası: {str(e)}", "ERROR")
        
    async def start(self):
        self.print_banner()
        
        credentials = self.get_credentials()
        if not credentials:
            input("\nDevam etmek için Enter tuşuna basın...")
            return
            
        if not self.confirm_operation():
            self.log("İşlem iptal edildi", "INFO")
            input("\nDevam etmek için Enter tuşuna basın...")
            return
            
        await self.execute_cloning(*credentials)
        input("\nİşlem tamamlandı. Çıkmak için Enter tuşuna basın...")

async def main():
    try:
        cloner = VexoraCloner()
        await cloner.start()
    except KeyboardInterrupt:
        print("\n\nİşlem kullanıcı tarafından durduruldu")
        input("Çıkmak için Enter tuşuna basın...")
    except Exception as e:
        print(f"\nKritik hata: {e}")
        print("Lütfen discord.py kütüphanesinin yüklü olduğundan emin olun:")
        print("pip install discord.py")
        input("Çıkmak için Enter tuşuna basın...")

if __name__ == "__main__":
    asyncio.run(main())