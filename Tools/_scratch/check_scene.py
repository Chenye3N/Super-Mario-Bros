"""Validate the hand-edited SampleScene.unity: unique ids, resolvable refs, roots, components."""
import re
import sys

PATH = r"D:\Unity\Super Mario Bros\Assets\Scenes\SampleScene.unity"
text = open(PATH, encoding="utf-8").read()

parts = re.split(r"^--- !u!(\d+) &(\d+)[^\n]*$", text, flags=re.M)
docs = {}
order = []
for i in range(1, len(parts), 3):
    cls, fid, body = int(parts[i]), int(parts[i + 1]), parts[i + 2]
    assert fid not in docs, f"duplicate fileID {fid}"
    docs[fid] = (cls, body)
    order.append(fid)

print(f"docs: {len(docs)}")

# every local reference must resolve
missing = []
for fid, (cls, body) in docs.items():
    for m in re.finditer(r"\{fileID: (-?\d+)(, guid: [0-9a-f]{32}, type: \d+)?\}", body):
        ref = int(m.group(1))
        if ref == 0 or m.group(2):
            continue
        if ref not in docs:
            missing.append((fid, cls, ref))
print("unresolved refs:", missing if missing else "none")

# GameObject <-> component back references
gos = {fid: body for fid, (cls, body) in docs.items() if cls == 1}
print(f"gameobjects: {len(gos)}")
for go, body in gos.items():
    name = re.search(r"m_Name: (.*)", body).group(1)
    comps = [int(x) for x in re.findall(r"- component: \{fileID: (\d+)\}", body)]
    for c in comps:
        assert c in docs, f"{name}: component {c} missing"
        back = re.search(r"m_GameObject: \{fileID: (\d+)\}", docs[c][1])
        assert back and int(back.group(1)) == go, f"{name}: comp {c} points to {back and back.group(1)}"
    print(f"  {name:14s} go={go} comps={[(c, docs[c][0]) for c in comps]}")

# SceneRoots
roots_doc = docs[9223372036854775807][1]
roots = [int(x) for x in re.findall(r"- \{fileID: (\d+)\}", roots_doc)]
print("roots:", roots)
for r in roots:
    assert docs[r][0] == 4, f"root {r} is not a Transform"
    go = int(re.search(r"m_GameObject: \{fileID: (\d+)\}", docs[r][1]).group(1))
    father = int(re.search(r"m_Father: \{fileID: (\d+)\}", docs[r][1]).group(1))
    assert father == 0, f"root {r} has a father"
    print(f"  root transform {r} -> {re.search('m_Name: (.*)', docs[go][1]).group(1)}")

# trigger check
for fid, (cls, body) in docs.items():
    if cls == 61:
        go = int(re.search(r"m_GameObject: \{fileID: (\d+)\}", body).group(1))
        size = re.search(r"m_Size: \{x: ([-\d.]+), y: ([-\d.]+)\}", body).groups()
        trig = re.search(r"m_IsTrigger: (\d)", body).group(1)
        print(f"  collider on {re.search('m_Name: (.*)', docs[go][1]).group(1)} size={size} isTrigger={trig}")

print("OK")
