# Run bench_scale.py first: this reads the scale.db it leaves behind.
import json, math, os, sqlite3, time, numpy as np
con = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scale.db"))
t=time.perf_counter(); rows = con.execute("SELECT id,embedding,importance,confidence FROM memories WHERE user_id='jaydeep' AND status='active' LIMIT 10000").fetchall(); t_sql=time.perf_counter()-t
t=time.perf_counter(); vecs=[json.loads(r[1]) for r in rows]; t_json=time.perf_counter()-t
q=vecs[0]
t=time.perf_counter()
for v in vecs:
    dot=sum(a*b for a,b in zip(q,v)); ma=math.sqrt(sum(a*a for a in q)); mb=math.sqrt(sum(b*b for b in v))
t_cos=time.perf_counter()-t
print(f"10k rows: sql fetch {t_sql*1000:.0f} ms, json.loads {t_json*1000:.0f} ms, pure-python cosine {t_cos*1000:.0f} ms")
# numpy, vectors pre-normalised and held in RAM as float32
for N in [10_000, 100_000, 1_000_000]:
    M = np.random.default_rng(1).standard_normal((N,768), dtype=np.float32); M /= np.linalg.norm(M,axis=1,keepdims=True)
    qv = M[0].copy(); imp = np.random.rand(N).astype(np.float32); conf=np.random.rand(N).astype(np.float32)
    t=time.perf_counter()
    for _ in range(10):
        s = M@qv*0.7 + imp*0.2 + conf*0.1; top = np.argpartition(-s,3)[:3]
    print(f"numpy in-RAM N={N:>9,}: {(time.perf_counter()-t)/10*1000:.1f} ms/query, matrix {M.nbytes/1e9:.2f} GB")
    del M
