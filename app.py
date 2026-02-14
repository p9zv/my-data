# =========================================
# Pro Data Cleaner - Professional Edition
# =========================================

import streamlit as st
import pandas as pd
import io
from rapidfuzz import process, fuzz

st.set_page_config(page_title="منصة تنظيف البيانات الاحترافية", page_icon="📊", layout="wide")

# ---------- تصميم احترافي ----------
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"]{
    direction: rtl;
    background: #020617;
    color: #e5e7eb;
}
.block-container{
    max-width:1100px;
    margin:auto;
}
h1{
    text-align:center;
    font-size:40px;
}
.stButton>button{
    background:linear-gradient(90deg,#2563eb,#1d4ed8);
    color:white;
    border-radius:14px;
    height:48px;
    font-weight:bold;
    width:100%;
}
.stDownloadButton>button{
    background:linear-gradient(90deg,#16a34a,#15803d)!important;
    color:white!important;
    border-radius:14px!important;
    height:55px!important;
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

def save():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 20:
        st.session_state.history.pop(0)

# ---------- رفع الملف ----------
file = st.file_uploader("ارفع ملف Excel أو CSV", type=["xlsx","csv"])

if file:
    if st.session_state.df is None:
        if file.name.endswith(".csv"):
            st.session_state.df = pd.read_csv(file)
        else:
            st.session_state.df = pd.read_excel(file)

if st.session_state.df is None:
    st.info("⬆️ ارفع ملف للبدء")
    st.stop()

df = st.session_state.df

# ---------- معلومات ----------
c1,c2 = st.columns(2)
c1.metric("عدد الصفوف", df.shape[0])
c2.metric("عدد الأعمدة", df.shape[1])

st.divider()

# ---------- عرض ----------
st.dataframe(df, use_container_width=True)

st.divider()

# ====================================================
# الأدوات
# ====================================================

tabs = st.tabs(["🧹 تنظيف", "🔁 استبدال", "🧠 تشابه إملائي", "↩️ تراجع"])

# --------- تنظيف ---------
with tabs[0]:
    st.subheader("حذف التكرار")
    if st.button("تنفيذ حذف التكرار"):
        save()
        st.session_state.df.drop_duplicates(inplace=True)
        st.success("تم حذف الصفوف المكررة")
        st.rerun()

# --------- استبدال ---------
with tabs[1]:
    st.subheader("استبدال داخل عمود")

    column = st.selectbox("اختر العمود", df.columns)
    old_value = st.text_input("القيمة القديمة")
    new_value = st.text_input("القيمة الجديدة")

    if st.button("تنفيذ الاستبدال"):
        if old_value != "":
            save()
            st.session_state.df[column] = st.session_state.df[column].astype(str).str.replace(old_value, new_value, regex=False)
            st.success("تم الاستبدال في كامل العمود")
            st.rerun()
        else:
            st.warning("اكتب القيمة القديمة أولاً")

# --------- التشابه الإملائي ---------
with tabs[2]:
    st.subheader("توحيد الكلمات المتشابهة")

    sim_col = st.selectbox("اختر العمود المراد توحيده", df.columns)

    threshold = st.slider("درجة التشابه", 70, 100, 85)

    if st.button("فحص التشابه"):
        values = df[sim_col].dropna().astype(str).unique().tolist()
        groups = {}

        for val in values:
            match = process.extractOne(val, groups.keys(), scorer=fuzz.ratio)
            if match and match[1] >= threshold:
                groups[match[0]].append(val)
            else:
                groups[val] = [val]

        st.write("المجموعات المكتشفة:")
        for k,v in groups.items():
            st.write(f"**{k}** ← {v}")

        if st.button("تطبيق التوحيد"):
            save()
            mapping={}
            for main,vars in groups.items():
                for x in vars:
                    mapping[x]=main
            st.session_state.df[sim_col]=st.session_state.df[sim_col].astype(str).replace(mapping)
            st.success("تم توحيد القيم المتشابهة")
            st.rerun()

# --------- التراجع ---------
with tabs[3]:
    if st.button("العودة لآخر خطوة"):
        if st.session_state.history:
            st.session_state.df = st.session_state.history.pop()
            st.rerun()
        else:
            st.warning("لا توجد خطوات سابقة")

st.divider()

# ---------- تحميل ----------
output = io.BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    st.session_state.df.to_excel(writer, index=False)

st.download_button(
    label="⬇️ تحميل الملف بعد التنظيف",
    data=output.getvalue(),
    file_name="cleaned_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
