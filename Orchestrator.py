from AgentLoader import loader


from AgentLoader import loader

def render(records):
    # records = [{"USER": "..."}, {"REQUIREMENT_ANALYSIS": "..."}, ...]
    lines = []
    for i, rec in enumerate(records):
        for key, value in rec.items():
            tag = "PROJECT" if (i == 0 and key == "USER") else key
            lines.append(f"###{tag} {value}")
    return "\n".join(lines)

def last_turns(records, n):
    # keep only the last n turns (a turn starts at each USER record)
    starts = [i for i, r in enumerate(records) if "USER" in r]
    return records[starts[-n]:] if n and len(starts) > n else records

if __name__ == "__main__":
    config = loader()
    models = config["models"]
    records = []

    while True:
        ip = input("\n> ")
        if ip.strip().lower() in ("done", "quit", "exit"):
            break
        records.append({"USER": ip})

        response = "INVALID RESPONSE"
        for model in models:
            response = model.generate(render(last_turns(records, config.get("context_size"))))
            records.append({model.name.upper(): response})

        print(response)
