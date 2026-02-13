import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components
from collections import Counter

# 1. إعدادات الصفحة
st.set_page_config(page_title="المحلل الاحترافي", page_icon="💎", layout="wide")

# 2. حقن CSS والأيقونات
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif !important;
        background-color: #030712 !important;
    }

    /* الحاوية الزجاجية الكبرى */
    .main-glass-box {
        background: rgba(31, 41, 55, 0.4);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 28px;
        padding: 30px;
        margin-bottom: 25px;
    }

    /* حاوية الأزرار الموحدة */
    [data-testid="stVerticalBlock"] > div:has(div.button-unit) {
        background: rgba(15, 23, 42, 0.6) !important;
        padding: 25px !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }

    /* ألوان الأزرار */
    div[data-testid="column"]:nth-of-type(1) button { background: #6366f1 !important; }
    div[data-testid="column"]:nth-of-type(2) button { background: #ef4444 !important; }
    div[data-testid="column"]:nth-of-type(3) button { background: #f59e0b !important; color: #111827 !important; }
    div[data-testid="column"]:nth-of-type(4) button { background: #3b82f6 !important; }

    .stButton>button {
        border-radius: 14px !important;
        height: 75px !important;
        font-weight: 700 !important;
        border: none !important;
        font-size: 1rem !important;
        transition: 0.3s;
    }

    /* لوحة الإحصائيات */
    .stats-card {
        background: rgba(17, 24, 39, 0.85);
        border-right: 5px solid #6366f1;
        padding: 25px;
        border-radius: 18px;
        margin: 20px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }

    h1, h2, h3, p, label { color: #f8fafc !important; }
    </style>
""", unsafe_allow_html=True)

# 3. إدارة البيانات
if 'df' not in st.session_state: st.session_state.df = None
if 'history' not in st.session_state: st.session_state.history = []

def save_state():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 10: st.session_state.history.pop(0)

# --- الواجهة ---

st.markdown('<div class="main-glass-box">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;'><i class='fas fa-cube'></i> المحلل الذكي</h1>", unsafe_allow_html=True)

file = st.file_uploader("", type=["xlsx", "csv"])

if file:
    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(file) if not file.name.endswith('.csv') else pd.read_csv(file)

    df = st.session_state.df

    # أدوات التحكم
    t1, t2 = st.columns(2)
    with t1:
        if st.button("تراجع عن آخر خطوة"):
            if st.session_state.history:
                st.session_state.df = st.session_state.history.pop()
                st.rerun()
    with t2:
        out = io.BytesIO()
        df.to_excel(out, index=False)
        st.download_button("تصدير النتائج", data=out.getvalue(), file_name="cleaned.xlsx")

    # الحاوية الموحدة للأزرار (باستخدام دالة container)
    with st.container():
        st.markdown('<div class="button-unit"></div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            with st.popover("استبدال"):
                old, new = st.text_input("الحالي"), st.text_input("الجديد")
                if st.button("تأكيد الاستبدال"):
                    save_state(); st.session_state.df.replace(old, new, inplace=True); st.rerun()
        with col2:
            with st.popover("حذف أعمدة"):
                d = st.multiselect("اختر:", df.columns)
                if st.button("تأكيد الحذف"):
                    save_state(); st.session_state.df.drop(columns=d, inplace=True); st.rerun()
        with col3:
            with st.popover("تحليل"):
                target = st.selectbox("العمود:", df.columns)
        with col4:
            with st.popover("تكرار"):
                st.write(f"المكرر: {df.duplicated().sum()}")
                if st.button("حذف المكررات"):
                    save_state(); st.session_state.df.drop_duplicates(inplace=True); st.rerun()

    # لوحة التحليل والفلترة
    st.markdown('<div class="stats-card">', unsafe_allow_html=True)
    st.markdown("<h3><i class='fas fa-magnifying-glass'></i> الفلترة والتحليل</h3>", unsafe_allow_html=True)
    
    f1, f2 = st.columns([2, 1])
    with f1:
        q = st.text_input("ابحث عن أحرف لتصفية الجدول:")
    with f2:
        a_col = st.selectbox("تحليل تكرار عمود:", df.columns)

    # معالجة الفلترة
    view_df = df.copy()
    if q:
        view_df = view_df[view_df.apply(lambda r: r.astype(str).str.contains(q, case=False).any(), axis=1)]

    # حساب التكرارات (دقيق 100%)
    if a_col:
        counts = view_df[a_col].value_counts().reset_index()
        counts.columns = ['القيمة', 'التكرار']
        st.dataframe(counts.head(10), use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # عرض الجدول
    st.markdown("### <i class='fas fa-list'></i> معاينة البيانات")
    st.dataframe(view_df, use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)
