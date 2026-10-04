import torch

class Model:
    def __init__(self, model, name="no_name", interactive: bool = False):
        super().__init__()
        self.model = model          # the agent object
        self.interactive = interactive
        self.final = False
        self.name = name

    def generate(self, prompt, max_tokens=200, temperature=0.0):
        with torch.no_grad():
            return self.model.model.generate(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
            )