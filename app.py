import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="محلل ملفات Excel المتقدم", page_icon="📊", layout="wide")

# 2. التصميم البصري (طبق الأصل للصور المرفقة)
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    /* الخلفية البنفسجية المتدرجة */
    .stApp {
        background: linear-gradient(180deg, #6e7df2 0%, #4b59c9 100%) !important;
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
    }

    /* الحاويات البيضاء (Cards) */
    .white-card {
        background: #ffffff;
        border-radius: 30px;
        padding: 30px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
    }

    /* العناوين الزرقاء */
    .main-title { color: #5c6bc0; font-weight: 700; font-size: 2.2rem; margin-bottom: 5px; }
    .sub-title { color: #757575; font-size: 1.1rem; }

    /* شبكة الأزرار الملونة */
    .btn-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 15px;
        margin-top: 20px;
    }

    /* تنسيق الأزرار كما في الصورة */
    div[data-testid="column"]:nth-of-type(1) button { background: #6f5cc3 !important; } /* بنفسجي */
    div[data-testid="column"]:nth-of-type(2) button { background: #e5534b !important; } /* أحمر */
    div[data-testid="column"]:nth-of-type(3) button { background: #f0ad4e !important; } /* برتقالي */
    div[data-testid="column"]:nth-of-type(4) button { background: #5086eb !important; } /* أزرق */
    
    /* زر التصدير الأخضر الكبير */
    .export-container button {
        background: #5cb885 !important;
        height: 60px !important;
        width: 100% !important;
        font-size: 1.3rem !important;
    }

    .stButton>button {
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        height: 80px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        transition: 0.3s transform ease;
    }
    .stButton>button:hover { transform: translateY(-3px); opacity: 0.9; }

    /* بيانات الملف الأسفل */
    .file-info { color: #616161; font-size: 1rem; margin-top: 15px; font-weight: 600; }

    /* منطقة الرفع */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #5c6bc0 !important;
        border-radius: 20px !important;
        background: #f8f9ff !important;
    }
    
    /* لوحة التحليل (Statistics Box) */
    .analysis-panel {
        background: #fdfdfd;
        border-right: 6px solid #5c6bc0;
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        text-align: right;
    }
    </style>
""", unsafe_allow_html=True)

# 3. منطق البيانات
if 'df' not in st.session_state: st.session_state.df = None
if 'history' not in st.session_state: st.session_state.history = []

def record():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 15: st.session_state.history.pop(0)

# --- واجهة المستخدم ---

# الهيدر العلوي
st.markdown("""
    <div class="white-card">
        <h1 class="main-title">محلل ملفات Excel المتقدم <i class="fas fa-chart-bar"></i></h1>
        <p class="sub-title">أداة شاملة لقراءة وتحليل وتعديل ملفات Excel</p>
    </div>
""", unsafe_allow_html=True)

# منطقة الرفع والبيانات
st.markdown('<div class="white-card">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["xlsx", "xls", "csv"])

if uploaded_file:
    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)
    
    df = st.session_state.df

    # شبكة الأزرار الأربعة
    col1, col2 = st.columns(2)
    with col1:
        with st.popover("🔄 استبدال"):
            o = st.text_input("القيمة القديمة")
            n = st.text_input("القيمة الجديدة")
            if st.button("تحديث"):
                record(); st.session_state.df.replace(o, n, inplace=True); st.rerun()
    with col2:
        with st.popover("🗑️ حذف المحدد"):
            d = st.multiselect("اختر الأعمدة:", df.columns)
            if st.button("تأكيد الحذف"):
                record(); st.session_state.df.drop(columns=d, inplace=True); st.rerun()

    col3, col4 = st.columns(2)
    with col3:
        with st.popover("🔍 النصوص المتشابهة"):
            analyze_col = st.selectbox("اختر العمود للتحليل:", df.columns)
    with col4:
        with st.popover("📑 المتكررات"):
            st.write(f"الصفوف المتكررة: {df.duplicated().sum()}")
            if st.button("إزالة كافة التكرارات"):
                record(); st.session_state.df.drop_duplicates(inplace=True); st.rerun()

    # زر التصدير (التصميم الأخضر العريض)
    st.markdown('<div class="export-container">', unsafe_allow_html=True)
    out = io.BytesIO()
    df.to_excel(out, index=False)
    st.download_button("<i class='fas fa-download'></i> تصدير", data=out.getvalue(), file_name="Edited.xlsx", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # شريط معلومات الملف (كما في الصورة)
    st.markdown(f"""
        <div class="file-info">
            الملف: {uploaded_file.name} | الصفوف: {len(df)} | الأعمدة: {len(df.columns)}
        </div>
    """, unsafe_allow_html=True)
    
    # ميزة التراجع
    if st.button("↩️ تراجع عن آخر تعديل", use_container_width=True):
        if st.session_state.history:
            st.session_state.df = st.session_state.history.pop()
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# لوحة التحليل والفلترة (المتطلبات الإضافية)
if uploaded_file:
    st.markdown('<div class="white-card" style="text-align: right;">', unsafe_allow_html=True)
    st.markdown("### <i class='fas fa-filter' style='color:#5c6bc0'></i> الفلترة والتحليل الذكي")
    
    f1, f2 = st.columns([2, 1])
    with f1:
        query = st.text_input("🔎 ابحث عن كلمة معينة لتصفية النتائج:")
    with f2:
        stat_col = st.selectbox("📊 إحصائيات التكرار لعمود:", df.columns)

    # تنفيذ الفلترة
    final_df = df.copy()
    if query:
        final_df = final_df[final_df.apply(lambda r: r.astype(str).str.contains(query, case=False).any(), axis=1)]

    # تنفيذ حساب التكرار
    if stat_col:
        counts = final_df[stat_col].value_counts().reset_index()
        counts.columns = ['القيمة', 'عدد التكرارات']
        st.dataframe(counts.head(10), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("#### <i class='fas fa-table'></i> استعراض البيانات")
    st.dataframe(final_df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# تحسين تفاعل الأزرار
components.html("""
<script>
    const btns = window.parent.document.querySelectorAll('button');
    btns.forEach(btn => {
        btn.addEventListener('mousedown', () => btn.style.transform = 'scale(0.95)');
        btn.addEventListener('mouseup', () => btn.style.transform = 'scale(1)');
    });
</script>
""", height=0)
