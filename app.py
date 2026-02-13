import streamlit as st
import pandas as pd
import io
from difflib import SequenceMatcher
from collections import Counter
# استدعاء المكتبة الناقصة لحل مشكلة الـ NameError
import streamlit.components.v1 as components 

# 1. إعدادات الصفحة
st.set_page_config(page_title="المحلل الذكي للبيانات", page_icon="💎", layout="wide")

# 2. التصميم الفخم (CSS) مع دعم اللغة العربية RTL
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif !important;
    }

    .stApp {
        background: radial-gradient(circle at center, #111827, #030712) !important;
    }

    /* الحاوية الزجاجية الرئيسية */
    .glass-container {
        background: rgba(31, 41, 55, 0.4);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 28px;
        padding: 40px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.5);
        margin-bottom: 25px;
        direction: rtl;
    }

    /* تنسيق ألوان الأزرار كما طلبت */
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
        color: white !important;
        width: 100%;
    }

    .stButton>button:hover { transform: translateY(-4px) scale(1.02); filter: brightness(1.1); }

    /* لوحة التحليل */
    .stats-card {
        background: rgba(17, 24, 39, 0.7);
        border-left: 5px solid #6366f1; /* تم تعديله لليسار ليناسب الـ RTL */
        padding: 25px;
        border-radius: 18px;
        margin: 20px 0;
        border: 1px solid rgba(255,255,255,0.05);
        text-align: right;
    }

    h1, h2, h3 { color: #f8fafc !important; text-align: center; }
    
    .stDataFrame { border-radius: 15px !important; border: 1px solid rgba(255,255,255,0.1) !important; }

    /* تحسين منطقة رفع الملفات */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed rgba(99, 102, 241, 0.4) !important;
        border-radius: 20px;
        background: rgba(31, 41, 55, 0.2);
    }
    
    label { color: #94a3b8 !important; font-weight: 600 !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. إدارة حالة التطبيق (Undo)
if 'df' not in st.session_state: st.session_state.df = None
if 'history' not in st.session_state: st.session_state.history = []

def record_state():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 20: st.session_state.history.pop(0)

def undo_action():
    if st.session_state.history:
        st.session_state.df = st.session_state.history.pop()
        st.rerun()

# --- بناء الواجهة ---

st.markdown('<div class="glass-container">', unsafe_allow_html=True)

st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="font-size: 2.5rem; margin-bottom: 10px;">نظام <span style="color:#6366f1">تحليل البيانات</span> المتقدم</h1>
        <p style="color:#94a3b8; font-size: 1.1rem;">قم بمعالجة ملفاتك بذكاء وبلمسة واحدة</p>
    </div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader("اسحب ملف الإكسل أو اضغط هنا لرفعه", type=["xlsx", "csv"])

if uploaded_file:
    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)

    df = st.session_state.df

    # أزرار الإجراءات السريعة
    act1, act2 = st.columns([1, 1])
    with act1:
        if st.button("↩️ تراجع عن الخطوة"): undo_action()
    with act2:
        output = io.BytesIO()
        df.to_excel(output, index=False)
        st.download_button("📥 تصدير الملف النهائي", data=output.getvalue(), file_name="Data_Cleaned.xlsx", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # الحاوية الموحدة للأزرار الأربعة
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        with st.popover("🔄 استبدال القيمة"):
            old_v = st.text_input("القيمة المراد تغييرها")
            new_v = st.text_input("القيمة الجديدة")
            if st.button("تنفيذ التغيير"):
                record_state(); st.session_state.df.replace(old_v, new_v, inplace=True); st.rerun()
    with c2:
        with st.popover("🗑️ حذف أعمدة"):
            cols_to_del = st.multiselect("اختر الأعمدة لحذفها:", df.columns)
            if st.button("تأكيد الحذف"):
                record_state(); st.session_state.df.drop(columns=cols_to_del, inplace=True); st.rerun()
    with c3:
        with st.popover("⚖️ فحص التشابه"):
            st.info("سيتم فحص الأسماء المتقاربة في الجدول بالأسفل بناءً على اختيارك")
            sim_col = st.selectbox("اختر العمود للفحص:", df.columns)
    with c4:
        with st.popover("📑 التكرارات"):
            dup_count = df.duplicated().sum()
            st.metric("إجمالي الصفوف المكررة", dup_count)
            if st.button("حذف كافة التكرارات"):
                record_state(); st.session_state.df.drop_duplicates(inplace=True); st.rerun()

    # --- لوحة التحليل والفلترة الذكية ---
    st.markdown('<div class="stats-card">', unsafe_allow_html=True)
    st.markdown("<h3><i class='fas fa-filter' style='color:#6366f1'></i> الفلترة والتحليل الإحصائي</h3>", unsafe_allow_html=True)
    
    f1, f2 = st.columns([2, 1])
    with f1:
        search_query = st.text_input("🔎 ابحث عن أحرف أو كلمات معينة لتصفية الجدول:")
    with f2:
        analyze_target = st.selectbox("📊 عرض الأكثر تكراراً في عمود:", df.columns)

    # تطبيق الفلترة الحية
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[filtered_df.apply(lambda r: r.astype(str).str.contains(search_query, case=False).any(), axis=1)]

    # إحصائيات التكرار
    if analyze_target:
        val_counts = filtered_df[analyze_target].value_counts().reset_index()
        val_counts.columns = ['القيمة', 'عدد التكرارات']
        st.write(f"**أعلى القيم تكراراً في عمود ({analyze_target}):**")
        st.dataframe(val_counts.head(10), use_container_width=True, hide_index=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # عرض الجدول الرئيسي
    st.markdown("<h3><i class='fas fa-database' style='color:#3b82f6'></i> استعراض البيانات النشطة</h3>", unsafe_allow_html=True)
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)

# 4. JavaScript للتفاعل الفيزيائي مع الأزرار
components.html("""
<script>
    const buttons = window.parent.document.querySelectorAll('button');
    buttons.forEach(btn => {
        btn.addEventListener('mousedown', () => btn.style.transform = 'scale(0.96)');
        btn.addEventListener('mouseup', () => btn.style.transform = 'scale(1)');
    });
</script>
""", height=0)
