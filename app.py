"""
FutureYou AI – Career Intelligence System
==========================================
Main Streamlit application entry point.
Run with:  streamlit run app.py
"""

import sys
import os
import json

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── Path setup ───────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

# ✅ FIXED IMPORTS (NO utils / database)
from career_predictor import predict_careers, simulate_skill_addition, predict_all_probabilities
from skill_gap import analyse_all_gaps, get_priority_skills
from roadmap_generator import generate_roadmap
from resume_parser import parse_resume, KNOWN_SKILLS
from github_analyzer import analyze_github
from db import save_session, save_prediction, save_simulation

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FutureYou AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Font imports ── */
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root palette ── */
:root {
    --bg:        #0a0e1a;
    --surface:   #111827;
    --surface2:  #1c2537;
    --accent:    #6366f1;
    --accent2:   #06b6d4;
    --green:     #10b981;
    --orange:    #f59e0b;
    --red:       #ef4444;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --border:    rgba(99,102,241,0.25);
}

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1220 0%, #111827 100%);
    border-right: 1px solid var(--border);
}

/* Sidebar text visible fix */
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* Remove dark highlight */
[data-testid="stSidebar"] .stRadio label {
    background: transparent !important;
    color: #e2e8f0 !important;
}

/* Remove hover dark background */
[data-testid="stSidebar"] .stRadio label:hover {
    background: transparent !important;
}

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 16px !important;
}

/* ── Inputs ── */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Space Grotesk', sans-serif !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    transition: opacity 0.2s, transform 0.1s !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    color: white !important;
}

/* ── Progress bars ── */
.stProgress > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent2)) !important;
}

/* ── Custom card styles ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 16px;
    color: #e2e8f0;   /* FIX: make text visible */
}

.card p, 
.card li,
.card span {
    color: #e2e8f0;   /* FIX: ensure text visible */
}

.card strong {
    color: #ffffff;   /* FIX: headings visible */
}

.career-badge {
    display: inline-block;
    background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(6,182,212,0.2));
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 13px;
    font-weight: 600;
    color: var(--accent2);
    margin: 4px 4px 4px 0;
}

.skill-pill-green {
    display: inline-block;
    background: rgba(16,185,129,0.15);
    border: 1px solid rgba(16,185,129,0.4);
    border-radius: 16px;
    padding: 3px 12px;
    font-size: 12px;
    font-weight: 500;
    color: #10b981;
    margin: 3px 3px 3px 0;
}

.skill-pill-red {
    display: inline-block;
    background: rgba(239,68,68,0.15);
    border: 1px solid rgba(239,68,68,0.4);
    border-radius: 16px;
    padding: 3px 12px;
    font-size: 12px;
    font-weight: 500;
    color: #ef4444;
    margin: 3px 3px 3px 0;
}

.skill-pill-yellow {
    display: inline-block;
    background: rgba(245,158,11,0.15);
    border: 1px solid rgba(245,158,11,0.4);
    border-radius: 16px;
    padding: 3px 12px;
    font-size: 12px;
    font-weight: 500;
    color: #f59e0b;
    margin: 3px 3px 3px 0;
}

.roadmap-phase {
    border-left: 3px solid var(--accent);
    padding-left: 16px;
    margin-bottom: 20px;
}

.hero-title {
    font-size: 52px;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #06b6d4, #10b981);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
    margin-bottom: 8px;
}

.hero-sub {
    font-size: 18px;
    color: var(--muted);
    margin-bottom: 32px;
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 24px 0;
}

.stat-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
}

