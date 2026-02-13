import streamlit as st
import pandas as pd
import io
from difflib import SequenceMatcher
from collections import Counter

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="Data Intelligence Pro", page_icon="💎", layout="wide")

# 2. حقن المكتبات والتصميم (CSS & Font Awesome)
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: radial-gradient(circle at center, #111827, #030712) !important;
        font-family: 'Cairo', sans-serif;
        direction: rtl;
    }

    /* الحاوية الرئيسية الفخمة */
    .glass-container {
        background: rgba(31, 41, 55, 0.4);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 28px;
        padding: 40px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        margin-bottom: 25px;
    }

    /* تنسيق ألوان الأزرار (أيقونات + خلفية) */
    div[data-testid="column"]:nth-of-type(1) button { background: #6366f1 !important; box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3); }
    div[data-testid="column"]:nth-of-type(2) button { background: #ef4444 !important; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); }
    div[data-testid="column"]:nth-of-type(3) button { background: #f59e0b !important; color: #111827 !important; box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3); }
    div[data-testid="column"]:nth-of-type(4) button { background: #3b82f6 !important; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3); }

    .stButton>button {
        border-radius: 16px !important;
        height: 70px !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }

    .stButton>button:hover {
        transform: translateY(-4px) scale(1.02);
        filter: brightness(1.1);
    }

    /* لوحة التحليل (Statistics Card) */
    .stats-card {
        background: rgba(17, 24, 39, 0.7);
        border-right: 5px solid #6366f1;
        padding: 25px;
        border-radius: 18px;
        margin: 20px 0;
        border: 1px solid rgba(255,255,255,0.05);
    }

    /* العناوين */
    h1, h2, h3 { color: #f8fafc !important; text-align: center; }
    
    /* الجداول */
    .stDataFrame { border-radius: 15px !important; border: 1px solid rgba(255,255,255,0.1) !important; }
    
    /* إخفاء سهم الرفع الافتراضي لتجميل الواجهة */
    [data-testid="stFileUploadDropzone"] { border: 2px dashed rgba(99, 102, 241, 0.4) !important; border-radius: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. الدوال البرمجية (Undo & Similarity)
if 'df' not in st.session_state: st.session_state.df = None
if 'history' not in st.session_state: st.session_state.history = []

def record_action():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 20: st.session_state.history.pop(0)

def perform_undo():
    if st.session_state.history:
        st.session_state.df = st.session_state.history.pop()
        st.rerun()

# --- بناء الواجهة الفخمة ---

st.markdown('<div class="glass-container">', unsafe_allow_html=True)

# الهيدر الاحترافي
st.markdown("""
    <div style="margin-bottom: 40px;">
        <h1 style="font-size: 2.8rem; margin-bottom: 10px;">PRO DATA <span style="color:#6366f1">ANALYZER</span></h1>
        <p style="text-align:center; color:#94a3b8; font-size: 1.1rem;">المعالجة الذكية والتحليل الإحصائي لملفات الإكسل</p>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["xlsx", "csv"])

if uploaded_file:
    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)

    df = st.session_state.df

    # أزرار الإجراءات السريعة (تراجع وتصدير)
    act1, act2 = st.columns([1, 1])
    with act1:
        if st.button("↩️ Undo Last Action", use_container_width=True): perform_undo()
    with act2:
        output = io.BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📥 Export Cleaned Data", data=output.getvalue(), file_name="Pro_Data_Export.xlsx", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # حاوية الأزرار الأربعة الملونة
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        with st.popover("🔄 Replace Value"):
            o = st.text_input("Current Value")
            n = st.text_input("New Value")
            if st.button("Update"):
                record_action(); st.session_state.df.replace(o, n, inplace=True); st.rerun()
    with c2:
        with st.popover("🗑️ Remove Column"):
            to_del = st.multiselect("Select columns:", df.columns)
            if st.button("Confirm Removal"):
                record_action(); st.session_state.df.drop(columns=to_del, inplace=True); st.rerun()
    with c3:
        with st.popover("⚖️ Similarity Link"):
            target_col = st.selectbox("Column for similarity:", df.columns)
            threshold = st.slider("Precision %", 50, 95, 80) / 100
            st.info("سيتم فحص المسميات المتقاربة في هذا العمود")
    with c4:
        with st.popover("📑 Duplicate Logic"):
            dups = df.duplicated().sum()
            st.metric("Total Duplicates", dups)
            if st.button("Remove All Duplicates"):
                record_action(); st.session_state.df.drop_duplicates(inplace=True); st.rerun()

    # --- قسم الفلترة الإبداعي وتحليل التكرار ---
    st.markdown('<div class="stats-card">', unsafe_allow_html=True)
    st.markdown("<h3><i class='fas fa-chart-line' style='color:#6366f1'></i> الفلترة والتحليل الذكي للمحتوى</h3>", unsafe_allow_html=True)
    
    f1, f2 = st.columns([2, 1])
    with f1:
        search_q = st.text_input("🔎 ابحث عن أحرف أو كلمات معينة لتصفية الجدول:")
    with f2:
        analyze_col = st.selectbox("📊 عرض الأكثر تكراراً في عمود:", df.columns)

    # معالجة البيانات بناءً على الفلاتر
    filtered_df = df.copy()
    if search_q:
        filtered_df = filtered_df[filtered_df.apply(lambda r: r.astype(str).str.contains(search_q, case=False).any(), axis=1)]

    # إحصائيات التكرار
    if analyze_col:
        counts = filtered_df[analyze_col].value_counts().reset_index()
        counts.columns = ['القيمة', 'عدد التكرار']
        st.markdown(f"**أعلى القيم تكراراً في عمود ({analyze_col}):**")
        st.dataframe(counts.head(10), use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # عرض الجدول الرئيسي الفخم
    st.markdown("<h3><i class='fas fa-database' style='color:#3b82f6'></i> مستعرض البيانات التفاعلي</h3>", unsafe_allow_html=True)
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)

# 4. JavaScript لتحسين تجربة المستخدم
components.html("""
<script>
    const btns = window.parent.document.querySelectorAll('button');
    btns.forEach(btn => {
        btn.addEventListener('mousedown', () => btn.style.transform = 'scale(0.95)');
        btn.addEventListener('mouseup', () => btn.style.transform = 'scale(1)');
    });
</script>
""", height=0)
