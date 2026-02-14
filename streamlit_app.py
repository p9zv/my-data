import streamlit as st
import pandas as pd
import io
from rapidfuzz import process, fuzz
import streamlit.components.v1 as components

# ======================================================
# كود إثبات الملكية لجوجل (Google Analytics ID)
# ======================================================
# ضع رقم الـ G الخاص بك هنا بدلاً من G-XXXXXXXXXX
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
# 1. إعدادات الصفحة وتحسين محركات البحث (SEO)
# ======================================================
st.set_page_config(
    page_title="محلل ومنظف ملفات إكسل الذكي | أداة مجانية أونلاين",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "# أداة احترافية لتنظيف ملفات Excel و CSV أونلاين. احذف التكرارات، استبدل القيم، وحلل البيانات بسهولة."
    }
)

# كود تقني لجوجل (Schema.org) لإظهار الموقع كأداة احترافية
st.markdown("""
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "Data Cleaner Pro",
      "operatingSystem": "Windows, MacOS, Android, iOS",
      "applicationCategory": "BusinessApplication",
      "description": "أداة عربية مجانية لتنظيف وتحليل ملفات الإكسل والبيانات الضخمة أونلاين."
    }
    </script>
""", unsafe_allow_html=True)

# ======================================================
# 2. CSS التصميم
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
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.stButton>button{
    background: linear-gradient(90deg, #0ea5e9, #2563eb);
    color:white; border-radius:12px; height:50px; width:100%; border:none; font-weight:bold;
}

.stButton>button:hover{
    background: linear-gradient(90deg, #0284c7, #1d4ed8);
}

.stDownloadButton>button{
    background: linear-gradient(90deg, #22c55e, #16a34a) !important;
    color:white !important; border-radius:15px !important; height:55px !important; width:100% !important;
}

.seo-text { visibility: hidden; height: 0; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 3. منطق البيانات (Session State)
# ======================================================
if "df" not in st.session_state: st.session_state.df = None
if "history" not in st.session_state: st.session_state.history = []
if "last_file" not in st.session_state: st.session_state.last_file = None

def save_history():
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
    st.markdown("<div class='seo-text'>تنظيف إكسل، حذف مكررات، تحليل بيانات محاسبية، CSV cleaner, Excel Online tool</div>", unsafe_allow_html=True)
    st.stop()

file_id = uploaded_file.name + str(uploaded_file.size)
if st.session_state.last_file != file_id:
    st.session_state.df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    st.session_state.history = []
    st.session_state.last_file = file_id

df = st.session_state.df

c1, c2 = st.columns(2)
with c1: st.markdown(f"<div class='metric-box'><h3>عدد الصفوف</h3><h2>{df.shape[0]}</h2></div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='metric-box'><h3>عدد الأعمدة</h3><h2>{df.shape[1]}</h2></div>", unsafe_allow_html=True)

st.divider()

search = st.text_input("🔍 بحث فوري داخل الجدول (مثال: اسم العميل، رقم الهاتف)")
view_df = df.copy()
if search:
    view_df = view_df[view_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)]

st.dataframe(view_df, use_container_width=True, hide_index=True)

col_l, col_m, col_r = st.columns([2,1,2])
with col_m:
    if st.button("↩️ تراجع"):
        if st.session_state.history:
            st.session_state.df = st.session_state.history.pop()
            st.rerun()

st.divider()

# ======================================================
# 5. الأدوات الذكية
# ======================================================
t1, t2 = st.tabs(["🧹 أدوات الحذف", "🔁 أدوات التعديل"])

with t1:
    with st.expander("🗑️ حذف أعمدة متعددة"):
        cols = st.multiselect("اختر الأعمدة", df.columns)
        if st.button("تنفيذ حذف الأعمدة"):
            save_history(); st.session_state.df.drop(columns=cols, inplace=True); st.rerun()

    with st.expander("📑 إزالة التكرارات"):
        st.write("عدد الصفوف المكررة تماماً:", df.duplicated().sum())
        if st.button("تصفية التكرار"):
            save_history(); st.session_state.df.drop_duplicates(inplace=True); st.rerun()

with t2:
    with st.expander("🔁 استبدال قيم (نصوص أو أرقام)"):
        rcol = st.selectbox("اختر العمود", df.columns, key="rep_tool")
        old = st.text_input("القيمة التي تريد استبدالها")
        new = st.text_input("القيمة الجديدة")
        if st.button("تأكيد الاستبدال"):
            save_history()
            st.session_state.df[rcol] = st.session_state.df[rcol].astype(str).str.replace(old, new, regex=False)
            st.rerun()

    with st.expander("🧠 فحص التشابه الذكي (AI)"):
        sim_col = st.selectbox("اختر عمود الأسماء مثلاً:", df.columns, key="sim_tool")
        if st.button("بدء الفحص"):
            values = df[sim_col].dropna().astype(str).unique()
            results = []
            for v in values[:150]:
                match, score, _ = process.extractOne(v, values, scorer=fuzz.ratio)
                if 85 < score < 100: results.append((v, match, score))
            if results:
                st.dataframe(pd.DataFrame(results, columns=["القيمة", "مشابهة لـ", "النسبة"]), use_container_width=True)
            else: st.success("البيانات نقية ولا يوجد تشابه")

st.divider()

# ======================================================
# 6. التصدير وأزرار النشر
# ======================================================
l, c, r = st.columns([2,3,2])
with c:
    buffer = io.BytesIO()
    st.session_state.df.to_excel(buffer, index=False)
    st.download_button("⬇️ تحميل الملف النظيف (Excel)", buffer.getvalue(), "cleaned_data.xlsx", use_container_width=True)

st.markdown("<br><h3 style='font-size:1.2rem;'>📢 ساعدنا في نشر الأداة</h3>", unsafe_allow_html=True)
# استبدل الرابط أدناه برابط موقعك الحقيقي
app_url = "https://my-data-p9zv-anl.streamlit.app" 
st.markdown(f"""
    <div style="text-align:center;">
        <a href="https://api.whatsapp.com/send?text=أداة رهيبة لتنظيف ملفات الإكسل مجاناً: {app_url}" target="_blank">
            <img src="https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white">
        </a>
        <a href="https://twitter.com/intent/tweet?url={app_url}&text=أنصحكم بهذه الأداة لتنظيف البيانات" target="_blank">
            <img src="https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white">
        </a>
    </div>
""", unsafe_allow_html=True)

st.markdown("<p style='text-align:center; font-size:0.8rem; color:#4b5563;'>جميع الحقوق محفوظة © 2026 - منصة تنظيف البيانات</p>", unsafe_allow_html=True)
