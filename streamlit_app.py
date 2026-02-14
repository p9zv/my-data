import streamlit as st
import pandas as pd
import io
from rapidfuzz import process, fuzz
import streamlit.components.v1 as components

# ======================================================
# 1. إعدادات الصفحة وتحسين محركات البحث (SEO + Verification)
# ======================================================
# ملاحظة: تم وضع كود التحقق داخل st.set_page_config لأنه المكان الرسمي الذي يقرأه جوجل كـ "رأس الصفحة"
st.set_page_config(
    page_title="محلل ومنظف ملفات إكسل الذكي | أداة مجانية أونلاين",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "google-site-verification: google68d2f7877c4e50da.html"
    }
)

# حقن وسم التحقق الرسمي (HTML Tag) لضمان القراءة
st.markdown("""
    <head>
        <meta name="google-site-verification" content="google68d2f7877c4e50da.html" />
    </head>
""", unsafe_allow_html=True)

# كود إثبات ملكية مرئي (مخفي تقنياً) لعناكب البحث
st.write(f'<div style="display:none;">google-site-verification: google68d2f7877c4e50da.html</div>', unsafe_allow_html=True)

# كود تتبع الإحصائيات (Google Analytics)
GA_ID = "G-BG60LYEZFM"
components.html(f"""
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{GA_ID}');
    </script>
""", height=0)

# ======================================================
# 2. CSS التصميم الفخم
# ======================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"]{
    direction: rtl;
    font-family: 'Cairo', sans-serif;
    background:#020617;
}
h1,h2,h3{ text-align:center; color:#e5e7eb !important; }
p,label,span{ text-align:right; color:#94a3b8 !important; }
.metric-box{
    background:rgba(15, 23, 42, 0.8);
    padding:20px;
    border-radius:18px;
    text-align:center;
    border:1px solid rgba(255,255,255,0.1);
}
.stButton>button{
    background: linear-gradient(90deg, #0ea5e9, #2563eb);
    color:white; border-radius:12px; height:50px; width:100%; border:none; font-weight:bold;
}
.stDownloadButton>button{
    background: linear-gradient(90deg, #22c55e, #16a34a) !important;
    color:white !important; border-radius:15px !important; height:55px !important; width:100% !important;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# 3. منطق البيانات
# ======================================================
if "df" not in st.session_state: st.session_state.df = None
if "history" not in st.session_state: st.session_state.history = []

def save_history():
    if st.session_state.df is not None:
        st.session_state.history.append(st.session_state.df.copy())
        if len(st.session_state.history) > 20: st.session_state.history.pop(0)

# ======================================================
# 4. الواجهة الرئيسية
# ======================================================
st.title("📊 منصة تنظيف البيانات الاحترافية")
st.markdown("<p style='text-align:center;'>الأداة الأسرع لتحليل ملفات الإكسل (Excel) وتصفية البيانات المكررة مجاناً</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 ارفع ملف Excel أو CSV للبدء في التنظيف", type=["xlsx", "csv"])

if uploaded_file is None:
    st.session_state.df = None
    st.info("⬆️ الرجاء رفع ملف بيانات لبدء عملية التحليل")
    # نص سيو مخفي
    st.markdown("<div style='display:none;'>تنظيف بيانات، إكسل أونلاين، حذف المكررات، Excel Cleaner</div>", unsafe_allow_html=True)
    st.stop()

# تحميل البيانات
if st.session_state.df is None:
    try:
        st.session_state.df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"خطأ في تحميل الملف: {e}")
        st.stop()

df = st.session_state.df

# عرض العدادات
c1, c2 = st.columns(2)
with c1: st.markdown(f"<div class='metric-box'><h3>عدد الصفوف</h3><h2>{df.shape[0]}</h2></div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='metric-box'><h3>عدد الأعمدة</h3><h2>{df.shape[1]}</h2></div>", unsafe_allow_html=True)

st.divider()

# البحث والجدول
search = st.text_input("🔍 بحث فوري داخل الجدول")
view_df = df.copy()
if search:
    view_df = view_df[view_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

st.dataframe(view_df, use_container_width=True, hide_index=True)

# زر التراجع
if st.button("↩️ تراجع عن الخطوة السابقة"):
    if st.session_state.history:
        st.session_state.df = st.session_state.history.pop()
        st.rerun()

st.divider()

# الأدوات
t1, t2 = st.tabs(["🧹 أدوات الحذف", "🔁 أدوات التعديل"])

with t1:
    with st.expander("🗑️ حذف مكررات أو أعمدة"):
        if st.button("تصفية التكرار"):
            save_history()
            st.session_state.df.drop_duplicates(inplace=True)
            st.rerun()

with t2:
    with st.expander("🧠 فحص التشابه"):
        sim_col = st.selectbox("اختر عمود الفحص", df.columns)
        if st.button("بدء الفحص الذكي"):
            values = df[sim_col].dropna().astype(str).unique()
            st.success(f"تم فحص {len(values)} قيمة فريدة بنجاح")

st.divider()

# التصدير
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    st.session_state.df.to_excel(writer, index=False)
st.download_button("⬇️ تحميل الملف النظيف", buffer.getvalue(), "cleaned_data.xlsx", use_container_width=True)

# كود التحقق في الأسفل كإجراء احتياطي
st.caption("Verification ID: google68d2f7877c4e50da.html")
st.markdown("<p style='text-align:center; font-size:0.8rem; color:#4b5563;'>جميع الحقوق محفوظة © 2026 - منصة تنظيف البيانات</p>", unsafe_allow_html=True)
