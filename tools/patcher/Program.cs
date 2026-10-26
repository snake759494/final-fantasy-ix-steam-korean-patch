using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using Microsoft.Win32;

class Program
{
    const string AppId = "377840";

    // (상대 경로, 원본 MD5, 패치본 MD5, xdelta 파일)
    static readonly (string Path, string Orig, string Patched, string Delta)[] Targets =
    {
        ("x64/FF9_Data/resources.assets", "8d917350d2f10c8e693d7aaed2f41299", "0feddb7e229daddf61183b6515c3f2f5", "x64_resources.assets.xdelta"),
        ("x64/FF9_Data/sharedassets2.assets", "f267fbbb8715059207658d28d1707e22", "0797d129ec0ca503531bc58a2ff6dd18", "x64_sharedassets2.assets.xdelta"),
        ("x64/FF9_Data/Managed/Assembly-CSharp.dll", "5b01d22c45fb5ad3c160ee951ee0a883", "3cf542b68f2bf09b46c2c2455d354396", "x64_Assembly-CSharp.dll.xdelta"),
        ("x86/FF9_Data/resources.assets", "04fa527e534847b11595d1106be60400", "1b5790c9eccf3628375697f850bfe65f", "x86_resources.assets.xdelta"),
        ("x86/FF9_Data/sharedassets2.assets", "77ebb5fea9763099d5488559ba95802e", "f94327a2b39764c8b6fd53401e2a153f", "x86_sharedassets2.assets.xdelta"),
        ("x86/FF9_Data/Managed/Assembly-CSharp.dll", "886a5a9d2d91cfe25c2cd383d77ecc95", "3280d8fa254f8d43e17e8295e5e6b271", "x86_Assembly-CSharp.dll.xdelta"),
    };

    // 이전 버전 패치본 해시 (원본 백업에서 다시 패치)
    static readonly HashSet<string> OldPatched = new HashSet<string>
    {
        "34a65ca60e5eae5c3738146a708f7a75", // v1.0 x64 Assembly-CSharp.dll
        "e77a6df87458cb99d2c680c83f54c24c", // v1.0 x86 Assembly-CSharp.dll
    };

    static string Here => AppContext.BaseDirectory;

    static int Main(string[] args)
    {
        Console.OutputEncoding = Encoding.UTF8;
        Console.WriteLine("==================================================");
        Console.WriteLine("   FINAL FANTASY IX (Steam) 한글패치 설치 프로그램");
        Console.WriteLine("==================================================\n");
        try
        {
            string game = args.FirstOrDefault(a => !a.StartsWith("-")) ?? FindGameDir();
            if (game == null)
            {
                Console.WriteLine("Steam에서 FF9 설치 경로를 찾지 못했습니다.");
                Console.Write("게임 폴더 경로를 직접 입력하세요: ");
                game = Console.ReadLine()?.Trim().Trim('"');
            }
            if (string.IsNullOrEmpty(game) || !File.Exists(Path.Combine(game, "FF9_Launcher.exe")))
            {
                Fail("올바른 FF9 게임 폴더가 아닙니다: " + game); Pause(args); return 1;
            }
            Console.WriteLine("게임 경로: " + game + "\n");

            if (Process.GetProcessesByName("FF9").Length > 0)
            {
                Fail("게임이 실행 중입니다. 게임을 종료한 뒤 다시 실행하세요."); Pause(args); return 1;
            }

            bool restore = args.Contains("-restore");
            if (!restore && !args.Contains("-y"))
            {
                Console.WriteLine("1) 한글패치 설치    2) 원본으로 복원    그 외) 종료");
                Console.Write("선택: ");
                var k = Console.ReadLine()?.Trim();
                if (k == "2") restore = true; else if (k != "1") return 0;
                Console.WriteLine();
            }
            int r = restore ? Restore(game) : Patch(game);
            Pause(args);
            return r;
        }
        catch (Exception e)
        {
            Console.WriteLine("\n오류: " + e.Message);
            Pause(args);
            return 1;
        }
    }

