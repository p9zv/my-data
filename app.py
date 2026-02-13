import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="محلل ملفات Excel المتقدم", layout="wide")

# 2. بناء التصميم (CSS) ليكون مطابقاً للصورة 100%
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    /* الخلفية المتدرجة كما في الصورة */
    .stApp {
        background: linear-gradient(180deg, #6e7df2 0%, #4b59c9 100%) !important;
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
    }

    /* البطاقة البيضاء الرئيسية */
    .main-card {
        background: white;
        border-radius: 30px;
        padding: 35px;
        margin: 10px auto;
        max-width: 900px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        text-align: center;
    }

    /* العناوين */
    .title-text { color: #5c6bc0; font-weight: 700; font-size: 2.2rem; margin-bottom: 5px; }
    .desc-text { color: #757575; font-size: 1.1rem; margin-bottom: 25px; }

    /* تخصيص الأزرار الملونة داخل الحاوية */
    div[data-testid="stColumn"] > div > div > div > button {
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        height: 85px !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        transition: 0.3s all;
    }

    /* ألوان الأزرار الأربعة بدقة */
    div[data-testid="column"]:nth-of-type(1) button { background: #6f5cc3 !important; } /* استبدال */
    div[data-testid="column"]:nth-of-type(2) button { background: #e5534b !important; } /* حذف */
    div[data-testid="column"]:nth-of-type(3) button { background: #f0ad4e !important; } /* المتشابهة */
    div[data-testid="column"]:nth-of-type(4) button { background: #5086eb !important; } /* المتكررات */

    /* زر التصدير الأخضر الكبير */
    .stDownloadButton > button {
        background: #5cb885 !important;
        color: white !important;
        height: 65px !important;
        width: 100% !important;
        border-radius: 15px !important;
        font-size: 1.4rem !important;
        margin-top: 15px !important;
    }

    /* منطقة رفع الملفات */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #5c6bc0 !important;
        border-radius: 20px !important;
        background: #f8f9ff !important;
    }

    /* شريط المعلومات الرمادي */
    .file-meta { color: #616161; font-size: 1rem; font-weight: 600; margin-top: 15px; }
    
    /* تنسيق الجداول */
    .stDataFrame { border-radius: 15px !important; overflow: hidden !important; border: 1px solid #eee !important; }
    </style>
""", unsafe_allow_html=True)

# 3. منطق معالجة البيانات
if 'df' not in st.session_state: st.session_state.df = None
if 'history' not in st.session_state: st.session_state.history = []

def record_state():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 10: st.session_state.history.pop(0)

# --- الواجهة البرمجية ---

# بطاقة العنوان (Header)
st.markdown("""
    <div class="main-card">
        <div class="title-text">📊 محلل ملفات Excel المتقدم</div>
        <div class="desc-text">أداة شاملة لقراءة وتحليل وتعديل ملفات Excel</div>
    </div>
""", unsafe_allow_html=True)

# بطاقة العمليات الرئيسية
with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("", type=["xlsx", "csv"])

    if uploaded_file:
        if st.session_state.df is None:
            st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)
        
        df = st.session_state.df

        # شبكة الأزرار الأربعة (استبدال، حذف، متشابهة، متكررات)
        # تم تقسيمها إلى صفين لضمان شكل المربع في الصورة
        row1_c1, row1_c2 = st.columns(2)
        with row1_c1:
            with st.popover("🔄 استبدال"):
                old_val = st.text_input("القيمة القديمة")
                new_val = st.text_input("القيمة الجديدة")
                if st.button("تنفيذ الاستبدال"):
                    record_state(); st.session_state.df.replace(old_val, new_val, inplace=True); st.rerun()
        with row1_c2:
            with st.popover("🗑️ حذف المحدد"):
                to_delete = st.multiselect("اختر الأعمدة لحذفها:", df.columns)
                if st.button("تأكيد الحذف"):
                    record_state(); st.session_state.df.drop(columns=to_delete, inplace=True); st.rerun()

        row2_c1, row2_c2 = st.columns(2)
        with row2_c1:
            with st.popover("🔍 النصوص المتشابهة"):
                st.info("سيتم تحليل العمود المختار في لوحة الإحصائيات بالأسفل")
                sim_col = st.selectbox("اختر العمود:", df.columns, key="sim")
        with row2_c2:
            with st.popover("📑 المتكررات"):
                st.write(f"عدد الصفوف المكررة: {df.duplicated().sum()}")
                if st.button("إزالة التكرار"):
                    record_state(); st.session_state.df.drop_duplicates(inplace=True); st.rerun()

        # زر التصدير الأخضر العريض أسفل الأزرار
        out_buffer = io.BytesIO()
        df.to_excel(out_buffer, index=False)
        st.download_button("📥 تصدير", data=out_buffer.getvalue(), file_name="output.xlsx", use_container_width=True)

        # معلومات الملف أسفل زر التصدير
        st.markdown(f"""
            <div class="file-meta">
                الملف: {uploaded_file.name} | الصفوف: {len(df)} | الأعمدة: {len(df.columns)}
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# لوحة النتائج والفلترة (البطاقة الثالثة)
if st.session_state.df is not None:
    st.markdown('<div class="main-card" style="text-align: right;">', unsafe_allow_html=True)
    st.subheader("🛠️ مركز الفلترة والتحليل")
    
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        search_query = st.text_input("🔎 ابحث عن أحرف أو كلمات معينة لتصفية الجدول:")
    with col_f2:
        stat_column = st.selectbox("📊 عرض الأكثر تكراراً في:", st.session_state.df.columns)

    # معالجة الفلترة
    filtered_df = st.session_state.df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)]

    # عرض إحصائيات التكرار بدقة
    if stat_column:
        counts = filtered_df[stat_column].value_counts().reset_index()
        counts.columns = ['القيمة', 'التكرار']
        st.write(f"**أعلى 10 قيم تكراراً في عمود ({stat_column}):**")
        st.dataframe(counts.head(10), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("#### 📋 معاينة البيانات النشطة")
    st.dataframe(filtered_df, use_container_width=True)
    
    if st.button("↩️ تراجع عن آخر خطوة", use_container_width=True):
        if st.session_state.history:
            st.session_state.df = st.session_state.history.pop()
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# تحسين تفاعل الضغط بـ JavaScript
components.html("""
<script>
    const btns = window.parent.document.querySelectorAll('button');
    btns.forEach(btn => {
        btn.addEventListener('mousedown', () => btn.style.transform = 'scale(0.96)');
        btn.addEventListener('mouseup', () => btn.style.transform = 'scale(1)');
    });
</script>
""", height=0)
