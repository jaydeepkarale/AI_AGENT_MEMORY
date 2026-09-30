# Does the right memory stay in Day 3's top-3 as the store grows?
# 12 "gold" memories each paired with a question that needs it; distractors are
# synthetic but realistic user facts from a template grammar. Real nomic-embed-text vectors.
import random, time, numpy as np
from emb import embed, score
rnd = random.Random(42)
gold = [
 ("User now uses AWS ECS for container orchestration.", "Which container platform should my examples target?"),
 ("User is allergic to peanuts.", "Suggest a snack for my afternoon."),
 ("User prefers concise explanations.", "Explain eventual consistency to me."),
 ("User prefers Python examples.", "Show me how to implement a retry with backoff."),
 ("User is preparing for a backend engineering interview.", "What should I focus on this week?"),
 ("User's daughter is named Aria.", "Help me plan a birthday party for my kid."),
 ("User lives in Pune.", "What's a good place for a weekend trip nearby?"),
 ("User's team uses PostgreSQL as the primary database.", "Which database features should I learn deeply?"),
 ("User mentioned they like hiking on weekends.", "Any ideas for this Saturday?"),
 ("User is vegetarian.", "Recommend a dinner recipe."),
 ("User works night shifts on Thursdays.", "When is a good time to schedule our study session?"),
 ("User is learning Rust in the evenings.", "Recommend a side project for me."),
]
roles=["platform engineer","data engineer","SRE","frontend developer","engineering manager","ML engineer","DBA","security engineer"]
tools=["Kubernetes","Terraform","Kafka","Redis","MongoDB","Django","FastAPI","React","Go","Java","Spark","Airflow","GraphQL","gRPC","Nginx","Elasticsearch","DynamoDB","Snowflake","Prometheus","Grafana","Jenkins","GitHub Actions","Helm","Istio","Ansible"]
verbs=["uses","used to use","is evaluating","dislikes","wants to learn","is migrating away from","has production experience with","is debugging an issue in"]
prefs=["prefers bullet points","prefers diagrams","prefers long-form explanations","prefers TypeScript examples","prefers Go examples","wants answers with trade-offs","prefers step-by-step guides","dislikes jargon"]
life=["enjoys cycling","plays chess","is training for a half marathon","has a dog named Bruno","is reading a book on distributed systems","drinks black coffee","is moving to a new apartment next month","plays the guitar","travels to Bangalore often","is learning Japanese","watches Formula 1","enjoys cooking Italian food","has two kids","commutes by metro","volunteers on Sundays"]
events=["attended KubeCon","finished a system design course","shipped a payments service","had an outage last week","got promoted recently","gave a talk on observability","started a new job","completed an AWS certification","joined an open source project","wrote a blog post on caching"]
def distractor():
    k=rnd.random()
    if k<.45: return f"User {rnd.choice(verbs)} {rnd.choice(tools)}{rnd.choice(['',' at work',' for a side project',' in production',' at their previous company'])}."
    if k<.6:  return f"User {rnd.choice(prefs)}."
    if k<.85: return f"User {rnd.choice(life)}."
    if k<.95: return f"User {rnd.choice(events)}."
    return f"User is a {rnd.choice(roles)}."
pool=[]; seen=set(g[0] for g in gold)
while len(pool)<1000:
    d=distractor()
    if d not in seen: seen.add(d); pool.append(d)
print(f"unique distractors generated: {len(pool)}")
t=time.perf_counter()
G=embed([g[0] for g in gold]); Q=embed([g[1] for g in gold]); P=embed(pool)
print(f"embedded {len(pool)+24} texts in {time.perf_counter()-t:.0f}s")
gi=np.array([rnd.uniform(.6,.95) for _ in gold]); gc=np.array([rnd.uniform(.8,.95) for _ in gold])
pi=np.array([rnd.uniform(.3,.95) for _ in pool]); pc=np.array([rnd.uniform(.7,.95) for _ in pool])
print("distractors | recall@3 (Day 3 score) | recall@3 (similarity only) | median rank of gold (Day 3 score)")
for n in [0,10,30,100,300,1000]:
    hitS=hitC=0; ranks=[]
    for j in range(len(gold)):
        D=np.vstack([G,P[:n]]); imp=np.concatenate([gi,pi[:n]]); conf=np.concatenate([gc,pc[:n]])
        s=D@Q[j]; sc=score(s,imp,conf)
        r=int((sc>sc[j]).sum())+1; ranks.append(r)
        hitS+= r<=3; hitC+= int((s>s[j]).sum())+1<=3
    print(f"{n:>11} | {hitS:>2}/12 | {hitC:>2}/12 | {int(np.median(ranks))}")
print("\nper-query detail (Day 3 score): rank at n=0 -> n=1000, and the top-3 at n=1000")
D=np.vstack([G,P]); imp=np.concatenate([gi,pi]); conf=np.concatenate([gc,pc]); texts=[g[0] for g in gold]+pool
for j,(m,q) in enumerate(gold):
    s0=G@Q[j]; sc0=score(s0,gi,gc); r0=int((sc0>sc0[j]).sum())+1
    s=D@Q[j]; sc=score(s,imp,conf); r=int((sc>sc[j]).sum())+1
    top=np.argsort(-sc)[:3]
    print(f"[{r0}->{r}] Q: {q}\n      gold: {m} (sim {s[j]:.2f})")
    for t in top: print(f"      top: {texts[t]} (sim {s[t]:.2f}, imp {imp[t]:.2f})")
