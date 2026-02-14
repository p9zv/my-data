import streamlit as st
import pandas as pd
import io
from rapidfuzz import process, fuzz
import streamlit.components.v1 as components

# ======================================================
# كود إثبات الملكية "الإجباري" (HTML Tag Injection)
# ======================================================
# وضع الكود في بداية الصفحة ليظهر في أول مسح لعناكب جوجل
st.markdown('<p style="color:#020617; font-size:1px;">google-site-verification: google68d2f7877c4e50da.html</p>', unsafe_allow_html=True)

# وسم التحقق الرسمي الذي يطلبه جوجل كـ HTML Tag
st.markdown('<meta name="google-site-verification" content="google68d2f7877c4e50da.html" />', unsafe_allow_html=True)

# إعدادات الصفحة
st.set_page_config(page_title="محلل ومنظف ملفات إكسل الذكي", page_icon="📊", layout="wide")

# كود تتبع الإحصائيات (رقم الـ G الخاص بك)
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
# بقية كود التطبيق (التصميم والوظائف)
# ======================================================
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
html, body, [data-testid="stAppViewContainer"]{ direction: rtl; font-family: 'Cairo', sans-serif; background:#020617; }
h1,h2,h3{ text-align:center; color:#e5e7eb !important; }
</style>""", unsafe_allow_html=True)

st.title("📊 منصة تنظيف البيانات الاحترافية")
st.info("أداة مجانية لتحليل وتصفية ملفات Excel و CSV")

# واجهة رفع الملفات والعمليات (نفس الكود السابق الخاص بك)
uploaded_file = st.file_uploader("📂 ارفع ملف Excel أو CSV", type=["xlsx", "csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
    st.write("عدد الصفوف:", df.shape[0])
    st.dataframe(df.head(10))
    
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button("⬇️ تحميل الملف", buffer.getvalue(), "cleaned.xlsx")
