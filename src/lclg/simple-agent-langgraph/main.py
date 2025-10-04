import operator
import logging
from typing import Any, Type

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain.agents import create_agent
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 1. Define custom tool classes inheriting from BaseTool
class AddToolInput(BaseModel):
    """Input for AddTool."""
    first_int: int = Field(description="First integer to add.")
    second_int: int = Field(description="Second integer to add.")

class AddTool(BaseTool):
    """A tool for adding two numbers."""
    name: str = "add"
    description: str = "use this tool to add two integers together"
    args_schema: Type[BaseModel] = AddToolInput

    def _run(self, first_int: int, second_int: int, **kwargs: Any) -> Any:
        logger.info(f"Adding {first_int} and {second_int}")
        return operator.add(first_int, second_int)

class MultiplyToolInput(BaseModel):
    """Input for MultiplyTool."""
    first_int: int = Field(description="First integer to multiply.")
    second_int: int = Field(description="Second integer to multiply.")

class MultiplyTool(BaseTool):
    """A tool for multiplying two numbers."""
    name: str = "multiply"
    description: str = "use this tool to multiply two integers together"
    args_schema: Type[BaseModel] = MultiplyToolInput

    def _run(self, first_int: int, second_int: int, **kwargs: Any) -> Any:
        logger.info(f"Multiplying {first_int} and {second_int}")
        return operator.mul(first_int, second_int)

# 2. Instantiate the custom tool classes
add_tool_instance = AddTool()
multiply_tool_instance = MultiplyTool()

# 3. Create the list of tools for the agent
tools = [add_tool_instance, multiply_tool_instance]

llm = ChatOllama(
    model="llama3.2:latest",
    temperature=0,
    base_url="http://localhost:11434"
)

# 5. Create the agent using langchain's create_agent
prompt = "You are a helpful assistant that can perform calculations. Use the available tools to answer questions."

logger.info("Creating legacy react agent")
legacy_react_agent = create_react_agent(llm, tools, prompt=prompt)
logger.info("Legacy react agent created")

logger.info("Creating Modern agent")
modern_agent = create_agent(llm, tools, prompt=prompt)
logger.info("Mordern Agent created")


# 6. Use the agent to invoke a query
if __name__ == "__main__":
    
    inputs = {"messages": [HumanMessage(content="What is the product of 5 and 3, plus 10?")]}

    logger.info("Invoking react agent")
    result = legacy_react_agent.invoke(inputs)
    logger.info(f"Legacy react agent result: {result['messages'][-1].content}")

    logger.info("Invoking modern agent")
    result = modern_agent.invoke(inputs) 
    logger.info(f"Modern agent result: {result['messages'][-1].content}")