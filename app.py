import streamlit as st
import pandas as pd
import io
from difflib import SequenceMatcher
from collections import Counter

# 1. إعدادات الصفحة
st.set_page_config(page_title="Data Intelligence Pro", page_icon="📊", layout="wide")

# 2. تضمين مكتبات الأيقونات (Font Awesome) وتنسيق CSS
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: radial-gradient(circle at center, #111827, #030712) !important;
        font-family: 'Cairo', sans-serif;
    }

    /* الحاوية الرئيسية الفخمة */
    .glass-container {
        background: rgba(31, 41, 55, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        padding: 35px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
    }

    /* أيقونات الأزرار */
    .icon-label { margin-left: 8px; font-size: 1.2rem; }

    /* تنسيق ألوان الأزرار (أيقونات + خلفية) */
    div[data-testid="column"]:nth-of-type(1) button { background: #6366f1 !important; }
    div[data-testid="column"]:nth-of-type(2) button { background: #ef4444 !important; }
    div[data-testid="column"]:nth-of-type(3) button { background: #f59e0b !important; color: #111827 !important; }
    div[data-testid="column"]:nth-of-type(4) button { background: #3b82f6 !important; }
    
    .stButton>button {
        border-radius: 14px !important;
        height: 65px !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex; align-items: center; justify-content: center;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 10px 20px rgba(0,0,0,0.3) !important;
    }

    /* لوحة التحليل (Statistics Card) */
    .stats-card {
        background: rgba(17, 24, 39, 0.8);
        border-right: 4px solid #3b82f6;
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
    }

    /* تعديل نصوص العناوين */
    h1, h2, h3 { color: #f8fafc !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. المنطق البرمجي (Undo System)
if 'df' not in st.session_state: st.session_state.df = None
if 'history' not in st.session_state: st.session_state.history = []

def save_state():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 20: st.session_state.history.pop(0)

# 4. الواجهة البرمجية
st.markdown('<div class="glass-container">', unsafe_allow_html=True)

# الهيدر مع أيقونة
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <i class="fas fa-microchip" style="font-size: 3rem; color: #6366f1; margin-bottom: 15px;"></i>
        <h1>نظام معالجة البيانات الذكي</h1>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["xlsx", "csv"])

if uploaded_file:
    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)
    
    df = st.session_state.df

    # أدوات التحكم العلوية
    c_top1, c_top2 = st.columns([1, 1])
    with c_top1:
        if st.button("↩️ Undo Action"):
            if st.session_state.history:
                st.session_state.df = st.session_state.history.pop()
                st.rerun()
    with c_top2:
        output = io.BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📥 Download Result", data=output.getvalue(), file_name="Pro_Export.xlsx")

    st.divider()

    # حاوية الأزرار الأربعة بالأيقونات
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        with st.popover("🔄 Replace"):
            old = st.text_input("Old Value")
            new = st.text_input("New Value")
            if st.button("Apply Change"):
                save_state(); st.session_state.df.replace(old, new, inplace=True); st.rerun()
    
    with col2:
        with st.popover("🗑️ Remove"):
            to_del = st.multiselect("Select Columns", df.columns)
            if st.button("Confirm Delete"):
                save_state(); st.session_state.df.drop(columns=to_del, inplace=True); st.rerun()

    with col3:
        with st.popover("⚖️ Similarity"):
            sim_col = st.selectbox("Column for Similarity Analysis", df.columns)
            threshold = st.slider("Similarity Threshold %", 50, 95, 80) / 100
    
    with col4:
        with st.popover("👯 Duplicates"):
            st.write(f"Identical Rows: {df.duplicated().sum()}")
            if st.button("Clear Duplicates"):
                save_state(); st.session_state.df.drop_duplicates(inplace=True); st.rerun()

    # --- قسم التحليل الفائق (الفلترة والتكرار) ---
    st.markdown('<div class="stats-card">', unsafe_allow_html=True)
    st.markdown("<h3><i class='fas fa-filter'></i> الفلترة والتحليل الإحصائي</h3>", unsafe_allow_html=True)
    
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        search_term = st.text_input("Search by characters (Filter Row)")
    with f_col2:
        target_analyze = st.selectbox("Analyze Frequency & Similarity in:", df.columns)

    # تطبيق الفلترة
    filtered_df = df.copy()
    if search_term:
        filtered_df = filtered_df[filtered_df.apply(lambda r: r.astype(str).str.contains(search_term, case=False).any(), axis=1)]

    # حساب التكرارات والتشابه
    if target_analyze:
        counts = filtered_df[target_analyze].value_counts().reset_index()
        counts.columns = ['Value', 'Occurrence']
        
        st.write(f"**Top Repeated Values in '{target_analyze}':**")
        st.dataframe(counts.head(10), use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # عرض الجدول الرئيسي الفخم
    st.markdown("<h3><i class='fas fa-table'></i> معاينة البيانات النشطة</h3>", unsafe_allow_html=True)
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)
