import os
import requests
import streamlit as st
from typing import Dict, List

# =========================
# Config (set via env or st.secrets)
# =========================
API_URL = st.secrets.get("API_URL", os.getenv("API_URL", "https://<api-id>.execute-api.<region>.amazonaws.com/prod/chat"))
API_KEY = st.secrets.get("API_KEY", os.getenv("API_KEY", ""))  # optional usage-plan key

st.set_page_config(page_title="Mimosa Mentor", page_icon="🧪", layout="wide")

# =========================
# Challenge catalog (metadata for selector & filters)
# =========================
LABS_META: List[Dict] = [
    {"name":"Doodle Drive","topic":"IDOR","owasp":"A01: Broken Access Control","difficulty":"Easy","week":"Week 1–2"},
    {"name":"Faster Than Light","topic":"Client-side timing","owasp":"A05: Security Misconfiguration","difficulty":"Medium","week":"Week 1–2"},
    {"name":"Poison Apples","topic":"CSRF","owasp":"A05: Security Misconfiguration","difficulty":"Medium","week":"Week 1–2"},
    {"name":"Nuclear Winter","topic":"Cookie manipulation","owasp":"A05: Security Misconfiguration","difficulty":"Easy","week":"Week 1–2"},
    {"name":"Bad Teacher","topic":"IDOR (marksheets)","owasp":"A01: Broken Access Control","difficulty":"Medium","week":"Week 3"},
    {"name":"Into the Shadows","topic":"Auth logic bypass","owasp":"A07: Identification & Authentication Failures","difficulty":"Hard","week":"Week 3"},
    {"name":"Pong","topic":"Client-side trust","owasp":"A04: Insecure Design","difficulty":"Easy","week":"Week 3"},
    {"name":"Biography","topic":"Stored XSS","owasp":"A03: Injection","difficulty":"Medium","week":"Week 3"},
    {"name":"XSS Basics","topic":"Reflected XSS","owasp":"A03: Injection","difficulty":"Easy","week":"Week 4"},
    {"name":"Christmas Workshop","topic":"DOM XSS","owasp":"A03: Injection","difficulty":"Medium","week":"Week 4"},
    {"name":"Fakebook v1","topic":"Stored XSS","owasp":"A03: Injection","difficulty":"Medium","week":"Week 4"},
    {"name":"Syndica","topic":"DOM Injection","owasp":"A03: Injection","difficulty":"Hard","week":"Week 4"},
    {"name":"Dazala","topic":"XSS filter evasion","owasp":"A03: Injection","difficulty":"Hard","week":"Week 4"},
    {"name":"Notflix","topic":"SQLi login","owasp":"A03: Injection","difficulty":"Medium","week":"Week 5"},
    {"name":"Fakebook v2","topic":"SQLi search","owasp":"A03: Injection","difficulty":"Hard","week":"Week 5"},
    {"name":"SQLi Basics","topic":"Classic SQL injection","owasp":"A03: Injection","difficulty":"Easy","week":"Week 5"},
    {"name":"SQLi Basics Two","topic":"Operator precedence SQLi","owasp":"A03: Injection","difficulty":"Hard","week":"Week 5"},
    {"name":"Logging Lab","topic":"Logging & monitoring","owasp":"A09: Logging & Monitoring Failures","difficulty":"Medium","week":"Practicals"},
    {"name":"Regex Practice","topic":"Validation","owasp":"A05: Security Misconfiguration","difficulty":"Easy","week":"Practicals"},
    {"name":"JWT Middleware Lab","topic":"JWT misuse","owasp":"A07: Identification & Authentication Failures","difficulty":"Medium","week":"Practicals"},
    {"name":"Queue Isolation","topic":"Misconfiguration / Insecure Design","owasp":"A05: Security Misconfiguration","difficulty":"Medium","week":"Practicals"},
]
HINT_STAGES = ["orientation", "surface", "context", "defense"]

