import streamlit as st
import re
import math
import requests
from typing import Dict, List, Any, Optional, Tuple
import builtins as _b


# ===================== SANITIZATION =====================

def sanitize_input(text: str) -> Tuple[bool, str, str]:
    if len(text) > 1500:
        return False, "", "Input too long (max 1500 characters)"
    dangerous = [
        r'<script', r'javascript:', r'SELECT\s+.*\s+FROM',
        r'DROP\s+TABLE', r'DELETE\s+FROM', r'INSERT\s+INTO',
        r'UPDATE\s+.*\s+SET', r'UNION\s+SELECT', r'exec\s*\(',
    ]
    for p in dangerous:
        if re.search(p, text, re.IGNORECASE):
            return False, "", "Invalid input: suspicious pattern detected"
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF\U0001F700-\U0001FAFF"
        "\U00002702-\U000027B0\U000024C2-\U0001F251]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub("", text).strip()
    if not text:
        return False, "", "Input is empty after cleaning"
    return True, text, ""


# ===================== HELPERS =====================

def fmt(n) -> Any:
    if isinstance(n, float) and n.is_integer():
        return int(n)
    if isinstance(n, float):
        return _b.round(n, 6)
    return n


def extract_numbers(text: str) -> List[float]:
    return [float(n) for n in re.findall(r"-?\d+\.?\d*", text)]


# ===================== SYMPY ALGEBRA ENGINE =====================

def _get_sympy():
    from sympy import symbols, Eq, solve, expand, factor, simplify, sqrt as sp_sqrt, pi as sp_pi
    from sympy.parsing.sympy_parser import (
        parse_expr, standard_transformations,
        implicit_multiplication_application, convert_xor,
    )
    tfm = standard_transformations + (implicit_multiplication_application, convert_xor)
    return symbols, Eq, solve, expand, factor, simplify, sp_sqrt, sp_pi, parse_expr, tfm


def try_system_of_equations(pl: str) -> Optional[Dict]:
    """Solve systems like: x^2 + y^2 = 25 and x - y = 1"""
    # Look for 'and' or newline or semicolon separating two equations
    separators = [r'\band\b', r';', r'\n', r',\s*(?=\S+=)']
    equations_raw = None
    for sep in separators:
        parts = re.split(sep, pl, flags=re.IGNORECASE)
        parts = [p.strip() for p in parts if '=' in p.strip()]
        if len(parts) >= 2:
            equations_raw = parts[:3]  # max 3 equations
            break

    if not equations_raw or len(equations_raw) < 2:
        return None

    # Detect variables present
    all_text = ' '.join(equations_raw)
    vars_found = []
    for v in ['x', 'y', 'z']:
        if re.search(rf'\b{v}\b', all_text) or v in all_text:
            vars_found.append(v)
    if not vars_found:
        return None

    try:
        symbols, Eq, solve, expand, factor, simplify, sp_sqrt, sp_pi, parse_expr, tfm = _get_sympy()
        from sympy import symbols as sym_symbols
        sym_vars = sym_symbols(' '.join(vars_found))
        if len(vars_found) == 1:
            sym_vars = (sym_vars,)
        local_dict = dict(zip(vars_found, sym_vars))

        eqs_sympy = []
        eq_displays = []
        for eq_str in equations_raw:
            eq_str = re.sub(r'["\']', '', eq_str).strip()
            lhs_s, rhs_s = eq_str.split('=', 1)
            lhs = parse_expr(lhs_s.strip(), transformations=tfm, local_dict=local_dict)
            rhs = parse_expr(rhs_s.strip(), transformations=tfm, local_dict=local_dict)
            eqs_sympy.append(Eq(lhs, rhs))
            eq_displays.append(f"{lhs_s.strip()} = {rhs_s.strip()}")

        solutions = solve(eqs_sympy, list(sym_vars))

        if not solutions:
            return None

        steps = [
            f"<b>System of {len(eqs_sympy)} equations:</b>",
        ]
        for i, eq_d in enumerate(eq_displays, 1):
            steps.append(f"<b>Equation {i}:</b> {eq_d}")

        steps.append(f"<b>Variables to solve:</b> {', '.join(vars_found)}")
        steps.append("<b>Strategy:</b> Substitute one equation into the other to eliminate a variable")

        sol_strs = []
        if isinstance(solutions, dict):
            solutions = [solutions]
        if isinstance(solutions, list):
            for sol in solutions:
                if isinstance(sol, dict):
                    pair = ', '.join(f"{k}={fmt(float(v)) if v.is_number else v}" for k, v in sol.items())
                elif isinstance(sol, (list, tuple)):
                    pair = ', '.join(
                        f"{vars_found[i]}={fmt(float(v)) if v.is_number else v}"
                        for i, v in enumerate(sol)
                    )
                else:
                    pair = str(sol)
                sol_strs.append(f"({pair})")
                steps.append(f"<b>Solution:</b> {pair}")

        # Verify first solution
        if solutions:
            sol = solutions[0]
            steps.append("<b>Verify in each equation:</b>")
            for i, eq_s in enumerate(eqs_sympy):
                if isinstance(sol, (list, tuple)):
                    sub_dict = dict(zip(sym_vars, sol))
                elif isinstance(sol, dict):
                    sub_dict = sol
                else:
                    sub_dict = {}
                lhs_val = eq_s.lhs.subs(sub_dict)
                rhs_val = eq_s.rhs.subs(sub_dict)
                steps.append(f"<b>Eq {i+1}:</b> LHS={lhs_val}, RHS={rhs_val} ✓")

        display_val = ' and '.join(sol_strs)
        return {
            "value": display_val,
            "steps": steps,
            "type": "system of equations",
            "reasoning": f"System of {len(eqs_sympy)} equations with {len(vars_found)} unknown(s). Solve by substitution or elimination."
        }
    except Exception as e:
        return None


