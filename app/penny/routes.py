"""
app/penny/routes.py — Penny AI Finance Chatbot

Routes:
  GET  /penny       → Chat UI page
  POST /penny/chat  → Receive JSON {"message":"..."}, return {"reply":"..."}

Penny has access to the user's real financial data via build_financial_context().
Uses Google Gemini API (google-generativeai) for natural language responses.
Falls back gracefully if GEMINI_API_KEY is not set.
"""

import os
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user

from app.penny.context import build_financial_context

penny_bp = Blueprint("penny", __name__)

PENNY_SYSTEM_PROMPT = """You are Penny, a smart, friendly, and empathetic personal finance AI assistant
built into PennyWise — a personal finance app.

You have access to the user's real financial data: their recent transactions, spending by category,
monthly budgets, savings goals, and income.

Your personality:
- Warm, encouraging, and non-judgmental
- Data-driven — always back up insights with numbers from the user's data
- Concise — keep responses short (2-5 sentences) unless the user asks for detail
- Use emojis sparingly but appropriately (💰, 📊, ✅, ⚠️)
- Never fabricate data — only use what's in the context
- If asked something you don't know, say so honestly

Your capabilities:
- Explain spending patterns and trends
- Warn about budget overruns
- Suggest ways to save money
- Celebrate financial wins (savings milestones, low spending months)
- Answer questions about specific transactions or categories
- Give simple financial advice (not professional financial advice)

Always address the user by their first name when you know it.
Never ask for sensitive information like passwords, full card numbers, or bank credentials.

---

USER FINANCIAL DATA:
{context}
"""

def _smart_fallback(user_message: str, context: str, user_name: str) -> str:
    """
    Intelligent rule-based responses derived from the user's real database context
    when no GEMINI_API_KEY is configured. Ensures Penny can answer real data queries!
    """
    msg = user_message.lower().strip()

    # Extract sections from context
    sections = {}
    current_sec = "header"
    sections[current_sec] = []
    for line in context.splitlines():
        if line.startswith("===") and line.endswith("==="):
            current_sec = line.strip("= ").lower()
            sections[current_sec] = []
        else:
            if line.strip():
                sections[current_sec].append(line.strip())

    # 1. Spending queries ("how much did i spend", "expenses", "spent", "spending")
    if any(k in msg for k in ["spend", "spent", "spending", "expense", "cost"]):
        this_month = sections.get("this month", [])
        top_cats = sections.get("top spending categories (last 90 days)", [])
        reply = [f"Hey {user_name}! 💸 Here is what your spending looks like:"]
        for line in this_month:
            reply.append(f"• {line}")
        if top_cats and top_cats[0] != "No expenses recorded in the last 90 days.":
            reply.append(f"\nYour highest spending category recently is {top_cats[0]}.")
        reply.append("\n💡 (Add a GEMINI_API_KEY to ask more complex financial questions!)")
        return "\n".join(reply)

    # 2. Budget queries ("budget", "over budget", "limit", "exceeded")
    if any(k in msg for k in ["budget", "limit", "overspend", "near"]):
        budgets = sections.get("monthly budgets", [])
        if budgets:
            reply = [f"Here is your budget health, {user_name}: 🎯"]
            for b in budgets:
                reply.append(f"• {b}")
            return "\n".join(reply)
        return f"Hey {user_name}, you haven't set any category budgets yet! 🎯 Head to the Budgets tab to set monthly limits and stay in control."

    # 3. Savings queries ("saving", "goal", "vault", "target")
    if any(k in msg for k in ["saving", "savings", "goal", "vault", "target"]):
        savings = sections.get("savings goals", [])
        if savings:
            reply = [f"Here is how your savings vaults are tracking, {user_name}: 🏦"]
            for s in savings:
                reply.append(f"• {s}")
            return "\n".join(reply)
        return f"Hey {user_name}, you haven't created any savings goals yet! 🏦 Start a goal in Savings Goals to track progress toward a big milestone."

    # 4. Summary / Overview queries
    if any(k in msg for k in ["summary", "overview", "report", "insights", "how am i doing", "status"]):
        this_month = sections.get("this month", [])
        top_cats = sections.get("top spending categories (last 90 days)", [])
        budgets = sections.get("monthly budgets", [])
        savings = sections.get("savings goals", [])
        reply = [f"📊 Financial Summary for {user_name}:"]
        if this_month:
            for line in this_month:
                reply.append(f"  {line}")
        if top_cats and top_cats[0] != "No expenses recorded in the last 90 days.":
            reply.append(f"\nTop Category: {top_cats[0]}")
        if budgets:
            reply.append(f"Active Budgets: {len(budgets)} tracked")
        if savings:
            reply.append(f"Savings Goals: {len(savings)} active")
        return "\n".join(reply)

    # 5. Default greeting & fallback
    this_month = sections.get("this month", [])
    spent_str = this_month[0] if this_month else "No spending recorded"
    return (
        f"Hey {user_name}! 👋 I'm Penny, your personal finance assistant.\n\n"
        f"Right now I can see your live financial data ({spent_str}). You can ask me:\n"
        f"• 'How much did I spend this month?'\n"
        f"• 'How are my budgets doing?'\n"
        f"• 'Give me a spending summary'\n"
        f"• 'Show my savings goals'\n\n"
        f"✨ To unlock free-form conversational AI reasoning, set the GEMINI_API_KEY in your environment!"
    )


