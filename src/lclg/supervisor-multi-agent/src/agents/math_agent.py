"""MathAgent for numerical problem-solving."""

import math
import re
from typing import Any, Dict, List, Optional
from langchain.tools import BaseTool, tool
from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentMessage


class CalculatorInput(BaseModel):
    """Input for the calculator tool."""
    expression: str = Field(description="Mathematical expression to evaluate")


class MathAgent(BaseAgent):
    """Agent specialized in mathematical problem-solving."""
    
    def __init__(
        self,
        llm: Optional[Any] = None,
        temperature: float = 0.1,
        model_name: str = "gpt-4",
        api_key: Optional[str] = None
    ):
        super().__init__(
            name="MathAgent",
            llm=llm,
            temperature=temperature,
            model_name=model_name,
            api_key=api_key
        )
    
    def _setup_tools(self) -> None:
        """Set up mathematical tools."""
        self.tools = [
            self._create_calculator_tool(),
            self._create_equation_solver_tool(),
            self._create_statistics_tool(),
            self._create_geometry_tool()
        ]
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the math agent."""
        return """You are a specialized mathematical problem-solving agent. Your expertise includes:

- Basic arithmetic operations (addition, subtraction, multiplication, division)
- Advanced mathematics (algebra, calculus, trigonometry, statistics)
- Equation solving and simplification
- Statistical analysis and probability
- Geometric calculations
- Mathematical modeling and optimization

When solving problems:
1. Break down complex problems into simpler steps
2. Show your work and reasoning clearly
3. Verify your calculations when possible
4. Provide explanations for mathematical concepts
5. Use appropriate mathematical notation

Always be precise and accurate in your calculations."""
    
    def _get_agent_type(self) -> str:
        """Get the agent type for prompt selection."""
        return "math"
    
    def _create_calculator_tool(self) -> BaseTool:
        """Create a safe calculator tool for mathematical expressions."""
        
        def calculate(expression: str) -> str:
            """Safely evaluate mathematical expressions."""
            try:
                # Remove any potentially dangerous characters
                safe_expression = re.sub(r'[^0-9+\-*/().\s]', '', expression)
                
                # Replace common mathematical functions
                safe_expression = safe_expression.replace('^', '**')
                
                # Evaluate the expression
                result = eval(safe_expression)
                return f"Result: {result}"
            except Exception as e:
                return f"Error calculating expression: {str(e)}"
        
        return tool("calculator")(calculate)
    
    def _create_equation_solver_tool(self) -> BaseTool:
        """Create a tool for solving simple equations."""
        
        @tool("equation_solver")
        def solve_equation(equation: str) -> str:
            """Solve simple linear equations."""
            try:
                # This is a simplified equation solver
                # For production, you'd want to use a proper symbolic math library
                if 'x' in equation:
                    # Simple linear equation solving
                    equation = equation.replace(' ', '')
                    if equation.startswith('x'):
                        equation = '1' + equation
                    
                    # Extract coefficients (simplified)
                    parts = equation.split('=')
                    if len(parts) == 2:
                        left, right = parts
                        # This is a very basic implementation
                        return f"To solve {equation}, you would need to isolate x. This requires more sophisticated parsing."
                    else:
                        return "Invalid equation format. Use format like '2x + 3 = 7'"
                else:
                    return "No variable 'x' found in equation"
            except Exception as e:
                return f"Error solving equation: {str(e)}"
        
        return solve_equation
    
    def _create_statistics_tool(self) -> BaseTool:
        """Create a tool for basic statistical calculations."""
        
        @tool("statistics")
        def calculate_statistics(data: str) -> str:
            """Calculate basic statistics from a list of numbers."""
            try:
                # Parse the data (expecting comma-separated numbers)
                numbers = [float(x.strip()) for x in data.split(',')]
                
                if not numbers:
                    return "No numbers provided"
                
                n = len(numbers)
                mean = sum(numbers) / n
                variance = sum((x - mean) ** 2 for x in numbers) / n
                std_dev = math.sqrt(variance)
                
                # Sort for median
                sorted_numbers = sorted(numbers)
                if n % 2 == 0:
                    median = (sorted_numbers[n//2 - 1] + sorted_numbers[n//2]) / 2
                else:
                    median = sorted_numbers[n//2]
                
                return f"""Statistics for {numbers}:
- Count: {n}
- Mean: {mean:.4f}
- Median: {median:.4f}
- Standard Deviation: {std_dev:.4f}
- Variance: {variance:.4f}
- Min: {min(numbers)}
- Max: {max(numbers)}"""
            except Exception as e:
                return f"Error calculating statistics: {str(e)}"
        
        return calculate_statistics
    
    def _create_geometry_tool(self) -> BaseTool:
        """Create a tool for geometric calculations."""
        
        @tool("geometry")
        def geometry_calculator(calculation: str) -> str:
            """Perform basic geometric calculations."""
            try:
                calculation = calculation.lower().strip()
                
                if "circle" in calculation:
                    # Extract radius if mentioned
                    radius_match = re.search(r'radius[:\s]*(\d+\.?\d*)', calculation)
                    if radius_match:
                        radius = float(radius_match.group(1))
                        area = math.pi * radius ** 2
                        circumference = 2 * math.pi * radius
                        return f"Circle with radius {radius}:\n- Area: {area:.4f}\n- Circumference: {circumference:.4f}"
                    else:
                        return "Please specify the radius of the circle"
                
                elif "rectangle" in calculation or "square" in calculation:
                    # Extract dimensions
                    length_match = re.search(r'length[:\s]*(\d+\.?\d*)', calculation)
                    width_match = re.search(r'width[:\s]*(\d+\.?\d*)', calculation)
                    
                    if length_match and width_match:
                        length = float(length_match.group(1))
                        width = float(width_match.group(1))
                        area = length * width
                        perimeter = 2 * (length + width)
                        return f"Rectangle {length}x{width}:\n- Area: {area}\n- Perimeter: {perimeter}"
                    else:
                        return "Please specify both length and width"
                
                elif "triangle" in calculation:
                    # Extract base and height
                    base_match = re.search(r'base[:\s]*(\d+\.?\d*)', calculation)
                    height_match = re.search(r'height[:\s]*(\d+\.?\d*)', calculation)
                    
                    if base_match and height_match:
                        base = float(base_match.group(1))
                        height = float(height_match.group(1))
                        area = 0.5 * base * height
                        return f"Triangle with base {base} and height {height}:\n- Area: {area}"
                    else:
                        return "Please specify both base and height"
                
                else:
                    return "Supported shapes: circle, rectangle, square, triangle. Please specify dimensions."
                    
            except Exception as e:
                return f"Error in geometry calculation: {str(e)}"
        
        return geometry_calculator
