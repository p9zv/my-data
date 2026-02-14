# =====================================
# Smart Excel Cleaner - Google Cloud Version
# تطبيق تنظيف وتحليل ملفات Excel و CSV
# =====================================

import streamlit as st
import pandas as pd
import io

# إعدادات الصفحة
st.set_page_config(
    page_title="منصة تنظيف ملفات الإكسل",
    page_icon="📊",
    layout="wide"
)

# تصميم خفيف وسريع مناسب لـ Cloud Run
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"]{
    direction: rtl;
    background:#0f172a;
    color:white;
}
h1,h2,h3{ text-align:center; }

.stButton>button{
    background:#2563eb;
    color:white;
    border-radius:10px;
    height:45px;
    font-weight:bold;
}

.stDownloadButton>button{
    background:#16a34a !important;
    color:white !important;
    border-radius:12px !important;
    height:50px !important;
}
</style>
""", unsafe_allow_html=True)

# عنوان الصفحة
st.title("📊 منصة تنظيف وتحليل ملفات الإكسل")
st.write("ارفع ملف Excel أو CSV وسيتم تحليله وتنظيفه مباشرة")

# رفع الملف
uploaded_file = st.file_uploader("📂 ارفع ملفك", type=["xlsx", "csv"])

if uploaded_file is None:
    st.info("⬆️ بانتظار رفع الملف")
    st.stop()

# قراءة الملف
try:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
except Exception:
    st.error("فشل قراءة الملف — تأكد أن الملف سليم")
    st.stop()

# إحصائيات
c1, c2 = st.columns(2)
c1.metric("عدد الصفوف", df.shape[0])
c2.metric("عدد الأعمدة", df.shape[1])

st.divider()

# البحث داخل البيانات
search = st.text_input("🔍 بحث داخل البيانات")
view_df = df.copy()

if search:
    view_df = view_df[
        view_df.apply(
            lambda r: r.astype(str).str.contains(search, case=False).any(),
            axis=1
        )
    ]

st.dataframe(view_df, use_container_width=True)

st.divider()

# حذف الصفوف المكررة
if st.button("🧹 حذف الصفوف المكررة"):
    df = df.drop_duplicates()
    st.success("تم حذف التكرار")

# حذف أعمدة محددة
cols = st.multiselect("اختر أعمدة لحذفها", df.columns)

if st.button("حذف الأعمدة المحددة"):
    if len(cols) > 0:
        df = df.drop(columns=cols)
        st.success("تم حذف الأعمدة")
    else:
        st.warning("اختر عموداً أولاً")

st.divider()

# تصدير الملف بعد التنظيف
output = io.BytesIO()
with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df.to_excel(writer, index=False)

st.download_button(
    label="⬇️ تحميل الملف بعد التنظيف",
    data=output.getvalue(),
    file_name="cleaned_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption("Cloud Version 1.0")
