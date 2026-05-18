import json
import os
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

with open("companies.json", "r") as f:
    COMPANIES = json.load(f)


def calculate_score(cgpa, skills, projects, internships, backlogs):
    """
    AI-powered placement readiness scorer using Groq.
    Returns a tuple: (total_score: int, breakdown: dict)
    breakdown = {
        "cgpa":        {"score": int, "max": 30, "reason": str},
        "skills":      {"score": int, "max": 25, "reason": str},
        "projects":    {"score": int, "max": 20, "reason": str},
        "internships": {"score": int, "max": 15, "reason": str},
        "backlogs":    {"score": int, "max": 0,  "reason": str},  # penalty, score is negative or 0
    }
    Falls back to rule-based scoring if Groq is unavailable.
    """
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        prompt = f"""
You are an expert placement readiness evaluator for Indian B.Tech CSE students.

Score this student's placement readiness profile out of 100. 
Evaluate holistically — consider not just quantity but quality and combinations.
For example, 3 relevant skills (DSA + Python + SQL) should score higher than 3 unrelated ones.
A student with internships but no projects should be scored differently than vice versa.

Student Profile:
- CGPA: {cgpa} / 10
- Skills: {', '.join(skills) if skills else 'None'}
- Projects Completed: {projects}
- Internships Done: {internships}
- Active Backlogs: {backlogs}

Scoring weights (use these as MAXIMUMS, not fixed brackets):
- CGPA: max 30 points
- Skills (quality + quantity + relevance): max 25 points
- Projects: max 20 points
- Internships: max 15 points
- Backlogs: penalty up to -15 points (0 backlogs = 0 penalty)

Respond ONLY with valid JSON. No explanation outside the JSON. Format exactly:
{{
  "cgpa":        {{"score": <int>, "reason": "<one short sentence>"}},
  "skills":      {{"score": <int>, "reason": "<one short sentence>"}},
  "projects":    {{"score": <int>, "reason": "<one short sentence>"}},
  "internships": {{"score": <int>, "reason": "<one short sentence>"}},
  "backlogs":    {{"score": <int>, "reason": "<one short sentence>"}}
}}

Rules:
- All scores must be integers
- cgpa score: 0 to 30
- skills score: 0 to 25
- projects score: 0 to 20
- internships score: 0 to 15
- backlogs score: -15 to 0 (negative penalty or zero)
- reason must be one sentence, plain text, no asterisks
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )

        raw = response.choices[0].message.content.strip()

        # strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        data = json.loads(raw)

        breakdown = {
            "cgpa":        {"score": int(data["cgpa"]["score"]),        "max": 30, "reason": data["cgpa"]["reason"]},
            "skills":      {"score": int(data["skills"]["score"]),      "max": 25, "reason": data["skills"]["reason"]},
            "projects":    {"score": int(data["projects"]["score"]),    "max": 20, "reason": data["projects"]["reason"]},
            "internships": {"score": int(data["internships"]["score"]), "max": 15, "reason": data["internships"]["reason"]},
            "backlogs":    {"score": int(data["backlogs"]["score"]),    "max": 0,  "reason": data["backlogs"]["reason"]},
        }

        total = sum(v["score"] for v in breakdown.values())
        total = max(0, min(total, 100))
        return total, breakdown

    except Exception:
        # --- Fallback: rule-based scoring ---
        breakdown = {}

        if cgpa >= 9.0:
            breakdown["cgpa"] = {"score": 30, "max": 30, "reason": "Exceptional CGPA — top tier for all recruiters."}
        elif cgpa >= 8.0:
            breakdown["cgpa"] = {"score": 25, "max": 30, "reason": "Strong CGPA — eligible for most companies."}
        elif cgpa >= 7.0:
            breakdown["cgpa"] = {"score": 20, "max": 30, "reason": "Decent CGPA — meets the 7.0 cutoff for many roles."}
        elif cgpa >= 6.0:
            breakdown["cgpa"] = {"score": 13, "max": 30, "reason": "Borderline CGPA — limits company options significantly."}
        else:
            breakdown["cgpa"] = {"score": 5, "max": 30, "reason": "Low CGPA — most companies will filter you out early."}

        skill_count = len(skills)
        if skill_count >= 7:
            breakdown["skills"] = {"score": 25, "max": 25, "reason": "Strong skill set — well-rounded profile."}
        elif skill_count >= 5:
            breakdown["skills"] = {"score": 20, "max": 25, "reason": "Good variety of skills for most roles."}
        elif skill_count >= 3:
            breakdown["skills"] = {"score": 13, "max": 25, "reason": "Moderate skills — a few more would help."}
        elif skill_count >= 1:
            breakdown["skills"] = {"score": 6, "max": 25, "reason": "Very few skills — focus on building core competencies."}
        else:
            breakdown["skills"] = {"score": 0, "max": 25, "reason": "No skills selected — critical gap."}

        if projects >= 4:
            breakdown["projects"] = {"score": 20, "max": 20, "reason": "Excellent project count — shows strong hands-on experience."}
        elif projects == 3:
            breakdown["projects"] = {"score": 15, "max": 20, "reason": "Good project count — solid practical experience."}
        elif projects == 2:
            breakdown["projects"] = {"score": 10, "max": 20, "reason": "Decent projects — build 1-2 more before placement."}
        elif projects == 1:
            breakdown["projects"] = {"score": 5, "max": 20, "reason": "Only 1 project — needs more to be competitive."}
        else:
            breakdown["projects"] = {"score": 0, "max": 20, "reason": "No projects — this is a major red flag for recruiters."}

        if internships >= 2:
            breakdown["internships"] = {"score": 15, "max": 15, "reason": "Multiple internships — strong industry exposure."}
        elif internships == 1:
            breakdown["internships"] = {"score": 10, "max": 15, "reason": "One internship — good start, real-world experience adds credibility."}
        else:
            breakdown["internships"] = {"score": 0, "max": 15, "reason": "No internships — try to get at least one before placements."}

        if backlogs == 0:
            breakdown["backlogs"] = {"score": 0, "max": 0, "reason": "No backlogs — clean academic record."}
        elif backlogs == 1:
            breakdown["backlogs"] = {"score": -5, "max": 0, "reason": "1 backlog — minor penalty, clear it ASAP."}
        elif backlogs == 2:
            breakdown["backlogs"] = {"score": -10, "max": 0, "reason": "2 backlogs — significant penalty, most companies will reject."}
        else:
            breakdown["backlogs"] = {"score": -15, "max": 0, "reason": f"{backlogs} backlogs — severe penalty, clearing these is the #1 priority."}

        total = sum(v["score"] for v in breakdown.values())
        total = max(0, min(total, 100))
        return total, breakdown

def match_companies(cgpa, skills, backlogs, goal):
    eligible = []
    skills_lower = [s.lower().strip() for s in skills]

    for company in COMPANIES:

        # filter by goal
        if goal == "Any IT job" and company["tier"] != "mass":
            continue
        if goal == "Mid-tier product" and company["tier"] == "top":
            continue

        # check CGPA
        if cgpa < company["min_cgpa"]:
            continue

        # check backlogs
        if backlogs > company["backlogs_allowed"]:
            continue

        # check skills
        required = [s.lower() for s in company["required_skills"]]
        if "any programming language" in required:
            match = True
        else:
            match = any(
                any(req in skill or skill in req for skill in skills_lower)
                for req in required
            )
        if not match:
            continue

        eligible.append({
            "name": company["name"],
            "tier": company["tier"],
            "package_lpa": company["package_lpa"],
            "description": company["description"]
        })

    return eligible

def get_stretch_companies(cgpa, skills, backlogs, goal, eligible_names):
    stretch = []
    skills_lower = [s.lower().strip() for s in skills]

    for company in COMPANIES:

        # skip already eligible companies
        if company["name"] in eligible_names:
            continue

        # filter by goal same as before
        if goal == "Any IT job" and company["tier"] != "mass":
            continue
        if goal == "Mid-tier product" and company["tier"] == "top":
            continue

        missing = []

        # check CGPA gap
        if cgpa < company["min_cgpa"]:
            gap = round(company["min_cgpa"] - cgpa, 1)
            missing.append(f"Need {gap} more CGPA (min: {company['min_cgpa']})")

        # check backlogs
       # check backlogs
        if backlogs > company["backlogs_allowed"]:
            if company["backlogs_allowed"] == 0:
                missing.append("Clear all backlogs — this company has a strict zero backlog policy")
            else:
                missing.append(f"Reduce backlogs to {company['backlogs_allowed']} or fewer")

        # check skills
        required = [s.lower() for s in company["required_skills"]]
        if "any programming language" not in required:
            missing_skills = []
            for req in required:
                req_words = req.replace(" ", "").replace("-", "")
                student_concat = " ".join(skills_lower).replace(" ", "").replace("-", "")
                direct_match = any(req in skill or skill in req for skill in skills_lower)
                abbrev_match = req_words in student_concat
                alias_match = (
                    ("dsa" in skills_lower and req in ["data structures", "algorithms"]) or
                    ("data structures" in skills_lower and req == "algorithms") or
                    ("ml" in skills_lower and req == "machine learning") or
                    ("ai" in skills_lower and req == "machine learning")
                )
                if not direct_match and not abbrev_match and not alias_match:
                    missing_skills.append(req)
            if missing_skills:
                missing.append(f"Learn: {', '.join(missing_skills)}")
        # only show if something small is missing (max 2 things)
        if 0 < len(missing) <= 2:
            stretch.append({
                "name": company["name"],
                "tier": company["tier"],
                "package_lpa": company["package_lpa"],
                "missing": missing
            })

    return stretch

def get_skills_gap(skills, goal):
    skills_lower = [s.lower().strip() for s in skills]

    # skills required for each goal tier
    goal_skills = {
        "Any IT job": [
            "data structures", "algorithms", "sql", "python",
            "communication skills", "aptitude", "problem solving"
        ],
        "Mid-tier product": [
            "data structures", "algorithms", "python", "sql",
            "system design basics", "problem solving", "javascript",
            "machine learning", "cloud basics"
        ],
        "Top product": [
            "data structures", "algorithms", "competitive programming",
            "system design", "problem solving", "python",
            "javascript", "machine learning", "cloud basics", "sql"
        ]
    }

    required = goal_skills.get(goal, [])
    missing = []

    for req in required:
        req_words = req.replace(" ", "").replace("-", "")
        student_concat = " ".join(skills_lower).replace(" ", "").replace("-", "")
        direct_match = any(req in skill or skill in req for skill in skills_lower)
        abbrev_match = req_words in student_concat
        alias_match = (
            ("dsa" in skills_lower and req in ["data structures", "algorithms"]) or
            ("ml" in skills_lower and req == "machine learning") or
            ("ai" in skills_lower and req == "machine learning")
        )
        if not direct_match and not abbrev_match and not alias_match:
            missing.append(req)

    # return top 3 missing skills
    return missing[:3]

def generate_action_plan(cgpa, skills, projects, internships, backlogs, goal, score, eligible_companies, stretch_companies, skills_gap):
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        eligible_names = [c["name"] for c in eligible_companies]
        stretch_names = [c["name"] for c in stretch_companies]

        prompt = f"""
