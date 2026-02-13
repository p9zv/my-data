}
import streamlit as st
import pandas as pd
import io
from rapidfuzz import process, fuzz

# ---------------- إعداد الصفحة ----------------
st.set_page_config(
    page_title="منصة تنظيف البيانات",
    page_icon="📊",
    layout="wide"
)

# ---------------- تصميم داكن احترافي ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

html, body, [data-testid="stAppViewContainer"]{
    direction: rtl;
    font-family: 'Cairo', sans-serif;
    background: #020617;
}

section[data-testid="stSidebar"]{
    background:#020617;
}

[data-testid="stDataFrame"]{
    border-radius:15px;
    border:1px solid rgba(255,255,255,0.1);
}

h1,h2,h3,label,p{
    color:#e5e7eb !important;
}

.stButton>button{
    background:#0ea5e9;
    color:white;
    border-radius:10px;
    height:45px;
    font-size:16px;
    border:none;
}

.stButton>button:hover{
    background:#0284c7;
}

.stDownloadButton>button{
    background:#22c55e;
    color:white;
    border-radius:10px;
    height:45px;
    font-size:16px;
    border:none;
}
</style>
""", unsafe_allow_html=True)

# ---------------- ذاكرة التطبيق ----------------
if "df" not in st.session_state:
    st.session_state.df = None

if "history" not in st.session_state:
    st.session_state.history = []

def save_history():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 15:
        st.session_state.history.pop(0)

# ---------------- العنوان ----------------
st.markdown("<h1 style='text-align:center;'>📊 منصة تنظيف البيانات لمحللي البيانات</h1>", unsafe_allow_html=True)

# ---------------- رفع الملف ----------------
uploaded_file = st.file_uploader("ارفع ملف Excel أو CSV", type=["xlsx","csv"])

if uploaded_file is not None and st.session_state.df is None:
    if uploaded_file.name.endswith(".csv"):
        st.session_state.df = pd.read_csv(uploaded_file)
    else:
        st.session_state.df = pd.read_excel(uploaded_file)

df = st.session_state.df

if df is None:
    st.info("⬆️ قم برفع ملف بيانات للبدء")
    st.stop()

# ---------------- معلومات سريعة ----------------
st.write(f"عدد الصفوف: {df.shape[0]} | عدد الأعمدة: {df.shape[1]}")

# ---------------- أدوات التنظيف ----------------
st.subheader("⚙️ أدوات التنظيف")

c1,c2,c3,c4 = st.columns(4)

# تراجع
with c1:
    if st.button("↩️ تراجع"):
        if st.session_state.history:
            st.session_state.df = st.session_state.history.pop()
            st.rerun()

# حذف أعمدة
with c2:
    columns_to_delete = st.multiselect("حذف أعمدة", df.columns)
    if st.button("تنفيذ حذف الأعمدة"):
        if columns_to_delete:
            save_history()
            st.session_state.df.drop(columns=columns_to_delete, inplace=True)
            st.rerun()

# إزالة التكرار
with c3:
    dup = df.duplicated().sum()
    st.write(f"الصفوف المكررة: {dup}")
    if st.button("إزالة التكرار"):
        save_history()
        st.session_state.df.drop_duplicates(inplace=True)
        st.rerun()

# تحميل الملف
with c4:
    buffer = io.BytesIO()
    st.session_state.df.to_excel(buffer, index=False)
    st.download_button("تحميل الملف بعد التنظيف", buffer.getvalue(), "cleaned_data.xlsx")

df = st.session_state.df

# ---------------- البحث ----------------
st.subheader("🔎 البحث داخل البيانات")
search_text = st.text_input("اكتب كلمة للبحث في جميع الأعمدة")

filtered_df = df.copy()
if search_text:
    filtered_df = filtered_df[
        filtered_df.apply(lambda row: row.astype(str).str.contains(search_text, case=False).any(), axis=1)
    ]

# ---------------- فلترة عمود ----------------
st.subheader("📂 فلترة عمود محدد")
filter_column = st.selectbox("اختر العمود للفلترة", df.columns)
unique_values = df[filter_column].dropna().unique()
selected_values = st.multiselect("اختر القيم", unique_values)

if selected_values:
    filtered_df = filtered_df[filtered_df[filter_column].isin(selected_values)]

# ---------------- عرض الجدول ----------------
st.subheader("📄 عرض البيانات")
st.dataframe(filtered_df, use_container_width=True)

# ---------------- كشف التشابه ----------------
st.subheader("🧠 كشف القيم المتشابهة")

similar_column = st.selectbox("اختر العمود المراد فحصه", df.columns, key="similar")

values = df[similar_column].dropna().astype(str).unique()
results = []

for v in values:
    matches = process.extract(v, values, scorer=fuzz.ratio, limit=5)
    for m in matches:
        if m[1] >= 85 and m[0] != v:
            results.append((v, m[0], m[1]))

if results:
    sim_df = pd.DataFrame(results, columns=["القيمة 1","القيمة 2","نسبة التشابه"])
    st.dataframe(sim_df, use_container_width=True)
else:
    st.success("لا توجد قيم متشابهة قو
