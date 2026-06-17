# 📚 Chain-of-Thought Math Problem Solver

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**An advanced hybrid math solver that combines a powerful built-in SymPy engine with multiple AI API providers (Anthropic Claude, Groq, Google Gemini, OpenRouter) to solve ANY math problem with chain-of-thought reasoning.**

---

## ✨ Live Demo

Try it live: [https://your-app-name.streamlit.app](https://your-app-name.streamlit.app)

---

## 📋 Table of Contents

- [Features](#-features)
- [How It Works](#-how-it-works)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Examples](#-examples)
- [API Providers](#-api-providers)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Features

### 🧠 **Chain-of-Thought Reasoning**
Shows every logical step in solving problems with transparent, verifiable calculations.

### 📝 **Natural Language Processing**
Understands math problems written in plain English — no need for special syntax.

### 🔢 **Comprehensive Math Capabilities**

#### Built-in Solver (SymPy Engine):
- **Arithmetic:** Addition, Subtraction, Multiplication, Division
- **BODMAS:** Full operator precedence with parentheses
- **Algebra:** Linear equations, Quadratic equations, Cubic equations
- **Systems of Equations:** 2x2 and 3x3 systems (linear and non-linear)
- **Percentages:** Single and chain percentages (markup/discount)
- **Averages:** Arithmetic mean of any number set
- **Square Roots:** Perfect and non-perfect squares
- **Powers & Exponents:** Any base with any exponent
- **Inverse/Reciprocal:** Multiplicative inverses
- **Work Rate Problems:** Worker-day calculations
- **Simple Interest:** Principal × Rate × Time / 100
- **Percentage Chains:** Markup then discount calculations

#### AI API Provider Support (Optional):
- **Calculus:** Derivatives, Integrals, Limits
- **Geometry:** Area, Volume, Trigonometry
- **Statistics:** Mean, Median, Mode, Standard Deviation
- **Linear Algebra:** Matrices, Vectors
- **Complex Word Problems:** Multi-step real-world scenarios
- **Any Math Problem:** If it's math, it can solve it

### 🌐 **Multi-Provider API Support**

| Provider | Free Tier | Best For |
|----------|-----------|----------|
| **Claude (Anthropic)** | ❌ No | Highest quality, complex problems |
| **Groq** | ✅ Yes | Fast, free, generous limits |
| **Google Gemini** | ✅ Yes | Free tier, 15 req/min |
| **OpenRouter** | ✅ Yes | Multiple free models |

### 💡 **Transparent Calculations**
Displays all intermediate calculations with step-by-step verification.

### 🎨 **Beautiful Web Interface**
User-friendly Streamlit web application with dark/light mode support.

### 📱 **Responsive Design**
Works perfectly on desktop, tablet, and mobile devices.

### ⚡ **Real-time Processing**
Instant solutions with detailed chain-of-thought reasoning.

---

## 🎯 How It Works

### The 6-Step Chain-of-Thought Process:

1. **Input Validation**: Sanitizes and validates user input (security first!)
2. **Problem Classification**: Identifies problem type (algebra, percentage, system, etc.)
3. **Built-in Solver**: Attempts to solve using SymPy engine
4. **API Fallback**: If built-in fails, uses selected AI provider
5. **Chain-of-Thought Generation**: Builds logical step-by-step solution path
6. **Result Display**: Shows reasoning, steps, and final answer

### Architecture Flow:

```
User Input → Sanitization → Built-in Solver (SymPy)
                                    ↓
                              Success? → YES → Display Result
                                    ↓ NO
                              AI Provider (Claude/Groq/Gemini/OpenRouter)
                                    ↓
                              Chain-of-Thought Generation
                                    ↓
                              Display Result with Steps
```

### Example Flow:

```
Input: "3x + 2y = 12 and x - y = 1"
    ↓
System Detection: 2 equations with 2 variables (x, y)
    ↓
SymPy Solver: Uses substitution/elimination
    ↓
Solution Found: x = 2.8, y = 1.8
    ↓
Chain-of-Thought:
    1. Equation 1: 3x + 2y = 12
    2. Equation 2: x - y = 1
    3. From (2): x = y + 1
    4. Substitute into (1): 3(y+1) + 2y = 12
    5. 3y + 3 + 2y = 12 → 5y = 9 → y = 1.8
    6. x = 1.8 + 1 = 2.8
    7. Verify: 3(2.8) + 2(1.8) = 8.4 + 3.6 = 12 ✓
    ↓
Final Answer: x = 2.8, y = 1.8
```

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/surabhi-chandrakant/Chain-of-Thought-Math-Solver-.git
cd Chain-of-Thought-Math-Solver-
```

2. **Create a virtual environment** (recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
streamlit run app.py
```

5. **Open your browser** and navigate to `http://localhost:8501`

---

## 🎮 Usage

### Web Interface (Recommended)

1. **Launch the Streamlit app**
2. **Type your math problem** in the text box
3. **Click "Solve"** or press Enter
4. **View the detailed chain-of-thought reasoning**
5. **See the final answer** with all calculation steps

### Python Library Usage

```python
from app import solve_local

# Solve a simple problem
result = solve_local("56 percent of 65")
print(result["value"])  # 36.4

# Solve a system of equations
result = solve_local("3x + 2y = 12 and x - y = 1")
print(result["value"])  # x = 2.8, y = 1.8

# Solve a quadratic
result = solve_local("x^2 - 5x + 6 = 0")
print(result["value"])  # 2, 3
```

### Using with API Provider

1. **Get API key** from your chosen provider
2. **Enter in sidebar** under "API Provider"
3. **Solve any problem** - built-in solver tries first, API is fallback

---

## 📚 Examples

### Example 1: System of Equations

**Input:** `"3x + 2y = 12 and x - y = 1"`

**Output:**
```
💡 Strategy: System of 2 equations with 2 unknowns. Solve by substitution.

🧠 Chain of Thought:
1. Equation 1: 3x + 2y = 12
2. Equation 2: x - y = 1
3. From (2): x = y + 1
4. Substitute into (1): 3(y+1) + 2y = 12
5. 3y + 3 + 2y = 12
6. 5y = 9
7. y = 1.8
8. x = 1.8 + 1 = 2.8
9. Verify: 3(2.8) + 2(1.8) = 8.4 + 3.6 = 12 ✓

✅ Final Answer: x = 2.8, y = 1.8
```

### Example 2: Quadratic Equation

**Input:** `"x^2 - 5x + 6 = 0"`

**Output:**
```
💡 Strategy: Quadratic equation in x. Expand, rearrange to standard form, factor.

🧠 Chain of Thought:
1. Equation: x² - 5x + 6 = 0
2. Factor: (x - 2)(x - 3) = 0
3. x - 2 = 0 → x = 2
4. x - 3 = 0 → x = 3
5. Verify: 2² - 5(2) + 6 = 4 - 10 + 6 = 0 ✓
6. Verify: 3² - 5(3) + 6 = 9 - 15 + 6 = 0 ✓

✅ Final Answer: x = 2, 3
```

### Example 3: Percentage Chain

**Input:** `"A product costs 120. marked up 25% then discounted 20%"`

**Output:**
```
💡 Strategy: Sequential percentage changes multiply, they don't add.

🧠 Chain of Thought:
1. Original price: 120
2. Apply 25% markup: 120 × 1.25 = 150
3. Apply 20% discount: 150 × 0.8 = 120
4. Net change: 0% from original
5. Note: 25% up then 20% down doesn't cancel!

✅ Final Answer: 120
```

### Example 4: Complex Word Problem

**Input:** `"If 8 workers finish in 6 days, how many days for 12 workers?"`

**Output:**
```
💡 Strategy: Work = workers × days. Same work / more workers = fewer days.

🧠 Chain of Thought:
1. Total work: 8 × 6 = 48 worker-days
2. With 12 workers: 48 ÷ 12 = 4 days

✅ Final Answer: 4 days
```

---

## 🔑 API Providers

### Anthropic (Claude)
- **Cost:** Paid ($3 per million tokens)
- **Quality:** Highest quality responses
- **Best for:** Complex math problems, calculus, statistics
- **Sign up:** [console.anthropic.com](https://console.anthropic.com)

### Groq (Free) ⭐ Recommended
- **Cost:** Free tier available
- **Speed:** Very fast (LPU inference)
- **Best for:** General math problems, quick responses
- **Sign up:** [console.groq.com](https://console.groq.com)

### Google Gemini (Free)
- **Cost:** Free tier (15 requests/minute)
- **Quality:** Good for most math problems
- **Best for:** Budget-friendly option
- **Sign up:** [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### OpenRouter (Free models)
- **Cost:** Free models available
- **Flexibility:** Multiple model choices
- **Best for:** Experimentation
- **Sign up:** [openrouter.ai](https://openrouter.ai)

---

## 🚢 Deployment

### Streamlit Cloud (Recommended - Free)

1. **Push code to GitHub**
```bash
git add .
git commit -m "Deploy Math Solver"
git push origin main
```

2. **Deploy on Streamlit Cloud**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Click "New app"
- Select your repository
- Set main file as `app.py`
- Click "Deploy"

Your app will be live at: `https://your-app-name.streamlit.app`

### Hugging Face Spaces

1. Create a Space at [huggingface.co/spaces](https://huggingface.co/spaces)
2. Choose Streamlit SDK
3. Upload `app.py` and `requirements.txt`
4. Your app is automatically deployed

### Docker Deployment

```bash
# Build Docker image
docker build -t math-solver .

# Run container
docker run -p 8080:8080 math-solver
```

---

## 📁 Project Structure

```
Chain-of-Thought-Math-Solver/
│
├── app.py                 # Main Streamlit web application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── LICENSE               # MIT License
└── .gitignore           # Git ignore file
```

---

## 🛡️ Security Features

- **Input Sanitization:** Removes dangerous patterns (SQL, XSS)
- **Emoji Filtering:** Strips emojis to prevent injection
- **Length Limiting:** Max 1500 characters
- **Suspicious Pattern Detection:** Blocks command injection
- **HTML Escaping:** Prevents XSS attacks
- **Safe Evaluation:** Uses restricted `eval()` with limited builtins

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [SymPy](https://www.sympy.org/) for symbolic mathematics
- Chain-of-Thought prompting research
- All contributors and users

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/surabhi-chandrakant/Chain-of-Thought-Math-Solver-/issues)
- **Email:** your.email@example.com

---

## ⭐ Show Your Support

If you found this project helpful, please give it a ⭐ on GitHub!

---

**Built with ❤️ using Chain-of-Thought AI and SymPy**

*Last Updated: June 2026*
