import streamlit as st
import pandas as pd
import io
from difflib import SequenceMatcher

# 1. إعدادات الصفحة
st.set_page_config(page_title="Excel Advanced Processor", page_icon="📊", layout="wide")

# 2. إدارة وضع الألوان (Dark/Light)
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

def toggle_theme():
    st.session_state.theme = 'dark' if st.session_state.theme == 'light' else 'light'

# 3. تصميم CSS المتغير حسب الوضع
if st.session_state.theme == 'light':
    bg_color = "#ffffff"
    text_color = "#2c3e50"
    card_bg = "#f8f9fa"
    border_color = "#e0e0e0"
else:
    bg_color = "#0e1117"
    text_color = "#ffffff"
    card_bg = "#1d2129"
    border_color = "#3d444d"

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"], .main {{ 
        font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; 
        background-color: {bg_color} !important; color: {text_color} !important;
    }}
    
    .main-header {{
        background: {card_bg}; padding: 25px; border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center;
        margin-bottom: 25px; border: 1px solid {border_color};
    }}

    /* ألوان الأزرار حسب الصورة */
    div[data-testid="column"]:nth-of-type(1) .stButton>button {{ background: #6c5ce7 !important; color: white !important; }} 
    div[data-testid="column"]:nth-of-type(2) .stButton>button {{ background: #ff7675 !important; color: white !important; }} 
    div[data-testid="column"]:nth-of-type(3) .stButton>button {{ background: #fdcb6e !important; color: white !important; }} 
    div[data-testid="column"]:nth-of-type(4) .stButton>button {{ background: #74b9ff !important; color: white !important; }} 
    
    .stButton>button {{ border-radius: 12px !important; font-weight: 700 !important; height: 55px !important; border: none !important; }}
    .export-btn button {{ background: #00b894 !important; color: white !important; width: 100% !important; }}
    
    .data-card {{ background: {card_bg}; border: 1px solid {border_color}; padding: 15px; border-radius: 12px; margin-bottom: 10px; }}
    </style>
    """, unsafe_allow_html=True)

# 4. الدوال المنطقية
def are_similar(str1, str2, threshold=0.75):
    s1 = str(str1).strip().lower().replace("أ", "ا").replace("إ", "ا").replace("ة", "ه")
    s2 = str(str2).strip().lower().replace("أ", "ا").replace("إ", "ا").replace("ة", "ه")
    return SequenceMatcher(None, s1, s2).ratio() > threshold

if 'df' not in st.session_state: st.session_state.df = None
if 'history' not in st.session_state: st.session_state.history = []

def save_step():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 15: st.session_state.history.pop(0)

# --- الواجهة ---
col_mode1, col_mode2 = st.columns([8, 2])
with col_mode2:
    mode_label = "الوضع الفاتح ☀️" if st.session_state.theme == 'dark' else "الوضع الداكن 🌙"
    st.button(mode_label, on_click=toggle_theme)

st.markdown(f"""
    <div class="main-header">
        <h1 style='color: #6c5ce7;'>📊 محلل ملفات Excel المتقدم</h1>
        <p style='color: {text_color};'>أداة شاملة لقراءة وتحليل وتعديل ملفات Excel</p>
    </div>
    """, unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["xlsx", "csv"])

if uploaded_file:
    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)
        save_step()

    df = st.session_state.df
    rows, cols = df.shape

    # لوحة التحكم
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    with c1: replace_clicked = st.button("🔄 استبدال")
    with c2: delete_clicked = st.button("🗑️ حذف المحدد")
    with c3: similar_clicked = st.button("🔍 النصوص المتشابهة")
    with c4: dup_clicked = st.button("📑 المتكررات")

    st.markdown('<div class="export-btn">', unsafe_allow_html=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📥 تصدير الملف (Excel)", data=output.getvalue(), file_name="Edited_File.xlsx")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"<p style='text-align:center; color:{text_color};'>الملف: {uploaded_file.name} | الصفوف: {rows} | الأعمدة: {cols}</p>", unsafe_allow_html=True)

    # تفعيل الأدوات
    if delete_clicked:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        cols_to_del = st.multiselect("اختر الأعمدة لحذفها:", df.columns)
        if st.button("تأكيد الحذف"):
            save_step(); st.session_state.df.drop(columns=cols_to_del, inplace=True); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    if similar_clicked:
        target = st.selectbox("اختر العمود للفحص:", df.columns)
        unique_vals = df[target].dropna().unique().astype(str)
        for i, v1 in enumerate(unique_vals[:30]):
            group = [v1] + [v2 for v2 in unique_vals[i+1:i+15] if are_similar(v1, v2)]
            if len(group) > 1:
                st.markdown(f'<div class="data-card">⚠️ مشابه لـ {v1}: {", ".join(group)}</div>', unsafe_allow_html=True)
                new_v = st.text_input(f"توحيد {v1}:", value=v1, key=v1)
                if st.button(f"اعتماد التوحيد لـ {v1}"):
                    save_step(); st.session_state.df[target].replace(group, new_v, inplace=True); st.rerun()

    # الجدول التفاعلي (تم إصلاح الخطأ)
    st.markdown(f"### 📋 معاينة البيانات ({'الوضع الداكن' if st.session_state.theme == 'dark' else 'الوضع الفاتح'})")
    st.dataframe(df, use_container_width=True, hide_index=True)
