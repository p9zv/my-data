# =========================================
# Pro Data Cleaner - Stable Final Version
# =========================================

import streamlit as st
import pandas as pd
import io
from rapidfuzz import fuzz

st.set_page_config(page_title="منصة تنظيف البيانات", page_icon="📊", layout="wide")

# ---------- CSS ----------
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"]{
    direction: rtl;
    background:#020617;
    color:#e5e7eb;
}
.block-container{max-width:1100px;margin:auto;}
h1{text-align:center;}
.stButton>button{
    background:linear-gradient(90deg,#2563eb,#1d4ed8);
    color:white;
    border-radius:12px;
    height:46px;
    width:100%;
}
.stDownloadButton>button{
    background:linear-gradient(90deg,#16a34a,#15803d)!important;
    color:white!important;
    border-radius:12px!important;
    height:52px!important;
    width:100%!important;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 منصة تنظيف البيانات الاحترافية")

# ---------- Session ----------
if "df" not in st.session_state:
    st.session_state.df = None
if "history" not in st.session_state:
    st.session_state.history = []

def save_state():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 20:
        st.session_state.history.pop(0)

# ---------- Upload ----------
file = st.file_uploader("ارفع ملف Excel أو CSV", type=["xlsx","csv"])

if file and st.session_state.df is None:
    try:
        if file.name.endswith(".csv"):
            st.session_state.df = pd.read_csv(file)
        else:
            st.session_state.df = pd.read_excel(file)
    except:
        st.error("فشل قراءة الملف")
        st.stop()

if st.session_state.df is None:
    st.info("⬆️ ارفع ملف للبدء")
    st.stop()

df = st.session_state.df

# ---------- Table ----------
st.dataframe(df, use_container_width=True)

# ---------- Undo ----------
if st.button("↩️ التراجع عن آخر عملية"):
    if st.session_state.history:
        st.session_state.df = st.session_state.history.pop()
        st.rerun()
    else:
        st.warning("لا توجد عمليات سابقة")

st.divider()

tabs = st.tabs(["📊 فحص التكرار", "🧹 حذف أعمدة", "🔁 استبدال", "🧠 التشابه الإملائي"])

# ==================================================
# 1- فحص التكرار
# ==================================================
with tabs[0]:
    col = st.selectbox("اختر العمود", df.columns, key="dupcol")

    if st.button("فحص التكرار"):
        duplicates = df[df.duplicated(subset=[col], keep=False)]

        if duplicates.empty:
            st.success("لا يوجد تكرار مطابق")
        else:
            st.warning(f"وجد {duplicates.shape[0]} صفوف مكررة")
            st.dataframe(duplicates)

        st.subheader("تشابه نصي تقريبي")
        values = df[col].dropna().astype(str).unique()
        found = False

        for i in range(len(values)):
            for j in range(i+1, len(values)):
                score = fuzz.ratio(values[i], values[j])
                if score > 85 and values[i] != values[j]:
                    st.write(f"🔎 {values[i]}  ↔  {values[j]}  ({score}%)")
                    found = True

        if not found:
            st.info("لا يوجد تشابه إملائي ملحوظ")

# ==================================================
# 2- حذف الأعمدة
# ==================================================
with tabs[1]:
    cols = st.multiselect("اختر الأعمدة المراد حذفها", df.columns, key="delcols")

    if st.button("تنفيذ حذف الأعمدة"):
        if cols:
            save_state()
            st.session_state.df.drop(columns=cols, inplace=True)
            st.success("تم حذف الأعمدة")
            st.rerun()
        else:
            st.warning("اختر عموداً")

# ==================================================
# 3- استبدال القيم
# ==================================================
with tabs[2]:
    column = st.selectbox("اختر العمود", df.columns, key="replacecol")
    old = st.text_input("القيمة القديمة")
    new = st.text_input("القيمة الجديدة")

    if st.button("تنفيذ الاستبدال"):
        if old:
            save_state()
            st.session_state.df[column] = st.session_state.df[column].astype(str).str.replace(old, new, regex=False)
            st.success("تم الاستبدال بنجاح")
            st.rerun()
        else:
            st.warning("اكتب القيمة القديمة")

# ==================================================
# 4- التشابه الإملائي (تحديد يدوي)
# ==================================================
with tabs[3]:
    sim_col = st.selectbox("اختر العمود", df.columns, key="simcol")
    threshold = st.slider("درجة التشابه", 70, 100, 85)

    if st.button("اكتشاف النصوص المتقاربة"):
        values = df[sim_col].dropna().astype(str).unique().tolist()
        groups=[]
        used=set()

        for v in values:
            if v in used:
                continue
            group=[v]
            used.add(v)
            for other in values:
                if other not in used:
                    if fuzz.ratio(v,other)>=threshold:
                        group.append(other)
                        used.add(other)
            if len(group)>1:
                groups.append(group)

        if not groups:
            st.success("لا توجد نصوص متقاربة")
        else:
            st.session_state.sim_groups = groups

    if "sim_groups" in st.session_state:
        for idx, g in enumerate(st.session_state.sim_groups):
            st.write("متشابهة:", g)
            replacement = st.text_input(f"النص الموحد للمجموعة {idx+1}", key=f"rep{idx}")
            if st.button(f"تطبيق المجموعة {idx+1}", key=f"apply{idx}"):
                save_state()
                for word in g:
                    st.session_state.df[sim_col]=st.session_state.df[sim_col].astype(str).str.replace(word,replacement,regex=False)
                st.success("تم التعديل")
                st.rerun()

st.divider()

# ---------- Download ----------
output = io.BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    st.session_state.df.to_excel(writer, index=False)

st.download_button(
    label="⬇️ تحميل الملف بعد التنظيف",
    data=output.getvalue(),
    file_name="cleaned_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
