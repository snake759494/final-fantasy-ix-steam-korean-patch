using Mono.Cecil; using Mono.Cecil.Cil; using System.Linq;
var src = args[0]; var dst = args[1];
var res = new DefaultAssemblyResolver(); res.AddSearchDirectory(System.IO.Path.GetDirectoryName(src)); res.AddSearchDirectory(args[2]);
var asm = AssemblyDefinition.ReadAssembly(src, new ReaderParameters { AssemblyResolver = res });
var mod = asm.MainModule;
// 1) 기본 이름(English(US)) 한글화
var ko = new[] { "지탄","비비","다가","스타이너","프레이야","쿠이나","에이코","앰버라","시나","시나","마커스","마커스","블랭크","블랭크","베아트릭스","베아트릭스","지탄","시나","마커스","블랭크" };
var m = mod.Types.SelectMany(t => t.Methods).First(x => x.Name == "CharacterDefaultName");
var ins = m.Body.Instructions.ToList();
int us = ins.FindIndex(i => i.OpCode == OpCodes.Ldstr && (string)i.Operand == "English(US)");
// switch 문자열 비교 이후, 첫 번째 "Zidane"부터 20개가 US 배열
int start = ins.FindIndex(us + 1, i => i.OpCode == OpCodes.Ldstr && (string)i.Operand == "Zidane");
int n = 0;
for (int k = start; n < 20; k++) if (ins[k].OpCode == OpCodes.Ldstr) ins[k].Operand = ko[n++];
// 2) 이름 입력 검증 정규식에 한글 허용
var v = mod.Types.First(t => t.Name == "NameSettingUI").Methods.First(x => x.Name == "ValidateInput");
var r = v.Body.Instructions.First(i => i.OpCode == OpCodes.Ldstr && ((string)i.Operand).StartsWith("[^"));
r.Operand = ((string)r.Operand).Replace("[^", "[^\uAC00-\uD7A3\u3131-\u318E\u1100-\u11FF\u0020");
System.Console.WriteLine($"US idx {us}, start {start}, regex {r.Operand}");
asm.Write(dst);
