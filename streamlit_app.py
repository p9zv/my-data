import streamlit as st
import pandas as pd
import io
from rapidfuzz import process, fuzz

# إعداد الصفحة
st.set_page_config(page_title="منصة تنظيف البيانات", page_icon="📊", layout="wide")

# ================= التصميم الداكن =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

html, body, [data-testid="stAppViewContainer"]{
    direction: rtl;
    font-family: 'Cairo', sans-serif;
    background-color: #020617;
}

h1,h2,h3,label,p,span{
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
    border:none;
}
</style>
""", unsafe_allow_html=True)

# ================= الذاكرة =================
if "df" not in st.session_state:
    st.session_state.df = None

if "history" not in st.session_state:
    st.session_state.history = []

def save_history():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 10:
        st.session_state.history.pop(0)

# ================= رفع الملف =================
st.title("📊 منصة تنظيف البيانات لمحللي البيانات")

uploaded_file = st.file_uploader("ارفع ملف Excel أو CSV", type=["xlsx","csv"])

if uploaded_file and st.session_state.df is None:
    if uploaded_file.name.endswith(".csv"):
        st.session_state.df = pd.read_csv(uploaded_file)
    else:
        st.session_state.df = pd.read_excel(uploaded_file)

df = st.session_state.df

if df is None:
    st.info("⬆️ قم برفع ملف بيانات للبدء")
    st.stop()

st.write(f"عدد الصفوف: {df.shape[0]} | عدد الأعمدة: {df.shape[1]}")

# ================= أدوات التنظيف =================
st.subheader("⚙️ أدوات التنظيف")
c1, c2, c3, c4 = st.columns(4)

# تراجع
with c1:
    if st.button("↩️ تراجع"):
        if st.session_state.history:
            st.session_state.df = st.session_state.history.pop()
            st.rerun()

# حذف أعمدة
with c2:
    cols_delete = st.multiselect("حدد الأعمدة", df.columns)
    if st.button("🗑️ حذف الأعمدة"):
        if cols_delete:
            save_history()
            st.session_state.df.drop(columns=cols_delete, inplace=True)
            st.rerun()

# حذف التكرار
with c3:
    dup_count = df.duplicated().sum()
    st.write(f"التكرار: {dup_count}")
    if st.button("إزالة التكرار"):
        save_history()
        st.session_state.df.drop_duplicates(inplace=True)
        st.rerun()

# تصدير
with c4:
    buffer = io.BytesIO()
    st.session_state.df.to_excel(buffer, index=False)
    st.download_button("📥 تحميل الملف", buffer.getvalue(), "cleaned_data.xlsx")

df = st.session_state.df

# ================= البحث =================
st.subheader("🔎 البحث داخل البيانات")
search = st.text_input("اكتب كلمة")

filtered_df = df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
    ]

# ================= فلترة =================
st.subheader("📂 فلترة حسب عمود")
filter_col = st.selectbox("اختر العمود", df.columns)
values = df[filter_col].dropna().unique()
chosen = st.multiselect("القيم", values)

if chosen:
    filtered_df = filtered_df[filtered_df[filter_col].isin(chosen)]

# ================= عرض الجدول =================
st.subheader("📄 البيانات")
st.dataframe(filtered_df, use_container_width=True)

# ================= كشف التشابه =================
st.subheader("🧠 كشف القيم المتشابهة")

similar_col = st.selectbox("اختر عمود الفحص", df.columns, key="sim")

vals = df[similar_col].dropna().astype(str).unique()
matches_list = []

for v in vals:
    matches = process.extract(v, vals, scorer=fuzz.ratio, limit=5)
    for m in matches:
        if m[1] >= 85 and m[0] != v:
            matches_list.append((v, m[0], m[1]))

if matches_list:
    sim_df = pd.DataFrame(matches_list, columns=["القيمة 1","القيمة 2","نسبة التشابه"])
    st.dataframe(sim_df, use_container_width=True)
else:
    st.success("لا توجد قيم متشابهة قوية")
