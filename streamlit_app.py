import streamlit as st
import pandas as pd
import io
from rapidfuzz import process, fuzz

# ======================================================
# إعداد الصفحة
# ======================================================
st.set_page_config(page_title="Data Cleaner Pro", page_icon="📊", layout="wide")

# ======================================================
# CSS تصميم احترافي
# ======================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

html, body, [data-testid="stAppViewContainer"]{
    direction: rtl;
    font-family: 'Cairo', sans-serif;
    background:#020617;
}

h1,h2,h3{
    text-align:center;
    color:#e5e7eb !important;
}

p,label,span{
    text-align:right;
    color:#e5e7eb !important;
}

.metric-box{
    background:#0f172a;
    padding:18px;
    border-radius:14px;
    text-align:center;
    border:1px solid rgba(255,255,255,0.08);
}

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
    border-radius:14px;
    height:52px;
    font-size:17px;
    border:none;
}

[data-testid="stDataFrame"]{
    border:1px solid rgba(255,255,255,0.1);
    border-radius:15px;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# Session State
# ======================================================
if "df" not in st.session_state:
    st.session_state.df = None

if "history" not in st.session_state:
    st.session_state.history = []

if "last_file" not in st.session_state:
    st.session_state.last_file = None


def save_history():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 20:
        st.session_state.history.pop(0)

# ======================================================
# العنوان
# ======================================================
st.title("📊 منصة تنظيف البيانات الاحترافية")

# ======================================================
# رفع الملف
# ======================================================
uploaded_file = st.file_uploader(
    "📂 ارفع ملف Excel أو CSV",
    type=["xlsx", "csv"],
    key="uploader"
)

# عند إزالة الملف
if uploaded_file is None:
    st.session_state.df = None
    st.session_state.last_file = None
    st.session_state.history = []
    st.info("⬆️ الرجاء رفع ملف بيانات للبدء")
    st.stop()

# تحميل الملف الجديد
file_id = uploaded_file.name + str(uploaded_file.size)

if st.session_state.last_file != file_id:
    if uploaded_file.name.endswith(".csv"):
        st.session_state.df = pd.read_csv(uploaded_file)
    else:
        st.session_state.df = pd.read_excel(uploaded_file)

    st.session_state.history = []
    st.session_state.last_file = file_id

df = st.session_state.df

# ======================================================
# معلومات البيانات
# ======================================================
c1, c2 = st.columns(2)

with c1:
    st.markdown(
        f"<div class='metric-box'><h3>عدد الصفوف</h3><h2>{df.shape[0]}</h2></div>",
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        f"<div class='metric-box'><h3>عدد الأعمدة</h3><h2>{df.shape[1]}</h2></div>",
        unsafe_allow_html=True
    )

st.divider()

# ======================================================
# البحث
# ======================================================
search = st.text_input("🔍 بحث داخل الجدول")

view_df = df.copy()
if search:
    view_df = view_df[
        view_df.apply(
            lambda r: r.astype(str).str.contains(search, case=False).any(),
            axis=1
        )
    ]

# ======================================================
# عرض الجدول
# ======================================================
st.dataframe(view_df, use_container_width=True, hide_index=True)

# ======================================================
# زر التراجع تحت الجدول (في المنتصف)
# ======================================================
col_left, col_mid, col_right = st.columns([2,1,2])

with col_mid:
    if st.button("↩️ تراجع"):
        if len(st.session_state.history) > 0:
            st.session_state.df = st.session_state.history.pop()
            st.rerun()

st.divider()

# ======================================================
# الأدوات
# ======================================================

# حذف عدة أعمدة
with st.expander("🗑️ حذف أعمدة متعددة"):
    cols = st.multiselect("اختر الأعمدة", df.columns)
    if st.button("تنفيذ حذف الأعمدة"):
        save_history()
        st.session_state.df.drop(columns=cols, inplace=True)
        st.rerun()

# حذف صف برقم الصف
with st.expander("🧹 حذف صف برقم الصف"):
    st.write("اكتب رقم الصف كما يظهر في الجدول (يبدأ من 1)")

    row_number = st.number_input(
        "رقم الصف",
        min_value=1,
        max_value=len(df),
        step=1
    )

    if st.button("تنفيذ حذف الصف"):
        save_history()
        index_to_drop = row_number - 1
        st.session_state.df = df.drop(df.index[index_to_drop])
        st.rerun()

# استبدال القيم
with st.expander("🔁 استبدال نص أو رقم"):
    rcol = st.selectbox("العمود", df.columns, key="rep")
    old = st.text_input("القيمة القديمة")
    new = st.text_input("القيمة الجديدة")
    if st.button("تنفيذ الاستبدال"):
        save_history()
        st.session_state.df[rcol] = (
            st.session_state.df[rcol]
            .astype(str)
            .str.replace(old, new, regex=False)
        )
        st.rerun()

# إزالة التكرار
with st.expander("📑 إزالة التكرار"):
    st.write("عدد الصفوف المكررة:", df.duplicated().sum())
    if st.button("حذف التكرار"):
        save_history()
        st.session_state.df.drop_duplicates(inplace=True)
        st.rerun()

# كشف التشابه
with st.expander("🧠 كشف النصوص المتشابهة"):
    sim_col = st.selectbox("اختر العمود", df.columns, key="sim")
    values = df[sim_col].dropna().astype(str).unique()
    results = []
    for v in values[:200]:
        match, score, _ = process.extractOne(v, values, scorer=fuzz.ratio)
        if score > 85 and v != match:
            results.append((v, match, score))

    if results:
        st.dataframe(
            pd.DataFrame(results, columns=["النص", "مشابه له", "نسبة التشابه"]),
            use_container_width=True
        )
    else:
        st.success("لا يوجد تشابه قوي")

st.divider()

# ======================================================
# زر التحميل في المنتصف
# ======================================================
left, center, right = st.columns([2,3,2])

with center:
    buffer = io.BytesIO()
    st.session_state.df.to_excel(buffer, index=False)
    st.download_button(
        "⬇️ تحميل ملف Excel النظيف",
        buffer.getvalue(),
        "cleaned_data.xlsx",
        use_container_width=True
    )
