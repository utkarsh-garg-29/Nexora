import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

with open("companies.json", "r") as f:
    COMPANIES = json.load(f)


def calculate_score(cgpa, skills, projects, internships, backlogs):
    score = 0

    # CGPA — max 30 points
    if cgpa >= 9.0:
        score += 30
    elif cgpa >= 8.0:
        score += 25
    elif cgpa >= 7.0:
        score += 20
    elif cgpa >= 6.0:
        score += 13
    else:
        score += 5

    # Skills — max 25 points
    skill_count = len(skills)
    if skill_count >= 7:
        score += 25
    elif skill_count >= 5:
        score += 20
    elif skill_count >= 3:
        score += 13
    elif skill_count >= 1:
        score += 6

    # Projects — max 20 points
    if projects >= 4:
        score += 20
    elif projects == 3:
        score += 15
    elif projects == 2:
        score += 10
    elif projects == 1:
        score += 5

    # Internships — max 15 points
    if internships >= 2:
        score += 15
    elif internships == 1:
        score += 10

    # Backlogs — penalty up to -15 points
    if backlogs == 1:
        score -= 5
    elif backlogs == 2:
        score -= 10
    elif backlogs >= 3:
        score -= 15

    return max(0, min(score, 100))

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
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
Format each point as a single clear sentence starting with a verb.
"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
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