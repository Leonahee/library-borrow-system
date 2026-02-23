import streamlit as st
import model
import controller


# =========================
# View helpers (reset form)
# =========================
def reset_book_form():
    st.session_state["new_title"] = ""
    st.session_state["new_author"] = ""


def on_save_book():
    title = st.session_state.get("new_title", "")
    author = st.session_state.get("new_author", "")
    ok, msgs = controller.create_book(title, author)
    if not ok:
        for m in msgs:
            st.error(m)
    else:
        for m in msgs:
            st.success(m)
        reset_book_form()


# =========================
# UI
# =========================


def render_book():
# -------- Books: Create --------
    st.subheader("เพิ่มข้อมูลหนังสือใหม่")
    st.text_input("ชื่อหนังสือ", key="new_title")
    st.text_input("ผู้แต่ง", key="new_author")


    col1, col2 = st.columns([1, 3])
    with col1:
        st.button("บันทึกข้อมูลหนังสือ", on_click=on_save_book)
    with col2:
        st.button("ล้างฟอร์ม", on_click=reset_book_form)


    # -------- Books: Read --------
    st.subheader("📖 รายการหนังสือทั้งหมดในระบบ")
    books_df = model.get_all_books()
    if books_df.empty:
        st.info("ยังไม่มีข้อมูลหนังสือในระบบ")
    else:
        st.dataframe(books_df, use_container_width=True)


    # -------- Books: Delete --------
    st.subheader("🗑 ลบข้อมูลหนังสือ")
    books_df = model.get_all_books()
    if books_df.empty:
        st.info("ยังไม่มีข้อมูลหนังสือในระบบ")
    else:
        for _, row in books_df.iterrows():
            c1, c2, c3 = st.columns([4, 3, 1])
            with c1:
                st.write(f"📘 **{row['title']}** — {row['author']}")
            with c2:
                st.write(f"รหัสหนังสือ: {row['id']}")
            with c3:
                if st.button("ลบ", key=f"delete_book_{row['id']}"):
                    controller.remove_book(int(row["id"]))
                    st.success("ลบข้อมูลหนังสือเรียบร้อยแล้ว")
                    st.rerun()


    # -------- Books: Update --------
    st.subheader("✏️ แก้ไขข้อมูลหนังสือ")
    if books_df.empty:
        st.info("ยังไม่มีข้อมูลให้แก้ไข")
    else:
        search_title = st.text_input("ค้นหาชื่อหนังสือที่ต้องการแก้ไข", key="search_title")


        if search_title.strip():
            filtered_df = books_df[books_df["title"].str.contains(search_title.strip(), case=False)]
        else:
            filtered_df = books_df


        if filtered_df.empty:
            st.warning("ไม่พบหนังสือตามคำค้นหา")
        else:
            book_options = [f"{row['id']} - {row['title']}" for _, row in filtered_df.iterrows()]
            selected_book = st.selectbox("เลือกหนังสือที่จะแก้ไข", book_options, key="selected_book")


            book_id = int(selected_book.split(" - ")[0])
            selected_row = books_df[books_df["id"] == book_id].iloc[0]


            with st.form("edit_book_form"):
                new_title = st.text_input("ชื่อหนังสือ", value=selected_row["title"])
                new_author = st.text_input("ผู้แต่ง", value=selected_row["author"])
                save_update = st.form_submit_button("บันทึกการแก้ไข")


            if save_update:
                ok, msgs = controller.edit_book(book_id, new_title, new_author)
                if not ok:
                    for m in msgs:
                        st.error(m)
                else:
                    for m in msgs:
                        st.success(m)
                    st.rerun()






# app.py
import streamlit as st


from pages import book_page
from pages import member_page
from pages import borrow_page


# =========================
# View helpers (reset form)
# =========================


# ซ่อนเมนูอัตโนมัติ (app/book page/...)
# ✅ ซ่อน Multi-page auto nav (Streamlit sidebar pages list) + fallback หลาย selector
st.markdown("""
<style>
/* 1) ตัวหลัก: Sidebar navigation ของ multipage */
section[data-testid="stSidebarNav"] {display: none !important;}


/* 2) fallback: เผื่อ DOM เปลี่ยนชื่อ/โครง */
div[data-testid="stSidebarNav"] {display: none !important;}
nav[data-testid="stSidebarNav"] {display: none !important;}


/* 3) fallback เพิ่มเติม: ซ่อนหัวข้อ Pages / รายการหน้า (บางเวอร์ชัน) */
div[data-testid="stSidebarNavItems"] {display: none !important;}
div[data-testid="stSidebarNavSeparator"] {display: none !important;}


/* 4) fallback สุดท้าย: ถ้า Streamlit render เป็น <ul>/<li> ใน sidebar */
aside ul:has(a[href*="?page="]) {display: none !important;}
aside ul:has(a[href*="/book_page"]) {display: none !important;}
aside ul:has(a[href*="/member_page"]) {display: none !important;}
aside ul:has(a[href*="/borrow_page"]) {display: none !important;}
</style>
""", unsafe_allow_html=True)
# =========================
# UI
# =========================
st.set_page_config(page_title="ระบบยืม-คืนหนังสือ", page_icon="📚")
st.title("📚 ระบบยืม-คืนหนังสือ (Streamlit + SQLite)")
st.write("ตัวอย่าง Web App เชื่อมฐานข้อมูล (ปรับโครงสร้างแบบ MVC เชิงแนวคิด)")


# menu = st.sidebar.radio("เมนู", ["📚 หนังสือ", "👤 สมาชิก", "🔄 ยืม-คืน"])
# if menu == "📚 หนังสือ":
#     book_page.render_book()
# elif menu == "👤 สมาชิก":
#     member_page.render_member()
# else:
#     borrow_page.render_borrow()


# ---------- เมนูแบบคลิกแถบ ----------
if "page" not in st.session_state:
    st.session_state.page = "books"


# --- เมนู ---
# ===== Sidebar Menu Title (Centered & Styled) =====
st.sidebar.markdown("""
<style>
.menu-title {
    text-align: center;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-top: 10px;
    margin-bottom: 20px;
}
</style>


<div class="menu-title">
    เมนู
</div>
""", unsafe_allow_html=True)


def nav_button(label, key, icon=""):
    active = (st.session_state.page == key)
    btn = st.sidebar.button(f"{icon} {label}", use_container_width=True, key=f"btn_{key}")
    if btn:
        st.session_state.page = key
        st.rerun()
    # ทำไฮไลต์แบบง่าย (ตัวหนา/ตัวชี้)
    # if active:
    #     st.sidebar.markdown(f"✅ **{label}**")


nav_button("หนังสือ", "books", "📚")
nav_button("สมาชิก", "members", "👤")
nav_button("ยืม-คืน", "borrows", "🔄")