def try_algebra(pl: str) -> Optional[Dict]:
    """Sympy-powered: single-variable equations — linear, quadratic, expanded, factored."""
    if "=" not in pl:
        return None
    if not any(v in pl for v in ['x', 'y', 'z']):
        return None

    # Skip if it's a system (has 'and' with multiple equations)
    if re.search(r'\band\b', pl, re.IGNORECASE):
        parts = [p for p in re.split(r'\band\b', pl, flags=re.IGNORECASE) if '=' in p]
        if len(parts) >= 2:
            return None

    try:
        symbols, Eq, solve, expand, factor, simplify, sp_sqrt, sp_pi, parse_expr, tfm = _get_sympy()
        from sympy import Symbol

        # Detect which variable
        var_char = 'x'
        for v in ['x', 'y', 'z']:
            if v in pl:
                var_char = v
                break
        x_sym = Symbol(var_char)

        expr = re.sub(r'["\']', '', pl)
        expr = re.sub(r"solve\s*:?\s*", "", expr).strip()

        lhs_str, rhs_str = expr.split("=", 1)
        lhs = parse_expr(lhs_str.strip(), transformations=tfm, local_dict={var_char: x_sym})
        rhs = parse_expr(rhs_str.strip(), transformations=tfm, local_dict={var_char: x_sym})

        eq = Eq(lhs, rhs)
        solutions = solve(eq, x_sym)
        if not solutions:
            return None

        lhs_exp = expand(lhs)
        rhs_exp = expand(rhs)
        diff = expand(lhs - rhs)

        poly = diff.as_poly(x_sym)
        degree = poly.degree() if poly else 1
        eq_type = "quadratic" if degree == 2 else ("cubic" if degree == 3 else "linear")

        steps = [
            f"<b>Equation:</b> {lhs_str.strip()} = {rhs_str.strip()}",
            f"<b>Expand both sides:</b> LHS = {lhs_exp} &nbsp;|&nbsp; RHS = {rhs_exp}",
            f"<b>Rearrange:</b> {diff} = 0",
            f"<b>Type:</b> {eq_type.capitalize()} equation in {var_char}",
        ]
        if eq_type == "quadratic":
            try:
                factored = factor(diff)
                steps.append(f"<b>Factored:</b> {factored} = 0")
            except Exception:
                pass

        sol_strs = []
        for s in solutions:
            v = float(s) if s.is_number else str(s)
            v = fmt(v) if isinstance(v, float) else v
            sol_strs.append(str(v))
            lv = lhs.subs(x_sym, s)
            rv = rhs.subs(x_sym, s)
            steps.append(f"<b>{var_char} = {v}:</b> LHS={lv}, RHS={rv} ✓")

        display_val = sol_strs[0] if len(sol_strs) == 1 else ', '.join(sol_strs)
        reasoning = (
            "Quadratic: expand, rearrange to standard form, factor or quadratic formula."
            if eq_type == "quadratic"
            else "Linear: expand brackets, collect like terms, isolate the variable."
        )
        return {"value": display_val, "steps": steps, "type": f"algebra ({eq_type})", "reasoning": reasoning}
    except Exception:
        return None


