import streamlit as st
import pandas as pd
import io
from difflib import SequenceMatcher

# 1. إعدادات الصفحة والظهور في محركات البحث
st.set_page_config(
    page_title="محلل البيانات الذكي | Excel Analyzer",
    page_icon="📊",
    layout="wide"
)

# 2. تصميم CSS (بنفسجي عصري وسلس)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .stButton>button { 
        background-image: linear-gradient(45deg, #6a11cb 0%, #2575fc 100%); 
        color: white; border-radius: 12px; transition: 0.3s; border: none; height: 3em; width: 100%;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(106, 17, 203, 0.4); }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .reportview-container .main { background: #fafafa; }
    </style>
    """, unsafe_allow_html=True)

# 3. دالة كشف التشابه
def are_similar(str1, str2, threshold=0.8):
    return SequenceMatcher(None, str1, str2).ratio() > threshold

# 4. إدارة الحالة (التراجع والإعادة)
if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.redo_stack = []

def save_step(df):
    st.session_state.history.append(df.copy())
    if len(st.session_state.history) > 15: # حفظ آخر 15 خطوة
        st.session_state.history.pop(0)
    st.session_state.redo_stack = []

# --- واجهة المستخدم ---
st.markdown("<h1 style='text-align: center; color: #6a11cb;'>📊 مختبر البيانات الاحترافي</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>نظف، حلل، وعدل ملفات Excel و CSV بكل سهولة</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📥 ارفع ملفك هنا (Excel, CSV)", type=["xlsx", "xls", "csv"])

if uploaded_file:
    if 'df' not in st.session_state:
        try:
            if uploaded_file.name.endswith('.csv'):
                df_init = pd.read_csv(uploaded_file)
            else:
                df_init = pd.read_excel(uploaded_file)
            st.session_state.df = df_init
            st.session_state.history = [df_init.copy()]
        except Exception as e:
            st.error(f"خطأ في قراءة الملف: {e}")

    if 'df' in st.session_state:
        df = st.session_state.df

        # شريط التراجع والإعادة والتصدير
        st.divider()
        c_undo, c_redo, c_exp = st.columns([1, 1, 2])
        with c_undo:
            if st.button("⬅️ تراجع (Undo)") and len(st.session_state.history) > 1:
                st.session_state.redo_stack.append(st.session_state.history.pop())
                st.session_state.df = st.session_state.history[-1].copy()
                st.rerun()
        with c_redo:
            if st.button("➡️ إعادة (Redo)") and st.session_state.redo_stack:
                next_step = st.session_state.redo_stack.pop()
                st.session_state.history.append(next_step)
                st.session_state.df = next_step.copy()
                st.rerun()
        with c_exp:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("💾 تحميل الملف النهائي (Excel)", data=output.getvalue(), file_name="Cleaned_Data.xlsx")

        # التبويبات (Tabs)
        tab1, tab2, tab3 = st.tabs(["✂️ حذف وتعديل", "🔄 استبدال ذكي", "🔍 كشف التشابه والمتكررات"])

        with tab1:
            st.subheader("إدارة الأعمدة والصفوف")
            selected_cols = st.multiselect("اختر الأعمدة للحذف:", df.columns)
            if st.button("🗑️ حذف الأعمدة المختارة"):
                if selected_cols:
                    save_step(df)
                    st.session_state.df = df.drop(columns=selected_cols)
                    st.success("تم الحذف!")
                    st.rerun()
                else: st.warning("الرجاء اختيار أعمدة")

        with tab2:
            st.subheader("استبدال القيم (نصوص أو أرقام)")
            col_in1, col_in2 = st.columns(2)
            old_v = col_in1.text_input("القيمة القديمة")
            new_v = col_in2.text_input("القيمة الجديدة")
            if st.button("🔄 تنفيذ الاستبدال في كل الجدول"):
                if old_v:
                    save_step(df)
                    # محاولة معالجة الأرقام
                    ov = float(old_v) if old_v.replace('.','',1).isdigit() else old_v
                    nv = float(new_v) if new_v.replace('.','',1).isdigit() else new_v
                    st.session_state.df = df.replace(ov, nv)
                    st.success("تم الاستبدال بنجاح")
                    st.rerun()

        with tab3:
            st.subheader("تحليل البيانات الذكي")
            target_col = st.selectbox("اختر العمود للفحص:", df.columns)
            col_b1, col_b2 = st.columns(2)
            
            if col_b1.button("📋 عرض القيم المتكررة"):
                dups = df[target_col].value_counts()
                st.write(dups[dups > 1])

            if col_b2.button("🔍 كشف نصوص متشابهة كتابياً"):
                unique_vals = df[target_col].dropna().unique().astype(str)
                checked = set()
                found = False
                for i, v1 in enumerate(unique_vals):
                    if v1 in checked: continue
                    group = [v1]
                    for v2 in unique_vals[i+1:]:
                        if are_similar(v1, v2):
                            group.append(v2)
                            checked.add(v2)
                    if len(group) > 1:
                        found = True
                        with st.expander(f"📍 مجموعة متشابهة: {v1}"):
                            st.write(f"القيم المكتشفة: {', '.join(group)}")
                            u_name = st.text_input("توحيد المجموعة إلى:", value=v1, key=f"u_{v1}")
                            if st.button("✅ اعتماد التوحيد", key=f"b_{v1}"):
                                save_step(df)
                                st.session_state.df[target_col] = st.session_state.df[target_col].replace(group, u_name)
                                st.rerun()
                    checked.add(v1)
                if not found: st.info("لا توجد نصوص متشابهة")

        # عرض الجدول
        st.divider()
        st.subheader("👀 معاينة البيانات الحالية")
        st.dataframe(df, use_container_width=True)

