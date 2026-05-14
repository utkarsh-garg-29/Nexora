import streamlit as st
from analyzer import (
    calculate_score,
    match_companies,
    get_stretch_companies,
    get_skills_gap,
    generate_action_plan,
    get_dream_company_gap,
    COMPANIES
)

st.set_page_config(
    
    page_title="Nexora — Placement Intelligence",
    page_icon="⚡",
    layout="centered"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
    }
    .block-container {
        padding-top: 2rem;
        max-width: 800px;
    }
    div[data-testid="stForm"] {
        border: 1px solid #2a2a4a;
        border-radius: 16px;
        padding: 2rem;
        background: rgba(255,255,255,0.03);
    }
    div.stButton > button {
        background: linear-gradient(90deg, #ff4b4b, #ff6b35);
        color: white;
        border-radius: 10px;
        height: 3.2rem;
        font-size: 1.05rem;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(255,75,75,0.3);
    }
    div.stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 25px rgba(255,75,75,0.5);
    }
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        margin-top: 1.2rem;
        margin-bottom: 0.4rem;
        color: #a78bfa;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    .skill-cat {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.8rem;
        margin-bottom: 0.2rem;
    }
    h1 {
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.title("⚡ Nexora")
st.subheader("AI-Powered Placement Intelligence Platform")
st.markdown("Enter your profile and find out **exactly** where you stand before placement season hits.")
st.divider()

# --- INPUT FORM ---
with st.form("profile_form"):

    st.markdown('<p class="section-title">Academic Profile</p>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, step=0.1, value=7.0)
        projects = st.number_input("Projects Completed", min_value=0, max_value=20, step=1, value=0)
    with col2:
        backlogs = st.number_input("Active Backlogs", min_value=0, max_value=20, step=1, value=0)
        internships = st.number_input("Internships Done", min_value=0, max_value=10, step=1, value=0)

    st.markdown('<p class="section-title">Technical Skills</p>', unsafe_allow_html=True)
    st.caption("Select all that apply")

    skill_categories = {
        "Programming Languages": ["Python", "Java", "C++", "C", "JavaScript"],
        "CS Fundamentals": ["DSA", "Algorithms", "OS", "DBMS", "CN"],
        "Web Development": ["React", "Node.js", "HTML/CSS", "Django", "Flask"],
        "Data & AI": ["ML", "SQL", "Data Analysis", "Deep Learning", "NLP"],
        "Other": ["Cloud", "System Design", "CP", "Git", "Problem Solving"]
    }

    selected_skills = []
    for category, skills_list in skill_categories.items():
        st.markdown(f'<p class="skill-cat">{category}</p>', unsafe_allow_html=True)
        cols = st.columns(len(skills_list))
        for i, skill in enumerate(skills_list):
            with cols[i]:
                if st.checkbox(skill, key=f"skill_{skill}"):
                    selected_skills.append(skill)

    st.markdown('<p class="section-title">Placement Goal</p>', unsafe_allow_html=True)
    goal = st.selectbox(
        "What is your target?",
        options=["Any IT job", "Mid-tier product", "Top product"],
        help="Any IT job = 3–6 LPA  |  Mid-tier = 8–15 LPA  |  Top product = 25+ LPA"
    )

    submitted = st.form_submit_button("Analyze My Profile 🚀", use_container_width=True)

    # --- RESULTS (inside form so data is available) ---
    if submitted:
        if not selected_skills:
            st.warning("Please select at least one skill.")
        else:
            with st.spinner("Analyzing your profile..."):
                score = calculate_score(cgpa, selected_skills, projects, internships, backlogs)
                eligible = match_companies(cgpa, selected_skills, backlogs, goal)
                eligible_names = [c["name"] for c in eligible]
                stretch = get_stretch_companies(cgpa, selected_skills, backlogs, goal, eligible_names)
                gap = get_skills_gap(selected_skills, goal)
                plan = generate_action_plan(cgpa, selected_skills, projects, internships, backlogs, goal, score, eligible, stretch, gap)

            # Save to session state for dream company section outside form
            st.session_state["analyzed"] = True
            st.session_state["eligible_names"] = eligible_names
            st.session_state["cgpa"] = cgpa
            st.session_state["skills"] = selected_skills
            st.session_state["backlogs"] = backlogs

            st.divider()

            # --- SCORE ---
            st.markdown("## Your Placement Readiness Score")
            if score >= 75:
                color, label, msg = "#22c55e", "Strong 💪", "Great profile! You are well placed for your goal."
            elif score >= 50:
                color, label, msg = "#f59e0b", "Decent 📈", "A few improvements can unlock significantly better companies."
            else:
                color, label, msg = "#ef4444", "Needs Work 🔧", "Follow the action plan below to improve fast."

            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color}22, {color}11);
                border: 1.5px solid {color}; border-radius: 16px; padding: 2rem;
                text-align: center; margin-bottom: 1rem;">
                <div style="font-size: 4rem; font-weight: 800; color: {color};">{score}</div>
                <div style="font-size: 1rem; color: #94a3b8; margin-top: -0.5rem;">out of 100</div>
                <div style="font-size: 1.2rem; font-weight: 600; color: {color}; margin-top: 0.5rem;">{label}</div>
                <div style="font-size: 0.9rem; color: #cbd5e1; margin-top: 0.5rem;">{msg}</div>
            </div>
            """, unsafe_allow_html=True)

            st.divider()

            # --- ELIGIBLE COMPANIES ---
            st.markdown("## ✅ Companies You Are Eligible For")
            if eligible:
                tier_colors = {"mass": "#3b82f6", "mid": "#8b5cf6", "top": "#f59e0b"}
                tier_labels = {"mass": "Mass Recruiter", "mid": "Mid-tier", "top": "Top Product"}
                cols = st.columns(2)
                for i, c in enumerate(eligible):
                    tc = tier_colors.get(c["tier"], "#64748b")
                    tl = tier_labels.get(c["tier"], c["tier"])
                    with cols[i % 2]:
                        st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.03); border: 1px solid {tc}55;
                            border-left: 4px solid {tc}; border-radius: 10px;
                            padding: 1rem 1.2rem; margin-bottom: 0.8rem;">
                            <div style="font-weight: 700; font-size: 1rem; color: white;">{c['name']}</div>
                            <div style="font-size: 0.85rem; color: {tc}; margin-top: 2px;">{tl}</div>
                            <div style="font-size: 1.1rem; font-weight: 600; color: #22c55e; margin-top: 6px;">₹{c['package_lpa']} LPA</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error("No companies match your current profile right now.")
                reasons = []
                if backlogs >= 2:
                    reasons.append(f"🚫 You have **{backlogs} active backlogs** — almost all companies require zero backlogs")
                elif backlogs == 1:
                    reasons.append("🚫 You have **1 active backlog** — most companies require zero backlogs")
                if cgpa < 6.0:
                    reasons.append(f"🚫 Your CGPA is **{cgpa}** — minimum required by most companies is 6.0")
                if reasons:
                    st.markdown("**Here's why:**")
                    for r in reasons:
                        st.markdown(r)
                st.markdown("**What to do next:**")
                next_steps = []
                if backlogs > 0:
                    next_steps.append("Clear your backlogs — this is the **#1 priority**")
                if cgpa < 6.0:
                    next_steps.append(f"Improve your CGPA — you need at least 6.0 (you have {cgpa})")
                if not next_steps:
                    next_steps.append("Review your skills and goal — try selecting more skills or lowering your target")
                for step in next_steps:
                    st.markdown(f"- {step}")

            st.divider()

            # --- STRETCH TARGETS ---
            st.markdown("## 🚀 Stretch Targets")
            if stretch:
                for c in stretch:
                    tc = {"mass": "#3b82f6", "mid": "#8b5cf6", "top": "#f59e0b"}.get(c["tier"], "#64748b")
                    missing_html = "".join(f'<div style="font-size:0.82rem; color:#94a3b8; margin-top:4px;">→ {m}</div>' for m in c["missing"])
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.02); border: 1px solid #2a2a4a;
                        border-left: 4px solid {tc}; border-radius: 10px;
                        padding: 1rem 1.2rem; margin-bottom: 0.8rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="font-weight:700; color:white;">{c['name']}</div>
                            <div style="font-weight:600; color:#f59e0b;">₹{c['package_lpa']} LPA</div>
                        </div>
                        {missing_html}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No stretch targets found for your goal.")

            st.divider()

            # --- SKILLS GAP ---
            st.markdown("## 📚 Top 3 Skills to Learn Next")
            if gap:
                skill_cols = st.columns(len(gap))
                for i, skill in enumerate(gap):
                    with skill_cols[i]:
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #a78bfa22, #60a5fa11);
                            border: 1px solid #a78bfa55; border-radius: 12px;
                            padding: 1.2rem; text-align: center;">
                            <div style="font-size: 1.5rem;">{'🥇' if i==0 else '🥈' if i==1 else '🥉'}</div>
                            <div style="font-weight: 600; color: #a78bfa; margin-top: 0.4rem;">{skill.title()}</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("You already have all key skills for your goal!")

            st.divider()

            # --- ACTION PLAN ---
            st.markdown("## 🗺️ Your Personalized Action Plan")
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.02); border: 1px solid #2a2a4a;
                border-radius: 12px; padding: 1.5rem; line-height: 1.9; color: #e2e8f0;">
                {plan.replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)


# --- DREAM COMPANY TRACKER (outside form — interactive dropdown) ---
if st.session_state.get("analyzed"):
    st.divider()
    st.markdown("## 🌟 Dream Company Tracker")

    all_company_names = [c["name"] for c in COMPANIES]
    s_eligible = st.session_state["eligible_names"]
    s_cgpa = st.session_state["cgpa"]
    s_skills = st.session_state["skills"]
    s_backlogs = st.session_state["backlogs"]

    # Auto suggestions
    closest = []
    for cname in all_company_names:
        if cname in s_eligible:
            continue
        g = get_dream_company_gap(s_cgpa, s_skills, s_backlogs, cname)
        if g:
            closest.append((len(g["missing"]), cname, g))
    closest.sort(key=lambda x: x[0])
    top_closest = closest[:3]

    if top_closest:
        st.markdown("#### 📍 Companies You Are Closest To")
        st.caption("Based on your current profile, these are your most reachable targets")
        cols = st.columns(len(top_closest))
        for i, (gap_count, cname, g) in enumerate(top_closest):
            tc = {"mass": "#3b82f6", "mid": "#8b5cf6", "top": "#f59e0b"}.get(g["tier"], "#64748b")
            with cols[i]:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.02); border: 1px solid {tc}55;
                    border-top: 3px solid {tc}; border-radius: 12px;
                    padding: 1rem; text-align: center;">
                    <div style="font-weight: 700; color: white; font-size: 1rem;">{g['name']}</div>
                    <div style="color: #22c55e; font-weight: 600; margin: 4px 0;">₹{g['package_lpa']} LPA</div>
                    <div style="font-size: 0.8rem; color: #ef4444; margin-top: 8px;">{gap_count} thing{'s' if gap_count != 1 else ''} missing</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("#### 🎯 Pick Your Dream Company")
    dream_company = st.selectbox(
        "Which company do you dream of?",
        options=all_company_names,
        key="dream_company_select"
    )

    if dream_company:
        g = get_dream_company_gap(s_cgpa, s_skills, s_backlogs, dream_company)
        if g:
            if dream_company in s_eligible:
                st.success(f"You are already eligible for {dream_company}! Apply now.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**✅ What you already have**")
                    if g["you_have"]:
                        for item in g["you_have"]:
                            st.markdown(f"""
                            <div style="background: #22c55e11; border-left: 3px solid #22c55e;
                            border-radius: 6px; padding: 6px 10px; margin-bottom: 6px;
                            font-size: 0.85rem; color: #86efac;">{item}</div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption("Nothing meets the requirements yet")
                with col2:
                    st.markdown("**❌ What you still need**")
                    if g["missing"]:
                        for item in g["missing"]:
                            st.markdown(f"""
                            <div style="background: #ef444411; border-left: 3px solid #ef4444;
                            border-radius: 6px; padding: 6px 10px; margin-bottom: 6px;
                            font-size: 0.85rem; color: #fca5a5;">{item}</div>
                            """, unsafe_allow_html=True)
                    else:
                        st.caption("Nothing missing!")