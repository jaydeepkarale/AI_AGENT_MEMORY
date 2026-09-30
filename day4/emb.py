import json, urllib.request, numpy as np
def embed(texts, prefix=""):
    out=[]
    for i in range(0,len(texts),32):
        body=json.dumps({"model":"nomic-embed-text","input":[prefix+t for t in texts[i:i+32]]}).encode()
        r=json.load(urllib.request.urlopen(urllib.request.Request("http://localhost:11434/api/embed",body,{"Content-Type":"application/json"}),timeout=120))
        out+=r["embeddings"]
    a=np.array(out,dtype=np.float32); return a/np.linalg.norm(a,axis=1,keepdims=True)
def score(sim,imp,conf): return sim*0.7+imp*0.2+conf*0.1   # Day 3 formula
