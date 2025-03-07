from ..tools import *
from ..working_memory import ReActChain
from .base_procedure import BaseProcedure
from typing import Dict, Any, Type, Union
from pydantic import BaseModel, Field, create_model


class ActionModel(BaseModel):
    action: Any = Field(...)

    class Config:
        @staticmethod
        def json_schema_extra(schema: Dict[str, Any], model: Type['ActionModel']) -> None:
            for prop in schema.get('properties', {}).values():
                prop.pop('title', None)

    @classmethod
    def create(cls, actions):
        return create_model(
            cls.__name__,
            action=(Union[tuple(actions)], Field(...)),
            __base__=cls
        )


class ActionProcedure(BaseProcedure):
    """A reasoning procedure that invokes the LLM to produce an action based on 
    the thought and context summary.

    This class extends the BaseProcedure to handle reasoning and action production. 
    It leverages a summary of the scratchpad, the last reasoning step, and the 
    agent's thoughts to generate actions using the LLM.

    Args:
        llm (LLMClient): The LLM client responsible for executing tasks based 
            on the prompt.
        prompt_template (str): The prompt template that will be formatted and 
            used as input to the LLM.

    Attributes:
        llm (LLMClient): The LLM client responsible for executing tasks based 
            on the prompt.
        prompt_template (str): The prompt template that will be formatted and 
            used as input to the LLM.

    Methods:
        run(summary, last_step, thought, actions): Generates actions based on 
            the given inputs using the LLM.
    """

    def run(self, summary: str, scratchpad: list, last_step: ReActChain, thought: str, actions: list):
        """Executes the action reasoning procedure based on the current context.

        This method formats the prompt using the given summary, the previous step 
        in the reasoning process (last_step), and the agent's current thought. 
        It then invokes the LLM to generate appropriate actions.

        Args:
            summary (str): The produced summary for the current chain.
            last_step (ReActChain): The last step in the reasoning chain, 
                representing the agent's prior thought process.
            thought (str): The produced thought for the current chain
            actions (list): List of the tools the agent has to choice. Each 
                tool is an instance of autopenbench.Tools

        Returns:
            ActionModel: The ActionModel formatted by the LLM
        """
        # Format the prompt
        prompt = self.prompt_template.format(
            summary=summary,
            last_step=last_step.to_str(),
            thought=thought
        )

        # Invoke LLM with the defined Action model
        llm_out = self.llm.invoke(
            response_model=ActionModel.create(actions),
            system_prompt=prompt,
            messages=scratchpad
        )

        return llm_out
