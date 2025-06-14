import ctypes
import ctypes.wintypes as wintypes
import psutil
import time
import sys

# --- الإعدادات (مثال لببجي على جيم لوب) ---
# !!! هام: هذه الإعدادات، خاصة الأنماط، هي مجرد مثال توضيحي وليست حقيقية !!!
# !!! يجب أن تجد النمط الصحيح بنفسك وتضعه هنا !!!
CONFIG = {
    # الخطوة 1: ضع اسم عملية المحاكي هنا
    "target_process": "AndroidEmulatorEn.exe",  # <-- تأكد من هذا الاسم عبر مدير المهام

    # الخطوة 2: ضع الأنماط التي وجدتها هنا
    "aob_pattern": "F3 0F 11 05 ?? ?? ?? ?? 8B 4D 08", # <-- مثال: نمط افتراضي يجب استبداله بالنمط الصحيح
    "replace_bytes": "90 90 90 90 90 90 90 90 8B 4D 08", # <-- مثال: البايتات الجديدة (غالبًا ما تكون NOPs لتعطيل شيء ما)

    # إعدادات إضافية
    "patch_all_occurrences": True,              # تعديل كل النتائج التي يجدها
    "search_interval": 5,                       # الانتظار 5 ثواني بين كل محاولة
}

# --- تعريفات واجهة برمجة تطبيقات ويندوز (WinAPI) ---
# (الكود المتبقي يبقى كما هو بدون تغيير)
kernel32 = ctypes.windll.kernel32

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_ACCESS = (PROCESS_QUERY_INFORMATION | PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE)

MEM_COMMIT = 0x1000

PAGE_NOACCESS = 0x01
PAGE_READONLY = 0x02
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08
PAGE_EXECUTE = 0x10
PAGE_EXECUTE_READ = 0x20
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_GUARD = 0x100
WRITABLE_MASK = (PAGE_READWRITE | PAGE_WRITECOPY | PAGE_EXECUTE_READWRITE | PAGE_EXECUTE_WRITECOPY)
READABLE_MASK = (WRITABLE_MASK | PAGE_READONLY | PAGE_EXECUTE_READ)

