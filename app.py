import streamlit as st
import re
from typing import Dict, List, Any

class ChainOfThoughtMathSolver:
    """A math problem solver that uses chain-of-thought reasoning"""
    
    def __init__(self):
        pass
        
    def solve(self, problem: str) -> Dict[str, Any]:
        """Main method to solve a math problem with chain-of-thought"""
        
        problem = problem.strip()
        understanding = self._understand_problem(problem)
        numbers = self._extract_numbers(problem)
        operations = self._identify_operations(problem)
        reasoning = self._build_reasoning_chain(problem, numbers, operations)
        result_data = self._calculate(problem, numbers, operations)
        
        return {
            'problem': problem,
            'understanding': understanding,
            'numbers_extracted': numbers,
            'operations_identified': operations,
            'chain_of_thought': reasoning,
            'result': result_data['value'],
            'calculation_steps': result_data['steps']
        }
    
    def _understand_problem(self, problem: str) -> str:
        problem_lower = problem.lower()
        
        if 'average' in problem_lower or 'mean' in problem_lower:
            return "This problem requires calculating the average (sum of numbers divided by count)"
        elif 'sum' in problem_lower or 'add' in problem_lower or 'total' in problem_lower or '+' in problem:
            return "This problem requires addition of numbers"
        elif 'difference' in problem_lower or 'subtract' in problem_lower or 'minus' in problem_lower or '-' in problem:
            return "This problem requires subtraction"
        elif 'product' in problem_lower or 'multiply' in problem_lower or 'times' in problem_lower or '*' in problem or '×' in problem:
            return "This problem requires multiplication"
        elif 'divide' in problem_lower or 'quotient' in problem_lower or '/' in problem or '÷' in problem:
            return "This problem requires division"
        elif 'percentage' in problem_lower or 'percent' in problem_lower or '%' in problem:
            return "This problem requires percentage calculation"
        elif 'square' in problem_lower or 'power' in problem_lower or '^' in problem:
            return "This problem requires exponentiation"
        else:
            return "This is a basic arithmetic problem"
    
    def _extract_numbers(self, problem: str) -> List[float]:
        pattern = r'-?\d+\.?\d*'
        numbers = re.findall(pattern, problem)
        return [float(num) for num in numbers if num]
    
    def _identify_operations(self, problem: str) -> List[str]:
        ops = []
        problem_lower = problem.lower()
        
        if 'plus' in problem_lower or 'add' in problem_lower or '+' in problem:
            ops.append('addition')
        if 'minus' in problem_lower or 'subtract' in problem_lower or '-' in problem:
            ops.append('subtraction')
        if 'times' in problem_lower or 'multiply' in problem_lower or '*' in problem or '×' in problem:
            ops.append('multiplication')
        if 'divided by' in problem_lower or 'divide' in problem_lower or '/' in problem or '÷' in problem:
            ops.append('division')
        if 'average' in problem_lower or 'mean' in problem_lower:
            ops.append('average')
        if 'percent' in problem_lower or '%' in problem_lower:
            ops.append('percentage')
        if 'square' in problem_lower or 'power' in problem_lower or '^' in problem:
            ops.append('exponent')
        if 'sum' in problem_lower or 'total' in problem_lower:
            ops.append('summation')
            
        return ops if ops else ['basic arithmetic']
    
    def _build_reasoning_chain(self, problem: str, numbers: List[float], operations: List[str]) -> List[str]:
        chain = []
        
        chain.append(f"Step 1: Let me understand the problem: {problem}")
        chain.append(f"Step 2: I need to {' and '.join(operations)} using the numbers I find.")
        
        if numbers:
            chain.append(f"Step 3: The numbers given are: {', '.join([str(n) for n in numbers])}")
        
        if 'average' in operations:
            if len(numbers) >= 1:
                total = sum(numbers)
                count = len(numbers)
                chain.append(f"Step 4: To find the average, I will sum all numbers: {total}")
                chain.append(f"Step 5: Then divide by the count ({count} numbers): {total} ÷ {count}")
        elif 'percentage' in operations or 'percent' in str(problem).lower():
            if len(numbers) >= 2:
                chain.append(f"Step 4: To find {numbers[0]}% of {numbers[1]}, multiply {numbers[0]}% by {numbers[1]}")
                chain.append(f"Step 5: Convert {numbers[0]}% to decimal: {numbers[0]/100}")
                chain.append(f"Step 6: Multiply: {numbers[0]/100} × {numbers[1]}")
        elif 'addition' in operations or 'summation' in operations:
            if len(numbers) >= 2:
                total = sum(numbers)
                chain.append(f"Step 4: Add all numbers: {' + '.join([str(n) for n in numbers])} = {total}")
        elif 'subtraction' in operations:
            if len(numbers) >= 2:
                chain.append(f"Step 4: Subtract the numbers: {numbers[0]} - {numbers[1]} = {numbers[0] - numbers[1]}")
        elif 'multiplication' in operations:
            if len(numbers) >= 2:
                product = numbers[0] * numbers[1]
                chain.append(f"Step 4: Multiply the numbers: {numbers[0]} × {numbers[1]} = {product}")
        elif 'division' in operations:
            if len(numbers) >= 2 and numbers[1] != 0:
                quotient = numbers[0] / numbers[1]
                chain.append(f"Step 4: Divide the numbers: {numbers[0]} ÷ {numbers[1]} = {quotient}")
        
        return chain
    
    def _calculate(self, problem: str, numbers: List[float], operations: List[str]) -> Dict[str, Any]:
        result = None
        calculation_steps = []
        
        try:
            if 'percent' in problem.lower() and len(numbers) >= 2:
                percent = numbers[0]
                value = numbers[1]
                result = (percent / 100) * value
                calculation_steps.append(f"Step 1: Identify the percentage: {percent}%")
                calculation_steps.append(f"Step 2: Identify the base value: {value}")
                calculation_steps.append(f"Step 3: Convert percentage to decimal: {percent}% = {percent/100}")
                calculation_steps.append(f"Step 4: Multiply decimal by base value: {percent/100} × {value}")
                calculation_steps.append(f"Step 5: Final result = {result}")
            
            elif 'average' in operations or 'mean' in operations:
                if numbers:
                    total = sum(numbers)
                    count = len(numbers)
                    result = total / count
                    calculation_steps.append(f"Sum = {total}")
                    calculation_steps.append(f"Count = {count}")
                    calculation_steps.append(f"Average = {total} ÷ {count} = {result}")
            
            elif 'percentage' in operations:
                if len(numbers) >= 2:
                    percent = numbers[0]
                    value = numbers[1]
                    result = (percent / 100) * value
                    calculation_steps.append(f"{percent}% of {value} = ({percent} ÷ 100) × {value}")
                    calculation_steps.append(f"= {percent/100} × {value}")
                    calculation_steps.append(f"= {result}")
            
            elif 'sum' in operations or 'addition' in operations or 'total' in operations or '+' in problem:
                if numbers:
                    result = sum(numbers)
                    calculation_steps.append(f"{' + '.join([str(n) for n in numbers])} = {result}")
            
            elif 'difference' in operations or 'subtraction' in operations or '-' in problem:
                if len(numbers) >= 2:
                    result = numbers[0] - numbers[1]
                    calculation_steps.append(f"{numbers[0]} - {numbers[1]} = {result}")
            
            elif 'product' in operations or 'multiplication' in operations or '*' in problem or '×' in problem:
                if len(numbers) >= 2:
                    result = numbers[0] * numbers[1]
                    calculation_steps.append(f"{numbers[0]} × {numbers[1]} = {result}")
            
            elif 'quotient' in operations or 'division' in operations or '/' in problem or '÷' in problem:
                if len(numbers) >= 2 and numbers[1] != 0:
                    result = numbers[0] / numbers[1]
                    calculation_steps.append(f"{numbers[0]} ÷ {numbers[1]} = {result}")
                elif numbers[1] == 0:
                    result = "undefined (division by zero)"
                    calculation_steps.append("Error: Cannot divide by zero")
            
            else:
                result = "Please rephrase your problem"
                calculation_steps.append("Try using words like 'percent of', 'average of', 'sum of', etc.")
        
        except Exception as e:
            result = f"Error: {str(e)}"
            calculation_steps.append(f"Calculation error: {str(e)}")
        
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 2)
        
        return {
            'value': result if result is not None else "No result",
            'steps': calculation_steps
        }