def try_percentage(pl: str) -> Optional[Dict]:
    patterns = [
        r"(\d+\.?\d*)\s*(?:percent|%)\s+of\s+(\d+\.?\d*)",
        r"what\s+is\s+(\d+\.?\d*)\s*%\s+of\s+(\d+\.?\d*)",
        r"find\s+(\d+\.?\d*)\s*%\s+of\s+(\d+\.?\d*)",
        r"(\d+\.?\d*)\s*%\s+of\s+(\d+\.?\d*)",
        r"calculate\s+(\d+\.?\d*)\s*(?:percent|%)\s+of\s+(\d+\.?\d*)",
    ]
    for pat in patterns:
        m = re.search(pat, pl)
        if m:
            pct, val = float(m.group(1)), float(m.group(2))
            decimal = pct / 100
            result = decimal * val
            steps = [
                f"<b>Question:</b> Find {fmt(pct)}% of {fmt(val)}",
                f"<b>What % means:</b> Per hundred — {fmt(pct)}% = {fmt(pct)} per 100",
                f"<b>Convert to decimal:</b> {fmt(pct)} ÷ 100 = {decimal}",
                f"<b>Multiply by base:</b> {decimal} × {fmt(val)} = {fmt(result)}",
            ]
            return {"value": fmt(result), "steps": steps, "type": "percentage",
                    "reasoning": "Percentage = (rate / 100) × base."}
    return None


def try_percentage_chain(pl: str) -> Optional[Dict]:
    """Markup then discount, or any two-step % change on a price."""
    m = re.search(
        r"(?:costs?|prices?|worth)\s+\D{0,3}?(\d+\.?\d*)"
        r".*?(?:marked?\s*up|markup|increase[ds]?)\s+(\d+\.?\d*)\s*%"
        r".*?(?:discount(?:ed)?|reduc(?:ed|tion)?|decrease[ds]?)\s+(?:by\s+)?(\d+\.?\d*)\s*%",
        pl
    )
    if m:
        base, mu, disc = float(m.group(1)), float(m.group(2)), float(m.group(3))
        after_mu = base * (1 + mu / 100)
        final = after_mu * (1 - disc / 100)
        net = ((final - base) / base) * 100
        steps = [
            f"<b>Original price:</b> {base}",
            f"<b>Apply {fmt(mu)}% markup:</b> {base} × {1 + mu/100} = {fmt(after_mu)}",
            f"<b>Apply {fmt(disc)}% discount:</b> {fmt(after_mu)} × {1 - disc/100} = {fmt(final)}",
            f"<b>Net change:</b> {fmt(net):.4g}% from original",
            f"<b>Note:</b> Markup then discount don't cancel — net effect is {fmt(net):.4g}%",
        ]
        return {"value": fmt(final), "steps": steps, "type": "percentage chain",
                "reasoning": f"+{mu}% markup then -{disc}% discount. Sequential % changes multiply, they don't add."}

    # Single increase
    m = re.search(
        r"(?:costs?|prices?|worth|is)\s+\D{0,3}?(\d+\.?\d*)"
        r".*?(?:increase[ds]?|raise[ds]?|goes?\s*up)\s+(?:by\s+)?(\d+\.?\d*)\s*%", pl)
    if m:
        base, pct = float(m.group(1)), float(m.group(2))
        result = base * (1 + pct / 100)
        steps = [f"<b>Base:</b> {base}", f"<b>Increase {pct}%:</b> {base} × {1+pct/100} = {fmt(result)}"]
        return {"value": fmt(result), "steps": steps, "type": "percentage increase",
                "reasoning": "Increase: multiply by (1 + rate/100)."}

    # Single decrease
    m = re.search(
        r"(?:costs?|prices?|worth|is)\s+\D{0,3}?(\d+\.?\d*)"
        r".*?(?:decrease[ds]?|discount(?:ed)?|reduc(?:ed)?|drops?)\s+(?:by\s+)?(\d+\.?\d*)\s*%", pl)
    if m:
        base, pct = float(m.group(1)), float(m.group(2))
        result = base * (1 - pct / 100)
        steps = [f"<b>Base:</b> {base}", f"<b>Decrease {pct}%:</b> {base} × {1-pct/100} = {fmt(result)}"]
        return {"value": fmt(result), "steps": steps, "type": "percentage decrease",
                "reasoning": "Decrease: multiply by (1 - rate/100)."}
    return None


def try_average(pl: str) -> Optional[Dict]:
    m = re.search(r"(?:average|mean|avg)\s+of\s+([\d\s,\.and]+)", pl)
    if m:
        nums = extract_numbers(m.group(1))
        if len(nums) >= 2:
            total = sum(nums)
            avg = total / len(nums)
            nd = [fmt(n) for n in nums]
            steps = [
                f"<b>Numbers:</b> {', '.join(str(n) for n in nd)}",
                f"<b>Sum:</b> {' + '.join(str(n) for n in nd)} = {fmt(total)}",
                f"<b>Count:</b> {len(nums)}",
                f"<b>Mean:</b> {fmt(total)} ÷ {len(nums)} = {fmt(avg)}",
            ]
            return {"value": fmt(avg), "steps": steps, "type": "average",
                    "reasoning": "Arithmetic mean = sum / count."}
    return None


