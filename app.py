import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components
from difflib import SequenceMatcher

# 1. إعدادات الصفحة (يجب أن تكون أول أمر)
st.set_page_config(page_title="PRO DATA ANALYZER", page_icon="💎", layout="wide")

# 2. تطبيق التنسيقات (CSS) - تم وضعها داخل دالة لمنع ظهورها كنص
def apply_custom_design():
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
        
        /* ضبط الاتجاه للعربية */
        .stApp {
            direction: rtl;
            text-align: right;
            background: radial-gradient(circle at center, #111827, #030712) !important;
            font-family: 'Cairo', sans-serif !important;
        }

        /* الحاوية الزجاجية */
        .glass-container {
            background: rgba(31, 41, 55, 0.4);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 28px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        }

        /* تنسيق الأزرار الأربعة */
        div[data-testid="column"]:nth-of-type(1) button { background: #6366f1 !important; }
        div[data-testid="column"]:nth-of-type(2) button { background: #ef4444 !important; }
        div[data-testid="column"]:nth-of-type(3) button { background: #f59e0b !important; color: #111827 !important; }
        div[data-testid="column"]:nth-of-type(4) button { background: #3b82f6 !important; }

        .stButton>button {
            border-radius: 16px !important;
            height: 65px !important;
            font-weight: 700 !important;
            width: 100%;
            border: none !important;
            transition: 0.3s;
            color: white !important;
        }
        
        .stButton>button:hover { transform: translateY(-3px); filter: brightness(1.2); }

        /* لوحة الإحصائيات */
        .stats-card {
            background: rgba(17, 24, 39, 0.8);
            border-right: 5px solid #6366f1;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
            border: 1px solid rgba(255,255,255,0.05);
        }

        h1, h2, h3, p, label { color: #f8fafc !important; }
        </style>
    """, unsafe_allow_html=True)

apply_custom_design()

# 3. منطق التراجع والبيانات
if 'df' not in st.session_state: st.session_state.df = None
if 'history' not in st.session_state: st.session_state.history = []

def record():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 10: st.session_state.history.pop(0)

# --- واجهة المستخدم ---

st.markdown('<div class="glass-container">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;'><i class='fas fa-gem'></i> المحلل الذكي الفخم</h1>", unsafe_allow_html=True)

file = st.file_uploader("ارفع ملف الإكسل هنا", type=["xlsx", "csv"])

if file:
    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(file) if not file.name.endswith('.csv') else pd.read_csv(file)

    df = st.session_state.df

    # أزرار علوية
    c_top1, c_top2 = st.columns(2)
    with c_top1:
        if st.button("↩️ تراجع عن الخطوة"):
            if st.session_state.history:
                st.session_state.df = st.session_state.history.pop()
                st.rerun()
    with c_top2:
        out = io.BytesIO()
        df.to_excel(out, index=False)
        st.download_button("📥 تحميل النتائج", data=out.getvalue(), file_name="output.xlsx")

    # الأزرار الملونة (الحاوية الموحدة)
    st.write("---")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.popover("🔄 استبدال"):
            v1 = st.text_input("القيمة الحالية")
            v2 = st.text_input("القيمة الجديدة")
            if st.button("تغيير الآن"):
                record(); st.session_state.df.replace(v1, v2, inplace=True); st.rerun()
    with col2:
        with st.popover("🗑️ حذف أعمدة"):
            d = st.multiselect("اختر:", df.columns)
            if st.button("حذف"):
                record(); st.session_state.df.drop(columns=d, inplace=True); st.rerun()
    with col3:
        with st.popover("🔍 تحليل"):
            st.info("اختر العمود للتحليل الإحصائي بالأسفل")
            target_analyze = st.selectbox("العمود:", df.columns)
    with col4:
        with st.popover("📑 تكرارات"):
            st.write(f"المكرر: {df.duplicated().sum()}")
            if st.button("تصفية"):
                record(); st.session_state.df.drop_duplicates(inplace=True); st.rerun()

    # لوحة الفلترة والتحليل
    st.markdown('<div class="stats-card">', unsafe_allow_html=True)
    st.subheader("🛠️ الفلترة والتحليل الذكي")
    
    f1, f2 = st.columns([2, 1])
    with f1:
        search = st.text_input("🔎 ابحث عن أحرف معينة لتصفية الجدول:")
    with f2:
        top_analyze = st.selectbox("📊 الأكثر تكراراً في:", df.columns, key="stat_col")

    # تطبيق الفلترة
    final_df = df.copy()
    if search:
        final_df = final_df[final_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

    # عرض الإحصائيات
    if top_analyze:
        counts = final_df[top_analyze].value_counts().reset_index()
        counts.columns = ['القيمة', 'التكرار']
        st.write(f"إحصائيات {top_analyze}:")
        st.dataframe(counts.head(5), use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # عرض الجدول
    st.markdown("### 📋 معاينة البيانات")
    st.dataframe(final_df, use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)

# تحسين تفاعل الأزرار
components.html("""
<script>
    const btns = window.parent.document.querySelectorAll('button');
    btns.forEach(btn => {
        btn.addEventListener('mousedown', () => btn.style.transform = 'scale(0.96)');
        btn.addEventListener('mouseup', () => btn.style.transform = 'scale(1)');
    });
</script>
""", height=0)
