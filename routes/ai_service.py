from dotenv import load_dotenv
from fastapi.responses import FileResponse
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from fastapi import FastAPI
from pydantic import BaseModel, Field, computed_field
from typing import List, Optional,Annotated,Literal
from fastapi.middleware.cors import CORSMiddleware
from fastapi import APIRouter

router = APIRouter()


class IdeaRequest(BaseModel):
    idea: str = Annotated[str, Field(..., description="The startup idea to analyze")]


load_dotenv()

API_KEY_1 = os.getenv("OPENROUTER_API_KEY_1")
API_KEY_2 = os.getenv("OPENROUTER_API_KEY_2")
API_KEY_3 = os.getenv("OPENROUTER_API_KEY_3")

agent_1 = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY_1,
    model="nvidia/nemotron-3-super-120b-a12b:free",
    temperature=0.3
)

agent_2 = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY_2,
    model="arcee-ai/trinity-mini:free",
    temperature=0.8
)

judge = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY_3,
    model="stepfun/step-3.5-flash:free",
    temperature=0.2
)


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

FORMAT:

🔴 Key Risks
⚠️ Failure Timeline Summary
⚔️ Major External Threats
🧠 Strategic Improvements
📊 Final Success Score (0-100 with justification)
✅ Final Verdict (Go / Pivot / Drop)

Be clear, structured, and decisive.
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
    final = run_judge(idea, out1, out2)

    return {
        "idea": idea,
        "risk_analysis": out1,
        "attack_analysis": out2,
        "final_result": final
    }

