import streamlit as st
import pandas as pd
import io
from difflib import SequenceMatcher

# 1. إعدادات الصفحة والوضع الداكن/الفاتح
st.set_page_config(page_title="Excel Advanced Processor", page_icon="📊", layout="wide")

if 'theme' not in st.session_state: st.session_state.theme = 'light'
if 'df' not in st.session_state: st.session_state.df = None
if 'history' not in st.session_state: st.session_state.history = []

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# ألوان الواجهة
bg = "#ffffff" if st.session_state.theme == 'light' else "#0e1117"
txt = "#2c3e50" if st.session_state.theme == 'light' else "#E0E0E0"
card = "#f8f9fa" if st.session_state.theme == 'light' else "#1d2129"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    .stApp {{ background-color: {bg} !important; color: {txt} !important; font-family: 'Cairo', sans-serif; }}
    .main-header {{ background: {card}; padding: 20px; border-radius: 20px; text-align: center; border: 1px solid #e0e0e0; }}
    
    /* ألوان الأزرار حسب الصورة */
    div[data-testid="column"]:nth-of-type(1) button {{ background: #6c5ce7 !important; color: white !important; }}
    div[data-testid="column"]:nth-of-type(2) button {{ background: #ff7675 !important; color: white !important; }}
    div[data-testid="column"]:nth-of-type(3) button {{ background: #fdcb6e !important; color: white !important; }}
    div[data-testid="column"]:nth-of-type(4) button {{ background: #74b9ff !important; color: white !important; }}
    .stButton>button {{ border-radius: 12px !important; font-weight: 700 !important; height: 55px !important; width: 100%; border: none !important; }}
    .export-btn button {{ background: #00b894 !important; color: white !important; }}
    </style>
    """, unsafe_allow_html=True)

def save_step():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 15: st.session_state.history.pop(0)

# --- الواجهة ---
c_t1, c_t2 = st.columns([8, 2])
with c_t2:
    if st.button("☀️" if st.session_state.theme == 'dark' else "🌙"):
        toggle_theme()
        st.rerun()

st.markdown('<div class="main-header"><h1>📊 محلل البيانات التفاعلي</h1></div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["xlsx", "csv"])

if uploaded_file:
    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)
        save_step()

    df = st.session_state.df

    # لوحة التحكم
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    # 1. زر الاستبدال
    with col1:
        with st.popover("🔄 استبدال"):
            v1 = st.text_input("القيمة القديمة")
            v2 = st.text_input("القيمة الجديدة")
            if st.button("تحديث"):
                save_step(); st.session_state.df.replace(v1, v2, inplace=True); st.rerun()

    # 2. زر الحذف (مدمج مع تحديد الجدول)
    with col2:
        st.button("🗑️ حذف المحدد (استخدم الجدول بالأسفل)")

    # 3. النصوص المتشابهة
    with col3:
        with st.popover("🔍 نصوص مشابهة"):
            target = st.selectbox("العمود:", df.columns)
            if st.button("فحص"):
                st.session_state.show_similar = target

    # 4. المتكررات
    with col4:
        with st.popover("📑 المتكررات"):
            st.write(df.duplicated().sum(), "صفوف متكررة بالكامل")
            if st.button("حذف التكرار"):
                save_step(); st.session_state.df.drop_duplicates(inplace=True); st.rerun()

    st.markdown('<div class="export-btn">', unsafe_allow_html=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📥 تصدير الملف", data=output.getvalue(), file_name="Edited.xlsx", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # --- الجزء التفاعلي الرئيسي ---
    st.markdown("### 🖱️ الجدول التفاعلي")
    st.info("طريقة الحذف: اضغط على الأعمدة التي تريد حذفها من الجدول أدناه، ثم اضغط زر الحذف الذي سيظهر.")

    # عرض الجدول مع خاصية اختيار الأعمدة
    selection = st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi_column" # هذا هو الأمر الذي يحتاج إصدار حديث
    )

    # التحقق من الأعمدة المختارة
    selected_cols_indices = selection.selection.columns
    if selected_cols_indices:
        selected_names = [df.columns[i] for i in selected_cols_indices]
        st.error(f"تم تحديد: {', '.join(selected_names)}")
        if st.button("🔥 احذف الأعمدة المختارة الآن"):
            save_step()
            st.session_state.df.drop(columns=selected_names, inplace=True)
            st.rerun()

    st.markdown(f"**الإحصائيات:** {df.shape[0]} صف | {df.shape[1]} عمود")
