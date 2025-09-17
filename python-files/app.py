import os
import streamlit as st
import concurrent.futures
import threading
import traceback
import inspect
import sqlite3
import hashlib
import platform
import uuid
import queue
import math
from streamlit_autorefresh import st_autorefresh

from data import data
from files import files
from listing import listing
from multi_listing import multi_listing, _drain_status_queue  # ✅ import queue UI updater

# ================== Streamlit Page Setup ==================
st.set_page_config(page_title="Meta Post - Facebook Listing App", page_icon="🌊")

# ================== CSS Styling ==================
st.markdown("""
<style>
.header-banner {
    background: linear-gradient(90deg, #4b6cb7, #182848);
    color: white;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.3);
    margin-bottom: 20px;
}
.stButton>button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    font-weight: bold;
    border-radius: 12px;
    padding: 10px 20px;
    transition: all 0.3s ease;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
}
.stButton>button:hover {
    transform: scale(1.05);
    background: linear-gradient(135deg, #764ba2, #667eea);
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header-banner">Meta Post - Facebook Listing App</div>', unsafe_allow_html=True)

# ================== Database Setup ==================
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT UNIQUE,
                 password TEXT,
                 device_id TEXT,
                 is_superadmin INTEGER DEFAULT 0,
                 is_active INTEGER DEFAULT 0
             )""")
    conn.commit()
    
    # Ensure superadmin always exists
    super_username = "superadmin"
    super_password = hashlib.sha256("MetaPost@123".encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE is_superadmin=1")
    super_user = c.fetchone()
    if not super_user:
        c.execute("INSERT INTO users (username, password, device_id, is_superadmin, is_active) VALUES (?,?,?,?,?)",
                  (super_username, super_password, "SUPER_DEVICE", 1, 1))
    conn.commit()
    conn.close()

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_device_id():
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, platform.node()))

init_db()

# ================== User Functions ==================
def signup(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, device_id, is_active) VALUES (?,?,?,0)",
                  (username, hash_pass(password), get_device_id()))
        conn.commit()
        return "Signup successful. Wait for superadmin approval."
    except sqlite3.IntegrityError:
        return "Username already exists."
    finally:
        conn.close()