    static int Patch(string game)
    {
        string xdelta = Path.Combine(Here, "xdelta.exe");
        if (!File.Exists(xdelta)) return Fail("xdelta.exe가 프로그램과 같은 폴더에 없습니다.");
        string backup = Path.Combine(game, "_original_backup");

        // 1단계: 모든 파일 상태 확인 (하나라도 모르는 버전이면 아무것도 바꾸지 않음)
        var todo = new List<(string Path, string Orig, string Patched, string Delta)>();
        foreach (var t in Targets)
        {
            string f = Path.Combine(game, t.Path);
            if (!File.Exists(f)) return Fail("파일이 없습니다: " + t.Path);
            Console.Write($"확인 중: {t.Path} ... ");
            string h = Md5(f);
            if (h == t.Patched) { Console.WriteLine("이미 패치됨"); continue; }
            if (OldPatched.Contains(h))
            {
                string ob = Path.Combine(backup, t.Path);
                if (!File.Exists(ob) || Md5(ob) != t.Orig)
                    return Fail("이전 버전 패치가 적용되어 있으나 원본 백업이 없습니다: " + t.Path + "\nSteam에서 '게임 파일 무결성 확인' 후 다시 시도하세요.");
                Console.WriteLine("이전 버전 패치 → 갱신");
                todo.Add(t);
                continue;
            }
            if (h != t.Orig)
            {
                Console.WriteLine("알 수 없는 버전");
                return Fail("게임 파일이 이 패치가 만들어진 버전과 다릅니다.\nSteam에서 '게임 파일 무결성 확인' 후 다시 시도하세요.");
            }
            Console.WriteLine("원본 확인");
            todo.Add(t);
        }
        if (todo.Count == 0) { Console.WriteLine("\n이미 한글패치가 모두 적용되어 있습니다."); return 0; }

        // 2단계: 백업 -> 패치(임시 파일) -> 검증 -> 교체
        foreach (var t in todo)
        {
            string f = Path.Combine(game, t.Path);
            string b = Path.Combine(backup, t.Path);
            Directory.CreateDirectory(Path.GetDirectoryName(b));
            if ((!File.Exists(b) || Md5(b) != t.Orig) && Md5(f) == t.Orig) File.Copy(f, b, true);
            string tmp = f + ".kortmp";
            Console.Write($"패치 중: {t.Path} ... ");
            var psi = new ProcessStartInfo(xdelta, $"-d -f -s \"{b}\" \"{Path.Combine(Here, "patch", t.Delta)}\" \"{tmp}\"")
            { UseShellExecute = false, CreateNoWindow = true, RedirectStandardError = true };
            using (var p = Process.Start(psi))
            {
                string err = p.StandardError.ReadToEnd(); p.WaitForExit();
                if (p.ExitCode != 0) { if (File.Exists(tmp)) File.Delete(tmp); return Fail("xdelta 실패: " + err); }
            }
            if (Md5(tmp) != t.Patched) { File.Delete(tmp); return Fail("패치 결과 검증 실패: " + t.Path); }
            File.Copy(tmp, f, true); File.Delete(tmp);
            Console.WriteLine("완료");
        }
        Console.WriteLine("\n한글패치가 완료되었습니다!");
        Console.WriteLine("게임 실행 후 언어를 '한국어'(기존 English (US) 자리)로 선택하세요.");
        Console.WriteLine("원본 파일 백업 위치: " + backup);
        return 0;
    }

    static int Restore(string game)
    {
        string backup = Path.Combine(game, "_original_backup");
        foreach (var t in Targets)
        {
            string b = Path.Combine(backup, t.Path), f = Path.Combine(game, t.Path);
            if (File.Exists(f) && Md5(f) == t.Orig) { Console.WriteLine($"원본 상태: {t.Path}"); continue; }
            if (!File.Exists(b) || Md5(b) != t.Orig)
                return Fail("백업이 없습니다: " + t.Path + "\nSteam에서 '게임 파일 무결성 확인'으로 복원하세요.");
            File.Copy(b, f, true);
            Console.WriteLine($"복원 완료: {t.Path}");
        }
        Console.WriteLine("\n원본으로 복원되었습니다.");
        return 0;
    }

    // Steam 설치 경로 -> libraryfolders.vdf -> appmanifest_377840.acf -> 게임 폴더
    static string FindGameDir()
    {
        var steamRoots = new List<string>();
        foreach (var (hive, key, val) in new[] {
            (Registry.CurrentUser, @"Software\Valve\Steam", "SteamPath"),
            (Registry.LocalMachine, @"SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
            (Registry.LocalMachine, @"SOFTWARE\Valve\Steam", "InstallPath") })
        {
            try { if (hive.OpenSubKey(key)?.GetValue(val) is string s) steamRoots.Add(s.Replace('/', '\\')); } catch { }
        }
        steamRoots.Add(@"C:\Program Files (x86)\Steam");
        var libs = new List<string>();
        foreach (var root in steamRoots.Distinct(StringComparer.OrdinalIgnoreCase))
        {
            libs.Add(root);
            string vdf = Path.Combine(root, "steamapps", "libraryfolders.vdf");
            if (File.Exists(vdf))
                foreach (Match m in Regex.Matches(File.ReadAllText(vdf), "\"path\"\\s+\"([^\"]+)\""))
                    libs.Add(m.Groups[1].Value.Replace("\\\\", "\\"));
        }
        foreach (var lib in libs.Distinct(StringComparer.OrdinalIgnoreCase))
        {
            string acf = Path.Combine(lib, "steamapps", $"appmanifest_{AppId}.acf");
            string dir = "FINAL FANTASY IX";
            if (File.Exists(acf))
            {
                var m = Regex.Match(File.ReadAllText(acf), "\"installdir\"\\s+\"([^\"]+)\"");
                if (m.Success) dir = m.Groups[1].Value;
            }
            string game = Path.Combine(lib, "steamapps", "common", dir);
            if (File.Exists(Path.Combine(game, "FF9_Launcher.exe"))) return game;
        }
        return null;
    }

    static string Md5(string f)
    {
        using var md5 = MD5.Create();
        using var s = File.OpenRead(f);
        return BitConverter.ToString(md5.ComputeHash(s)).Replace("-", "").ToLowerInvariant();
    }

    static int Fail(string msg) { Console.WriteLine("\n" + msg); return 1; }

    static void Pause(string[] args)
    {
        if (args.Contains("-y") || args.Contains("-restore")) return;
        Console.WriteLine("\n아무 키나 누르면 종료합니다.");
        try { Console.ReadKey(true); } catch { }
    }
}