# Streamlit UI
st.set_page_config(
    page_title="Chain-of-Thought Math Solver",
    page_icon="🧮",
    layout="wide"
)

st.title("🧮 Chain-of-Thought Math Problem Solver")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📚 About")
    st.markdown("""
    This AI-powered math solver uses **Chain-of-Thought reasoning** to break down problems step by step.
    
    ### Capabilities:
    - ✅ Percentages
    - ✅ Averages
    - ✅ Addition/Subtraction
    - ✅ Multiplication/Division
    - ✅ Word problems
    
    ### Example Problems:
    - "56 percent of 65"
    - "What is the average of 15, 20, 25, and 30?"
    - "Calculate 25% of 200"
    - "Find the sum of 45, 67, and 89"
    - "What is 15 times 8?"
    """)
    
    st.markdown("---")
    st.caption("Made with ❤️ using Chain-of-Thought AI")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔍 Enter Your Math Problem")
    user_input = st.text_area(
        "Type your math problem here:",
        placeholder="Example: 56 percent of 65",
        height=100
    )
    
    if st.button("🚀 Solve Problem", type="primary"):
        if user_input:
            with st.spinner("Thinking through the problem..."):
                solver = ChainOfThoughtMathSolver()
                solution = solver.solve(user_input)
                
                # Display results
                st.markdown("---")
                st.subheader("💡 Solution")
                
                # Understanding
                with st.expander("📖 Problem Understanding", expanded=True):
                    st.info(solution['understanding'])
                
                # Extracted Information
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Numbers Extracted", len(solution['numbers_extracted']))
                    st.write(f"**Numbers:** {solution['numbers_extracted']}")
                with col_b:
                    st.metric("Operations", len(solution['operations_identified']))
                    st.write(f"**Operations:** {', '.join(solution['operations_identified'])}")
                
                # Chain of Thought
                with st.expander("🧠 Chain of Thought Reasoning", expanded=True):
                    for step in solution['chain_of_thought']:
                        st.write(f"• {step}")
                
                # Calculation Steps
                with st.expander("📊 Calculation Steps", expanded=True):
                    for step in solution['calculation_steps']:
                        st.write(f"• {step}")
                
                # Final Answer
                st.markdown("---")
                st.markdown("### ✅ Final Answer")
                st.success(f"**{solution['result']}**", icon="🎯")
        else:
            st.warning("Please enter a math problem!")

with col2:
    st.subheader("🎯 Quick Examples")
    examples = [
        "56 percent of 65",
        "Average of 15, 20, 25, 30",
        "25% of 200",
        "Sum of 45, 67, 89",
        "15 times 8",
        "100 minus 35"
    ]
    
    for example in examples:
        if st.button(f"📝 {example}", key=example):
            user_input = example
            st.rerun()
    
    st.markdown("---")
    st.subheader("📈 Features")
    st.markdown("""
    - **Step-by-step reasoning**
    - **Transparent calculations**
    - **Natural language processing**
    - **Real-time responses**
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Built with Chain-of-Thought prompting | Solves math problems by breaking them down into logical steps</p>
</div>
""", unsafe_allow_html=True)