import re
from typing import Optional
from openai import OpenAI
import json
from pydantic import BaseModel, Field, ValidationError


class TechItem(BaseModel):
    name: str = Field(description="Language or technology, e.g. 'Python'")
    purpose: str = Field(description="What it is used for, e.g. 'Backend development'")

class ProjectExtraction(BaseModel):
    project_type: str | None = Field(
        default=None,
        description="Kind of project only, e.g. 'IoT', 'mobile app', 'web app', 'CLI tool'"
    )
    project_description: str | None = Field(
        default=None,
        description="What the project does and who it is for"
    )
    team_size: int | None = None

    rules: list[str] = Field(
            default_factory=list,
            description="user preferences and constraints"
        )

    functional_requirements: list[str] = Field(
        default_factory=list,
        description="Functional requirements explicitly stated by the user"
    )

    non_functional_requirements: list[str] = Field(
        default_factory=list,
        description="Non-functional requirements explicitly stated by the user"
    )

    techstack: list[TechItem] = Field(
        default_factory=list,
        description=(
            "Languages and technologies mapped to their purposes, as mentioned by the user."
        )
    )

    database_design: str | None = Field(
        default=None,
        description="Complete database design in string format"
    )

    project_planning: str | None = Field(
        default=None,
        description="Complete project planning details in string format"
    )

    architecture_design: str | None = Field(
        default=None,
        description="Complete software architecture design in string format"
    )

    testcases: list[str] = Field(
        default_factory=list,
        description="Test cases explicitly mentioned by the user"
    )


class ContextManager:
    def __init__(self,model:str="gpt-6-luna",max_retries:int=2):
        self.model = model
        self.max_retries = max_retries
        self.client = OpenAI()

    @staticmethod
    def _coerce(context) -> Optional[ProjectExtraction]:
        """Normalise whatever the caller passes. Returns None if there is no context yet."""
        if context is None:
            return None
        if isinstance(context, ProjectExtraction):
            return context
        if isinstance(context, str):
            if not context.strip():
                return None
            context = json.loads(context)
        if isinstance(context, dict):
            # drop Mongo bookkeeping fields if the raw document was passed in
            context = {k: v for k, v in context.items() if k not in ("_id", "updated_at")}
            if not context:
                return None
            return ProjectExtraction(**context)
        raise TypeError(f"Unsupported context type: {type(context)}")
 
    def _new_prompt(self, new_input: str) -> str:
        return (
            "The user is describing a NEW software project. Extract the details into "
            "the schema and return ONLY the JSON.\n\n"
            "Rules:\n"
            "- Fill only what the user actually stated; leave everything else null or empty.\n"
            "- any personal preferences and constraints specified by the user goes in the rules list.\n"
            "- Do not invent requirements, tech choices or designs.\n\n"
            f"Schema:\n{ProjectExtraction.model_json_schema()}\n\n"
            f"User input:\n{new_input}"
        )
 
    def _update_prompt(self, current: ProjectExtraction, new_input: str) -> str:
        return (
            "You maintain the context of an existing software project. Update it using "
            "the new input and return ONLY the full updated JSON matching the schema.\n\n"
            "Rules:\n"
            "- Keep all existing information unless the new input contradicts or replaces it.\n"
            "- Newer information overrides older information.\n"
            "- Add new items to lists; do not drop existing items unless told to remove them.\n"
            "- any personal preferences and constraints specified by the user goes in the rules list.\n"
            "- Do not invent facts that are in neither the current context nor the new input.\n\n"
            f"Schema:\n{ProjectExtraction.model_json_schema()}\n\n"
            f"Current context:\n{current.model_dump_json()}\n\n"
            f"New input:\n{new_input}"
        )
 
    def _call_llm(self, prompt: str) -> str:
        r = self.client.chat.completions.parse(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format=ProjectExtraction,
        )
        return r.choices[0].message.content or ""
 
    @staticmethod
    def _strip_fences(text: str) -> str:
        return re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
 
    def update(self, context: ProjectExtraction, new_input: str) -> ProjectExtraction:
        """Return the new/updated context for this input."""
        current = self._coerce(context)
        prompt = (
            self._new_prompt(new_input)
            if current is None
            else self._update_prompt(current, new_input)
        )
 
        last_error = None
        for _ in range(self.max_retries + 1):
            raw = self._call_llm(prompt)
            try:
                return ProjectExtraction.model_validate_json(self._strip_fences(raw))
            except ValidationError as e:
                last_error = e
                prompt += f"\n\nYour last output was invalid: {e}\nFix it and return only the JSON."
 
        raise RuntimeError(f"LLM failed to return valid context: {last_error}")
 
    
        