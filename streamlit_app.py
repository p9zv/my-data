import streamlit as st
import pandas as pd
import io
from rapidfuzz import process, fuzz

# ---------------- إعداد الصفحة ----------------
st.set_page_config(
    page_title="المحلل الاحترافي للبيانات",
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

[data-testid="stDataFrame"]{
    border-radius:15px;
    border:1px solid rgba(255,255,255,0.1);
}

h1,h2,h3,label,p{
    color:#e5e7eb !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- الذاكرة ----------------
if "df" not in st.session_state:
    st.session_state.df = None

if "history" not in st.session_state:
    st.session_state.history = []

def record():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 10:
        st.session_state.history.pop(0)

# ---------------- العنوان ----------------
st.markdown("<h1 style='text-align:center;'>📊 المحلل الاحترافي للبيانات</h1>", unsafe_allow_html=True)

# ---------------- رفع الملف ----------------
file = st.file_uploader("ارفع ملف Excel أو CSV", type=["xlsx","csv"])

if file:
    if file.name.endswith(".csv"):
        st.session_state.df = pd.read_csv(file)
    else:
        st.session_state.df = pd.read_excel(file)

df = st.session_state.df

# ---------------- أدوات التنظيف ----------------
if df is not None:

    st.subheader("⚙️ أدوات التنظيف")

    c1,c2,c3,c4 = st.columns(4)

    # التراجع
    with c1:
        if st.button("↩️ تراجع"):
            if st.session_state.history:
                st.session_state.df = st.session_state.history.pop()
                st.rerun()

    # حذف الأعمدة
    with c2:
        cols = st.multiselect("🗑️ اختر الأعمدة المراد حذفها", df.columns)
        if st.button("تنفيذ الحذف"):
            if cols:
                record()
                st.session_state.df.drop(columns=cols, inplace=True)
                st.rerun()

    # إزالة التكرار
    with c3:
        st.write(f"عدد الصفوف المكررة: {df.duplicated().sum()}")
        if st.button("إزالة التكرار"):
            record()
            st.session_state.df.drop_duplicates(inplace=True)
            st.rerun()

    # تصدير الملف
    with c4:
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button("📥 تحميل الملف بعد التنظيف", data=buffer.getvalue(), file_name="cleaned.xlsx")

# ---------------- البحث داخل البيانات ----------------
if df is not None:

    st.subheader("🔎 البحث داخل الجدول")

    search = st.text_input("اكتب كلمة للبحث داخل جميع الأعمدة")

    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[
            filtered_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
        ]

    st.dataframe(filtered_df, use_container_width=True)

# ---------------- تحليل التكرارات ----------------
if df is not None:

    st.subheader("📊 القيم الأكثر تكرارًا")

    col = st.selectbox("اختر العمود لتحليل التكرار", df.columns)

    counts = df[col].astype(str).value_counts().reset_index()
    counts.columns = ["القيمة","عدد التكرارات"]

    st.dataframe(counts, use_container_width=True)

# ---------------- كشف القيم المتشابهة ----------------
if df is not None:

    st.subheader("🧠 كشف القيم المتشابهة")

    col2 = st.selectbox("اختر العمود", df.columns, key="sim")

    values = df[col2].dropna().astype(str).unique()

    matches_list = []

    for v in values:
        matches = process.extract(v, values, scorer=fuzz.ratio, limit=5)
        for m in matches:
            if m[1] >= 85 and m[0] != v:
                matches_list.append((v, m[0], m[1]))

    if matches_list:
        sim_df = pd.DataFrame(matches_list, columns=["القيمة 1","القيمة 2","نسبة التشابه"])
        st.dataframe(sim_df, use_container_width=True)
    else:
        st.success("لا توجد قيم متشابهة قوية")
