import streamlit as st
import model
from datetime import date
import pandas as pd
import plotly.express as px
import io

# ===== PDF (ภาษาไทย) =====
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def render_report():
    st.subheader("📊 รายงานสรุประบบยืม-คืนหนังสือ")

    # =========================
    # 1) กราฟวงกลม : สถานะหนังสือ
    # =========================
    st.markdown("### 1) สัดส่วนหนังสือตามสถานะ")

    status_df = model.get_book_status_summary()

    if status_df.empty:
        st.info("ไม่มีข้อมูลหนังสือ")
    else:
        fig = px.pie(
            status_df,
            names="สถานะหนังสือ",
            values="จำนวน",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(status_df, use_container_width=True)

    st.divider()

    # =========================
    # 2) กราฟแท่ง : จำนวนการยืมรายเดือน
    # =========================
    st.markdown("### 2) จำนวนการยืมรายเดือน")

    col1, col2 = st.columns(2)

    with col1:
        month_start = st.date_input("วันที่เริ่มต้น", date(2025, 6, 1))
    with col2:
        month_end = st.date_input("วันที่สิ้นสุด", date.today())

    if month_start > month_end:
        st.warning("วันที่เริ่มต้นต้องไม่มากกว่าวันที่สิ้นสุด")
        return

    monthly_df = model.get_borrow_summary_by_month(
        month_start.isoformat(),
        month_end.isoformat()
    )

    if monthly_df.empty:
        st.info("ไม่พบข้อมูลการยืม")
    else:
        st.bar_chart(monthly_df.set_index("เดือน")["จำนวนการยืม"])
        st.dataframe(monthly_df, use_container_width=True)

    st.divider()

    # =========================
    # 3) รายการผู้ยืม–คืน
    # =========================
    st.markdown("### 3) รายการผู้ยืม–คืนทั้งหมด")

    col1, col2, col3 = st.columns(3)

    with col1:
        report_start = st.date_input("วันที่เริ่มต้น (รายงาน)", date(2025, 6, 1))
    with col2:
        report_end = st.date_input("วันที่สิ้นสุด (รายงาน)", date.today())
    with col3:
        status_label = st.selectbox(
            "สถานะ",
            ["ทั้งหมด", "ยังไม่คืน", "คืนแล้ว"]
        )

    if report_start > report_end:
        st.warning("วันที่เริ่มต้นต้องไม่มากกว่าวันที่สิ้นสุด")
        return

    status_map = {
        "ทั้งหมด": "all",
        "ยังไม่คืน": "borrowed",
        "คืนแล้ว": "returned"
    }

    report_df = model.get_borrow_report(
        report_start.isoformat(),
        report_end.isoformat(),
        status_map[status_label]
    )

    if report_df.empty:
        st.info("ไม่พบข้อมูลตามเงื่อนไข")
        return

    st.dataframe(report_df, use_container_width=True)

    st.divider()

    # =========================
    # 4) ส่งออกรายงาน
    # =========================
    st.markdown("### 4) ส่งออกรายงาน")

    # ---------- CSV ----------
    csv_buffer = io.StringIO()
    report_df.to_csv(csv_buffer, index=False)

    st.download_button(
        "⬇️ ดาวน์โหลด CSV",
        csv_buffer.getvalue(),
        "borrow_return_report.csv",
        "text/csv"
    )

    # ---------- Excel ----------
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        report_df.to_excel(writer, index=False, sheet_name="BorrowReport")

    st.download_button(
        "⬇️ ดาวน์โหลด Excel",
        excel_buffer.getvalue(),
        "borrow_return_report.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # ---------- PDF (ภาษาไทย) ----------
    pdfmetrics.registerFont(
        TTFont("THSarabun", "fonts/THSarabunNew.ttf")
    )

    pdf_buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ThaiTitle",
            fontName="THSarabun",
            fontSize=18,
            leading=22,
            alignment=1
        )
    )
    styles.add(
        ParagraphStyle(
            name="ThaiNormal",
            fontName="THSarabun",
            fontSize=14,
            leading=18
        )
    )

    elements = []

    elements.append(
        Paragraph("รายงานผู้ยืม–คืนหนังสือ", styles["ThaiTitle"])
    )
    elements.append(
        Paragraph(
            f"ช่วงวันที่ {report_start} ถึง {report_end}",
            styles["ThaiNormal"]
        )
    )
    elements.append(Paragraph("<br/>", styles["ThaiNormal"]))

    table_data = [list(report_df.columns)] + report_df.values.tolist()

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, -1), "THSarabun"),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(table)
    doc.build(elements)

    st.download_button(
        "⬇️ ดาวน์โหลด PDF (ภาษาไทย)",
        pdf_buffer.getvalue(),
        "borrow_return_report.pdf",
        "application/pdf"
    )
