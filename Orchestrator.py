from bson import ObjectId
import json_repair
from AgentLoader import loader
from Resources.ContextHandler import ContextManager,ProjectExtraction
from pydantic import ValidationError
import os

OPENAI_API_KEY = key = os.environ["OPENAI_API_KEY"]  


def apply_output(context, raw):
    try:
        parsed = json_repair.loads(raw)
        if not isinstance(parsed, dict) or not (parsed.keys() & ProjectExtraction.model_fields.keys()):
            return context 
        return ProjectExtraction.model_validate(parsed)
    except (ValidationError, ValueError, TypeError):
        return context


def render_context(context) -> str:
    data = context.model_dump()
    sections = []

    for key, value in data.items():
        if value is None or value == [] or value == "":
            continue 

        title = key.replace("_", " ").title() 

        if isinstance(value, list):
            lines = []
            for item in value:
                if isinstance(item, dict):
                    # e.g. techstack: {"name": "Python", "purpose": "Backend"}
                    lines.append("- " + ": ".join(str(v) for v in item.values()))
                else:
                    lines.append(f"- {item}")
            body = "\n".join(lines)
        else:
            body = str(value)

        sections.append(f"## {title}\n{body}")

    return "\n\n".join(sections)


class Orcestrator:
    def __init__(self):
        self.config=loader()
        self.context_manager=ContextManager()
        self.db=self.config["database"]

    def run(self,prompt:str|None,id:str|None):
        if prompt=="" or prompt==None:
            return "Please proivde a proper output"
        
        matches = self.db.find({"_id": id})
        if not matches:

            raise SystemExit("No project with that id")
        
        project = matches[0]
        main_prompt = project.get("main_prompt")
        chats = project.get("chats", [])
        saved = project.get("context")
        context = ProjectExtraction(**saved) if saved else None

        question=prompt
            
        
        if not main_prompt:
            main_prompt = question
            self.db.update({"_id": id}, {"main_prompt": main_prompt})
        
        context = self.context_manager.update(new_input=question, context=context)
        self.db.update({"_id": id}, {"context": context.model_dump()})
        
        for model in self.config["models"]:
            raw = model.generate(context.model_dump_json())
            context = apply_output(context, raw)
                # persist after every agent so a crash mid-round doesn't lose progress
            self.db.update({"_id": project_id}, {"context": context.model_dump()})
        
        chats.append({"prompt": question, "output": render_context(context)})
        self.db.update({"_id": project_id}, {"chats": chats})


        
        
            
if __name__ == "__main__":
    
    
    o=Orcestrator()
    project_id = ObjectId(input("project id> ").strip())
    
    while True:
            question=input(">")
            if question.strip().lower() in ("quit", "exit"):
                break
            o.run(question,project_id)

        
            

        
            