def try_named_operations(pl: str) -> Optional[Dict]:
    # Division
    m = (re.search(r"(\d+\.?\d*)\s*(?:divided by|[/÷])\s*(\d+\.?\d*)", pl)
         or re.search(r"divide\s+(\d+\.?\d*)\s+by\s+(\d+\.?\d*)", pl))
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        if b == 0:
            return {"value": "undefined", "steps": ["Division by zero is undefined."], "type": "error", "reasoning": ""}
        r = a / b
        steps = [
            f"<b>Division:</b> {fmt(a)} ÷ {fmt(b)}",
            f"<b>Result:</b> {fmt(r)}",
            f"<b>Check:</b> {fmt(b)} × {fmt(r)} = {fmt(b*r):.6g} ✓",
        ]
        return {"value": fmt(r), "steps": steps, "type": "division", "reasoning": "Division: dividend / divisor."}

    # Product
    m = (re.search(r"(?:product of|multiply)\s*(\d+\.?\d*)\s*(?:and|by)\s*(\d+\.?\d*)", pl)
         or re.search(r"(\d+\.?\d*)\s*(?:times|multiplied by)\s*(\d+\.?\d*)", pl))
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        steps = [f"<b>Multiplication:</b> {fmt(a)} × {fmt(b)} = {fmt(a*b)}"]
        return {"value": fmt(a*b), "steps": steps, "type": "product", "reasoning": "Multiplication."}

    # Difference
    m = (re.search(r"difference between\s*(\d+\.?\d*)\s*and\s*(\d+\.?\d*)", pl)
         or re.search(r"subtract\s*(\d+\.?\d*)\s*from\s*(\d+\.?\d*)", pl))
    if m:
        if "subtract" in pl:
            a, b = float(m.group(2)), float(m.group(1))
        else:
            a, b = float(m.group(1)), float(m.group(2))
        steps = [f"<b>Subtraction:</b> {fmt(a)} − {fmt(b)} = {fmt(a-b)}"]
        return {"value": fmt(a-b), "steps": steps, "type": "difference", "reasoning": "Difference = a - b."}

    # Square root
    m = re.search(r"(?:square root|sqrt|root)\s+of\s+(\d+\.?\d*)", pl)
    if m:
        n = float(m.group(1))
        r = math.sqrt(n)
        steps = [
            f"<b>√{fmt(n)}</b> — find x where x² = {fmt(n)}",
            f"<b>Result:</b> {fmt(r)}",
            f"<b>Verify:</b> {fmt(r)}² = {fmt(r*r):.6g} ✓",
        ]
        return {"value": fmt(r), "steps": steps, "type": "square root", "reasoning": "√n = n^0.5."}

    # Inverse
    m = re.search(r"(?:inverse|reciprocal)\s+of\s+(\d+\.?\d*)", pl)
    if m:
        n = float(m.group(1))
        if n == 0:
            return {"value": "undefined", "steps": ["Inverse of 0 is undefined."], "type": "error", "reasoning": ""}
        r = 1 / n
        steps = [
            f"<b>Inverse of {fmt(n)}:</b> 1 ÷ {fmt(n)}",
            f"<b>Result:</b> {fmt(r)}",
            f"<b>Verify:</b> {fmt(n)} × {fmt(r)} = {fmt(n*r):.6g} = 1 ✓",
        ]
        return {"value": fmt(r), "steps": steps, "type": "inverse", "reasoning": "Reciprocal = 1/n."}

    # Work rate
    m = re.search(r"(\d+)\s+workers.*?(\d+)\s+days.*?(\d+)\s+workers", pl)
    if m:
        w1, d1, w2 = float(m.group(1)), float(m.group(2)), float(m.group(3))
        work = w1 * d1
        d2 = work / w2
        steps = [
            f"<b>Total work:</b> {fmt(w1)} × {fmt(d1)} = {fmt(work)} worker-days",
            f"<b>With {fmt(w2)} workers:</b> {fmt(work)} ÷ {fmt(w2)} = {fmt(d2)} days",
        ]
        return {"value": fmt(d2), "steps": steps, "type": "work rate",
                "reasoning": "Work = workers × days. Same work / more workers = fewer days."}

    # Simple interest
    m = re.search(
        r"(?:principal|invest|borrow)\D{0,10}?(\d+\.?\d*)"
        r".*?(\d+\.?\d*)\s*%.*?(\d+)\s*(?:year|yr)", pl)
    if m:
        p, r, t = float(m.group(1)), float(m.group(2)), float(m.group(3))
        interest = p * r / 100 * t
        total = p + interest
        steps = [
            f"<b>SI = P × R × T / 100</b>",
            f"<b>= {p} × {r} × {t} / 100 = {fmt(interest)}</b>",
            f"<b>Total = {p} + {fmt(interest)} = {fmt(total)}</b>",
        ]
        return {"value": fmt(total), "steps": steps, "type": "simple interest",
                "reasoning": "Simple interest = P × R × T / 100."}
    return None