def _call_gemini_rest(prompt: str, system_instruction: str, api_key: str) -> str:
    """
    Direct HTTPS REST call to Google Generative Language API (Gemini 3.8 Flash).
    Ultra-lightweight, avoids gRPC connection hangs on serverless runtimes.
    """
    import urllib.request
    import json

    # Try contemporary models in preference order
    for model_name in ["gemini-3.8-flash", "gemini-flash-latest"]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            payload = {
                "system_instruction": {"parts": [{"text": system_instruction}]},
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 512},
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                result = json.loads(response.read().decode("utf-8"))
                candidates = result.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and parts[0].get("text"):
                        return parts[0].get("text", "").strip()
        except Exception:
            continue
    return ""


def _get_gemini_response(user_message: str, context: str, user_name: str) -> str:
    """
    Call Google Gemini API and return the assistant's reply.
    Falls back gracefully to smart rule-based DB responses if the API key is not set or times out.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return _smart_fallback(user_message, context, user_name)

    # 1. Try high-speed direct REST call first
    try:
        reply = _call_gemini_rest(
            user_message, PENNY_SYSTEM_PROMPT.format(context=context), api_key
        )
        if reply:
            return reply
    except Exception:
        pass

    # 2. Try google.generativeai SDK as secondary option
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-3.8-flash",
            system_instruction=PENNY_SYSTEM_PROMPT.format(context=context),
        )
        response = model.generate_content(
            user_message,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=512,
            ),
        )
        if response and response.text:
            return response.text.strip()
    except Exception:
        pass

    # 3. Always return real data via smart fallback if AI call fails
    return _smart_fallback(user_message, context, user_name)


@penny_bp.route("/")
@penny_bp.route("")
@login_required
def index():
    """Render the Penny chat UI page."""
    return render_template("penny/chat.html")


@penny_bp.route("/chat", methods=["POST"])
@login_required
def chat():
    """
    Receive a chat message from the user, build financial context,
    call Gemini, and return the AI response as JSON.

    Request JSON: {"message": "How much did I spend this month?"}
    Response JSON: {"reply": "You spent ₹X this month across Y categories..."}
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    if len(user_message) > 1000:
        return jsonify({"error": "Message too long (max 1000 characters)"}), 400

    # Build financial context from DB
    try:
        context = build_financial_context(current_user)
    except Exception:
        context = f"User: {current_user.name}, Currency: {current_user.currency}"

    # Get AI response
    reply = _get_gemini_response(user_message, context, current_user.name.split()[0])

    return jsonify({"reply": reply})
