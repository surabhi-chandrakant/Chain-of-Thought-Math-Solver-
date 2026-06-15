# 🧮 Chain-of-Thought Math Problem Solver

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://cot-math-solver.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

An intelligent math problem solver that uses **Chain-of-Thought reasoning** to break down and solve mathematical problems step by step. Unlike traditional calculators, this solver shows you exactly how it arrives at each answer through transparent, logical reasoning.

## ✨ Live Demo

Try it live: [https://your-app-name.streamlit.app](https://cot-math-solver.streamlit.app/)

## 📋 Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## 🚀 Features

- **🧠 Chain-of-Thought Reasoning**: Shows every logical step in solving problems
- **📝 Natural Language Processing**: Understands math problems written in plain English
- **🎯 Multiple Problem Types**:
  - Percentages (e.g., "56 percent of 65")
  - Averages and Means
  - Addition, Subtraction, Multiplication, Division
  - Powers and Exponents
  - Word Problems
- **💡 Transparent Calculations**: Displays all intermediate calculations
- **🌐 Web Interface**: User-friendly Streamlit web application
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **⚡ Real-time Processing**: Instant solutions with detailed reasoning

## 🎯 How It Works

The solver uses a 5-step Chain-of-Thought process:

1. **Problem Understanding**: Identifies what type of math problem it is
2. **Number Extraction**: Extracts all numerical values from the text
3. **Operation Identification**: Recognizes mathematical operations (words and symbols)
4. **Reasoning Chain**: Builds a logical step-by-step solution path
5. **Calculation**: Performs the actual computation with detailed steps

Input: "56 percent of 65"
↓
Understanding: Percentage calculation
↓
Numbers: [56, 65]
↓
Operation: percentage
↓
Reasoning: 56% → decimal (0.56) → multiply by 65
↓
Result: 36.4


## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Local Installation

1. **Clone the repository**
```bash
git clone https://github.com/surabhi-chandrakant/Chain-of-Thought-Math-Solver-.git
cd math-solver

pip install -r requirements.txt

streamlit run app.py



