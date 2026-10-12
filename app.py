import json
import urllib.parse
from datetime import date
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="P-1466 Daily POD", page_icon="📋", layout="wide")

FILE = Path("pod_data.json")
SECTIONS = [
    ("Day Shift", "☀️"),
    ("Night Shift", "🌙"),
    ("Weekly Off", "🟡"),
    ("Leave", "🔴"),
]
SECTION_NAMES = [s for s, _ in SECTIONS]
GRID_COLS = 4

DEFAULT_NAMES = [
    "Roshan", "Milind", "Avinash", "Shubham", "Apoorv",
    "Manoj", "Pravin", "Om", "Omkar", "Prashant",
    "Obulesu", "Sudeep", "Adesh", "Rohan", "Chotelal",
    "Akshay", "Ravi Teja", "Dhaneshwar", "Rehman", "Ashish",
]


# ---------------------------------------------------------------- storage
def load_data():
    if FILE.exists():
        try:
            with FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            st.error("Could not read pod_data.json. Restore a valid backup.")
            st.stop()
        data.setdefault("employees", [])
        data.setdefault("attendance", {})
        # Migrate old name-based records to employee IDs.
        id_by_name = {e["name"]: e["id"] for e in data["employees"]}
        for rec in data["attendance"].values():
            for sec, vals in rec.items():
                vals = [id_by_name.get(v) if isinstance(v, str) else v for v in vals]
                rec[sec] = [v for v in vals if v is not None]
        return data

    return {
        "employees": [
            {"id": i, "name": n, "active": True} for i, n in enumerate(DEFAULT_NAMES, 1)
        ],
        "attendance": {},
    }


def save_data():
    tmp = FILE.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(st.session_state.data, f, indent=2, ensure_ascii=False)
    tmp.replace(FILE)


if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data
employees = [e for e in data["employees"] if e.get("active", True)]
name_of = {e["id"]: e["name"] for e in data["employees"]}
active_ids = [e["id"] for e in employees]


# ---------------------------------------------------------------- helpers
def cb_key(day_key, section, emp_id):
    return f"cb_{day_key}_{section}_{emp_id}"


def assign_key(day_key):
    return f"assign_{day_key}"


def on_toggle(day_key, section, emp_id):
    """Checkbox callback: assign / unassign an employee (one section only)."""
    assign = st.session_state[assign_key(day_key)]
    if st.session_state[cb_key(day_key, section, emp_id)]:
        assign[emp_id] = section
    elif assign.get(emp_id) == section:
        assign.pop(emp_id, None)


def clear_day(day_key):
    st.session_state[assign_key(day_key)] = {}


def copy_previous(day_key):
    earlier = sorted(d for d in data["attendance"] if d < day_key)
    if not earlier:
        return
    prev = data["attendance"][earlier[-1]]
    assign = {}
    for s in SECTION_NAMES:
        for i in prev.get(s, []):
            if i in active_ids and i not in assign:
                assign[i] = s
    st.session_state[assign_key(day_key)] = assign


def build_report(day, assignments):
    total = len(employees)
    present = len(assignments["Day Shift"]) + len(assignments["Night Shift"])
    lines = [
        "📋 *P-1466 DAILY POD & SHIFT SCHEDULE*",
        f"📅 *Date: {day.strftime('%d.%m.%Y')}*",
        "",
        "━━━━━━━━━━━━━━━━━━",
        "👥 *ATTENDANCE / MANPOWER*",
        f"Total Strength: {total}",
        f"Total Present: {present}/{total}",
        "",
    ]
    for section, emoji in SECTIONS:
        names = [name_of[i] for i in assignments[section]]
        lines.append(f"{emoji} *{section.upper()} ({len(names)})*")
        if names:
            lines.extend(f"{n}. {nm}" for n, nm in enumerate(names, 1))
        else:
            lines.append("None")
        lines.append("")
    lines.append("_P-1466 | Daily Manpower Report_")
    return "\n".join(lines)


# ---------------------------------------------------------------- UI
st.title("📋 P-1466 Daily POD")
st.caption("Tick names under each section. A name ticked in one section is hidden from the others.")

col1,col2,col3,col4 = st.columns(4)
with col1:
    day = st.date_input("📅 Report Date", value=date.today())
    day_key = day.isoformat()
    saved = data["attendance"].get(day_key, {})

with col2:
 st.markdown("")
