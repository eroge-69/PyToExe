#include <Windows.h>
#include <TlHelp32.h>
#include <Psapi.h>
#include <iostream>
#include <vector>
#include <random>
#include <chrono>
#include <thread>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <wincrypt.h>
#pragma comment(lib, "crypt32.lib")
#pragma comment(lib, "advapi32.lib")

#define FIVEM_PROCESS "FiveM_GTAProcess.exe"
#define TARGET_MODULE "gta-core-five.dll"
#define STEALTH_SLEEP_MIN 1000
#define STEALTH_SLEEP_MAX 10000

namespace Asteral {
    class StealthEngine {
    private:
        std::random_device rd;
        std::mt19937 gen;
        std::uniform_int_distribution<> dis;

    public:
        StealthEngine() : gen(rd()), dis(STEALTH_SLEEP_MIN, STEALTH_SLEEP_MAX) {}

        void RandomSleep() {
            std::this_thread::sleep_for(std::chrono::milliseconds(dis(gen)));
        }

        void AntiDebugCheck() {
            if (IsDebuggerPresent()) {
                ExitProcess(0);
            }
        }

        void HideThread(HANDLE hThread) {
            typedef NTSTATUS(NTAPI* pNtSetInformationThread)(HANDLE, UINT, PVOID, ULONG);
            pNtSetInformationThread NtSIT = (pNtSetInformationThread)GetProcAddress(GetModuleHandle("ntdll.dll"), "NtSetInformationThread");
            if (NtSIT) {
                NtSIT(hThread, 0x11, 0, 0);
            }
        }
    };

    class ProcessUtils {
    public:
        DWORD GetProcessId(const char* processName) {
            HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
            PROCESSENTRY32 pe;
            pe.dwSize = sizeof(PROCESSENTRY32);
            if (Process32First(snapshot, &pe)) {
                do {
                    if (strcmp(pe.szExeFile, processName) == 0) {
                        CloseHandle(snapshot);
                        return pe.th32ProcessID;
                    }
                } while (Process32Next(snapshot, &pe));
            }
            CloseHandle(snapshot);
            return 0;
        }

        DWORD_PTR GetModuleBase(DWORD pid, const char* modName) {
            HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid);
            MODULEENTRY32 me;
            me.dwSize = sizeof(MODULEENTRY32);
            if (Module32First(snapshot, &me)) {
                do {
                    if (strcmp(me.szModule, modName) == 0) {
                        CloseHandle(snapshot);
                        return (DWORD_PTR)me.modBaseAddr;
                    }
                } while (Module32Next(snapshot, &me));
            }
            CloseHandle(snapshot);
            return 0;
        }

        bool InjectDLL(DWORD pid, const char* dllPath) {
            HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
            if (!hProcess) return false;

            LPVOID pRemoteMem = VirtualAllocEx(hProcess, NULL, strlen(dllPath) + 1, MEM_COMMIT, PAGE_READWRITE);
            if (!pRemoteMem) {
                CloseHandle(hProcess);
                return false;
            }

            WriteProcessMemory(hProcess, pRemoteMem, dllPath, strlen(dllPath) + 1, NULL);
            HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)LoadLibraryA, pRemoteMem, 0, NULL);
            if (!hThread) {
                VirtualFreeEx(hProcess, pRemoteMem, 0, MEM_RELEASE);
                CloseHandle(hProcess);
                return false;
            }

            WaitForSingleObject(hThread, INFINITE);
            VirtualFreeEx(hProcess, pRemoteMem, 0, MEM_RELEASE);
            CloseHandle(hThread);
            CloseHandle(hProcess);
            return true;
        }
    };

    class CheatEngine {
    private:
        StealthEngine stealth;
        ProcessUtils utils;

    public:
        void Run() {
            stealth.AntiDebugCheck();
            stealth.HideThread(GetCurrentThread());

            DWORD pid = 0;
            while (!(pid = utils.GetProcessId(FIVEM_PROCESS))) {
                stealth.RandomSleep();
            }

            DWORD_PTR moduleBase = 0;
            while (!(moduleBase = utils.GetModuleBase(pid, TARGET_MODULE))) {
                stealth.RandomSleep();
            }

            // Encrypted payload path (decrypt at runtime)
            std::vector<BYTE> encryptedPath = { 
                0x12, 0x34, 0x56, 0x78, 0x90, 0xAB, 0xCD, 0xEF // Example encrypted data
            };
            std::string dllPath = DecryptString(encryptedPath);

            if (utils.InjectDLL(pid, dllPath.c_str())) {
                // Success
            } else {
                // Fallback injection methods
            }
        }

        std::string DecryptString(const std::vector<BYTE>& data) {
            DATA_BLOB in, out;
            in.pbData = const_cast<BYTE*>(data.data());
            in.cbData = data.size();
            if (CryptUnprotectData(&in, NULL, NULL, NULL, NULL, 0, &out)) {
                std::string result(reinterpret_cast<char*>(out.pbData), out.cbData);
                LocalFree(out.pbData);
                return result;
            }
            return "";
        }
    };
}

int main() {
    Asteral::CheatEngine cheat;
    cheat.Run();
    return 0;
}