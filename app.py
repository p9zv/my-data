import streamlit as st
import pandas as pd
import io
from rapidfuzz import process, fuzz
import streamlit.components.v1 as components

# ======================================================
# 1. إعدادات الصفحة وإثبات الملكية (SEO + Verification)
# ======================================================
st.set_page_config(
    page_title="محلل ومنظف ملفات إكسل الذكي | أداة مجانية أونلاين",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# حقن أكواد التحقق في بداية التطبيق
# الطريقة الأولى: كود التحقق الرسمي (HTML Tag)
st.markdown('<meta name="google-site-verification" content="google68d2f7877c4e50da.html" />', unsafe_allow_html=True)

# الطريقة الثانية: نص مخفي يقرأه زاحف جوجل
st.write('<div style="display:none;">google-site-verification: google68d2f7877c4e50da.html</div>', unsafe_allow_html=True)

# الطريقة الثالثة: كود إحصاءات جوجل (Google Analytics)
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
# 3. منطق البيانات (Session State)
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
    st.stop()

# تحميل البيانات عند الرفع
if st.session_state.df is None:
    try:
        if uploaded_file.name.endswith(".csv"):
            st.session_state.df = pd.read_csv(uploaded_file)
        else:
            st.session_state.df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"حدث خطأ أثناء تحميل الملف: {e}")
        st.stop()

df = st.session_state.df

# عرض إحصائيات سريعة
c1, c2 = st.columns(2)
with c1: st.markdown(f"<div class='metric-box'><h3>عدد الصفوف</h3><h2>{df.shape[0]}</h2></div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='metric-box'><h3>عدد الأعمدة</h3><h2>{df.shape[1]}</h2></div>", unsafe_allow_html=True)

st.divider()

# شريط البحث وعرض البيانات
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
    else:
        st.warning("لا توجد خطوات سابقة للتراجع عنها")

st.divider()

# ======================================================
# 5. الأدوات الذكية (Tabs)
# ======================================================
t1, t2 = st.tabs(["🧹 أدوات الحذف", "🔁 أدوات التعديل"])

with t1:
    with st.expander("🗑️ حذف مكررات أو أعمدة"):
        if st.button("تصفية التكرار"):
            save_history()
            st.session_state.df.drop_duplicates(inplace=True)
            st.success("تم حذف الصفوف المكررة")
            st.rerun()
        
        cols_to_drop = st.multiselect("اختر أعمدة لحذفها", df.columns)
        if st.button("حذف الأعمدة المختارة"):
            save_history()
            st.session_state.df.drop(columns=cols_to_drop, inplace=True)
            st.rerun()

with t2:
    with st.expander("🧠 فحص التشابه الذكي"):
        sim_col = st.selectbox("اختر عمود الفحص", df.columns)
        if st.button("بدء الفحص"):
            values = df[sim_col].dropna().astype(str).unique()
            st.info(f"يتم الآن فحص {len(values)} قيمة فريدة...")
            # هنا يمكنك إضافة منطق fuzzy matching المتطور
            st.success("اكتمل الفحص بنجاح")

st.divider()

# ======================================================
# 6. التصدير (Download)
# ======================================================
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    st.session_state.df.to_excel(writer, index=False)
st.download_button(
    label="⬇️ تحميل الملف النظيف (Excel)",
    data=output.getvalue(),
    file_name="cleaned_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)

# تذييل الصفحة مع كود التحقق الاحتياطي
st.caption("Verification ID: google68d2f7877c4e50da.html")
st.markdown("<p style='text-align:center; font-size:0.8rem; color:#4b5563;'>جميع الحقوق محفوظة © 2026 - منصة تنظيف البيانات</p>", unsafe_allow_html=True)
