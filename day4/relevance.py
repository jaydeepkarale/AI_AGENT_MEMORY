import numpy as np
from emb import embed, score
# (content, importance, confidence, created_at) - a plausible store after a few weeks of chatting
M = [
 ("User used Kubernetes at their previous company.",                0.8, 0.95, "2026-07-02"),
 ("User now uses AWS ECS for container orchestration.",            0.8, 0.95, "2026-09-20"),
 ("User is preparing for a backend engineering interview.",         0.9, 0.95, "2026-09-01"),
 ("User prefers concise explanations.",                             0.7, 0.90, "2026-08-10"),
 ("User prefers Python examples.",                                  0.7, 0.90, "2026-08-10"),
 ("User is a platform engineer.",                                   0.9, 0.95, "2026-07-01"),
 ("User is allergic to peanuts.",                                   0.95,0.95, "2026-08-15"),
 ("User's daughter is named Aria.",                                 0.9, 0.95, "2026-08-20"),
 ("User completed a Kubernetes certification.",                     0.6, 0.90, "2026-07-15"),
 ("User mentioned they like hiking on weekends.",                   0.3, 0.80, "2026-09-05"),
 ("User is interested in learning Rust.",                           0.4, 0.70, "2026-09-10"),
]
Q = ["What container orchestration platform am I using these days?",
     "Suggest a snack for my afternoon.",
     "What's the weather like today?",
     "Can you give me some weekend activity ideas?",
     "Explain how a hash map works."]
for prefix_d, prefix_q, label in [("", "", "Day 3 as written (no task prefixes)"), ("search_document: ", "search_query: ", "with nomic task prefixes")]:
    D = embed([m[0] for m in M], prefix_d); QV = embed(Q, prefix_q)
    print(f"\n#### {label}")
    sims = D@D.T; iu=np.triu_indices(len(M),1)
    print(f"memory-vs-memory cosine: min {sims[iu].min():.2f}  median {np.median(sims[iu]):.2f}  max {sims[iu].max():.2f}")
    for q, qv in zip(Q, QV):
        s = D@qv
        ranked = sorted(range(len(M)), key=lambda i: -score(s[i], M[i][1], M[i][2]))
        print(f"\nQ: {q}   (query-memory cosine range {s.min():.2f}..{s.max():.2f})")
        for r,i in enumerate(ranked[:4]):
            print(f"  {r+1}. score {score(s[i],M[i][1],M[i][2]):.3f}  sim {s[i]:.3f}  imp {M[i][1]}  {M[i][3]}  {M[i][0]}")
