param([string]$cmd, [string]$arg = "")
Add-Type -AssemblyName UIAutomationClient,UIAutomationTypes,System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class W {
  [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
}
"@
$G = "C:\Program Files (x86)\Steam\steamapps\common\FINAL FANTASY IX"
switch ($cmd) {
  "launch" {
    Start-Process -FilePath "$G\FF9_Launcher.exe" -WorkingDirectory $G
    Start-Sleep 5
    $p = Get-Process FF9_Launcher
    $root = [System.Windows.Automation.AutomationElement]::FromHandle($p.MainWindowHandle)
    $c = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::AutomationIdProperty, "PlayButton")
    $b = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $c)
    $h = [IntPtr]$b.Current.NativeWindowHandle
    $l = [IntPtr]((10 -shl 16) -bor 10)
    [W]::PostMessage($h, 0x201, [IntPtr]1, $l) | Out-Null
    Start-Sleep -Milliseconds 100
    [W]::PostMessage($h, 0x202, [IntPtr]0, $l) | Out-Null
    "clicked"
  }
  "shot" {
    $p = Get-Process FF9 -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $p) { "no game"; break }
    $h = $p.MainWindowHandle
    $r = New-Object W+RECT; [W]::GetWindowRect($h, [ref]$r) | Out-Null
    $w = $r.R - $r.L; $hh = $r.B - $r.T
    $bmp = New-Object System.Drawing.Bitmap $w, $hh
    $g = [System.Drawing.Graphics]::FromImage($bmp); $dc = $g.GetHdc()
    [W]::PrintWindow($h, $dc, 2) | Out-Null
    $g.ReleaseHdc($dc); $bmp.Save($arg); "saved $w x $hh"
  }
  "key" {
    # 백그라운드 키 입력(WM_KEYDOWN/UP) — arg는 가상키 코드(10진)
    $p = Get-Process FF9 | Select-Object -First 1
    $vk = [IntPtr][int]$arg
    [W]::PostMessage($p.MainWindowHandle, 0x100, $vk, [IntPtr]0) | Out-Null
    Start-Sleep -Milliseconds 120
    [W]::PostMessage($p.MainWindowHandle, 0x101, $vk, [IntPtr]0) | Out-Null
    "key $arg"
  }
  "kill" { Get-Process FF9, FF9_Launcher -ErrorAction SilentlyContinue | Stop-Process -Force; "killed" }
}
