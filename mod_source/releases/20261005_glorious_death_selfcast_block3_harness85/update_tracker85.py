# -*- coding: utf-8 -*-
"""Round-85 tracker update - the ONLY two allowed changes.

(i)  add the standing rule: mutually exclusive abilities are auto-rejected
     without asking the user (rule 8).
(ii) mark the existing mutual-exclusivity rejects as
     `rejected (auto: mutual exclusivity)` (10 occurrences: 5 §2 Decision
     lines + 5 §3a status cells).
Nothing else is touched.
"""
import io, hashlib

P = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_ability_tracker.md"
s = io.open(P, encoding="utf-8").read()
orig_len = len(s)

ANCHOR = ("7. **Rampage is no longer an automatic rejection:** a loss-of-control / Rampage effect is flagged and decided case by case (Fluid Injection! and Fury of Ursun were approved with it).\n")
assert s.count(ANCHOR) == 1, "rule 7 anchor"
RULE8 = ("8. **Mutual exclusivity is an automatic rejection:** an ability the collection finds mutually exclusive with another "
         "is auto-rejected WITHOUT asking the user case by case, and is marked `rejected (auto: mutual exclusivity)` "
         "(this is the standing form of rule 3).\n")
s = s.replace(ANCHOR, ANCHOR + RULE8, 1)

OLD = "rejected (mutual exclusivity)"
NEW = "rejected (auto: mutual exclusivity)"
n = s.count(OLD)
assert n == 10, ("mutual-exclusivity tokens", n)
s = s.replace(OLD, NEW)

assert s.count(NEW) == 11, "replaced count"   # 10 re-marked + 1 in rule 8's own text
assert s.count(OLD) == 0, "old token remains"
assert s.count("8. **Mutual exclusivity is an automatic rejection:**") == 1, "rule 8 present"

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("tracker updated: %d -> %d bytes" % (orig_len, len(s)))
print("standing rule 8 added; 10 mutual-exclusivity rejects re-marked")
print("sha256", hashlib.sha256(s.encode("utf-8")).hexdigest()[:32])