You are a placement advisor for Indian B.Tech CSE students.

Here is a student's profile:
- CGPA: {cgpa}
- Skills: {', '.join(skills)}
- Projects: {projects}
- Internships: {internships}
- Active Backlogs: {backlogs}
- Placement Goal: {goal}
- Placement Readiness Score: {score}/100
- Currently Eligible For: {', '.join(eligible_names) if eligible_names else 'None'}
- Stretch Companies: {', '.join(stretch_names) if stretch_names else 'None'}
- Top Skills to Learn: {', '.join(skills_gap) if skills_gap else 'None'}

Give a personalized action plan with exactly 5 points.
Each point should be specific, actionable, and realistic for an Indian B.Tech student.
Be direct and practical. No generic advice.

Format STRICTLY like this:
1. Main action point starting with a verb
   → specific sub-step or detail
   → another sub-step if needed

2. Main action point starting with a verb
   → specific sub-step or detail

(and so on till 5)

Rules:
- Main points must be numbered 1 to 5
- Sub-points must start with → on a new line
- Each → must be on its own separate line
- No paragraphs, no long sentences, no asterisks, no dashes
- Use only the data provided, do not give generic advice
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Replace: "gpt-4o-mini"
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=400
        )

        return response.choices[0].message.content

    except Exception as e:
        # fallback if OpenAI fails
        plan = []
        if backlogs > 0:
            plan.append(f"Clear your {backlogs} active backlog(s) immediately — most companies have a zero backlog policy.")
        if skills_gap:
            plan.append(f"Start learning {skills_gap[0]} — it is the most critical missing skill for your {goal} goal.")
        if projects < 3:
            plan.append("Build at least 2 more projects and host them on GitHub to strengthen your profile.")
        if internships == 0:
            plan.append("Apply for internships on Internshala or LinkedIn — even a 1-month internship adds 10 points to your score.")
        if cgpa < 7.0:
            plan.append("Focus on improving your CGPA this semester — a 7.0+ CGPA unlocks significantly more companies.")
        plan.append("Practice 2 DSA problems daily on LeetCode to build consistency before placement season.")
        return "\n".join(f"{i+1}. {p}" for i, p in enumerate(plan))