# =========================
# Helpers
# =========================
def call_lambda(message: str, timeout: int = 45) -> str:
    headers = {"content-type": "application/json"}
    if API_KEY:
        headers["x-api-key"] = API_KEY
    try:
        r = requests.post(API_URL, json={"message": message}, headers=headers, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        return data.get("reply") or "⚠️ Backend returned no reply."
    except requests.exceptions.HTTPError as e:
        return f"⚠️ HTTP {r.status_code}: {r.text[:300]}"
    except Exception as e:
        return f"⚠️ Network error: {e}"

def format_router_message(agent: str, lab: str, action: str, extra: Dict = None) -> str:
    extra = extra or {}
    lines = [f"[{agent}]", f"lab: {lab}", f"action: {action}"]
    for k, v in extra.items():
        lines.append(f"{k}: {v}")
    lines.append(f"Please respond as {agent} for lab '{lab}' with action '{action}'.")
    return "\n".join(lines)

def challenge_selector(labs_meta: List[Dict]) -> str:
    st.subheader("🎯 Select a Challenge")
    q = st.text_input("Search by name/topic…", placeholder="e.g., SQLi, CSRF, IDOR, XSS…").strip().lower()
    ow = sorted({l["owasp"] for l in labs_meta})
    diffs = ["Easy","Medium","Hard"]
    weeks = ["Week 1–2","Week 3","Week 4","Week 5","Practicals"]

    c1,c2,c3,c4 = st.columns([1,1,1,1.2])
    with c1: f_owasp = st.multiselect("OWASP", ow)
    with c2: f_diff  = st.multiselect("Difficulty", diffs)
    with c3: f_week  = st.multiselect("Week", weeks)
    with c4: sort_by = st.selectbox("Sort by", ["Name","Difficulty","Week"])

    def keep(l):
        if q and (q not in l["name"].lower() and q not in l["topic"].lower() and q not in l["owasp"].lower()):
            return False
        if f_owasp and l["owasp"] not in f_owasp: return False
        if f_diff  and l["difficulty"] not in f_diff: return False
        if f_week  and l["week"] not in f_week: return False
        return True

    rows = [l for l in labs_meta if keep(l)]
    if sort_by == "Name":
        rows.sort(key=lambda x: x["name"])
    elif sort_by == "Difficulty":
        order = {"Easy":0,"Medium":1,"Hard":2}
        rows.sort(key=lambda x: (order.get(x["difficulty"],99), x["name"]))
    else:
        worder = {"Week 1–2":1,"Week 3":2,"Week 4":3,"Week 5":4,"Practicals":5}
        rows.sort(key=lambda x: (worder.get(x["week"],99), x["name"]))

    st.caption(f"{len(rows)} challenges match your filters.")
    selected = st.session_state.get("selected_lab", rows[0]["name"] if rows else "")
    grid = st.columns(3) if rows else []
    for i, lab in enumerate(rows):
        with grid[i % 3]:
            st.markdown(f"### {lab['name']}")
            st.markdown(f"- **Topic:** {lab['topic']}\n- **OWASP:** {lab['owasp']}\n- **Difficulty:** {lab['difficulty']}\n- **Week:** {lab['week']}")
            if st.button("Select", key=f"select_{lab['name']}"):
                st.session_state["selected_lab"] = lab["name"]
                selected = lab["name"]
            st.divider()
    if not rows:
        st.info("No results. Adjust your filters.")

    with st.expander("Quick picker"):
        all_names = [l["name"] for l in labs_meta]
        idx = all_names.index(selected) if selected in all_names else 0
        pick = st.selectbox("Pick by name", all_names, index=idx)
        if pick != selected:
            st.session_state["selected_lab"] = pick
            selected = pick

    st.success(f"Selected: **{selected}**" if selected else "Nothing selected yet.")
    return selected

def get_stage(lab: str) -> int:
    return st.session_state.get("hint_stage_by_lab", {}).get(lab, 0)

def set_stage(lab: str, idx: int):
    if "hint_stage_by_lab" not in st.session_state:
        st.session_state["hint_stage_by_lab"] = {}
    st.session_state["hint_stage_by_lab"][lab] = max(0, min(idx, len(HINT_STAGES)-1))

def add_chat(role: str, content: str):
    if "chat" not in st.session_state:
        st.session_state["chat"] = []
    st.session_state["chat"].append((role, content))

def export_current_view(lab: str, content: Dict[str, str]) -> str:
    md = [f"# {lab}\n"]
    if content.get("hint"): md += ["## Hints\n", content["hint"], "\n"]
    if content.get("code"): md += ["## Code Compare\n", content["code"], "\n"]
    if content.get("verify"): md += ["## Verify\n", content["verify"], "\n"]
    return "".join(md)

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.header("🧭 Controls")
    st.text_input("API URL", value=API_URL, key="api_url_display", disabled=True)
    st.caption("Set via env `API_URL` or Streamlit secrets.")
    selected_lab = challenge_selector(LABS_META)

    c1, c2 = st.columns(2)
    if c1.button("🔁 Reset hints"):
        set_stage(selected_lab, 0)
        st.toast(f"Hint stage reset for {selected_lab}")
    if c2.button("🔎 Health check"):
        reply = call_lambda("[Verifier]\naction: ping\nPlease respond with 'pong'.")
        st.toast(reply[:120])

    st.write("---")
    st.subheader("Quick Actions")
    if st.button("💡 First hint (Orientation)"):
        set_stage(selected_lab, 0)
        msg = format_router_message("HintGuide", selected_lab, "hint", {"stage": HINT_STAGES[0]})
        add_chat("assistant", call_lambda(msg))
    if st.button("➡️ Next hint"):
        idx = min(get_stage(selected_lab) + 1, len(HINT_STAGES) - 1)
        set_stage(selected_lab, idx)
        msg = format_router_message("HintGuide", selected_lab, "hint", {"stage": HINT_STAGES[idx]})
        add_chat("assistant", call_lambda(msg))
    if st.button("🪞 Reflections"):
        add_chat("assistant", call_lambda(format_router_message("HintGuide", selected_lab, "reflection")))
    if st.button("🙅 Misconceptions"):
        add_chat("assistant", call_lambda(format_router_message("HintGuide", selected_lab, "misconception")))
    st.write("---")
    if st.button("🧩 Show code (vulnerable vs hardened)"):
        add_chat("assistant", call_lambda(format_router_message("CodeTutor", selected_lab, "code_compare", {"lang":"nodejs"})))
    if st.button("✅ Verify checks"):
        add_chat("assistant", call_lambda(format_router_message("Verifier", selected_lab, "verify")))

# =========================
# Main area
# =========================
st.title("🧪 Mimosa Mentor")
st.caption("Streamlit client → API Gateway → Lambda → OpenAI (multi-agent router in Studio).")

# Show chat/history
if "chat" in st.session_state and st.session_state["chat"]:
    for role, content in st.session_state["chat"]:
        with st.chat_message(role if role in ("user","assistant") else "assistant"):
            st.markdown(content)

# Freeform chat box
if user_msg = st.chat_input(f"Ask about {selected_lab}… (e.g., 'Show code compare')"):
    add_chat("user", user_msg)
    add_chat("assistant", call_lambda(user_msg))
    st.experimental_rerun()

# Export section
st.write("---")
st.subheader("📥 Export current view")
hint_blob = next((c for r,c in st.session_state.get("chat", []) if "[HintGuide]" in c or "Hint" in c), "")
code_blob = next((c for r,c in st.session_state.get("chat", []) if "[CodeTutor]" in c or "```" in c), "")
verify_blob = next((c for r,c in st.session_state.get("chat", []) if "[Verifier]" in c or "verify" in c.lower()), "")
md = export_current_view(selected_lab, {"hint": hint_blob, "code": code_blob, "verify": verify_blob})
st.download_button("Download .md", data=md, file_name=f"{selected_lab.replace(' ','_')}.md", mime="text/markdown")