.stat-box .number {
    font-size: 36px;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.stat-box .label {
    font-size: 13px;
    color: var(--muted);
    margin-top: 4px;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE DEFAULTS
# ═══════════════════════════════════════════════════════════════════════════════
def _init_state():
    defaults = {
        "page":           "🏠 Home",
        "user_skills":    [],
        "predictions":    [],
        "skill_gaps":     {},
        "roadmap":        {},
        "github_data":    {},
        "session_id":     None,
        "analysis_done":  False,
        "user_name":      "",
        "user_email":     "",
        "github_username":"",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 10px;'>
        <div style='font-size:40px'>🚀</div>
        <div style='font-size:22px; font-weight:700; background:linear-gradient(135deg,#6366f1,#06b6d4);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
            FutureYou AI
        </div>
        <div style='font-size:12px; color:#64748b; margin-top:4px;'>Career Intelligence System</div>
    </div>
    <hr style='border-color: rgba(99,102,241,0.25); margin: 12px 0;'/>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["🏠 Home", "👤 Profile Input", "📊 Results & Roadmap",
         "🎮 Career Simulator", "📂 GitHub Analysis", "💾 History"],
        key="nav_radio",
        label_visibility="collapsed",
    )
    st.session_state.page = page

    st.markdown("<hr style='border-color: rgba(99,102,241,0.15); margin: 16px 0;'/>",
                unsafe_allow_html=True)

    if st.session_state.analysis_done and st.session_state.predictions:
        top = st.session_state.predictions[0]
        st.markdown(f"""
        <div style='background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.3);
                    border-radius:10px; padding:14px; text-align:center;'>
            <div style='font-size:11px; color:#64748b; margin-bottom:4px;'>TOP MATCH</div>
            <div style='font-size:15px; font-weight:600; color:#e2e8f0;'>{top['career']}</div>
            <div style='font-size:22px; font-weight:700; color:#10b981; margin-top:4px;'>
                {top['probability']*100:.0f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center;
            font-size:11px;
            color:#64748b;
            margin-top:30px;
            padding-top:10px;
            border-top:1px solid rgba(99,102,241,0.15);'>
    Built with ❤️ using Streamlit
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.markdown("""
    <div style='padding: 40px 0 20px;'>
        <div class='hero-title'>Discover Your<br>Future Career Path</div>
        <div class='hero-sub'>
            AI-powered analysis of your skills, resume, and GitHub profile<br>
            to predict the perfect career and build your personalised roadmap.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='stat-box'>
            <div class='number'>10+</div>
            <div class='label'>Career Paths Analysed</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='stat-box'>
            <div class='number'>66</div>
            <div class='label'>Skills Tracked</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='stat-box'>
            <div class='number'>99%</div>
            <div class='label'>Model Accuracy</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🧠 How it works")
        st.markdown("""
        <div class='card'>
            <p>1️⃣ &nbsp;<strong>Upload your resume</strong> or enter your skills manually</p>
            <p>2️⃣ &nbsp;<strong>Connect your GitHub</strong> to analyse your project portfolio</p>
            <p>3️⃣ &nbsp;<strong>Get AI predictions</strong> for your top 3 career matches</p>
            <p>4️⃣ &nbsp;<strong>View skill gaps</strong> and a personalised learning roadmap</p>
            <p>5️⃣ &nbsp;<strong>Simulate growth</strong> by adding new skills to see impact</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("### 🎯 Supported Career Paths")
        careers = [
            "Data Scientist", "Machine Learning Engineer",
            "Full Stack Developer", "DevOps Engineer",
            "Cybersecurity Analyst", "Android Developer",
            "iOS Developer", "Data Engineer",
            "NLP Engineer", "Cloud Architect",
        ]
        badges = " ".join([f"<span class='career-badge'>{c}</span>" for c in careers])
        st.markdown(f"<div class='card'>{badges}</div>", unsafe_allow_html=True)

    st.info("👈 **Get started** – Click **Profile Input** in the sidebar to begin your analysis.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PROFILE INPUT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "👤 Profile Input":
    st.markdown("## 👤 Your Profile")
    st.markdown("Fill in your details below. The more you provide, the better the predictions.")

    # ── Personal info ────────────────────────────────────────────────────────
    with st.expander("🧑 Personal Information", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            name  = st.text_input("Full Name", value=st.session_state.user_name,
                                  placeholder="e.g. Priya Sharma")
        with c2:
            email = st.text_input("Email (optional)", value=st.session_state.user_email,
                                  placeholder="e.g. priya@example.com")
        st.session_state.user_name  = name
        st.session_state.user_email = email

    # ── Resume upload ────────────────────────────────────────────────────────
    with st.expander("📄 Resume Upload (PDF)", expanded=True):
        uploaded = st.file_uploader("Upload your resume", type=["pdf"],
                                    help="Your resume will be scanned for skills automatically.")
        resume_skills: list[str] = []
        if uploaded:
            with st.spinner("Parsing resume …"):
                result = parse_resume(uploaded_file=uploaded)
            resume_skills = result["skills"]
            st.success(f"✅ Extracted **{len(resume_skills)} skills** from your resume "
                       f"({result['word_count']} words)")
            if resume_skills:
                pills = " ".join(f"<span class='skill-pill-green'>{s}</span>"
                                 for s in resume_skills)
                st.markdown(pills, unsafe_allow_html=True)

    # ── Manual skills ────────────────────────────────────────────────────────
    with st.expander("🛠️ Skills (Manual Entry)", expanded=True):
        st.caption("Select your skills from the list below. These will be merged with resume-parsed skills.")
        manual_skills = st.multiselect(
            "Choose your skills",
            options=sorted(KNOWN_SKILLS),
            default=st.session_state.user_skills if st.session_state.user_skills else [],
            help="Type to search for a skill.",
        )

    # ── GitHub ───────────────────────────────────────────────────────────────
    with st.expander("🐙 GitHub Username (optional)", expanded=False):
        gh_user = st.text_input(
            "GitHub Username",
            value=st.session_state.github_username,
            placeholder="e.g. torvalds",
        )
        st.session_state.github_username = gh_user

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Merge skills ─────────────────────────────────────────────────────────
    all_skills = list(set(resume_skills + manual_skills))

    if all_skills:
        st.markdown(f"**Combined skill set ({len(all_skills)} skills):**")
        pills = " ".join(f"<span class='skill-pill-green'>{s}</span>" for s in sorted(all_skills))
        st.markdown(pills, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    btn_col, _ = st.columns([1, 3])
    with btn_col:
        analyse = st.button("🚀 Analyse My Profile", use_container_width=True,
                            disabled=len(all_skills) == 0)

    if analyse:
        if len(all_skills) < 2:
            st.warning("Please add at least 2 skills to proceed.")
        else:
            with st.spinner("Running AI analysis …"):
                st.session_state.user_skills = all_skills

                # Predictions
                preds = predict_careers(all_skills, top_n=3)
                st.session_state.predictions = preds
                top_careers = [p["career"] for p in preds]

                # Skill gaps
                gaps = analyse_all_gaps(all_skills, top_careers)
                st.session_state.skill_gaps = gaps

                # Roadmap for top career
                top_gap   = gaps[top_careers[0]]
                roadmap   = generate_roadmap(
                    top_careers[0],
                    top_gap["missing_required"],
                    top_gap["missing_bonus"],
                )
                st.session_state.roadmap = roadmap

                # GitHub
                if st.session_state.github_username:
                    gh = analyze_github(st.session_state.github_username)
                    st.session_state.github_data = gh

                # DB
                sid = save_session(name, email, gh_user)
                st.session_state.session_id = sid
                save_prediction(sid, all_skills, preds, gaps)

                st.session_state.analysis_done = True

            st.success("✅ Analysis complete! Head to **Results & Roadmap** in the sidebar.")
            st.balloons()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: RESULTS & ROADMAP
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Results & Roadmap":
    if not st.session_state.analysis_done:
        st.info("👈 Complete your profile analysis first.")
        st.stop()

    preds  = st.session_state.predictions
    gaps   = st.session_state.skill_gaps
    skills = st.session_state.user_skills
    rdmap  = st.session_state.roadmap

    st.markdown("## 📊 Your Career Analysis")

    tab1, tab2, tab3 = st.tabs(["🏆 Career Predictions", "🔍 Skill Gap Analysis", "🗺️ Learning Roadmap"])

    # ─── TAB 1: Predictions ─────────────────────────────────────────────────
    with tab1:
        st.markdown("### Your Top Career Matches")
        col_cards = st.columns(len(preds))
        rank_icons = ["🥇", "🥈", "🥉"]
        colors = ["#6366f1", "#06b6d4", "#10b981"]

        for i, pred in enumerate(preds):
            with col_cards[i]:
                pct = pred["probability"] * 100
                st.markdown(f"""
                <div class='card' style='text-align:center; border-color:{colors[i]}44;'>
                    <div style='font-size:32px'>{rank_icons[i]}</div>
                    <div style='font-size:16px; font-weight:600; color:{colors[i]};
                                margin:8px 0;'>{pred['career']}</div>
                    <div style='font-size:36px; font-weight:700; color:{colors[i]};'>{pct:.0f}%</div>
                    <div style='font-size:12px; color:#64748b; margin-top:4px;'>Match Score</div>
                </div>
                """, unsafe_allow_html=True)
                st.progress(pred["probability"])

        # Radar / bar chart of all probs
        st.markdown("### Confidence Distribution")
        all_probs = predict_all_probabilities(skills)
        df_probs  = pd.DataFrame([
            {"Career": k, "Probability": v * 100}
            for k, v in sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
        ])
        fig = px.bar(
            df_probs, x="Probability", y="Career", orientation="h",
            color="Probability",
            color_continuous_scale=["#1c2537", "#6366f1", "#06b6d4"],
            template="plotly_dark",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Grotesk"),
            showlegend=False,
            coloraxis_showscale=False,
            height=380,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    # ─── TAB 2: Skill Gap ───────────────────────────────────────────────────
    with tab2:
        career_sel = st.selectbox(
            "Select a career to inspect",
            options=list(gaps.keys()),
        )
        gap = gaps[career_sel]

        c1, c2, c3 = st.columns(3)
        c1.metric("Readiness Score",  f"{gap['readiness']}%")
        c2.metric("Skills Matched",   len(gap["matched"]))
        c3.metric("Skills Missing",   len(gap["missing_required"]) + len(gap["missing_bonus"]))

        st.progress(gap["readiness"] / 100)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### ✅ Skills You Have")
            if gap["matched"]:
                pills = " ".join(f"<span class='skill-pill-green'>{s}</span>"
                                 for s in gap["matched"])
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.caption("None matched yet.")

            st.markdown("#### 🟡 Nice-to-Have (Bonus)")
            if gap["missing_bonus"]:
                pills = " ".join(f"<span class='skill-pill-yellow'>{s}</span>"
                                 for s in gap["missing_bonus"])
                st.markdown(pills, unsafe_allow_html=True)

        with c2:
            st.markdown("#### ❌ Critical Missing Skills")
            if gap["missing_required"]:
                pills = " ".join(f"<span class='skill-pill-red'>{s}</span>"
                                 for s in gap["missing_required"])
                st.markdown(pills, unsafe_allow_html=True)
            else:
                st.success("You meet all required skills!")

        # Donut chart
        matched_n  = len(gap["matched"])
        missing_n  = len(gap["missing_required"])
        bonus_n    = len(gap["missing_bonus"])
        fig2 = go.Figure(go.Pie(
            labels=["Matched", "Missing Required", "Missing Bonus"],
            values=[matched_n or 0.01, missing_n or 0.01, bonus_n or 0.01],
            hole=0.65,
            marker_colors=["#10b981", "#ef4444", "#f59e0b"],
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Grotesk", color="#e2e8f0"),
            legend=dict(orientation="h", y=-0.1),
            height=320,
            margin=dict(l=0, r=0, t=0, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ─── TAB 3: Roadmap ─────────────────────────────────────────────────────
    with tab3:
        if not rdmap:
            st.info("Run the analysis first.")
        else:
            st.markdown(f"### 🗺️ Learning Roadmap: **{rdmap['career']}**")
            st.markdown(f"Estimated completion: **~{rdmap['total_weeks']} weeks** "
                        f"(studying ~10 hrs/week)")

            for phase in rdmap["phases"]:
                st.markdown(f"<div class='roadmap-phase'>", unsafe_allow_html=True)
                st.markdown(f"#### {phase['label']}")
                for skill in phase["skills"]:
                    badge = "🔴" if skill["priority"] == "required" else "🟡"
                    with st.container():
                        c1, c2, c3 = st.columns([3, 1, 2])
                        c1.markdown(f"{badge} **{skill['skill'].title()}**")
                        c2.markdown(f"`~{skill['weeks']}w`")
                        c3.markdown(f"[📚 Learn]({skill['resource']})")
                st.markdown("</div>", unsafe_allow_html=True)

            if st.button("🔄 Regenerate Roadmap for Different Career"):
                career_for_map = st.selectbox("Pick career", list(gaps.keys()))
                g = gaps[career_for_map]
                st.session_state.roadmap = generate_roadmap(
                    career_for_map, g["missing_required"], g["missing_bonus"]
                )
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: CAREER SIMULATOR
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🎮 Career Simulator":
    if not st.session_state.analysis_done:
        st.info("👈 Complete your profile analysis first.")
        st.stop()

    st.markdown("## 🎮 Career Growth Simulator")
    st.markdown("See how adding a **new skill** shifts your career probability in real time.")

    missing_skills = []
    for gap in st.session_state.skill_gaps.values():
        missing_skills.extend(gap["missing_required"])
        missing_skills.extend(gap["missing_bonus"])
    missing_skills = sorted(set(missing_skills))

    new_skill = st.selectbox(
        "Select a skill to add",
        options=missing_skills or KNOWN_SKILLS,
        help="Only skills you don't already have are shown.",
    )

    if st.button("⚡ Simulate", use_container_width=False):
        with st.spinner("Calculating impact …"):
            sim = simulate_skill_addition(st.session_state.user_skills, new_skill)

        # Save simulation
        if st.session_state.session_id:
            save_simulation(
                st.session_state.session_id,
                st.session_state.user_skills,
                new_skill,
                sim["before"],
                sim["after"],
            )

        st.success(f"Simulating: adding **{new_skill}** to your profile")

        # Build comparison dataframe (top 5 careers by delta)
        sorted_deltas = sorted(sim["delta"].items(), key=lambda x: abs(x[1]), reverse=True)[:6]
        careers_show  = [x[0] for x in sorted_deltas]

        df_sim = pd.DataFrame({
            "Career":  careers_show * 2,
            "Probability": (
                [sim["before"][c] * 100 for c in careers_show] +
                [sim["after"][c]  * 100 for c in careers_show]
            ),
            "State": ["Before"] * len(careers_show) + ["After"] * len(careers_show),
        })

        fig = px.bar(
            df_sim, x="Career", y="Probability", color="State",
            barmode="group",
            color_discrete_map={"Before": "#334155", "After": "#6366f1"},
            template="plotly_dark",
            title=f"Impact of adding '{new_skill}'",
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Space Grotesk"),
            legend=dict(orientation="h", y=1.1),
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

        # Delta table
        st.markdown("### 📈 Probability Changes")
        delta_rows = []
        for career in careers_show:
            d = sim["delta"][career] * 100
            arrow = "⬆️" if d > 0 else ("⬇️" if d < 0 else "➡️")
            delta_rows.append({
                "Career":    career,
                "Before":    f"{sim['before'][career]*100:.1f}%",
                "After":     f"{sim['after'][career]*100:.1f}%",
                "Change":    f"{arrow} {abs(d):.1f}%",
            })
        st.dataframe(pd.DataFrame(delta_rows), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: GITHUB ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📂 GitHub Analysis":
    st.markdown("## 🐙 GitHub Profile Analysis")

    gh_user = st.text_input(
        "Enter GitHub Username",
        value=st.session_state.github_username,
        placeholder="e.g. torvalds",
    )

    if st.button("🔍 Fetch & Analyse", use_container_width=False):
        if not gh_user:
            st.warning("Please enter a GitHub username.")
        else:
            with st.spinner(f"Fetching repos for @{gh_user} …"):
                data = analyze_github(gh_user)
                st.session_state.github_data    = data
                st.session_state.github_username = gh_user

    data = st.session_state.github_data
    if data and data.get("repo_count", 0) > 0:
        c1, c2, c3 = st.columns(3)
        c1.metric("Public Repos",    data["repo_count"])
        c2.metric("Languages Found", len(data["top_languages"]))
        c3.metric("Skills Inferred", len(data["skills"]))

        if data["top_languages"]:
            st.markdown("### 📊 Language Distribution")
            langs, counts = zip(*data["top_languages"])
            fig = px.pie(
                names=langs, values=counts,
                color_discrete_sequence=px.colors.sequential.Plasma_r,
                template="plotly_dark",
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Space Grotesk"),
                height=320,
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🛠️ Inferred Skills from GitHub")
        if data["skills"]:
            pills = " ".join(f"<span class='skill-pill-green'>{s}</span>"
                             for s in data["skills"])
            st.markdown(pills, unsafe_allow_html=True)

        st.markdown("### 📂 Top Repositories")
        for repo in data["repos"][:10]:
            with st.container():
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.markdown(f"**{repo['name']}** – {repo['description'] or '_No description_'}")
                c2.markdown(f"⭐ {repo['stars']}")
                c3.markdown(f"`{repo['language'] or 'N/A'}`")

        if st.button("➕ Add GitHub Skills to My Profile"):
            merged = list(set(st.session_state.user_skills + data["skills"]))
            st.session_state.user_skills = merged
            st.success(f"Added {len(data['skills'])} GitHub skills to your profile. "
                       "Re-run analysis from Profile Input.")

    elif data:
        st.warning(f"No public repositories found for **{gh_user}**. "
                   "Check the username or the account may be private.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HISTORY
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "💾 History":
    st.markdown("## 💾 Recent Analyses")

    from db import get_recent_predictions, clear_predictions
    records = get_recent_predictions(limit=15)

    # Clear History Button (Top Right)
    col1, col2 = st.columns([6,1])
    with col2:
        if st.button("🗑️ Clear"):
            clear_predictions()
            st.success("History Cleared Successfully")
            st.rerun()

    if not records:
        st.info("No analysis history yet. Run an analysis to see records here.")
    else:
        for rec in records:
            try:
                careers = json.loads(rec["top_careers"])
                skills  = json.loads(rec["skills_input"])
                top     = careers[0]["career"] if careers else "N/A"
                pct     = careers[0]["probability"] * 100 if careers else 0

                with st.expander(
                    f"🧑 {rec.get('name') or 'Anonymous'} · {top} "
                    f"({pct:.0f}%) · {rec['created_at'][:16]}"
                ):
                    st.markdown(f"**Email:** {rec.get('email') or '—'}")
                    st.markdown(
                        f"**Skills ({len(skills)}):** "
                        + ", ".join(skills[:12])
                        + ("…" if len(skills) > 12 else "")
                    )

                    st.markdown("**Predictions:**")
                    for c in careers:
                        st.markdown(
                            f"  - {c['career']} – {c['probability']*100:.1f}%"
                        )

            except Exception:
                pass