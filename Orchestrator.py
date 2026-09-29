from AgentLoader import loader
from numpy import dot
from numpy.linalg import norm

from sentence_transformers import SentenceTransformer
import numpy as np

_model = SentenceTransformer("all-MiniLM-L6-v2")  # loaded once at import, not per call


def embed_fn(text: str):
    return _model.encode(text)


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def has_converged(prev_council, current_council, threshold=0.9):
    v1 = embed_fn(prev_council)
    v2 = embed_fn(current_council)
    return cosine_similarity(v1, v2) >= threshold


def iterate(models, prompt):
    results = []
    for model in models:
        response = model.generate(prompt)
        results.append({"agent": model.name, "response": response})

    return results

def Looping(models,prompt,previous_result=None,depth=0,max_depth=5):
    current_result=iterate(models,prompt)
    results=f"{prompt}\n" + "\n".join(f"{r['agent']}: {r['response']}" for r in current_result)
    if depth+1==max_depth: return current_result,results
    if previous_result ==None:
        return Looping(models,results,results,depth+1)
    if has_converged(str(previous_result),str(results)): return current_result,results
    else: return Looping(models,results,results,depth+1)
    

if __name__ == "__main__":
    config = loader()
    db=config["database"]
    while True:
        doc = {"prompt": "", "iteration": []}
        prompt = input(">")
        doc["prompt"]=prompt
        while True:
            res_list,result=Looping(models=config["models"],prompt=prompt)
            entry = {r["agent"]: r["response"] for r in res_list}
            entry["council"] = result
            doc["iteration"].append(entry)
            print(result)
            prompt=input(">")
            if prompt.strip().lower() == "done": break
            doc["iteration"][-1]["user"] = prompt
            prompt=f"{result}+\nuser response : {prompt}"

        db.insert("chats", doc)


        

        

    
            
            
