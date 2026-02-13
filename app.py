import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components
from collections import Counter

# 1. إعدادات الصفحة
st.set_page_config(page_title="PRO DATA ANALYZER", page_icon="💎", layout="wide")

# 2. حقن المكتبات والتصميم (CSS الموحد)
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif !important;
        background: #030712 !important;
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
    .buttons-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 15px;
        background: rgba(15, 23, 42, 0.6);
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 25px;
    }

    /* تنسيق ألوان الأزرار الأربعة */
    div[data-testid="column"]:nth-of-type(1) button { background: #6366f1 !important; }
    div[data-testid="column"]:nth-of-type(2) button { background: #ef4444 !important; }
    div[data-testid="column"]:nth-of-type(3) button { background: #f59e0b !important; color: #111827 !important; }
    div[data-testid="column"]:nth-of-type(4) button { background: #3b82f6 !important; }

    .stButton>button {
        border-radius: 14px !important;
        height: 75px !important;
        font-weight: 700 !important;
        width: 100%;
        border: none !important;
        font-size: 1.1rem !important;
        color: white !important;
        transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    .stButton>button:hover { transform: scale(1.05); filter: brightness(1.2); }

    /* لوحة الإحصائيات الفخمة */
    .stats-card {
        background: rgba(17, 24, 39, 0.85);
        border-right: 5px solid #6366f1;
        padding: 25px;
        border-radius: 18px;
        margin: 20px 0;
        border: 1px solid rgba(255,255,255,0.1);
    }

    h1, h2, h3, p, label { color: #f8fafc !important; }
    .stDataFrame { border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 15px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. إدارة البيانات
if 'df' not in st.session_state: st.session_state.df = None
if 'history' not in st.session_state: st.session_state.history = []

def record():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 15: st.session_state.history.pop(0)

# --- الواجهة البرمجية ---

st.markdown('<div class="main-glass-box">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center;'><i class='fas fa-shield-halved' style='color:#6366f1'></i> المحلل الذكي الاحترافي</h1>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("", type=["xlsx", "csv"])

if uploaded_file:
    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)

    df = st.session_state.df

    # أدوات التصدير والتراجع في الأعلى
    c_tools1, c_tools2 = st.columns([1, 1])
    with c_tools1:
        if st.button("↩️ تراجع عن التعديل"):
            if st.session_state.history:
                st.session_state.df = st.session_state.history.pop()
                st.rerun()
    with c_tools2:
        output = io.BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📥 تصدير الملف المحسن", data=output.getvalue(), file_name="Pro_Data.xlsx", use_container_width=True)

    # حاوية الأزرار الموحدة (التصميم المطلوب)
    st.markdown('<div class="buttons-grid">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        with st.popover("🔄 استبدال"):
            v_old = st.text_input("القيمة القديمة")
            v_new = st.text_input("القيمة الجديدة")
            if st.button("تحديث البيانات"):
                record(); st.session_state.df.replace(v_old, v_new, inplace=True); st.rerun()
    
    with col2:
        with st.popover("🗑️ حذف أعمدة"):
            to_drop = st.multiselect("اختر الأعمدة:", df.columns)
            if st.button("تأكيد الحذف"):
                record(); st.session_state.df.drop(columns=to_drop, inplace=True); st.rerun()

    with col3:
        with st.popover("🔍 تحليل التشابه"):
            target_col = st.selectbox("اختر العمود للفحص:", df.columns)
            st.info("سيتم عرض تكرارات هذا العمود في لوحة التحليل بالأسفل")

    with col4:
        with st.popover("📑 تكرار الصفوف"):
            st.write(f"الصفوف المتكررة بالكامل: {df.duplicated().sum()}")
            if st.button("إزالة التكرار"):
                record(); st.session_state.df.drop_duplicates(inplace=True); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # --- لوحة الفلترة والتحليل الفخم (مركزية) ---
    st.markdown('<div class="stats-card">', unsafe_allow_html=True)
    st.markdown("<h3><i class='fas fa-chart-bar' style='color:#6366f1'></i> مركز الفلترة والتحليل الذكي</h3>", unsafe_allow_html=True)
    
    f1, f2 = st.columns([2, 1])
    with f1:
        search_query = st.text_input("🔎 ابحث عن أحرف معينة لتصفية الجدول بالكامل:")
    with f2:
        analyze_col = st.selectbox("📊 عرض الأكثر تكراراً في عمود:", df.columns, key="main_analyze")

    # تطبيق الفلترة الحية
    final_df = df.copy()
    if search_query:
        final_df = final_df[final_df.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)]

    # حساب التكرار الصحيح
    if analyze_col:
        # حساب التكرارات بدقة 100%
        val_counts = final_df[analyze_target if 'analyze_target' in locals() else analyze_col].value_counts().reset_index()
        val_counts.columns = ['القيمة', 'عدد التكرارات']
        st.markdown(f"**نتائج تحليل العمود: {analyze_col}**")
        st.dataframe(val_counts.head(10), use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # عرض الجدول الرئيسي
    st.markdown("### <i class='fas fa-table'></i> استعراض البيانات")
    st.dataframe(final_df, use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)

# تحسين تفاعل الأزرار بواسطة JS
components.html("""
<script>
    const buttons = window.parent.document.querySelectorAll('button');
    buttons.forEach(btn => {
        btn.addEventListener('mousedown', () => btn.style.transform = 'scale(0.96)');
        btn.addEventListener('mouseup', () => btn.style.transform = 'scale(1)');
    });
</script>
""", height=0)
