import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components

# 1. إعدادات الصفحة
st.set_page_config(page_title="محلل ملفات Excel المتقدم", page_icon="📊", layout="wide")

# 2. حقن التصميم الموحد (CSS) من صورتك ومواصفاتك
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(180deg, #6e7df2 0%, #4b59c9 100%) !important;
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
    }

    .white-card {
        background: #ffffff;
        border-radius: 30px;
        padding: 30px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
    }

    .main-title { color: #5c6bc0; font-weight: 700; font-size: 2.2rem; margin-bottom: 5px; }
    .sub-title { color: #757575; font-size: 1.1rem; }

    /* تنسيق الأزرار الأربعة الملونة */
    div[data-testid="column"]:nth-of-type(1) button { background: #6f5cc3 !important; }
    div[data-testid="column"]:nth-of-type(2) button { background: #e5534b !important; }
    div[data-testid="column"]:nth-of-type(3) button { background: #f0ad4e !important; }
    div[data-testid="column"]:nth-of-type(4) button { background: #5086eb !important; }

    .stButton>button {
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        height: 70px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        width: 100%;
    }

    /* زر التصدير الأخضر الكبير */
    .export-btn button {
        background: #5cb885 !important;
        height: 60px !important;
    }

    .file-info { color: #616161; font-size: 1rem; margin-top: 15px; font-weight: 600; }

    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #5c6bc0 !important;
        border-radius: 20px !important;
        background: #f8f9ff !important;
    }
    
    label { color: #5c6bc0 !important; font-weight: 700 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. منطق إدارة البيانات
if 'df' not in st.session_state: st.session_state.df = None
if 'history' not in st.session_state: st.session_state.history = []

def record_change():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 10: st.session_state.history.pop(0)

# --- واجهة المستخدم ---

# الحاوية العلوية (العنوان)
st.markdown("""
    <div class="white-card">
        <h1 class="main-title"><i class="fas fa-file-excel"></i> محلل ملفات Excel المتقدم</h1>
        <p class="sub-title">أداة شاملة لقراءة وتحليل وتعديل ملفات Excel</p>
    </div>
""", unsafe_allow_html=True)

# حاوية الرفع والعمليات
st.markdown('<div class="white-card">', unsafe_allow_html=True)

if st.session_state.df is None:
    uploaded_file = st.file_uploader("", type=["xlsx", "xls", "csv"])
    if uploaded_file:
        st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)
        st.rerun()

if st.session_state.df is not None:
    df = st.session_state.df
    
    # شبكة الأزرار الأربعة (استبدال، حذف، متشابهة، مكررات)
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        with st.popover("🔄 استبدال"):
            old = st.text_input("القيمة القديمة")
            new = st.text_input("الجديدة")
            if st.button("تأكيد التغيير"):
                record_change(); st.session_state.df.replace(old, new, inplace=True); st.rerun()
    with row1_col2:
        with st.popover("🗑️ حذف المحدد"):
            cols_to_del = st.multiselect("اختر الأعمدة:", df.columns)
            if st.button("حذف الآن"):
                record_change(); st.session_state.df.drop(columns=cols_to_del, inplace=True); st.rerun()

    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        with st.popover("🔍 النصوص المتشابهة"):
            st.info("اختر العمود للفحص في قسم التحليل بالأسفل")
            analyze_col = st.selectbox("العمود المستهدف:", df.columns)
    with row2_col2:
        with st.popover("📑 المتكررات"):
            st.write(f"الصفوف المتكررة: {df.duplicated().sum()}")
            if st.button("تصفية المتكررات"):
                record_change(); st.session_state.df.drop_duplicates(inplace=True); st.rerun()

    # زر التصدير الأخضر
    st.markdown('<div class="export-btn">', unsafe_allow_html=True)
    out = io.BytesIO()
    df.to_excel(out, index=False)
    st.download_button("📥 تصدير", data=out.getvalue(), file_name="output.xlsx", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # معلومات الملف
    st.markdown(f'<div class="file-info">الصفوف: {len(df)} | الأعمدة: {len(df.columns)}</div>', unsafe_allow_html=True)
    
    if st.button("↩️ تراجع"):
        if st.session_state.history:
            st.session_state.df = st.session_state.history.pop()
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# حاوية التحليل والجدول (كما في أسفل الصورة)
if st.session_state.df is not None:
    st.markdown('<div class="white-card" style="text-align: right;">', unsafe_allow_html=True)
    st.subheader("📊 الفلترة والتحليل الذكي")
    
    search_q = st.text_input("🔎 ابحث داخل الجدول:")
    stat_target = st.selectbox("عرض تكرار القيم في عمود:", st.session_state.df.columns)
    
    # تطبيق الفلترة
    display_df = st.session_state.df.copy()
    if search_q:
        display_df = display_df[display_df.apply(lambda r: r.astype(str).str.contains(search_q, case=False).any(), axis=1)]
    
    # عرض التكرارات
    if stat_target:
        counts = display_df[stat_target].value_counts().reset_index()
        counts.columns = ['القيمة', 'التكرار']
        st.dataframe(counts.head(10), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.dataframe(display_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# تعزيز التفاعل بـ JS
components.html("""
<script>
    const btns = window.parent.document.querySelectorAll('button');
    btns.forEach(btn => {
        btn.addEventListener('mousedown', () => btn.style.transform = 'scale(0.96)');
        btn.addEventListener('mouseup', () => btn.style.transform = 'scale(1)');
    });
</script>
""", height=0)
