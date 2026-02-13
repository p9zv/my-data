import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components
from difflib import SequenceMatcher

# 1. إعدادات الصفحة
st.set_page_config(page_title="Advanced Excel Processor", page_icon="📊", layout="wide")

# 2. تصميم الواجهة الموحد (CSS & JS)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    .stApp {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        font-family: 'Cairo', sans-serif;
    }

    /* حاوية الأزرار الرئيسية */
    .buttons-container {
        background-color: #1E293B;
        padding: 20px;
        border-radius: 24px;
        border: 1px solid #334155;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }

    /* الهيدر */
    .header-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 30px;
        border-radius: 24px;
        text-align: center;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }

    /* تنسيق ألوان الأزرار كما في الصورة */
    div[data-testid="column"]:nth-of-type(1) button { background: #6c5ce7 !important; } /* استبدال */
    div[data-testid="column"]:nth-of-type(2) button { background: #ff7675 !important; } /* حذف */
    div[data-testid="column"]:nth-of-type(3) button { background: #fdcb6e !important; color: #1e293b !important; } /* نصوص مشابهة */
    div[data-testid="column"]:nth-of-type(4) button { background: #74b9ff !important; color: #1e293b !important; } /* متكررات */
    
    .stButton>button {
        border-radius: 16px !important;
        font-weight: 700 !important;
        height: 70px !important;
        width: 100%;
        border: none !important;
        transition: transform 0.2s;
    }
    
    .stButton>button:hover {
        transform: scale(1.02);
    }

    /* زر التراجع والتصدير */
    .undo-section { display: flex; justify-content: flex-end; gap: 10px; margin-bottom: 10px; }
    .stDownloadButton>button { background: #00b894 !important; border-radius: 12px !important; }

    /* الجدول */
    [data-testid="stDataFrame"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 15px !important;
    }
    </style>

    <script>
    // إضافة تأثير اهتزاز بسيط عند الضغط على الأزرار (JavaScript)
    const buttons = window.parent.document.querySelectorAll('button');
    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            btn.style.transform = 'scale(0.95)';
            setTimeout(() => btn.style.transform = 'scale(1)', 100);
        });
    });
    </script>
    """, unsafe_allow_html=True)

# 3. المنطق البرمجي (Undo & Save)
if 'df' not in st.session_state: st.session_state.df = None
if 'history' not in st.session_state: st.session_state.history = []

def save_step():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 15: st.session_state.history.pop(0)

def undo():
    if st.session_state.history:
        st.session_state.df = st.session_state.history.pop()
        st.rerun()

# --- واجهة التطبيق ---

# حاوية الهيدر
st.markdown("""
    <div class="header-card">
        <h1 style="color:#74b9ff; margin:0;">📊 محلل ملفات Excel المتقدم</h1>
        <p style="opacity:0.7;">أداة احترافية مدمجة لتنظيف ومعالجة البيانات</p>
    </div>
    """, unsafe_allow_html=True)

# منطقة الرفع
uploaded_file = st.file_uploader("", type=["xlsx", "csv"])

if uploaded_file:
    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)

    df = st.session_state.df

    # شريط التراجع والتصدير (بأزرار صغيرة في الأعلى)
    c_u1, c_u2 = st.columns([1, 5])
    with c_u1:
        if st.button("↩️ Undo", help="تراجع عن آخر خطوة"):
            undo()
    with c_u2:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("📥 Export Excel", data=output.getvalue(), file_name="Edited_Data.xlsx")

    # الحاوية الموحدة للأزرار (كما في صورتك)
    st.markdown('<div class="buttons-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        with st.popover("🔄 استبدال"):
            old = st.text_input("القيمة الحالية")
            new = st.text_input("القيمة الجديدة")
            if st.button("تأكيد الاستبدال"):
                save_step(); st.session_state.df.replace(old, new, inplace=True); st.rerun()
    
    with col2:
        with st.popover("🗑️ حذف المحدد"):
            cols = st.multiselect("اختر الأعمدة لحذفها:", df.columns)
            if st.button("حذف نهائي"):
                save_step(); st.session_state.df.drop(columns=cols, inplace=True); st.rerun()

    with col3:
        with st.popover("🔍 النصوص المتشابهة"):
            target = st.selectbox("اختر العمود للفحص:", df.columns)
            if st.button("بدء التحليل الذكي"):
                st.session_state.show_smart = target
    
    with col4:
        with st.popover("📑 المتكررات"):
            st.write(f"الصفوف المكررة: {df.duplicated().sum()}")
            if st.button("حذف التكرارات"):
                save_step(); st.session_state.df.drop_duplicates(inplace=True); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # عرض معلومات الملف
    st.markdown(f"""
        <p style='text-align:center; color:#74b9ff;'>
            الملف: {uploaded_file.name} | الصفوف: {df.shape[0]} | الأعمدة: {df.shape[1]}
        </p>
    """, unsafe_allow_html=True)

    # الجدول التفاعلي
    st.dataframe(df, use_container_width=True, hide_index=True)

# 4. إضافة JavaScript خارجي (اختياري لتحسين المظهر)
components.html("""
<script>
    // كود JS لإضافة تأثيرات بصرية على الجداول عند التحميل
    console.log("Dashboard Ready");
</script>
""", height=0)
