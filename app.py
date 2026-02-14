# =========================================
# Data Standardizer PRO (Google Ready)
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
.block-container{max-width:1200px;margin:auto;}
h1{text-align:center;}
.stTextInput input{background:#0f172a;color:white;}
.stButton>button{
    background:linear-gradient(90deg,#2563eb,#1d4ed8);
    color:white;
    border-radius:12px;
    height:46px;
    width:100%;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 منصة توحيد وتنظيف البيانات")

# ---------- Session ----------
if "df" not in st.session_state:
    st.session_state.df = None
if "history" not in st.session_state:
    st.session_state.history = []

def save_state():
    st.session_state.history.append(st.session_state.df.copy())

# ---------- Upload ----------
file = st.file_uploader("ارفع ملف Excel أو CSV", type=["xlsx","csv"])

if file and st.session_state.df is None:
    if file.name.endswith(".csv"):
        st.session_state.df = pd.read_csv(file)
    else:
        st.session_state.df = pd.read_excel(file)

if st.session_state.df is None:
    st.info("⬆️ ارفع ملف للبدء")
    st.stop()

df = st.session_state.df

# ==================================================
# 🔎 فلتر البحث الحرفي
# ==================================================
st.subheader("البحث داخل البيانات")

search_text = st.text_input("اكتب أي كلمة للبحث داخل كامل الجدول")

if search_text:
    mask = df.astype(str).apply(lambda row: row.str.contains(search_text, case=False, na=False)).any(axis=1)
    filtered_df = df[mask]
    st.dataframe(filtered_df, use_container_width=True)
else:
    st.dataframe(df, use_container_width=True)

st.divider()

tabs = st.tabs(["📊 تحليل وتوحيد القيم", "🧹 حذف أعمدة", "🔁 استبدال شامل"])

# ==================================================
# 1️⃣ تحليل التكرار الحقيقي
# ==================================================
with tabs[0]:

    col = st.selectbox("اختر العمود المراد تحليله", df.columns)

    if st.button("تحليل القيم المتكررة"):

        values = df[col].dropna().astype(str)

        freq = values.value_counts()

        st.subheader("أكثر القيم ظهوراً")
        st.dataframe(freq.reset_index().rename(columns={"index":"القيمة",col:"عدد التكرار"}))

        # --- تجميع النصوص المتقاربة ---
        unique_values = list(freq.index)
        groups=[]
        used=set()

        for val in unique_values:
            if val in used:
                continue
            group=[val]
            used.add(val)

            for other in unique_values:
                if other not in used:
                    if fuzz.token_sort_ratio(val,other) > 80:
                        group.append(other)
                        used.add(other)

            if len(group)>1:
                groups.append(group)

        if groups:
            st.subheader("نصوص متقاربة (اختر النص المعتمد)")

            for i,g in enumerate(groups):
                st.write("النصوص المكتشفة:",g)

                canonical = st.text_input(f"النص المعتمد للمجموعة {i+1}", key=f"canon{i}")

                if st.button(f"تطبيق التوحيد {i+1}", key=f"apply{i}"):
                    save_state()
                    for word in g:
                        st.session_state.df[col]=st.session_state.df[col].astype(str).str.replace(word,canonical,regex=False)
                    st.success("تم توحيد النصوص")
                    st.rerun()

        else:
            st.success("لا توجد اختلافات إملائية كبيرة")

# ==================================================
# 2️⃣ حذف أعمدة متعددة
# ==================================================
with tabs[1]:
    cols = st.multiselect("اختر الأعمدة المراد حذفها", df.columns)

    if st.button("تنفيذ الحذف"):
        if cols:
            save_state()
            st.session_state.df.drop(columns=cols, inplace=True)
            st.success("تم حذف الأعمدة")
            st.rerun()

# ==================================================
# 3️⃣ استبدال شامل
# ==================================================
with tabs[2]:
    column = st.selectbox("اختر العمود", df.columns)
    old = st.text_input("النص أو الرقم القديم")
    new = st.text_input("النص الجديد")

    if st.button("تنفيذ الاستبدال"):
        save_state()
        st.session_state.df[column]=st.session_state.df[column].astype(str).str.replace(old,new,regex=False)
        st.success("تم الاستبدال")
        st.rerun()

st.divider()

# ---------- Download ----------
output = io.BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    st.session_state.df.to_excel(writer, index=False)

st.download_button(
    label="⬇️ تحميل الملف بعد التنظيف",
    data=output.getvalue(),
    file_name="cleaned_data.xlsx"
)
