import streamlit as st
from supabase import create_client
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ---------------- Supabase Setup ----------------
url = "https://agwvyufagtgcbhwubrea.supabase.co"        # replace with your Supabase project URL
key = "sb_publishable_KCgoFKPF8kdYD8ocSNWqBw__xnPl90e"   # replace with your Supabase anon key
supabase = create_client(url, key)

# ---------------- Notebook Style ----------------
st.set_page_config(page_title="📝 Personal Note", page_icon="📝")
st.title("📝 Personal Note")

# ---------------- Real-time Auto-refresh ----------------
st_autorefresh(interval=2000, key="refresh")

# ---------------- First-time Password ----------------
if "unlocked" not in st.session_state:
    if "note_password" in st.session_state:
        st.session_state.unlocked = True
    else:
        st.session_state.unlocked = False

if not st.session_state.unlocked:
    password_input = st.text_input("Enter password:", type="password")
    if st.button("Unlock"):
        if password_input == "N+A":
            st.session_state.unlocked = True
            st.session_state.note_password = password_input
            st.success("Unlocked ✅")
        else:
            st.error("Wrong password ❌")
    st.stop()

# ---------------- Note ID (acts as chat room) ----------------
note_id = st.text_input("Enter note name:", type="password")
if not note_id:
    st.info("Enter a note name to access this Personal Note")
    st.stop()

# ---------------- Add Message / Note ----------------
msg = st.chat_input("Write a message...")
if msg:
    supabase.table("messages").insert({
        "note_id": note_id,
        "text": msg,
        "created_at": datetime.utcnow().isoformat(),  # convert to string
        "seen_at": None,
        "sender": "me"
    }).execute()

# ---------------- Display Messages ----------------
now = datetime.utcnow()
messages = supabase.table("messages").select("*").eq("note_id", note_id).order("created_at").execute().data
to_delete = []

for m in messages:
    # Auto-delete messages 5 min after viewing
    if m.get("seen_at") and (now - m["seen_at"]).total_seconds() > 300:
        to_delete.append(m["id"])
        continue
    with st.chat_message("📝 Personal Note"):
        st.write(m["text"])
    if not m.get("seen_at"):
    supabase.table("messages").update({
        "seen_at": datetime.utcnow().isoformat()
    }).eq("id", m["id"]).execute()

# Delete old messages
for m_id in to_delete:
    supabase.table("messages").delete().eq("id", m_id).execute()

# ---------------- Clear All ----------------
if st.button("🧹 Clear All Messages"):
    supabase.table("messages").delete().eq("note_id", note_id).execute()
    st.success("All messages cleared ✅")
