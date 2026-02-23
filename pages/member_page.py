import streamlit as st
import model
import controller

# =========================
# View helpers (reset form)
# =========================
def reset_member_form():
    st.session_state["member_code"] = ""
    st.session_state["member_name"] = ""
    st.session_state["gender"] = "ไม่ระบุ"
    st.session_state["member_email"] = ""
    st.session_state["member_phone"] = ""
    st.session_state["is_active"] = True

# =========================
# UI Render Function
# =========================
def render_member():
    st.header("👤 จัดการข้อมูลสมาชิก")

    # ====== Logic: Flag Reset Member Form ======
    if st.session_state.get("_reset_member_next_run", False):
        reset_member_form()
        st.session_state["_reset_member_next_run"] = False

    # -------- 1. Members: Create --------
    st.subheader("สมัครสมาชิกใหม่")
    with st.form("member_form"):
        col_a, col_b = st.columns(2)

        with col_a:
            member_code = st.text_input("รหัสสมาชิก (เช่น M001)", max_chars=10, key="member_code")
            member_name = st.text_input("ชื่อ - สกุล", key="member_name")
            gender = st.selectbox("เพศ", ["ไม่ระบุ", "หญิง", "ชาย", "อื่น ๆ"], key="gender")

        with col_b:
            email = st.text_input("อีเมล", key="member_email")
            phone = st.text_input("เบอร์โทรศัพท์", key="member_phone")
            is_active = st.checkbox("ยังใช้งานอยู่", value=True, key="is_active")

        btn_col1, btn_col2 = st.columns([1, 3])
        with btn_col1:
            submitted = st.form_submit_button("บันทึกข้อมูลสมาชิก")
        with btn_col2:
            st.form_submit_button("ล้างฟอร์ม", on_click=reset_member_form)

    if submitted:
        ok, msgs = controller.create_member(member_code, member_name, gender, email, phone, is_active)
        if not ok:
            for m in msgs:
                st.error("⚠ " + m)
        else:
            for m in msgs:
                st.success(m)
            # ตั้งค่าให้ล้างฟอร์มในการรันครั้งหน้าและ Refresh หน้าจอ
            st.session_state["_reset_member_next_run"] = True
            st.rerun()

    st.divider()

    # -------- 2. Members: Read + Delete --------
    st.subheader("📋 รายชื่อสมาชิกทั้งหมด")
    members_df = model.get_all_members()
    if members_df.empty:
        st.info("ยังไม่มีข้อมูลสมาชิกในระบบ")
    else:
        # แสดงตารางภาพรวม
        st.dataframe(members_df, use_container_width=True)
        
        st.write("---")
        st.caption("จัดการรายบุคคล")
        for _, row in members_df.iterrows():
            c1, c2, c3, c4 = st.columns([3, 3, 2, 1])
            with c1:
                st.write(f"**{row['รหัสสมาชิก']}** : {row['ชื่อสกุล']}")
            with c2:
                st.write(row["อีเมล"] if row["อีเมล"] else "-")
            with c3:
                st.write(f"สถานะ: {row['สถานะ']}")
            with c4:
                if st.button("ลบ", key=f"delete_member_{row['id']}"):
                    controller.remove_member(int(row["id"]))
                    st.success(f"ลบสมาชิก {row['ชื่อสกุล']} เรียบร้อยแล้ว")
                    st.rerun()

    st.divider()

    # -------- 3. Members: Update --------
    st.subheader("✏️ แก้ไขข้อมูลสมาชิก")
    if members_df.empty:
        st.info("ยังไม่มีข้อมูลให้แก้ไข")
    else:
        member_options = [
            f"{row['id']} - {row['รหัสสมาชิก']} : {row['ชื่อสกุล']}"
            for _, row in members_df.iterrows()
        ]
        selected = st.selectbox("เลือกสมาชิกที่จะแก้ไข", member_options, key="selected_member_update")
        selected_id = int(selected.split(" - ")[0])
        selected_row = members_df[members_df["id"] == selected_id].iloc[0]

        with st.form("edit_member_form"):
            col1, col2 = st.columns(2)

            with col1:
                edit_member_code = st.text_input("รหัสสมาชิก", value=selected_row["รหัสสมาชิก"])
                edit_name = st.text_input("ชื่อ - สกุล", value=selected_row["ชื่อสกุล"])
                current_gender = selected_row["เพศ"] if selected_row["เพศ"] else "ไม่ระบุ"
                gender_list = ["ไม่ระบุ", "หญิง", "ชาย", "อื่น ๆ"]
                edit_gender = st.selectbox(
                    "เพศ",
                    gender_list,
                    index=gender_list.index(current_gender) if current_gender in gender_list else 0
                )

            with col2:
                edit_email = st.text_input("อีเมล", value=selected_row["อีเมล"] if selected_row["อีเมล"] else "")
                edit_phone = st.text_input("เบอร์โทรศัพท์", value=selected_row["เบอร์โทร"] if selected_row["เบอร์โทร"] else "")
                edit_is_active = st.checkbox("ยังใช้งานอยู่", value=(selected_row["สถานะ"] == "ใช้งาน"))

            update_submitted = st.form_submit_button("บันทึกการแก้ไข")

        if update_submitted:
            ok, msgs = controller.edit_member(
                member_id=selected_id,
                new_code=edit_member_code,
                new_name=edit_name,
                gender=edit_gender,
                email=edit_email,
                phone=edit_phone,
                is_active=edit_is_active,
                old_code=selected_row["รหัสสมาชิก"],
                old_email=selected_row["อีเมล"] or ""
            )
            if not ok:
                for m in msgs:
                    st.error("⚠ " + m)
            else:
                for m in msgs:
                    st.success(m)
                st.rerun()