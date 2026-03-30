from dotenv import load_dotenv
from fastapi.responses import FileResponse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from langchain_groq import ChatGroq
from fastapi import FastAPI
from pydantic import BaseModel, Field, computed_field
from typing import List, Optional,Annotated,Literal
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

router = APIRouter( prefix="/ai", tags=["AI Analysis"], responses={404: {"description": "Not found"}})


class IdeaRequest(BaseModel):
    idea: str = Annotated[str, Field(..., description="The startup idea to analyze")]


load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

agent_1 = ChatGroq(model="groq/compound", temperature=0.2 , groq_api_key=api_key)
agent_2 = ChatGroq(model="openai/gpt-oss-20b", temperature=0.3, groq_api_key=api_key)
judge   = ChatGroq(model="openai/gpt-oss-120b", temperature=0, groq_api_key=api_key)
# agent_1 = ChatGroq(
#     groq_api_key =api_key,
#     model="llama3-70b-8192",
#     temperature=0.3
# )

# agent_2 = ChatOpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key=API_KEY_2,
#     model="openai/gpt-oss-120b:free",
#     temperature=0.8
# )

# judge = ChatOpenAI(
#     base_url="https://openrouter.ai/api/v1",
#     api_key=API_KEY_3,
#     model="liquid/lfm-2.5-1.2b-thinking:free",
#     temperature=0.2
# )


def run_agent(agent, system_role: str, idea: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_role),
        ("human", "{idea}")
    ])

    chain = prompt | agent
    return chain.invoke({"idea": idea}).content
def run_agent_1(idea: str):
    prompt = f"""
You are a Startup Risk Analyst AI.

Analyze the following startup idea deeply:

IDEA:
{idea}

TASKS:

1. Weaknesses & Risks:
- Identify planning gaps
- Feasibility issues
- Lack of uniqueness

2. Failure Prediction Timeline:
- Month 1:
- Month 3:
- Month 6:

3. Success Score (0-100%):
- Give a number
- Justify based on:
  - Market viability
  - Competition
  - Technical feasibility

Be brutally honest and analytical.
"""
    return agent_1.invoke(prompt).content


def run_agent_2(idea: str):
    prompt = f"""
You are a hostile startup critic AI.

Startup Idea:
{idea}

TASKS:

1. Simulate Attacks:
- Competitors
- Investors
- Customers
- Security threats

2. Multi-Perspective Evaluation:
- Investor POV
- Engineer POV
- End-user POV
- Critic POV

3. Improvements:
- Suggest pivots
- Better business models
- Technical improvements
- Recovery strategies

Be aggressive, realistic, and detailed.
"""
    return agent_2.invoke(prompt).content

# def trim_text(text: str, max_chars: int = 1000) -> str:
#     if not text:
#         return ""
#     text = text.strip()
#     return text[:max_chars] + ("..." if len(text) > max_chars else "")

def run_judge(idea: str, out1: str, out2: str):
    prompt = f"""
You are an expert Startup Evaluator AI.

Startup Idea:
{idea}

You are given two analyses:

--- ANALYSIS 1 (Risk Analyst) ---
{out1}

--- ANALYSIS 2 (Attack Simulator) ---
{out2}

TASKS:

1. Combine both analyses intelligently
2. Remove redundancy
3. Resolve contradictions
4. Highlight the MOST critical risks
5. Provide FINAL STRUCTURED OUTPUT:

- Output ONLY valid JSON
- No markdown, no explanation, no extra text
- No tables
- No repetition
- Keep it concise

FORMAT:

{{
  "key_risks": ["point1", "point2", "point3"],
  "failure_timeline": {{
    "0-6 months": "text",
    "6-18 months": "text",
    "18-36 months": "text"
  }},
  "external_threats": ["point1", "point2"],
  "improvements": ["point1", "point2"],
  "success_score": "number with reason",
  "verdict": "Go / Pivot / Drop"
}}
"""
    return judge.invoke(prompt).content

# if __name__ == "__main__":
#     idea = input("Enter your startup idea: ")

#     print("\nRunning AI 1 (Risk Analyst)...")
#     out1 = run_agent_1(idea)

#     print("\nRunning AI 2 (Attack Simulator)...")
#     out2 = run_agent_2(idea)

#     print("\nRunning Judge AI...")
#     final = run_judge(idea, out1, out2)

#     print("\n================ FINAL OUTPUT ================\n")
#     print(final)

@router.post("/analyze")
def analyze_idea(request: IdeaRequest):
    idea = request.idea

    out1 = run_agent_1(idea)
    out2 = run_agent_2(idea)

    # ✅ ADD HERE
    # out1 = trim_text(out1, 1000)
    # out2 = trim_text(out2, 1000)

    final = run_judge(idea, out1, out2)
    return {
        "idea": idea,
        "risk_analysis": out1,
        "attack_analysis": out2,
        "final_result": final
    }

