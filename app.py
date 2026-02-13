import streamlit as st
import pandas as pd
import io
import streamlit.components.v1 as components

# ============ إعداد الصفحة ============
st.set_page_config(page_title="PRO DATA ANALYZER", page_icon="💎", layout="wide")

# تحميل FontAwesome داخل DOM الحقيقي (مهم جداً)
components.html("""
<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
""", height=0)

# ============ CSS ============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    direction: rtl;
    text-align: right;
    font-family: 'Cairo', sans-serif !important;
    background: #030712 !important;
}

.main-glass-box {
    background: rgba(31, 41, 55, 0.4);
    backdrop-filter: blur(15px);
    border-radius: 28px;
    padding: 30px;
}

.buttons-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    background: rgba(15, 23, 42, 0.6);
    padding: 20px;
    border-radius: 20px;
}

.stButton>button {
    border-radius: 14px !important;
    height: 70px !important;
    font-weight: bold !important;
    font-size: 1.05rem !important;
}

.stats-card {
    background: rgba(17, 24, 39, 0.85);
    border-right: 5px solid #6366f1;
    padding: 25px;
    border-radius: 18px;
    margin-top: 20px;
}

h1, h2, h3, p, label { color: #f8fafc !important; }
</style>
""", unsafe_allow_html=True)

# ============ Session State ============
if "df" not in st.session_state:
    st.session_state.df = None

if "history" not in st.session_state:
    st.session_state.history = []

if "file" not in st.session_state:
    st.session_state.file = None

def record():
    if st.session_state.df is not None:
        st.session_state.history.append(st.session_state.df.copy())
        if len(st.session_state.history) > 20:
            st.session_state.history.pop(0)

# ============ العنوان ============
st.markdown('<div class="main-glass-box">', unsafe_allow_html=True)
st.markdown("<h1 style='text-align:center'><i class='fas fa-shield-halved'></i> المحلل الذكي الاحترافي</h1>", unsafe_allow_html=True)

# ============ رفع الملف ============
uploaded = st.file_uploader("📂 ارفع ملف Excel أو CSV", type=["xlsx","csv"])

if uploaded is not None and uploaded.name != st.session_state.file:
    try:
        if uploaded.name.endswith(".csv"):
            st.session_state.df = pd.read_csv(uploaded)
        else:
            st.session_state.df = pd.read_excel(uploaded)

        st.session_state.file = uploaded.name
        st.session_state.history = []

    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")

# ============ عند وجود بيانات ============
if st.session_state.df is not None:

    df = st.session_state.df

    # أدوات أعلى
    c1, c2 = st.columns(2)

    with c1:
        if st.button("↩️ تراجع"):
            if st.session_state.history:
                st.session_state.df = st.session_state.history.pop()
                st.rerun()

    with c2:
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button("📥 تصدير Excel", buffer.getvalue(), "Pro_Data.xlsx")

    # ============ الأزرار ============
    st.markdown('<div class="buttons-grid">', unsafe_allow_html=True)
    b1, b2, b3, b4 = st.columns(4)

    # استبدال
    with b1:
        with st.popover("🔄 استبدال"):
            old = st.text_input("القيمة القديمة")
            new = st.text_input("القيمة الجديدة")
            if st.button("تنفيذ"):
                record()
                st.session_state.df.replace(old, new, inplace=True)
                st.rerun()

    # حذف أعمدة
    with b2:
        with st.popover("🗑️ حذف أعمدة"):
            cols = st.multiselect("اختر الأعمدة", df.columns)
            if st.button("حذف"):
                record()
                st.session_state.df.drop(columns=cols, inplace=True)
                st.rerun()

    # إزالة التكرار
    with b3:
        with st.popover("📑 إزالة التكرار"):
            st.write("عدد الصفوف المكررة:", df.duplicated().sum())
            if st.button("تنظيف"):
                record()
                st.session_state.df = st.session_state.df.drop_duplicates().reset_index(drop=True)
                st.rerun()

    # تحليل عمود
    with b4:
        analyze_col = st.selectbox("📊 تحليل عمود", df.columns)

    st.markdown('</div>', unsafe_allow_html=True)

    # ============ الفلترة الصحيحة ============
    st.markdown('<div class="stats-card">', unsafe_allow_html=True)

    search = st.text_input("🔎 بحث داخل الجدول")

    if search:
        mask = df.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False))
        filtered_df = df[mask.any(axis=1)].copy()
    else:
        filtered_df = df.copy()

    filtered_df.reset_index(drop=True, inplace=True)

    # ============ تحليل التكرار الصحيح ============
    if analyze_col:

        series = filtered_df[analyze_col].astype(str).str.strip()
        series = series.replace("", "فارغ")
        series = series.fillna("فارغ")

        counts = series.value_counts().reset_index()
        counts.columns = ["القيمة", "عدد التكرارات"]

        st.markdown(
            f"<h3><i class='fas fa-chart-column'></i> تحليل العمود: {analyze_col}</h3>",
            unsafe_allow_html=True
        )

        st.dataframe(counts, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ============ عرض الجدول ============
    st.markdown("<h3><i class='fas fa-table'></i> استعراض البيانات</h3>", unsafe_allow_html=True)
    st.dataframe(filtered_df, use_container_width=True, hide_index=True)

st.markdown('</div>', unsafe_allow_html=True)

# تأثير ضغط الأزرار
components.html("""
<script>
const buttons = window.parent.document.querySelectorAll('button');
buttons.forEach(btn => {
    btn.addEventListener('mousedown', () => btn.style.transform = 'scale(0.96)');
    btn.addEventListener('mouseup', () => btn.style.transform = 'scale(1)');
});
</script>
""", height=0)
