import torch
from peft import LoraConfig, get_peft_model, set_peft_model_state_dict
from transformers import AutoTokenizer, AutoModelForCausalLM

_BASES = {}  # base_model_id -> (tokenizer, peft_model), shared across agent

class Model:
    def __init__(self, model, name="no_name", interactive: bool = False):
        super().__init__()
        self.model = model          # the agent object
        self.interactive = interactive
        self.final = False
        self.name = name

    def generate(self, prompt, max_tokens=500, temperature=0.0):
        with torch.no_grad():
            return self.model.model.generate(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )


class HFModel:
    def __init__(self, ckpt: dict, name=None, interactive: bool = False, device=None):
        self.name = name or ckpt["agent_name"]
        self.interactive = interactive
        self.final = False
        self.system_prompt = ckpt["system_prompt"]
        self.device = str(device) if device else ("cuda" if torch.cuda.is_available() else "cpu")

        base_id = ckpt["base_model_id"]
        cfg = LoraConfig(**ckpt["lora_cfg"])

        if base_id not in _BASES:
            tok = AutoTokenizer.from_pretrained(base_id)
            base = AutoModelForCausalLM.from_pretrained(
                base_id,
                torch_dtype=torch.bfloat16 if self.device.startswith("cuda") else torch.float32,
            ).to(self.device)
            _BASES[base_id] = (tok, get_peft_model(base, cfg, adapter_name=self.name))
        else:
            _BASES[base_id][1].add_adapter(self.name, cfg)

        self.tokenizer, self.peft = _BASES[base_id]
        set_peft_model_state_dict(self.peft, ckpt["adapter_state"], adapter_name=self.name)
        self.peft.eval()

    def generate(self, prompt, max_tokens=2048, temperature=0.0):
        self.peft.set_adapter(self.name)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt},
        ]
        inputs = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, enable_thinking=False,
            return_tensors="pt", return_dict=True,
        ).to(self.device)

        kw = {"max_new_tokens": max_tokens, "pad_token_id": self.tokenizer.pad_token_id or self.tokenizer.eos_token_id}
        kw.update(do_sample=True, temperature=temperature) if temperature > 0 else kw.update(do_sample=False)

        with torch.no_grad():
            out = self.peft.generate(**inputs, **kw)
        return self.tokenizer.decode(out[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)