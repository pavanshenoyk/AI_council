class Model:

    def __init__(self,model,name="no_name",interactive:bool=False):
        super().__init__()
        self.model=model
        self.interactive=interactive
        self.final=False
        self.name=name



    def generate(self, prompt):
        response=self.model.generate(prompt)
        return response

        
    