"""
Test runner for ContextManager.

Put this next to your ContextManager file, then:

    export OPENAI_API_KEY=...
    python test_context_manager.py                 # expects context_manager.py
    python test_context_manager.py my_module_name  # if your file is named differently

Part 1 runs offline (no API calls). Part 2 calls the model, so it costs a few
tiny requests. Assertions on model output are deliberately loose (case-insensitive
substring checks) because LLM wording varies between runs.
"""

import importlib
import json
import os
import sys
import traceback

# paste your key here
OPENAI_API_KEY = "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"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

mod = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "context_manager")
ContextManager = mod.ContextManager
ProjectExtraction = mod.ProjectExtraction

results = []


def check(name, fn):
    try:
        fn()
        results.append((name, True, ""))
        print(f"  PASS  {name}")
    except Exception as e:
        results.append((name, False, f"{type(e).__name__}: {e}"))
        print(f"  FAIL  {name}\n        {type(e).__name__}: {e}")
        if "-v" in sys.argv:
            traceback.print_exc()


def has(text, needle):
    return needle.lower() in (text or "").lower()


# ---------------------------------------------------------------- part 1: offline

print("\nPart 1: offline (_coerce)")

coerce = ContextManager._coerce


def t_none():
    assert coerce(None) is None


def t_empty_str():
    assert coerce("") is None
    assert coerce("   ") is None


def t_empty_dict():
    assert coerce({}) is None


def t_mongo_bookkeeping_only():
    assert coerce({"_id": "abc", "updated_at": "2026-01-01"}) is None


def t_dict_with_data():
    out = coerce({"_id": "abc", "updated_at": "x", "frontend": "React", "team_size": 3})
    assert isinstance(out, ProjectExtraction)
    assert out.frontend == "React" and out.team_size == 3


def t_json_string():
    out = coerce(json.dumps({"backend": "FastAPI"}))
    assert isinstance(out, ProjectExtraction) and out.backend == "FastAPI"


def t_model_passthrough():
    m = ProjectExtraction(database="Postgres")
    assert coerce(m) is m


def t_bad_type():
    try:
        coerce(123)
    except TypeError:
        return
    raise AssertionError("expected TypeError")


def t_defaults():
    m = ProjectExtraction()
    assert m.techstack == [] and m.testcases == []
    assert m.functional_requirements == [] and m.non_functional_requirements == []


for n, f in [
    ("None -> no context", t_none),
    ("'' / whitespace -> no context", t_empty_str),
    ("{} -> no context", t_empty_dict),
    ("mongo bookkeeping only -> no context", t_mongo_bookkeeping_only),
    ("dict with data (strips _id/updated_at)", t_dict_with_data),
    ("JSON string", t_json_string),
    ("ProjectExtraction passthrough", t_model_passthrough),
    ("unsupported type raises TypeError", t_bad_type),
    ("schema defaults are empty lists", t_defaults),
]:
    check(n, f)

# ---------------------------------------------------------------- part 2: live API

print("\nPart 2: live API (needs OPENAI_API_KEY)")

try:
    cm = ContextManager()
except Exception as e:
    print(f"  Could not create ContextManager: {e}")
    cm = None

state = {}

if cm:
    def t_new_project():
        ctx = cm.update(
            None,
            "Building an inventory app, team of 3, React frontend and FastAPI "
            "backend with Postgres.",
        )
        assert isinstance(ctx, ProjectExtraction)
        assert ctx.team_size == 3, f"team_size={ctx.team_size}"
        assert has(ctx.frontend, "react"), f"frontend={ctx.frontend}"
        assert has(ctx.backend, "fastapi"), f"backend={ctx.backend}"
        assert has(ctx.database, "postgres"), f"database={ctx.database}"
        state["ctx1"] = ctx
        print(f"        -> {ctx.model_dump_json()}")

    def t_no_invention():
        ctx = state.get("ctx1")
        assert ctx, "needs test above to pass"
        # nothing about tests or planning was said
        assert ctx.testcases == [], f"invented testcases: {ctx.testcases}"
        assert not ctx.project_planning, f"invented planning: {ctx.project_planning}"

    def t_empty_string_is_new():
        ctx = cm.update("", "Small blog platform, solo developer, Django backend.")
        assert has(ctx.backend, "django"), f"backend={ctx.backend}"
        assert ctx.team_size == 1 or ctx.team_size is None, f"team_size={ctx.team_size}"

    def t_update_overrides_and_preserves():
        ctx1 = state.get("ctx1")
        assert ctx1, "needs the new-project test to pass"
        ctx2 = cm.update(
            ctx1,
            "Actually we're switching the database to MongoDB. "
            "The system must support 1000 concurrent users.",
        )
        assert has(ctx2.database, "mongo"), f"database not updated: {ctx2.database}"
        assert ctx2.team_size == 3, f"team_size lost: {ctx2.team_size}"
        assert has(ctx2.frontend, "react"), f"frontend lost: {ctx2.frontend}"
        assert has(ctx2.backend, "fastapi"), f"backend lost: {ctx2.backend}"
        reqs = ctx2.functional_requirements + ctx2.non_functional_requirements
        assert any("1000" in r for r in reqs), f"1000-users requirement missing: {reqs}"
        state["ctx2"] = ctx2
        print(f"        -> {ctx2.model_dump_json()}")

    def t_list_append_keeps_old():
        ctx2 = state.get("ctx2")
        assert ctx2, "needs the update test to pass"
        ctx3 = cm.update(ctx2, "Users should also be able to export reports as PDF.")
        reqs = ctx3.functional_requirements + ctx3.non_functional_requirements
        assert any("pdf" in r.lower() for r in reqs), f"pdf requirement missing: {reqs}"
        assert any("1000" in r for r in reqs), f"old requirement dropped: {reqs}"
        state["ctx3"] = ctx3

    def t_mongo_style_doc():
        ctx3 = state.get("ctx3")
        assert ctx3, "needs the previous test to pass"
        doc = {"_id": "proj-1", "updated_at": "2026-10-11", **ctx3.model_dump()}
        ctx4 = cm.update(doc, "Add a test case: login fails with a wrong password.")
        assert any("password" in t.lower() for t in ctx4.testcases), f"testcases={ctx4.testcases}"
        assert has(ctx4.database, "mongo"), f"database lost: {ctx4.database}"

    def t_techstack_shape():
        ctx = cm.update(None, "We use Python for the backend and React for the UI.")
        assert ctx.techstack, "techstack empty"
        assert all(hasattr(t, "name") and hasattr(t, "purpose") for t in ctx.techstack)
        names = " ".join(t.name.lower() for t in ctx.techstack)
        assert "python" in names and "react" in names, f"techstack={ctx.techstack}"

    for n, f in [
        ("new project from None", t_new_project),
        ("does not invent unstated fields", t_no_invention),
        ("'' treated as new project", t_empty_string_is_new),
        ("update overrides database, preserves the rest", t_update_overrides_and_preserves),
        ("list append keeps old items", t_list_append_keeps_old),
        ("raw Mongo-style doc as context", t_mongo_style_doc),
        ("techstack comes back as name/purpose objects", t_techstack_shape),
    ]:
        check(n, f)

# ---------------------------------------------------------------- summary

passed = sum(1 for _, ok, _ in results if ok)
print(f"\n{passed}/{len(results)} passed")
if passed != len(results):
    print("\nFailures:")
    for name, ok, msg in results:
        if not ok:
            print(f"  - {name}: {msg}")
    print("\nRe-run with -v for full tracebacks.")
    sys.exit(1)