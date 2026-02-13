import streamlit as st
import pandas as pd
import io
from rapidfuzz import process, fuzz

# ---------- إعداد الصفحة ----------
st.set_page_config(page_title="Data Cleaner Pro", page_icon="📊", layout="wide")

# ---------- التصميم ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

html, body, [data-testid="stAppViewContainer"]{
    direction: rtl;
    font-family: 'Cairo', sans-serif;
    background:#020617;
}

h1,h2,h3,label,p{
    color:#e5e7eb !important;
}

.metric-box{
    background:#0f172a;
    padding:18px;
    border-radius:14px;
    text-align:center;
    border:1px solid rgba(255,255,255,0.08);
}

.stButton>button{
    background:#0ea5e9;
    color:white;
    border-radius:10px;
    height:45px;
    border:none;
    width:100%;
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
    width:100%;
}
</style>
""", unsafe_allow_html=True)

# ---------- الذاكرة ----------
if "df" not in st.session_state:
    st.session_state.df = None

if "history" not in st.session_state:
    st.session_state.history = []

def save_history():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 15:
        st.session_state.history.pop(0)

# ---------- رفع الملف ----------
st.title("📊 منصة تنظيف البيانات الاحترافية")

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

# =====================================================
# ======= معلومات البيانات (أول ما يراه المحلل) =======
# =====================================================

colA, colB = st.columns(2)

with colA:
    st.markdown(f"<div class='metric-box'><h3>عدد الصفوف</h3><h2>{df.shape[0]}</h2></div>", unsafe_allow_html=True)

with colB:
    st.markdown(f"<div class='metric-box'><h3>عدد الأعمدة</h3><h2>{df.shape[1]}</h2></div>", unsafe_allow_html=True)

st.divider()

# =====================================================
# ================= حذف الأعمدة ========================
# =====================================================

st.subheader("🧱 حذف الأعمدة غير المهمة")

cols_delete = st.multiselect("اختر الأعمدة المراد حذفها", df.columns)

if st.button("حذف الأعمدة المحددة"):
    if cols_delete:
        save_history()
        st.session_state.df.drop(columns=cols_delete, inplace=True)
        st.rerun()

# =====================================================
# ================= حذف الصفوف ========================
# =====================================================

st.subheader("🗑️ حذف صفوف")

row_indices = st.multiselect(
    "اختر أرقام الصفوف للحذف",
    df.index.tolist()
)

if st.button("حذف الصفوف المحددة"):
    if row_indices:
        save_history()
        st.session_state.df.drop(index=row_indices, inplace=True)
        st.rerun()

# =====================================================
# ================= الاستبدال =========================
# =====================================================

st.subheader("🔁 استبدال القيم")

rep_col = st.selectbox("اختر العمود", df.columns)
old_val = st.text_input("القيمة القديمة")
new_val = st.text_input("القيمة الجديدة")

if st.button("تنفيذ الاستبدال"):
    if old_val != "":
        save_history()
        st.session_state.df[rep_col] = st.session_state.df[rep_col].astype(str).str.replace(old_val, new_val, regex=False)
        st.rerun()

# =====================================================
# ================= البحث والفلترة =====================
# =====================================================

st.subheader("🔎 البحث والفلترة")

search = st.text_input("بحث عام داخل الجدول")

filtered_df = st.session_state.df.copy()

if search:
    filtered_df = filtered_df[
        filtered_df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
    ]

filter_col = st.selectbox("فلترة حسب عمود", st.session_state.df.columns)
vals = st.session_state.df[filter_col].dropna().unique()
chosen = st.multiselect("القيم", vals)

if chosen:
    filtered_df = filtered_df[filtered_df[filter_col].isin(chosen)]

st.dataframe(filtered_df, use_container_width=True)

# =====================================================
# ================= كشف التشابه ========================
# =====================================================

st.subheader("🧠 كشف القيم المتشابهة")

sim_col = st.selectbox("اختر العمود للفحص", st.session_state.df.columns, key="sim")

values = st.session_state.df[sim_col].dropna().astype(str).unique()
similar = []

for v in values:
    matches = process.extract(v, values, scorer=fuzz.ratio, limit=5)
    for m in matches:
        if m[1] >= 85 and m[0] != v:
            similar.append((v, m[0], m[1]))

if similar:
    sim_df = pd.DataFrame(similar, columns=["القيمة 1","القيمة 2","نسبة التشابه"])
    st.dataframe(sim_df, use_container_width=True)
else:
    st.success("لا توجد قيم متشابهة")

# =====================================================
# ================= إزالة التكرار ======================
# =====================================================

st.subheader("♻️ إزالة التكرار")

dup = st.session_state.df.duplicated().sum()
st.write(f"عدد الصفوف المكررة: {dup}")

if st.button("إزالة الصفوف المكررة"):
    save_history()
    st.session_state.df.drop_duplicates(inplace=True)
    st.rerun()

# =====================================================
# ================= التصدير ============================
# =====================================================

st.subheader("📥 تحميل الملف بعد التنظيف")

buffer = io.BytesIO()
st.session_state.df.to_excel(buffer, index=False)
st.download_button("تحميل Excel", buffer.getvalue(), "cleaned_data.xlsx")
