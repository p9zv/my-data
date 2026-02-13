import streamlit as st
import pandas as pd
import io
from rapidfuzz import process, fuzz

# ==================================================
# إعداد الصفحة
# ==================================================
st.set_page_config(page_title="Data Cleaner Pro", page_icon="📊", layout="wide")

# ==================================================
# التصميم الاحترافي (توسيط + RTL + أزرار وسط)
# ==================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

html, body, [data-testid="stAppViewContainer"]{
    direction: rtl;
    font-family: 'Cairo', sans-serif;
    background:#020617;
}

/* العناوين وسط */
h1,h2,h3{
    text-align:center;
    color:#e5e7eb !important;
}

/* النصوص يمين */
p,label,span{
    text-align:right;
    color:#e5e7eb !important;
}

/* صندوق الإحصائيات */
.metric-box{
    background:#0f172a;
    padding:18px;
    border-radius:14px;
    text-align:center;
    border:1px solid rgba(255,255,255,0.08);
}

/* الأزرار بالوسط */
.stButton{
    display:flex;
    justify-content:center;
}

.stButton>button{
    background:#0ea5e9;
    color:white;
    border-radius:12px;
    height:48px;
    width:100%;
    border:none;
    font-size:15px;
}

.stButton>button:hover{
    background:#0284c7;
}

.stDownloadButton{
    display:flex;
    justify-content:center;
}

.stDownloadButton>button{
    background:#22c55e;
    color:white;
    border-radius:12px;
    height:48px;
    width:60%;
    border:none;
}

[data-testid="stDataFrame"]{
    border:1px solid rgba(255,255,255,0.1);
    border-radius:15px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# الذاكرة
# ==================================================
if "df" not in st.session_state:
    st.session_state.df = None

if "history" not in st.session_state:
    st.session_state.history = []

def save_history():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 15:
        st.session_state.history.pop(0)

# ==================================================
# العنوان
# ==================================================
st.title("📊 منصة تنظيف البيانات الاحترافية")

# ==================================================
# رفع الملف
# ==================================================
uploaded_file = st.file_uploader("ارفع ملف Excel أو CSV", type=["xlsx","csv"])

if uploaded_file and st.session_state.df is None:
    if uploaded_file.name.endswith(".csv"):
        st.session_state.df = pd.read_csv(uploaded_file)
    else:
        st.session_state.df = pd.read_excel(uploaded_file)

df = st.session_state.df

if df is None:
    st.info("⬆️ قم برفع ملف البيانات للبدء")
    st.stop()

# ==================================================
# إحصائيات البيانات
# ==================================================
colA, colB = st.columns(2)

with colA:
    st.markdown(f"<div class='metric-box'><h3>عدد الصفوف</h3><h2>{df.shape[0]}</h2></div>", unsafe_allow_html=True)

with colB:
    st.markdown(f"<div class='metric-box'><h3>عدد الأعمدة</h3><h2>{df.shape[1]}</h2></div>", unsafe_allow_html=True)

st.divider()

# ==================================================
# البحث والفلترة
# ==================================================
st.subheader("🔎 البحث والفلترة")

search = st.text_input("بحث داخل كل الجدول")

filtered_df = df.copy()
if search:
    filtered_df = filtered_df[
        filtered_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
    ]

filter_col = st.selectbox("فلترة حسب عمود", df.columns)
values = df[filter_col].dropna().unique()
chosen = st.multiselect("اختر القيم", values)

if chosen:
    filtered_df = filtered_df[filtered_df[filter_col].isin(chosen)]

st.dataframe(filtered_df, use_container_width=True)

# ==================================================
# أدوات التنظيف (قوائم منسدلة)
# ==================================================
st.divider()
st.subheader("🛠️ أدوات التنظيف")

c1, c2, c3, c4, c5 = st.columns(5)

# حذف الأعمدة
with c1:
    with st.popover("🧱 حذف الأعمدة"):
        cols = st.multiselect("الأعمدة", st.session_state.df.columns)
        if st.button("تنفيذ حذف الأعمدة"):
            if cols:
                save_history()
                st.session_state.df.drop(columns=cols, inplace=True)
                st.rerun()

# حذف الصفوف
with c2:
    with st.popover("🗑️ حذف الصفوف"):
        rows = st.multiselect("أرقام الصفوف", st.session_state.df.index.tolist())
        if st.button("تنفيذ حذف الصفوف"):
            if rows:
                save_history()
                st.session_state.df.drop(index=rows, inplace=True)
                st.rerun()

# الاستبدال
with c3:
    with st.popover("🔁 استبدال القيم"):
        col = st.selectbox("العمود", st.session_state.df.columns)
        old = st.text_input("القيمة القديمة")
        new = st.text_input("القيمة الجديدة")
        if st.button("تنفيذ الاستبدال"):
            if old != "":
                save_history()
                st.session_state.df[col] = st.session_state.df[col].astype(str).str.replace(old, new, regex=False)
                st.rerun()

# إزالة التكرار
with c4:
    with st.popover("♻️ إزالة التكرار"):
        dup = st.session_state.df.duplicated().sum()
        st.write(f"عدد الصفوف المكررة: {dup}")
        if st.button("إزالة الآن"):
            save_history()
            st.session_state.df.drop_duplicates(inplace=True)
            st.rerun()

# كشف التشابه
with c5:
    with st.popover("🧠 كشف التشابه"):
        sim_col = st.selectbox("اختر العمود", st.session_state.df.columns)
        values = st.session_state.df[sim_col].dropna().astype(str).unique()
        sim = []
        for v in values:
            matches = process.extract(v, values, scorer=fuzz.ratio, limit=5)
            for m in matches:
                if m[1] >= 85 and m[0] != v:
                    sim.append((v, m[0], m[1]))

        if sim:
            sim_df = pd.DataFrame(sim, columns=["القيمة 1","القيمة 2","نسبة التشابه"])
            st.dataframe(sim_df, use_container_width=True)
        else:
            st.info("لا توجد قيم متشابهة")

# ==================================================
# تصدير الملف
# ==================================================
st.divider()
st.subheader("📥 تحميل الملف بعد التنظيف")

buffer = io.BytesIO()
st.session_state.df.to_excel(buffer, index=False)
st.download_button("تحميل Excel", buffer.getvalue(), "cleaned_data.xlsx")
