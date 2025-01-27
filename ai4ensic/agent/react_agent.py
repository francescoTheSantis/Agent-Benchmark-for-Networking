from .base_agent import BaseAgent
from ..working_memory import ReActChain
from ..procedures import ReActProcedure
from ..prompts import REACT_TEMPLATE
from termcolor import cprint


class ReActAgent(BaseAgent):
    """An autonomous agent that can reason and act based on observations and a 
    given task.

    This class extends the BaseAgent class and implements the step method to perform
    autonomous reasoning and action selection.

    Args:
        prompt_template (str): A template string for formatting the agent's prompt.
        llm (LLMClient): An instance of the LLM client for generating responses.
        working_memory (ReActScratchpad): An instance to manage the agent's working memory.
        tools (list): A list of tool functions available to the agent.
        logpath (str, optional): Path to save logs. Defaults to None.

    Attributes:
        prompt_template (str): The template for formatting the agent's prompt.
        working_memory (ReActScratchpad): The agent's working memory.
        llm (LLMClient): The LLM client used by the agent.
        tools (dict): A dictionary of available tools, keyed by their names.
        logpath (str): Path for saving logs.
        task (str): The current task assigned to the agent.
        prompt (str): The formatted prompt for the current task.
        last_step (ReActChain): The most recent step in the agent's reasoning chain.
        start (bool): Flag indicating if this is the start of a new task.

    Methods:
        reset(task): Resets the agent's state for a new task.
        update_memory(observation): Updates the agent's working memory with a new observation.
        write_logs(fpath): Writes the agent's memory logs to a file.
        agent_finish(observation): Finalizes the agent's task with a final observation.
        step(observation): Performs a single step in the agent's reasoning process.
    """

    def step(self, observation: str):
        """Performs a single step in the agent's autonomous reasoning and action process.

        This method implements the core logic of the autonomous agent, including:
        1. Updating the working memory with the new observation
        2. Producing a thought about the next action and selecting and formatting the next action

        Args:
            observation (str): The current observation to process.

        Returns:
            ReActChain: The updated last step of the agent's reasoning chain.
        """

        # Update Working Memory
        self.update_memory(observation)

        # Get scratchpad and prompt
        self.scratchpad = self.working_memory.to_messages()
        instructions = self.prompt_template.format(input=self.task)

        react_procedure = ReActProcedure(self.llm, REACT_TEMPLATE)
        llm_out = react_procedure.run(
            context=instructions,
            scratchpad=self.scratchpad,
            last_step=self.last_step,
            actions=self.tools
        )
        thought = llm_out.thought
        cprint(f'Thought: {thought}', color='cyan')
        action = llm_out.action
        tool = action.__class__.__name__
        cprint(f'Action: {tool}({action})', color='magenta')

        # Format the last reasoning chain
        self.last_step = ReActChain.format('', thought, action)

        return self.last_step
