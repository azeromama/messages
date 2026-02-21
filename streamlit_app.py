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

# ---------------- Note ID (acts as notebook link) ----------------
note_id = st.text_input("Enter note name (share this with others):")
if not note_id:
    st.info("Enter a note name to access this Personal Note")
    st.stop()

# ---------------- Add Message / Note ----------------
msg = st.text_area("Write in your note...")
if st.button("Save"):
    if msg:
        supabase.table("messages").insert({
            "note_id": note_id,
            "text": msg,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        st.success("Saved ✅")

# ---------------- Display Notes ----------------
messages = supabase.table("messages").select("*").eq("note_id", note_id).order("created_at").execute().data

for m in messages:
    st.markdown(f"- {m['text']}")

# ---------------- Clear All ----------------
if st.button("🧹 Clear All Notes"):
    supabase.table("messages").delete().eq("note_id", note_id).execute()
    st.success("All notes cleared ✅")
