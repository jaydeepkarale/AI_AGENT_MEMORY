# Replays Day 3's exact storage + retrieval path (memory.py unchanged, retrieval.py's
# cosine + ranking copied verbatim) on synthetic 768-d vectors, to time
# "store one memory" vs "retrieve top-3" as the memory count grows.
# The query embedding (one Ollama call) is excluded: it's constant in N.
import json, math, os, random, sqlite3, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "day3"))  # use Day 3's memory.py unchanged
import memory
from memory import init_db, save_memory, get_memories

def cosine_similarity(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    ma = math.sqrt(sum(x*x for x in a)); mb = math.sqrt(sum(y*y for y in b))
    return 0.0 if ma == 0 or mb == 0 else dot/(ma*mb)

def retrieve(user_id, qv, top_k=3):
    out = []
    for m in get_memories(user_id):
        if not m[5]: continue
        s = cosine_similarity(qv, json.loads(m[5]))
        out.append((s*0.7 + m[3]*0.2 + m[4]*0.1, m[0], m[1], m[2]))
    out.sort(reverse=True, key=lambda i: i[0]); return out[:top_k]

rnd = random.Random(7)
vec = lambda: [rnd.gauss(0, 1) for _ in range(768)]
memory.DB_NAME = os.path.join(HERE, "scale.db")  # throwaway benchmark DB (~1.6 GB at 100k)
if os.path.exists(memory.DB_NAME): os.remove(memory.DB_NAME)
init_db()
con = sqlite3.connect(memory.DB_NAME)
now = "2026-09-30T00:00:00"
have = 0
print("N,save_ms,retrieve_ms,db_MB")
for N in [10, 100, 1000, 10000, 100000]:
    rows = [("jaydeep", f"memory {i}", "semantic", rnd.random(), rnd.random(), json.dumps(vec()), "active", now, now) for i in range(have, N)]
    con.executemany("INSERT INTO memories (user_id,content,memory_type,importance,confidence,embedding,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?)", rows); con.commit(); have = N
    t = time.perf_counter()
    for _ in range(5): save_memory("other_user", "probe", "semantic", 0.5, 0.9, vec())
    save_ms = (time.perf_counter()-t)/5*1000
    qv = vec(); reps = 3 if N <= 10000 else 1
    t = time.perf_counter()
    for _ in range(reps): retrieve("jaydeep", qv)
    ret_ms = (time.perf_counter()-t)/reps*1000
    print(f"{N},{save_ms:.2f},{ret_ms:.1f},{os.path.getsize(memory.DB_NAME)/1e6:.1f}", flush=True)
