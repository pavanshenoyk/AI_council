from config import config
import torch
import os
from Resources.AgentWrapper import Model,HFModel
from Resources.DatabaseFunc import MongoDBController
def loader():
    response={
        "models":[],
        "database":"",
        "context_collectison":""
    }

    device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )

    
    for agent in config["agents"]:
        if not agent["enable"]: continue
        if agent["API"]:continue #too be developed
        model_path=os.path.join(os.getcwd(),"Agents",agent["name"],"agent.pt")
        try:
            model = torch.load(model_path, map_location=device, weights_only=agent["weight_only"])
        except Exception as e:
            raise RuntimeError(f"[loader] Failed to load agent '{agent['name']}': {e}") from e
        if isinstance(model, dict) and "adapter_state" in model:
            response["models"].append(HFModel(model, agent["name"], agent["interactive"], device))
        else:
            response["models"].append(Model(model, agent["name"], agent["interactive"]))

    if config["db_url"]=="": 
        db=MongoDBController(db_name=config["db_name"],collection=config["context_collection"])
    else:
        db=MongoDBController(uri=config["db_url"],db_name=config["db_name"],collection=config["context_collection"])

    try:
        db.connect()
        response["database"] = db
    except Exception as e:
        raise RuntimeError(f"[loader] Could not connect to database: {e}") from e
    return response    

