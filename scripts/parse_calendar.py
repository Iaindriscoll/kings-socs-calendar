import json, re
from datetime import datetime, timezone

def unfold(s):
    return re.sub(r"\r?\n[ \t]", "", s)

def get(block, name):
    m = re.search(r"^" + re.escape(name) + r"(?:;[^:]*)?:(.*)$", block, re.M)
    return m.group(1).strip() if m else ""

def parse(v):
    if not v: return None
    z = v.endswith("Z")
    v = v.rstrip("Z")
    for fmt in ("%Y%m%dT%H%M%S", "%Y%m%d"):
        try:
            d = datetime.strptime(v, fmt)
            return d.replace(tzinfo=timezone.utc) if z else d.replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    return None

def clean(v):
    return v.replace("\\n"," ").replace("\\, ",", ").replace("\\,",",").replace("\\;",";")

raw = unfold(open("calendar.ics", encoding="utf-8-sig", errors="replace").read())
now = datetime.now(timezone.utc)
events = []
for b in re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", raw, re.S):
    start = parse(get(b,"DTSTART")); end = parse(get(b,"DTEND"))
    if not start or (end or start) < now: continue
    events.append({
        "start": start.isoformat(),
        "end": end.isoformat() if end else "",
        "allDay": "T" not in get(b,"DTSTART"),
        "title": clean(get(b,"SUMMARY")),
        "location": clean(get(b,"LOCATION"))
    })
events.sort(key=lambda e:e["start"])
json.dump({"events":events[:40]}, open("calendar.json","w",encoding="utf-8"), ensure_ascii=False, indent=2)