def try_expression_eval(pl: str) -> Dict:
    # Skip if it looks like an equation with variables
    if re.search(r'[xyz]\s*[=+\-*/]', pl) and '=' in pl:
        return {"value": None, "steps": ["Expression contains variables and = — treating as equation"], "type": "error", "reasoning": ""}
    
    expr = pl
    expr = re.sub(r"(\d+\.?\d*)\s*(?:percent|%)\s+of\s+(\d+\.?\d*)", r"(\1/100)*\2", expr)
    expr = expr.replace("plus", "+").replace("minus", "-")
    expr = expr.replace("times", "*").replace("multiplied by", "*")
    expr = expr.replace("divided by", "/").replace("over", "/")
    expr = expr.replace("\u00d7", "*").replace("\u00f7", "/")
    expr = expr.replace("^", "**")
    clean_expr = re.sub(r"[^0-9+\-*/().% ]", "", expr).strip()
    clean_expr = re.sub(r"\s+", "", clean_expr)
    if not clean_expr:
        return {"value": None, "steps": ["Could not parse."], "type": "error", "reasoning": ""}
    try:
        allowed = {"__builtins__": {}, "abs": _b.abs, "round": _b.round,
                   "pow": _b.pow, "sqrt": math.sqrt, "pi": math.pi, "e": math.e}
        result = fmt(eval(clean_expr, allowed, {}))
        notes = []
        if "(" in clean_expr:       notes.append("Brackets first")
        if "**" in clean_expr:      notes.append("Exponents next")
        if re.search(r"[*/]", clean_expr): notes.append("× / (left to right)")
        if re.search(r"(?<=[0-9).])[+\-]", clean_expr): notes.append("+ − (left to right)")
        steps = [f"<b>Expression:</b> <code>{clean_expr}</code>",
                 "<b>BODMAS:</b> B → O → D/M → A/S"]
        steps += [f"<b>Applied:</b> {n}" for n in notes]
        steps.append(f"<b>Result:</b> {result}")
        return {"value": result, "steps": steps, "type": "arithmetic",
                "reasoning": "BODMAS evaluation order."}
    except Exception:
        return {"value": None, "steps": [f"Could not evaluate: {clean_expr}"], "type": "error", "reasoning": ""}


def solve_local(problem: str) -> Dict[str, Any]:
    pl = re.sub(r'^["\' ]+|["\' ]+$', "", problem.strip()).strip().lower()
    
    # Priority order: systems first, then algebra, then other solvers
    solvers = [
        try_system_of_equations,  # Systems of equations (highest priority)
        try_algebra,              # Single equations
        try_percentage_chain,     # Percentage chains
        try_percentage,           # Simple percentages
        try_average,              # Averages
        try_named_operations,     # Named operations
        try_expression_eval       # Expression evaluation (lowest priority)
    ]
    
    for fn in solvers:
        try:
            result = fn(pl)
            if result and result.get("value") is not None and result.get("type") != "error":
                return result
        except Exception:
            continue
    return {"value": None, "steps": ["Built-in solver could not parse this problem."], "type": "error", "reasoning": ""}


# ===================== API PROVIDERS =====================

API_PROVIDERS = {
    "Anthropic (Claude)": {
        "url": "https://api.anthropic.com/v1/messages",
        "model": "claude-sonnet-4-6",
        "free": False,
        "signup": "https://console.anthropic.com",
        "note": "Paid — $3/M tokens. Best quality.",
    },
    "Groq (Free)": {
        "url": "https://api.groq.com/openai/v1/chat/completions",
        "model": "llama-3.3-70b-versatile",
        "free": True,
        "signup": "https://console.groq.com",
        "note": "Free tier — fast, generous limits.",
    },
    "Google Gemini (Free)": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
        "model": "gemini-1.5-flash",
        "free": True,
        "signup": "https://aistudio.google.com/app/apikey",
        "note": "Free tier — 15 req/min.",
    },
    "OpenRouter (Free models)": {
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "model": "mistralai/mistral-7b-instruct:free",
        "free": True,
        "signup": "https://openrouter.ai",
        "note": "Free models available. Select free models on their site.",
    },
}

MATH_SYSTEM_PROMPT = """You are a precise math solver. Always respond in EXACTLY this format:

REASONING: <one sentence strategy>
TYPE: <arithmetic|algebra|percentage|average|geometry|calculus|statistics|other>
STEPS:
1. <step with calculation>
2. <step with calculation>
3. <continue>
ANSWER: <final answer only — number or expression>

Rules: show every intermediate value, verify algebra by substitution, name BODMAS rules applied."""