def get_dream_company_gap(cgpa, skills, backlogs, company_name):
    skills_lower = [s.lower().strip() for s in skills]
    company = next((c for c in COMPANIES if c["name"].lower() == company_name.lower()), None)

    if not company:
        return None

    gap = {
        "name": company["name"],
        "package_lpa": company["package_lpa"],
        "tier": company["tier"],
        "missing": [],
        "you_have": []
    }

    # CGPA
    if cgpa >= company["min_cgpa"]:
        gap["you_have"].append(f"CGPA {cgpa} meets the {company['min_cgpa']} minimum")
    else:
        gap["missing"].append(f"Improve CGPA from {cgpa} to {company['min_cgpa']} (need {round(company['min_cgpa'] - cgpa, 1)} more)")

    # Backlogs
    if backlogs <= company["backlogs_allowed"]:
        gap["you_have"].append("Backlog requirement met")
    else:
        gap["missing"].append("Clear all active backlogs — strict zero backlog policy")

    # Skills
    required = [s.lower() for s in company["required_skills"]]
    if "any programming language" in required:
        gap["you_have"].append("Basic programming requirement met")
    else:
        for req in required:
            req_words = req.replace(" ", "").replace("-", "")
            student_concat = " ".join(skills_lower).replace(" ", "").replace("-", "")
            direct_match = any(req in skill or skill in req for skill in skills_lower)
            abbrev_match = req_words in student_concat
            alias_match = (
                ("dsa" in skills_lower and req in ["data structures", "algorithms"]) or
                ("ml" in skills_lower and req == "machine learning") or
                ("cp" in skills_lower and req == "competitive programming")
            )
            if direct_match or abbrev_match or alias_match:
                gap["you_have"].append(f"You know {req}")
            else:
                gap["missing"].append(f"Learn {req}")

    return gap