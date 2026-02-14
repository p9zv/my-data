# =====================================
# Smart Excel Cleaner - Stable Version
# =====================================

import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="تنظيف ملفات الإكسل", page_icon="📊", layout="wide")

# ===== تصميم =====
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"]{
    direction: rtl;
    background:#0f172a;
    color:white;
}
h1{text-align:center;}

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

st.title("📊 منصة تنظيف وتحليل ملفات الإكسل")

# ===== ذاكرة التطبيق (المهم جداً) =====
if "df" not in st.session_state:
    st.session_state.df = None

if "history" not in st.session_state:
    st.session_state.history = []

def save_history():
    if st.session_state.df is not None:
        st.session_state.history.append(st.session_state.df.copy())
        if len(st.session_state.history) > 15:
            st.session_state.history.pop(0)

# ===== رفع الملف =====
uploaded_file = st.file_uploader("📂 ارفع ملف Excel أو CSV", type=["xlsx","csv"])

if uploaded_file:
    if st.session_state.df is None:
        try:
            if uploaded_file.name.endswith(".csv"):
                st.session_state.df = pd.read_csv(uploaded_file)
            else:
                st.session_state.df = pd.read_excel(uploaded_file)
        except:
            st.error("الملف غير صالح")
            st.stop()

if st.session_state.df is None:
    st.info("⬆️ ارفع ملف للبدء")
    st.stop()

df = st.session_state.df

# ===== احصائيات =====
c1,c2 = st.columns(2)
c1.metric("عدد الصفوف", df.shape[0])
c2.metric("عدد الأعمدة", df.shape[1])

st.divider()

# ===== البحث =====
search = st.text_input("🔍 بحث داخل البيانات")
view_df = df.copy()

if search:
    view_df = view_df[
        view_df.apply(lambda r: r.astype(str).str.contains(search, case=False).any(), axis=1)
    ]

st.dataframe(view_df, use_container_width=True)

st.divider()

# ===== أدوات =====
col1,col2,col3 = st.columns(3)

with col1:
    if st.button("🧹 حذف الصفوف المكررة"):
        save_history()
        st.session_state.df.drop_duplicates(inplace=True)
        st.success("تم حذف التكرار")
        st.rerun()

with col2:
    columns_to_delete = st.multiselect("اختر أعمدة لحذفها", df.columns)
    if st.button("حذف الأعمدة"):
        if columns_to_delete:
            save_history()
            st.session_state.df.drop(columns=columns_to_delete, inplace=True)
            st.success("تم حذف الأعمدة")
            st.rerun()
        else:
            st.warning("اختر عموداً أولاً")

with col3:
    if st.button("↩️ تراجع"):
        if st.session_state.history:
            st.session_state.df = st.session_state.history.pop()
            st.rerun()
        else:
            st.warning("لا توجد خطوات سابقة")

st.divider()

# ===== تحميل =====
output = io.BytesIO()
with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
    st.session_state.df.to_excel(writer, index=False)

st.download_button(
    label="⬇️ تحميل الملف بعد التنظيف",
    data=output.getvalue(),
    file_name="cleaned_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
