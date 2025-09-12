import discord
import asyncio
import sys
import os
from typing import Optional

# إعدادات البوت
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

# متغيرات عامة
selected_guild: Optional[discord.Guild] = None
bot_ready = False

def clear_screen():
    """تنظيف الشاشة"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """طباعة الرأس"""
    clear_screen()
    print("\033[91m" + "="*50)
    print("        🔥 AZRAEL Discord Controller 🔥")
    print("="*50 + "\033[0m")
    print()

def print_error(message):
    """طباعة رسالة خطأ"""
    print(f"\033[91m❌ {message}\033[0m")

def print_success(message):
    """طباعة رسالة نجاح"""
    print(f"\033[92m✅ {message}\033[0m")

def print_info(message):
    """طباعة معلومات"""
    print(f"\033[93mℹ️  {message}\033[0m")

def get_user_input(prompt):
    """الحصول على مدخل المستخدم"""
    try:
        return input(f"\033[96m{prompt}\033[0m").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\033[91mتم إلغاء العملية.\033[0m")
        return None

def display_guilds():
    """عرض قائمة السيرفرات"""
    print_header()
    print("\033[93m📋 السيرفرات المتاحة:\033[0m")
    print("-" * 40)
    
    if not client.guilds:
        print_error("لا توجد سيرفرات! تأكد أن البوت مدعو للسيرفرات.")
        return None
    
    for idx, guild in enumerate(client.guilds, 1):
        member_count = guild.member_count if guild.member_count else len(guild.members)
        print(f"\033[96m{idx}.\033[0m {guild.name}")
        print(f"   🆔 ID: {guild.id}")
        print(f"   👥 الأعضاء: {member_count}")
        print(f"   📅 تاريخ الإنشاء: {guild.created_at.strftime('%Y-%m-%d')}")
        print()
    
    choice = get_user_input("اختر رقم السيرفر (أو اكتب 'back' للعودة): ")
    
    if choice is None or choice.lower() == 'back':
        return None
    
    try:
        guild_idx = int(choice) - 1
        if 0 <= guild_idx < len(client.guilds):
            return client.guilds[guild_idx]
        else:
            print_error("رقم السيرفر غير صحيح!")
            input("اضغط Enter للمتابعة...")
            return None
    except ValueError:
        print_error("يرجى إدخال رقم صحيح!")
        input("اضغط Enter للمتابعة...")
        return None

def display_main_menu():
    """عرض القائمة الرئيسية"""
    print_header()
    
    if selected_guild:
        print(f"\033[92m🎯 السيرفر المحدد: {selected_guild.name}\033[0m")
        print()
    
    print("\033[93m📋 القائمة الرئيسية:\033[0m")
    print("-" * 30)
    print("1️⃣  اختيار السيرفر")
    print("2️⃣  إرسال رسالة")
    print("3️⃣  حذف قناة")
    print("4️⃣  إنشاء قناة")
    print("5️⃣  حظر عضو")
    print("6️⃣  طرد عضو")
    print("7️⃣  إنشاء رول")
    print("8️⃣  إعطاء رول")
    print("9️⃣  إزالة رول")
    print("🔟  إعادة تسمية قناة")
    print("1️⃣1️⃣  إعادة تسمية رول")
    print("1️⃣2️⃣  عرض الأعضاء")
    print("0️⃣  الخروج")
    print()

def get_text_channels(guild):
    """الحصول على القنوات النصية"""
    return [ch for ch in guild.channels if isinstance(ch, discord.TextChannel)]

def get_voice_channels(guild):
    """الحصول على القنوات الصوتية"""
    return [ch for ch in guild.channels if isinstance(ch, discord.VoiceChannel)]

def display_channels(channels, channel_type="قناة"):
    """عرض القنوات"""
    if not channels:
        print_error(f"لا توجد {channel_type}!")
        return None
    
    print(f"\033[93m📋 {channel_type} المتاحة:\033[0m")
    for idx, channel in enumerate(channels, 1):
        emoji = "💬" if isinstance(channel, discord.TextChannel) else "🔊"
        print(f"{idx}. {emoji} {channel.name}")
    
    choice = get_user_input(f"اختر رقم {channel_type}: ")
    if choice is None:
        return None
    
    try:
        channel_idx = int(choice) - 1
        if 0 <= channel_idx < len(channels):
            return channels[channel_idx]
    except ValueError:
        pass
    
    print_error("رقم القناة غير صحيح!")
    return None

def display_members(guild, limit=20):
    """عرض الأعضاء"""
    members = [m for m in guild.members if not m.bot]
    if not members:
        print_error("لا يوجد أعضاء!")
        return None
    
    print(f"\033[93m👥 الأعضاء ({len(members)} عضو):\033[0m")
    display_limit = min(limit, len(members))
    
    for idx, member in enumerate(members[:display_limit], 1):
        status_emoji = {
            discord.Status.online: "🟢",
            discord.Status.idle: "🟡", 
            discord.Status.dnd: "🔴",
            discord.Status.offline: "⚫"
        }.get(member.status, "⚫")
        
        print(f"{idx}. {status_emoji} {member.display_name} ({member.name})")
    
    if len(members) > limit:
        print(f"\n... و {len(members) - limit} عضو آخر")
    
    choice = get_user_input(f"اختر رقم العضو (1-{display_limit}): ")
    if choice is None:
        return None
    
    try:
        member_idx = int(choice) - 1
        if 0 <= member_idx < display_limit:
            return members[member_idx]
    except ValueError:
        pass
    
    print_error("رقم العضو غير صحيح!")
    return None

def display_roles(guild):
    """عرض الأدوار"""
    roles = [role for role in guild.roles if role.name != "@everyone"]
    if not roles:
        print_error("لا توجد أدوار!")
        return None
    
    print("\033[93m🎭 الأدوار المتاحة:\033[0m")
    for idx, role in enumerate(roles, 1):
        print(f"{idx}. {role.name} ({len(role.members)} عضو)")
    
    choice = get_user_input("اختر رقم الدور: ")
    if choice is None:
        return None
    
    try:
        role_idx = int(choice) - 1
        if 0 <= role_idx < len(roles):
            return roles[role_idx]
    except ValueError:
        pass
    
    print_error("رقم الدور غير صحيح!")
    return None

async def send_message_func():
    """إرسال رسالة"""
    if not selected_guild:
        print_error("يرجى اختيار سيرفر أولاً!")
        return
    
    print_header()
    channels = get_text_channels(selected_guild)
    channel = display_channels(channels, "القنوات النصية")
    
    if not channel:
        return
    
    message = get_user_input("اكتب الرسالة: ")
    if not message:
        return
    
    try:
        await channel.send(message)
        print_success(f"تم إرسال الرسالة إلى #{channel.name}")
    except discord.Forbidden:
        print_error("ليس لديك صلاحية للكتابة في هذه القناة!")
    except Exception as e:
        print_error(f"خطأ في إرسال الرسالة: {e}")

async def delete_channel_func():
    """حذف قناة"""
    if not selected_guild:
        print_error("يرجى اختيار سيرفر أولاً!")
        return
    
    print_header()
    print("1. قناة نصية")
    print("2. قناة صوتية")
    
    choice = get_user_input("اختر نوع القناة: ")
    if choice == "1":
        channels = get_text_channels(selected_guild)
        channel = display_channels(channels, "القنوات النصية")
    elif choice == "2":
        channels = get_voice_channels(selected_guild)
        channel = display_channels(channels, "القنوات الصوتية")
    else:
        print_error("اختيار غير صحيح!")
        return
    
    if not channel:
        return
    
    confirm = get_user_input(f"هل تريد حذف القناة #{channel.name}? (نعم/لا): ")
    if confirm and confirm.lower() in ['نعم', 'yes', 'y']:
        try:
            await channel.delete()
            print_success(f"تم حذف القناة #{channel.name}")
        except discord.Forbidden:
            print_error("ليس لديك صلاحية لحذف هذه القناة!")
        except Exception as e:
            print_error(f"خطأ في حذف القناة: {e}")

async def create_channel_func():
    """إنشاء قناة"""
    if not selected_guild:
        print_error("يرجى اختيار سيرفر أولاً!")
        return
    
    print_header()
    print("1. قناة نصية")
    print("2. قناة صوتية")
    
    choice = get_user_input("اختر نوع القناة: ")
    name = get_user_input("اسم القناة: ")
    
    if not name:
        return
    
    try:
        if choice == "1":
            channel = await selected_guild.create_text_channel(name)
            print_success(f"تم إنشاء القناة النصية #{channel.name}")
        elif choice == "2":
            channel = await selected_guild.create_voice_channel(name)
            print_success(f"تم إنشاء القناة الصوتية {channel.name}")
        else:
            print_error("اختيار غير صحيح!")
    except discord.Forbidden:
        print_error("ليس لديك صلاحية لإنشاء قنوات!")
    except Exception as e:
        print_error(f"خطأ في إنشاء القناة: {e}")

async def ban_user_func():
    """حظر عضو"""
    if not selected_guild:
        print_error("يرجى اختيار سيرفر أولاً!")
        return
    
    print_header()
    member = display_members(selected_guild)
    if not member:
        return
    
    reason = get_user_input("سبب الحظر (اختياري): ") or "لا يوجد سبب"
    confirm = get_user_input(f"هل تريد حظر {member.display_name}? (نعم/لا): ")
    
    if confirm and confirm.lower() in ['نعم', 'yes', 'y']:
        try:
            await member.ban(reason=reason)
            print_success(f"تم حظر {member.display_name}")
        except discord.Forbidden:
            print_error("ليس لديك صلاحية لحظر هذا العضو!")
        except Exception as e:
            print_error(f"خطأ في حظر العضو: {e}")

async def kick_user_func():
    """طرد عضو"""
    if not selected_guild:
        print_error("يرجى اختيار سيرفر أولاً!")
        return
    
    print_header()
    member = display_members(selected_guild)
    if not member:
        return
    
    reason = get_user_input("سبب الطرد (اختياري): ") or "لا يوجد سبب"
    confirm = get_user_input(f"هل تريد طرد {member.display_name}? (نعم/لا): ")
    
    if confirm and confirm.lower() in ['نعم', 'yes', 'y']:
        try:
            await member.kick(reason=reason)
            print_success(f"تم طرد {member.display_name}")
        except discord.Forbidden:
            print_error("ليس لديك صلاحية لطرد هذا العضو!")
        except Exception as e:
            print_error(f"خطأ في طرد العضو: {e}")

async def create_role_func():
    """إنشاء رول"""
    if not selected_guild:
        print_error("يرجى اختيار سيرفر أولاً!")
        return
    
    print_header()
    name = get_user_input("اسم الرول: ")
    if not name:
        return
    
    color_input = get_user_input("لون الرول (hex بدون #, مثال: FF0000): ")
    
    try:
        if color_input:
            color = discord.Color(int(color_input, 16))
        else:
            color = discord.Color.default()
        
        role = await selected_guild.create_role(name=name, color=color)
        print_success(f"تم إنشاء الرول {role.name}")
    except discord.Forbidden:
        print_error("ليس لديك صلاحية لإنشاء أدوار!")
    except ValueError:
        print_error("لون غير صحيح!")
    except Exception as e:
        print_error(f"خطأ في إنشاء الرول: {e}")

async def assign_role_func():
    """إعطاء رول"""
    if not selected_guild:
        print_error("يرجى اختيار سيرفر أولاً!")
        return
    
    print_header()
    print("اختر العضو:")
    member = display_members(selected_guild)
    if not member:
        return
    
    print("\nاختر الرول:")
    role = display_roles(selected_guild)
    if not role:
        return
    
    try:
        await member.add_roles(role)
        print_success(f"تم إعطاء رول {role.name} للعضو {member.display_name}")
    except discord.Forbidden:
        print_error("ليس لديك صلاحية لإدارة الأدوار!")
    except Exception as e:
        print_error(f"خطأ في إعطاء الرول: {e}")

async def remove_role_func():
    """إزالة رول"""
    if not selected_guild:
        print_error("يرجى اختيار سيرفر أولاً!")
        return
    
    print_header()
    print("اختر العضو:")
    member = display_members(selected_guild)
    if not member:
        return
    
    # عرض أدوار العضو فقط
    member_roles = [role for role in member.roles if role.name != "@everyone"]
    if not member_roles:
        print_error("هذا العضو ليس لديه أدوار!")
        return
    
    print(f"\nأدوار {member.display_name}:")
    for idx, role in enumerate(member_roles, 1):
        print(f"{idx}. {role.name}")
    
    choice = get_user_input("اختر رقم الرول لإزالته: ")
    if choice is None:
        return
    
    try:
        role_idx = int(choice) - 1
        if 0 <= role_idx < len(member_roles):
            role = member_roles[role_idx]
            await member.remove_roles(role)
            print_success(f"تم إزالة رول {role.name} من {member.display_name}")
        else:
            print_error("رقم الرول غير صحيح!")
    except ValueError:
        print_error("يرجى إدخال رقم صحيح!")
    except discord.Forbidden:
        print_error("ليس لديك صلاحية لإدارة الأدوار!")
    except Exception as e:
        print_error(f"خطأ في إزالة الرول: {e}")

async def rename_channel_func():
    """إعادة تسمية قناة"""
    if not selected_guild:
        print_error("يرجى اختيار سيرفر أولاً!")
        return
    
    print_header()
    print("1. قناة نصية")
    print("2. قناة صوتية")
    
    choice = get_user_input("اختر نوع القناة: ")
    if choice == "1":
        channels = get_text_channels(selected_guild)
        channel = display_channels(channels, "القنوات النصية")
    elif choice == "2":
        channels = get_voice_channels(selected_guild)
        channel = display_channels(channels, "القنوات الصوتية")
    else:
        print_error("اختيار غير صحيح!")
        return
    
    if not channel:
        return
    
    new_name = get_user_input(f"الاسم الجديد للقناة {channel.name}: ")
    if not new_name:
        return
    
    try:
        await channel.edit(name=new_name)
        print_success(f"تم تغيير اسم القناة إلى {new_name}")
    except discord.Forbidden:
        print_error("ليس لديك صلاحية لتعديل هذه القناة!")
    except Exception as e:
        print_error(f"خطأ في إعادة تسمية القناة: {e}")

async def rename_role_func():
    """إعادة تسمية رول"""
    if not selected_guild:
        print_error("يرجى اختيار سيرفر أولاً!")
        return
    
    print_header()
    role = display_roles(selected_guild)
    if not role:
        return
    
    new_name = get_user_input(f"الاسم الجديد للرول {role.name}: ")
    if not new_name:
        return
    
    try:
        await role.edit(name=new_name)
        print_success(f"تم تغيير اسم الرول إلى {new_name}")
    except discord.Forbidden:
        print_error("ليس لديك صلاحية لتعديل هذا الرول!")
    except Exception as e:
        print_error(f"خطأ في إعادة تسمية الرول: {e}")

def show_members_func():
    """عرض الأعضاء"""
    if not selected_guild:
        print_error("يرجى اختيار سيرفر أولاً!")
        return
    
    print_header()
    print(f"🏰 سيرفر: {selected_guild.name}")
    print(f"👥 إجمالي الأعضاء: {selected_guild.member_count}")
    print()
    
    # تقسيم الأعضاء حسب الحالة
    online = [m for m in selected_guild.members if m.status == discord.Status.online and not m.bot]
    idle = [m for m in selected_guild.members if m.status == discord.Status.idle and not m.bot]
    dnd = [m for m in selected_guild.members if m.status == discord.Status.dnd and not m.bot]
    offline = [m for m in selected_guild.members if m.status == discord.Status.offline and not m.bot]
    bots = [m for m in selected_guild.members if m.bot]
    
    print(f"🟢 متصل: {len(online)}")
    print(f"🟡 خامل: {len(idle)}")
    print(f"🔴 مشغول: {len(dnd)}")
    print(f"⚫ غير متصل: {len(offline)}")
    print(f"🤖 بوتات: {len(bots)}")
    print()
    
    # عرض بعض الأعضاء المتصلين
    if online:
        print("🟢 الأعضاء المتصلين:")
        for member in online[:10]:
            print(f"   • {member.display_name}")
        if len(online) > 10:
            print(f"   ... و {len(online) - 10} عضو آخر")

@client.event
async def on_ready():
    global bot_ready
    bot_ready = True
    
    print_header()
    print_success("تم الاتصال بنجاح!")
    print_info(f"اسم البوت: {client.user.name}")
    print_info(f"ID: {client.user.id}")
    print_info(f"السيرفرات: {len(client.guilds)}")
    print()
    
    if client.guilds:
        print("📋 السيرفرات المتصل بها:")
        for guild in client.guilds:
            print(f"   • {guild.name} ({guild.member_count} عضو)")
    else:
        print_error("البوت غير موجود في أي سيرفر!")
    
    print()
    input("اضغط Enter للبدء...")

async def main_loop():
    """الحلقة الرئيسية للبرنامج"""
    global selected_guild
    
    while True:
        if not bot_ready:
            await asyncio.sleep(0.5)
            continue
            
        display_main_menu()
        choice = get_user_input("اختر من القائمة: ")
        
        if choice is None:
            continue
            
        if choice == "0":
            print_info("تم إغلاق البرنامج بأمان.")
            await client.close()
            break
        elif choice == "1":
            selected_guild = display_guilds()
            if selected_guild:
                print_success(f"تم اختيار سيرفر: {selected_guild.name}")
                input("اضغط Enter للمتابعة...")
        elif choice == "2":
            await send_message_func()
            input("اضغط Enter للمتابعة...")
        elif choice == "3":
            await delete_channel_func()
            input("اضغط Enter للمتابعة...")
        elif choice == "4":
            await create_channel_func()
            input("اضغط Enter للمتابعة...")
        elif choice == "5":
            await ban_user_func()
            input("اضغط Enter للمتابعة...")
        elif choice == "6":
            await kick_user_func()
            input("اضغط Enter للمتابعة...")
        elif choice == "7":
            await create_role_func()
            input("اضغط Enter للمتابعة...")
        elif choice == "8":
            await assign_role_func()
            input("اضغط Enter للمتابعة...")
        elif choice == "9":
            await remove_role_func()
            input("اضغط Enter للمتابعة...")
        elif choice == "10":
            await rename_channel_func()
            input("اضغط Enter للمتابعة...")
        elif choice == "11":
            await rename_role_func()
            input("اضغط Enter للمتابعة...")
        elif choice == "12":
            show_members_func()
            input("اضغط Enter للمتابعة...")
        else:
            print_error("اختيار غير صحيح!")
            input("اضغط Enter للمتابعة...")

async def main():
    """الدالة الرئيسية"""
    print_header()
    print("\033[93m🚀 مرحباً بك في AZRAEL Discord Controller\033[0m")
    print()
    
    token = get_user_input("🔑 أدخل توكن البوت: ")
    if not token:
        print_error("لم يتم إدخال توكن!")
        return
    
    try:
        print_info("جاري الاتصال...")
        
        # تشغيل البوت والحلقة الرئيسية معاً
        await asyncio.gather(
            client.start(token),
            main_loop()
        )
        
    except discord.LoginFailure:
        print_error("توكن غير صحيح!")
    except KeyboardInterrupt:
        print_info("تم إيقاف البرنامج بواسطة المستخدم.")
    except Exception as e:
        print_error(f"خطأ: {e}")
    finally:
        if not client.is_closed():
            await client.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\033[91mتم إغلاق البرنامج.\033[0m")
    except Exception as e:
        print(f"\033[91mخطأ فادح: {e}\033[0m")
        sys.exit(1)