class MemoryPatcher:
    """
    فئة لتغليف منطق البحث عن نمط البايتات وتعديله في ذاكرة عملية أخرى.
    """

    def __init__(self, config):
        self.config = config
        self.target_pid = None
        self.process_handle = None
        self.bytes_pattern, self.mask = self._parse_pattern(config["aob_pattern"])
        self.patch_bytes = bytes.fromhex(config["replace_bytes"].replace(" ", ""))

    def _parse_pattern(self, pattern_str: str) -> tuple[list[int], list[str]]:
        """يُحلل النمط النصي إلى قائمة بايتات وقناع."""
        bytes_list = []
        mask_list = []
        for byte in pattern_str.split():
            if byte in ("??", "?"):
                bytes_list.append(0x00)
                mask_list.append("?")
            else:
                bytes_list.append(int(byte, 16))
                mask_list.append("x")
        return bytes_list, mask_list

    def _find_process(self) -> bool:
        """يبحث عن معرّف العملية (PID) بناءً على اسمها."""
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'].lower() == self.config["target_process"].lower():
                self.target_pid = proc.info['pid']
                print(f"[✅] تم العثور على العملية '{self.config['target_process']}' (PID: {self.target_pid})")
                return True
        self.target_pid = None
        return False

    def _open_process(self) -> bool:
        """يفتح العملية للحصول على صلاحية الوصول إلى ذاكرتها."""
        self.process_handle = kernel32.OpenProcess(PROCESS_ACCESS, False, self.target_pid)
        if not self.process_handle:
            error_code = kernel32.GetLastError()
            print(f"[❌] فشل في فتح العملية (PID: {self.target_pid}). رمز الخطأ: {error_code}")
            print("[!] تأكد من تشغيل البرنامج كمسؤول (Run as Administrator).")
            return False
        return True

    def scan_and_patch(self) -> int:
        """
        يمسح ذاكرة العملية بحثًا عن النمط ويقوم بتعديله.
        يعيد عدد التعديلات التي تمت.
        """
        if not self._open_process():
            return 0

        patches_count = 0
        mbi = wintypes.MEMORY_BASIC_INFORMATION()
        address = 0

        while kernel32.VirtualQueryEx(self.process_handle, ctypes.c_void_p(address), ctypes.byref(mbi), ctypes.sizeof(mbi)):
            if mbi.State == MEM_COMMIT and (mbi.Protect & READABLE_MASK) and not (mbi.Protect & PAGE_GUARD):
                buffer = ctypes.create_string_buffer(mbi.RegionSize)
                bytes_read = ctypes.c_size_t(0)
                
                kernel32.ReadProcessMemory(self.process_handle, ctypes.c_void_p(address), buffer, mbi.RegionSize, ctypes.byref(bytes_read))
                
                for i in range(bytes_read.value - len(self.bytes_pattern) + 1):
                    if self._match_pattern(buffer, i):
                        patch_address = address + i
                        print(f"[🎯] تم العثور على النمط في العنوان: 0x{patch_address:X}")
                        
                        if self._apply_patch(patch_address, mbi.Protect):
                            patches_count += 1
                            if not self.config["patch_all_occurrences"]:
                                kernel32.CloseHandle(self.process_handle)
                                return patches_count
                        else:
                            print(f"[⚠️] فشل تعديل الذاكرة في العنوان: 0x{patch_address:X}")

            address += mbi.RegionSize

        kernel32.CloseHandle(self.process_handle)
        return patches_count

    def _match_pattern(self, buffer: bytes, offset: int) -> bool:
        """يتحقق من تطابق النمط في موقع معين داخل المخزن المؤقت."""
        for i in range(len(self.bytes_pattern)):
            if self.mask[i] == "x" and buffer[offset + i] != self.bytes_pattern[i]:
                return False
        return True

    def _apply_patch(self, address: int, original_protection: int) -> bool:
        """يقوم بتعديل الذاكرة في العنوان المحدد مع تغيير الحماية واستعادتها."""
        old_protect = wintypes.DWORD(0)
        
        success = kernel32.VirtualProtectEx(
            self.process_handle, ctypes.c_void_p(address), len(self.patch_bytes),
            PAGE_EXECUTE_READWRITE, ctypes.byref(old_protect)
        )
        if not success:
            print(f"[❌] فشل في تغيير حماية الذاكرة. رمز الخطأ: {kernel32.GetLastError()}")
            return False

        written = ctypes.c_size_t(0)
        success = kernel32.WriteProcessMemory(
            self.process_handle, ctypes.c_void_p(address), self.patch_bytes,
            len(self.patch_bytes), ctypes.byref(written)
        )
        if not success:
            print(f"[❌] فشل في الكتابة على الذاكرة. رمز الخطأ: {kernel32.GetLastError()}")
        
        kernel32.VirtualProtectEx(
            self.process_handle, ctypes.c_void_p(address), len(self.patch_bytes),
            old_protect.value, ctypes.byref(wintypes.DWORD(0))
        )
        
        return success

def main():
    """الدالة الرئيسية لتشغيل البرنامج."""
    print("[▶️] بدء تشغيل أداة التعديل التلقائي...")

    patcher = MemoryPatcher(CONFIG)
    
    while True:
        if not patcher._find_process():
            print(f"[⏳] في انتظار بدء العملية '{CONFIG['target_process']}'...")
            time.sleep(CONFIG["search_interval"])
            continue
        
        print("[ℹ️] جارِ البحث عن النمط وتعديله...")
        patches_made = patcher.scan_and_patch()
        
        if patches_made > 0:
            print(f"\n[🎉] اكتمل التعديل بنجاح. تم تطبيق {patches_made} تعديل/تعديلات.")
            break
        else:
            print(f"[🔄] لم يتم العثور على النمط أو أن اللعبة محمية. المحاولة مرة أخرى بعد {CONFIG['search_interval']} ثانية...")
            time.sleep(CONFIG["search_interval"])

if __name__ == "__main__":
    try:
        is_admin = (ctypes.windll.shell32.IsUserAnAdmin() != 0)
    except:
        is_admin = False
    
    if not is_admin:
        print("[❌] صلاحيات المسؤول مطلوبة! يرجى تشغيل البرنامج كمسؤول.")
        input("اضغط Enter للخروج.")
    else:
        main()
        print("\n[⏹️] تم إغلاق الأداة.")
        input("اضغط Enter للخروج.")