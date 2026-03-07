from app.graph.base import BaseAgent

PyObject = dict

class NodeExtrator(BaseAgent):
    
    model_name = "gpt-4.1"
    prompt_name = "prompt_01"

    async def __call__(self, state):

        prompt_vars = {}
        prompt = self.prompt_template.format_messages(**prompt_vars)

        llm = self.model.with_structured_output(PyObject)
        output = await llm.ainvoke(prompt)
        return {"attribute": output}


class EdgeExtractor(BaseAgent):
    
    model_name = "gpt-4.1"
    prompt_name = "prompt_01"

    async def __call__(self, state):

        prompt_vars = {}
        prompt = self.prompt_template.format_messages(**prompt_vars)

        llm = self.model.with_structured_output(PyObject)
        output = await llm.ainvoke(prompt)
        return {"attribute": output}

class GraphWriter(BaseAgent):
    
    model_name = "gpt-4.1"
    prompt_name = "prompt_01"

    async def __call__(self, state):

        prompt_vars = {}
        prompt = self.prompt_template.format_messages(**prompt_vars)

        llm = self.model.with_structured_output(PyObject)
        output = await llm.ainvoke(prompt)
        return {"attribute": output}