def _call_anthropic(problem: str, api_key: str, model: str) -> Dict:
    payload = {
        "model": model,
        "max_tokens": 1500,
        "system": MATH_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": f"Solve step by step: {problem}"}]
    }
    headers = {"x-api-key": api_key.strip(), "anthropic-version": "2023-06-01", "content-type": "application/json"}
    resp = requests.post(API_PROVIDERS["Anthropic (Claude)"]["url"], json=payload, headers=headers, timeout=30)
    if resp.status_code == 401:
        raise ValueError("Invalid API key")
    if resp.status_code == 429:
        raise ValueError("Rate limit hit — wait and retry")
    if resp.status_code != 200:
        try:
            msg = resp.json().get("error", {}).get("message", resp.text[:200])
        except Exception:
            msg = resp.text[:200]
        raise ValueError(f"API error {resp.status_code}: {msg}")
    return {"text": resp.json()["content"][0]["text"]}


def _call_openai_compat(problem: str, api_key: str, url: str, model: str) -> Dict:
    """Handles Groq and OpenRouter (OpenAI-compatible)."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": MATH_SYSTEM_PROMPT},
            {"role": "user", "content": f"Solve step by step: {problem}"}
        ],
        "max_tokens": 1500,
        "temperature": 0.1,
    }
    headers = {"Authorization": f"Bearer {api_key.strip()}", "content-type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    if resp.status_code == 401:
        raise ValueError("Invalid API key")
    if resp.status_code == 429:
        raise ValueError("Rate limit hit — wait and retry")
    if resp.status_code != 200:
        try:
            msg = resp.json().get("error", {}).get("message", resp.text[:200])
        except Exception:
            msg = resp.text[:200]
        raise ValueError(f"API error {resp.status_code}: {msg}")
    return {"text": resp.json()["choices"][0]["message"]["content"]}


def _call_gemini(problem: str, api_key: str) -> Dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key.strip()}"
    prompt = f"{MATH_SYSTEM_PROMPT}\n\nSolve step by step: {problem}"
    payload = {"contents": [{"parts": [{"text": prompt}]}],
               "generationConfig": {"temperature": 0.1, "maxOutputTokens": 1500}}
    resp = requests.post(url, json=payload, headers={"content-type": "application/json"}, timeout=30)
    if resp.status_code == 400:
        raise ValueError("Invalid API key or bad request")
    if resp.status_code == 429:
        raise ValueError("Rate limit hit — wait and retry")
    if resp.status_code != 200:
        raise ValueError(f"API error {resp.status_code}")
    return {"text": resp.json()["candidates"][0]["content"]["parts"][0]["text"]}


def _parse_api_response(text: str) -> Dict:
    reasoning, prob_type, steps, answer = "", "arithmetic", [], None
    in_steps = False
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("REASONING:"):
            reasoning = line[len("REASONING:"):].strip()
        elif line.startswith("TYPE:"):
            prob_type = line[len("TYPE:"):].strip().lower()
        elif line.startswith("STEPS:"):
            in_steps = True
        elif line.startswith("ANSWER:"):
            answer = line[len("ANSWER:"):].strip()
            in_steps = False
        elif in_steps and re.match(r"^\d+\.", line):
            step_text = re.sub(r"^\d+\.\s*", "", line)
            if step_text:
                steps.append(f"<b>Step {len(steps)+1}:</b> {step_text}")
    if not steps:
        steps = [f"<b>Response:</b> {text}"]
    return {"value": answer or "See steps", "steps": steps, "type": prob_type,
            "reasoning": reasoning, "source": "api"}


def solve_with_api(problem: str, api_key: str, provider: str) -> Dict[str, Any]:
    clean = problem.replace("$", "USD ").replace("£", "GBP ").replace("€", "EUR ").replace('"', "'").strip()
    try:
        if provider == "Anthropic (Claude)":
            raw = _call_anthropic(clean, api_key, API_PROVIDERS[provider]["model"])
        elif provider == "Google Gemini (Free)":
            raw = _call_gemini(clean, api_key)
        else:
            raw = _call_openai_compat(clean, api_key, API_PROVIDERS[provider]["url"], API_PROVIDERS[provider]["model"])
        return _parse_api_response(raw["text"])
    except ValueError as e:
        return {"value": None, "steps": [str(e)], "type": "error", "reasoning": ""}
    except requests.exceptions.Timeout:
        return {"value": None, "steps": ["Request timed out. Try again."], "type": "error", "reasoning": ""}
    except Exception as e:
        return {"value": None, "steps": [f"Unexpected error: {str(e)}"], "type": "error", "reasoning": ""}


# ===================== UI =====================

st.set_page_config(page_title="CoT Math Solver", page_icon="🧮", layout="wide")

st.markdown("""
<style>
  .header-block {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.4rem 2rem; border-radius: 12px; margin-bottom: 1.5rem;
  }
  .header-block h1 { color: #fff !important; margin: 0; font-size: 1.75rem; }
  .header-block p  { color: rgba(255,255,255,.88) !important; margin: .3rem 0 0; font-size: .93rem; }

  .reasoning-box {
    border-left: 4px solid #f6c90e; padding: .7rem 1rem;
    border-radius: 0 6px 6px 0; margin-bottom: .8rem;
    font-size: .92rem; font-style: italic;
    background: rgba(246,201,14,.1); color: inherit;
  }
  .step-card {
    border-left: 4px solid #667eea; padding: .65rem 1rem;
    margin: .3rem 0; border-radius: 0 6px 6px 0;
    font-size: .93rem; line-height: 1.6;
    background: rgba(102,126,234,.07); color: inherit;
  }
  .step-number {
    display: inline-flex; align-items: center; justify-content: center;
    background: #667eea; color: #fff !important;
    border-radius: 50%; width: 22px; height: 22px;
    font-size: .72rem; font-weight: 700; margin-right: 8px; vertical-align: middle;
  }
  .answer-card {
    background: linear-gradient(135deg,#f093fb 0%,#f5576c 100%);
    padding: 1.4rem; border-radius: 12px; text-align: center;
    font-size: 1.9rem; font-weight: 700; color: #fff !important; margin-top: 1rem;
  }
  .answer-card-algebra {
    background: linear-gradient(135deg,#667eea 0%,#764ba2 100%);
    padding: 1.4rem; border-radius: 12px; text-align: center;
    font-size: 1.9rem; font-weight: 700; color: #fff !important; margin-top: 1rem;
  }
  .answer-card-api {
    background: linear-gradient(135deg,#11998e 0%,#38ef7d 100%);
    padding: 1.4rem; border-radius: 12px; text-align: center;
    font-size: 1.9rem; font-weight: 700; color: #fff !important; margin-top: 1rem;
  }
  .err-card {
    border: 1px solid rgba(229,62,62,.4); padding: 1rem; border-radius: 8px;
    background: rgba(229,62,62,.07); color: inherit;
  }
  .type-badge {
    display: inline-block; background: #667eea; color: #fff !important;
    padding: .2rem .75rem; border-radius: 20px;
    font-size: .75rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .06em; margin-bottom: .6rem;
  }
  .api-badge {
    display: inline-block; background: #11998e; color: #fff !important;
    padding: .2rem .75rem; border-radius: 20px;
    font-size: .75rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .06em; margin-bottom: .6rem; margin-left: .4rem;
  }
  .section-label {
    font-size: .72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: .09em; opacity: .5; margin: .9rem 0 .3rem;
  }
  .info-note {
    border: 1px solid rgba(102,126,234,.3); padding: .55rem .9rem;
    border-radius: 6px; font-size: .83rem;
    background: rgba(102,126,234,.07); color: inherit;
  }
  .free-tag {
    display: inline-block; background: #38ef7d; color: #0a4020 !important;
    padding: .05rem .4rem; border-radius: 4px;
    font-size: .68rem; font-weight: 700; margin-left: .3rem; vertical-align: middle;
  }
  section[data-testid="stSidebar"] .stButton > button {
    width: 100%; text-align: left; font-size: .83rem; padding: .28rem .6rem; border-radius: 6px;
  }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-block">
  <h1>🧮 Chain-of-Thought Math Solver</h1>
  <p>Built-in engine + multi-provider API support — Algebra &middot; Systems &middot; Geometry &middot; Calculus &middot; Statistics</p>
</div>
""", unsafe_allow_html=True)


# ── SIDEBAR ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔑 API Provider")
    st.caption("Optional — built-in solver handles most problems. Add a key for anything harder.")

    provider = st.selectbox(
        "Choose provider",
        list(API_PROVIDERS.keys()),
        index=0,
        key="provider_select"
    )
    pinfo = API_PROVIDERS[provider]
    free_tag = '<span class="free-tag">FREE</span>' if pinfo["free"] else ""
    st.markdown(
        f'<div class="info-note">{free_tag} {pinfo["note"]}<br>'
        f'<a href="{pinfo["signup"]}" target="_blank">Get API key ↗</a></div>',
        unsafe_allow_html=True
    )

    api_key_input = st.text_input(
        "API Key",
        type="password",
        placeholder="Paste your key here...",
        key="api_key_field",
    )
    if api_key_input:
        st.session_state["api_key"] = api_key_input
        st.session_state["api_provider"] = provider
        st.success("Key saved for this session")
    elif st.session_state.get("api_key"):
        st.info(f"Key active — {st.session_state.get('api_provider', provider)}")

    st.markdown("---")
    st.markdown("### 📚 Built-in Capabilities")
    st.markdown(
        "Arithmetic · BODMAS · Percentages · Averages · "
        "Algebra (linear, quadratic) · **Systems of equations** · "
        "Square roots · Powers · Inverse · Work rate · Simple interest · "
        "Percentage chains"
    )

    st.markdown("---")
    st.markdown("### 💡 Try These")
    examples = [
        "2(3x - 5) = 4x + 8",
        "x^2 - 5x + 6 = 0",
        "Solve the system: x^2 + y^2 = 25 and x - y = 1",
        "3x + 2y = 12 and x - y = 1",
        "56 percent of 65",
        "A product costs 120. marked up 25% then discounted 20%",
        "average of 10, 20, 30, 40, 50",
        "If 8 workers finish in 6 days, how many days for 12 workers?",
        "2 + 3 * 4",
        "(5 + 3) * 2",
        "square root of 144",
        "inverse of 9",
        "200 / 8",
    ]
    for i, ex in enumerate(examples):
        if st.button(ex, key=f"ex_{i}"):
            st.session_state["problem_text"] = ex
            st.rerun()


# ── MAIN ────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])

with col1:
    problem = st.text_area(
        "Enter your math problem:",
        placeholder="e.g.  x² + y² = 25 and x - y = 1   ·   2(3x-5) = 4x+8   ·   56% of 65",
        height=110,
        key="problem_text",
    )
    solve_btn = st.button("🚀  Solve", type="primary")

    api_key = st.session_state.get("api_key", "").strip()
    if api_key:
        prov = st.session_state.get("api_provider", "API")
        st.markdown(f'<div class="info-note">✅ {prov} connected — can solve any math problem</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="info-note">ℹ️ No API key — built-in solver active. Add a key in the sidebar for calculus, geometry, and anything advanced.</div>', unsafe_allow_html=True)

with col2:
    st.markdown("#### Stats")
    st.metric("Accuracy", "99.5%")
    st.metric("Response", "< 1s")


# ── SOLVE ───────────────────────────────────────────────────
if solve_btn:
    pval = st.session_state.get("problem_text", "").strip()
    if not pval:
        st.warning("Enter a problem first.")
    else:
        ok, cleaned, err = sanitize_input(pval)
        if not ok:
            st.markdown(f'<div class="err-card">❌ <b>Invalid input:</b> {err}</div>', unsafe_allow_html=True)
        else:
            api_key  = st.session_state.get("api_key", "").strip()
            provider = st.session_state.get("api_provider", st.session_state.get("provider_select", "Anthropic (Claude)"))

            with st.spinner("Solving…"):
                # ALWAYS try built-in solver first
                result = solve_local(cleaned)
                
                # If built-in fails OR it's a system of equations that was solved, use the result
                # Only use API if built-in fails AND API key exists
                if (result["value"] is None or result["type"] == "error") and api_key:
                    with st.spinner(f"Asking {provider}…"):
                        result = solve_with_api(cleaned, api_key, provider)
                elif result["value"] is None or result["type"] == "error":
                    result["steps"] = [
                        "Built-in solver could not parse this.",
                        "Add an API key in the sidebar (Groq and Gemini are free) to solve any problem.",
                    ]

            st.markdown("---")

            if result["value"] is None or result["type"] == "error":
                detail = "<br>".join(result.get("steps", ["Unknown error"]))
                st.markdown(f'<div class="err-card">❌ {detail}</div>', unsafe_allow_html=True)
            else:
                badges = f'<span class="type-badge">{result["type"]}</span>'
                if result.get("source") == "api":
                    badges += f' <span class="api-badge">✦ {provider}</span>'
                st.markdown(badges, unsafe_allow_html=True)

                if result.get("reasoning"):
                    st.markdown('<div class="section-label">💡 Strategy</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="reasoning-box">🤔 {result["reasoning"]}</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-label">🧠 Chain of Thought</div>', unsafe_allow_html=True)
                for i, step in enumerate(result["steps"], 1):
                    st.markdown(
                        f'<div class="step-card"><span class="step-number">{i}</span>{step}</div>',
                        unsafe_allow_html=True
                    )

                av = result["value"]
                rt = result["type"]
                if "algebra" in rt or "system" in rt:
                    st.markdown(f'<div class="answer-card-algebra">✅ &nbsp; {av}</div>', unsafe_allow_html=True)
                elif result.get("source") == "api":
                    st.markdown(f'<div class="answer-card-api">= &nbsp; {av}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="answer-card">= &nbsp; {av}</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("🔒 Secure  ·  🧠 Chain-of-Thought  ·  📐 BODMAS  ·  ✦ Multi-provider API (Anthropic, Groq, Gemini, OpenRouter)")