def login(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT id, password, device_id, is_superadmin, is_active FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    if not user:
        return None, "User not found."
    if user[1] != hash_pass(password):
        return None, "Incorrect password."
    if not user[4]:
        return None, "Account not approved by superadmin."

    # ✅ Device lock only for normal users
    if not user[3] and user[2] != get_device_id():
        return None, "This account is locked to another device."

    return {"id": user[0], "username": username, "is_superadmin": bool(user[3])}, "Login successful."

# ================== Admin Panel ==================
def admin_panel(admin_username):
    st_autorefresh(interval=5000, key="admin_panel_refresh")
    st.title("👑 Superadmin Panel - Meta Post")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT id, username, device_id, is_superadmin, is_active FROM users ORDER BY id DESC")
    users = c.fetchall()

    # ---------- Summary ----------
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_active=1")
    active_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM users WHERE is_active=0")
    pending_users = c.fetchone()[0]

    st.markdown("### 📊 User Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", total_users)
    col2.metric("Active Users", active_users)
    col3.metric("Pending Users", pending_users)
    st.markdown("---")

    st.markdown("### 👥 Manage Users")

    if not users:
        st.info("No users found.")
        conn.close()
        return

    # Pagination controls (5 per page)
    users_per_page = 5
    total_pages = max(1, math.ceil(len(users) / users_per_page))
    if "admin_page" not in st.session_state:
        st.session_state.admin_page = 1
    page_col1, page_col2, page_col3 = st.columns([1,2,1])
    with page_col1:
        if st.button("◀ Prev"):
            st.session_state.admin_page = max(1, st.session_state.admin_page - 1)
    with page_col2:
        st.session_state.admin_page = st.number_input("Page", min_value=1, max_value=total_pages,
                                                      value=st.session_state.admin_page, step=1,
                                                      key="admin_page_input")
    with page_col3:
        if st.button("Next ▶"):
            st.session_state.admin_page = min(total_pages, st.session_state.admin_page + 1)

    page = int(st.session_state.admin_page)
    start_idx = (page - 1) * users_per_page
    end_idx = start_idx + users_per_page
    page_users = users[start_idx:end_idx]

    # Header row
    hdr1, hdr2, hdr3, hdr4, hdr5 = st.columns([2,2,1,1,2])
    hdr1.markdown("**Username**")
    hdr2.markdown("**Device**")
    hdr3.markdown("**Role**")
    hdr4.markdown("**Status**")
    hdr5.markdown("**Actions**")

    for uid, uname, dev, su, act in page_users:
        row1, row2, row3, row4, row5 = st.columns([2,2,1,1,2])
        row1.write(uname)
        row2.write(dev if dev else "No Device")
        row3.write("👑 Superadmin" if su else "🙍 User")
        row4.write("✅ Active" if act else "❌ Pending")

        with row5:
            if not su:  # normal user only
                if st.button("Block" if act else "Approve", key=f"toggle_{uid}"):
                    c.execute("UPDATE users SET is_active=? WHERE id=?", (0 if act else 1, uid))
                    conn.commit()
                    st.experimental_rerun()
                if st.button("Delete", key=f"delete_{uid}"):
                    c.execute("DELETE FROM users WHERE id=?", (uid,))
                    conn.commit()
                    st.experimental_rerun()

    # Superadmin settings
    st.markdown("---")
    st.markdown("### 🔑 Superadmin Settings")
    new_username = st.text_input("New Username", value=admin_username, key="su_user")
    new_password = st.text_input("New Password", type="password", key="su_pass")

    if st.button("Update Superadmin"):
        if new_username and new_password:
            c.execute("UPDATE users SET username=?, password=? WHERE is_superadmin=1",
                      (new_username, hash_pass(new_password)))
            conn.commit()
            st.success("Superadmin credentials updated. Please log in again.")
            st.session_state.user = None
            st.experimental_rerun()

    conn.close()

# ================== Main App ==================
def main():
    if "user" not in st.session_state:
        st.session_state.user = None

    # ---------- Login / Signup ----------
    if st.session_state.user is None:
        st.title("Meta Post - Login")
        option = st.selectbox("Choose:", ["Login", "Signup"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if option == "Signup":
            if st.button("Signup"):
                st.success(signup(username, password))
        else:
            if st.button("Login"):
                user, msg = login(username, password)
                if user:
                    st.session_state.user = user
                    st.success(msg)
                else:
                    st.error(msg)
        st.stop()

    # ---------- After Login ----------
    st.markdown(f"### Welcome, {st.session_state.user['username']} - Meta Post")

    if "executor" not in st.session_state:
        st.session_state.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    if "futures" not in st.session_state:
        st.session_state.futures = {}
    if "stop_events" not in st.session_state:
        st.session_state.stop_events = {"listing": None, "multi_listing": None}
    if "log_queue" not in st.session_state:
        st.session_state.log_queue = queue.Queue()
    if "run_headless" not in st.session_state:
        st.session_state.run_headless = True

    def run_wrapper(func, stop_event, *args):
        try:
            sig = inspect.signature(func)
            if len(sig.parameters) >= 1:
                result = func(stop_event, *args)
            else:
                result = func()
            return {"ok": True, "result": result}
        except Exception as e:
            return {"ok": False, "error": str(e), "trace": traceback.format_exc()}

    def _apply_headless_env():
        if st.session_state.get("run_headless"):
            os.environ["FORCE_HEADLESS"] = "1"
        else:
            os.environ.pop("FORCE_HEADLESS", None)

    def start_listing_only():
        _apply_headless_env()
        se = threading.Event()
        st.session_state.stop_events["listing"] = se
        fut = st.session_state.futures.get("listing")
        if fut is None or fut.done():
            st.session_state.futures["listing"] = st.session_state.executor.submit(run_wrapper, listing, se)
        else:
            st.info("Listing is already running.")

    def stop_listing():
        ev = st.session_state.stop_events.get("listing")
        if ev:
            ev.set()

    def start_multi_only(num_windows=2):
        _apply_headless_env()
        se = threading.Event()
        st.session_state.stop_events["multi_listing"] = se
        fut = st.session_state.futures.get("multi_listing")
        if fut is None or fut.done():
            st.session_state.futures["multi_listing"] = st.session_state.executor.submit(
                run_wrapper, multi_listing, se, num_windows
            )
        else:
            st.info("Multi-listing is already running.")

    def stop_multi_listing():
        ev = st.session_state.stop_events.get("multi_listing")
        if ev:
            ev.set()

    # ---------- Sidebar ----------
    st.sidebar.title("Navigation")
    page_options = ["Dashboard", "Data", "Files"]
    if st.session_state.user["is_superadmin"]:
        page_options.append("Admin Panel")

    page = st.sidebar.selectbox("Go to:", page_options)

    if page == "Dashboard":
        st.title("Automation Section - Meta Post")
        run_headless = st.checkbox("Run headless (no browser windows)",
                                   value=st.session_state.get("run_headless", True),
                                   key="run_headless_ui")
        st.session_state.run_headless = run_headless

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Listing"):
                start_listing_only()
            if st.button("Stop Listing"):
                stop_listing()
        with col2:
            if st.button("Start Multi-Listing"):
                start_multi_only(2)
            if st.button("Stop Multi-Listing"):
                stop_multi_listing()

        st.write("### Jobs Status")
        futures = st.session_state.futures
        for name in ("listing", "multi_listing"):
            fut = futures.get(name)
            if fut is None:
                st.write(f"- **{name}**: not started")
                continue
            try:
                if fut.running():
                    st.info(f"🔄 {name} is running...")
                elif fut.done():
                    try:
                        res = fut.result()
                        if isinstance(res, dict) and res.get("ok"):
                            st.success(f"✅ {name} completed → {res.get('result')}")
                        else:
                            st.error(f"❌ {name} failed — {res.get('error') if isinstance(res, dict) else 'Unknown error'}")
                            trace_text = res.get("trace") if isinstance(res, dict) else None
                            with st.expander("Error details"):
                                if trace_text:
                                    st.code(trace_text)
                                else:
                                    st.write("No traceback available.")
                    except Exception as e:
                        st.error(f"- **{name}**: ERROR retrieving future result: {e}")
                else:
                    st.warning(f"- **{name}**: queued")
            except Exception as e:
                st.error(f"Error while checking job status for {name}: {e}")

        # ✅ Live Multi-Listing Status Table + Progress
        st.write("### Live Multi-Listing Status")
        _drain_status_queue()

        st.write("### Live Logs")
        if "log_container" not in st.session_state:
            st.session_state.log_container = st.empty()
        log_box = st.session_state.log_container.container()
        if "log_queue" in st.session_state:
            try:
                while not st.session_state.log_queue.empty():
                    msg_type, message = st.session_state.log_queue.get()
                    if msg_type == "success":
                        log_box.success(message)
                    elif msg_type == "error":
                        log_box.error(message)
                    else:
                        log_box.info(message)
            except Exception as e:
                log_box.error(f"Log processing error: {e}")

    elif page == "Data":
        data()
    elif page == "Files":
        files()
    elif page == "Admin Panel":
        admin_panel(st.session_state.user["username"])

if __name__ == "__main__":
    main()