# Employee management
 with st.expander("➕ Manage Employee Names"):
    with st.form("add_employee", clear_on_submit=True):
        new_name = st.text_input("New employee name")
        if st.form_submit_button("Add Employee"):
            new_name = new_name.strip()
            if not new_name:
                st.error("Enter an employee name.")
            elif any(e["name"].casefold() == new_name.casefold() for e in data["employees"]):
                st.error("This employee already exists.")
            else:
                new_id = max([e["id"] for e in data["employees"]] + [0]) + 1
                data["employees"].append({"id": new_id, "name": new_name, "active": True})
                save_data()
                st.rerun()

    for emp in data["employees"]:
        c1, c2, c3 = st.columns([3, 1, 2])
        renamed = c1.text_input(
            "Name", value=emp["name"], key=f"name_{emp['id']}", label_visibility="collapsed"
        ).strip()
        active = c2.checkbox("Active", value=emp.get("active", True), key=f"active_{emp['id']}")
        changed = False
        if active != emp.get("active", True):
            emp["active"] = active
            changed = True
        if renamed and renamed != emp["name"]:
            if any(o["id"] != emp["id"] and o["name"].casefold() == renamed.casefold()
                   for o in data["employees"]):
                c3.error("Name exists")
            else:
                emp["name"] = renamed
                changed = True
        if changed:
            save_data()
            st.rerun()

# Assignment state for the selected date: {employee_id: section}
ak = assign_key(day_key)
if ak not in st.session_state:
    init = {}
    for s in SECTION_NAMES:
        for i in saved.get(s, []):
            if i in active_ids and i not in init:
                init[i] = s
    st.session_state[ak] = init
assign = st.session_state[ak]
for i in [i for i in assign if i not in active_ids]:
    assign.pop(i)

# Sync checkbox widget states with the assignment before they are drawn.
for s in SECTION_NAMES:
    for i in active_ids:
        st.session_state[cb_key(day_key, s, i)] = assign.get(i) == s

b1, b2, _ = st.columns([1, 1, 3])
with col3:
 b1.button("📋 Copy previous day", on_click=copy_previous, args=(day_key,), use_container_width=True)
with col4:
 b2.button("🧹 Clear all", on_click=clear_day, args=(day_key,), use_container_width=True)

st.subheader("☑️ Daily Shift Selection")

for section, emoji in SECTIONS:
    with st.container(border=True):
        count = sum(1 for v in assign.values() if v == section)
        st.markdown(f"**{emoji} {section}** — {count}")

        # Show only people who are unassigned or already in THIS section.
        visible = [i for i in active_ids if assign.get(i) in (None, section)]
        if not visible:
            st.caption("No names left to select.")
            continue

        cols = st.columns(GRID_COLS)
        for n, i in enumerate(visible):
            cols[n % GRID_COLS].checkbox(
                name_of[i],
                key=cb_key(day_key, section, i),
                on_change=on_toggle,
                args=(day_key, section, i),
            )

# Final assignments (in employee order)
assignments = {s: [i for i in active_ids if assign.get(i) == s] for s in SECTION_NAMES}

unassigned = [name_of[i] for i in active_ids if i not in assign]
if unassigned:
    st.info(f"**Not yet assigned ({len(unassigned)}):** " + ", ".join(unassigned))
else:
    st.success("Everyone is assigned.")

present = len(assignments["Day Shift"]) + len(assignments["Night Shift"])
cols = st.columns(6)
cols[0].metric("Total", len(employees))
cols[1].metric("Present", present)
cols[2].metric("Day", len(assignments["Day Shift"]))
cols[3].metric("Night", len(assignments["Night Shift"]))
cols[4].metric("Weekly Off", len(assignments["Weekly Off"]))
cols[5].metric("Leave", len(assignments["Leave"]))

if st.button("💾 Save Daily POD", type="primary", use_container_width=True):
    data["attendance"][day_key] = assignments
    save_data()
    saved = assignments
    st.success("Daily POD saved successfully.")

if saved and any(set(saved.get(s, [])) != set(assignments[s]) for s in SECTION_NAMES):
    st.caption("⚠️ Unsaved changes for this date.")

st.divider()
st.subheader("📲 WhatsApp Sharing")

message = build_report(day, assignments)
st.text_area("WhatsApp message preview", message, height=380)

st.link_button(
    "💬 Choose WhatsApp Recipient & Send",
    "https://wa.me/?text=" + urllib.parse.quote(message),
    use_container_width=True,
)
st.caption("WhatsApp opens with the report prefilled. Pick a contact or group and tap Send.")

d1, d2 = st.columns(2)
d1.download_button(
    "⬇️ Download Report as TXT",
    data=message,
    file_name=f"P1466_POD_{day_key}.txt",
    mime="text/plain",
    use_container_width=True,
)
d2.download_button(
    "📦 Backup All Data",
    data=json.dumps(data, indent=2, ensure_ascii=False),
    file_name="pod_data_backup.json",
    mime="application/json",
    use_container_width=True,
)
