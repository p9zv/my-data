import streamlit as st
import pandas as pd
import io
from difflib import SequenceMatcher

# 1. إعدادات الصفحة
st.set_page_config(page_title="Data Processor Pro", page_icon="📊", layout="wide")

# 2. تصميم الـ CSS الموحد (ثبات الألوان ومنع تداخل الوضع الداكن)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    
    .main { background-color: #ffffff !important; }
    html, body, [class*="css"] { 
        font-family: 'Cairo', sans-serif; 
        text-align: right; direction: rtl; color: #2c3e50 !important;
    }

    h1, h2, h3, h4, p, span, label { color: #2c3e50 !important; }

    /* تنسيق البطاقات */
    .data-card {
        border: 2px solid #6200ea;
        padding: 15px;
        border-radius: 12px;
        background-color: #f8f9fa !important;
        margin-bottom: 10px;
    }
    
    /* تنسيق الأزرار */
    .stButton>button { 
        background: #6200ea !important;
        color: white !important; 
        border-radius: 8px !important;
        font-weight: 700 !important;
        width: 100%;
    }
    
    /* الجداول */
    [data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border: 1px solid #dee2e6 !important;
    }

    /* التبويبات */
    .stTabs [data-baseweb="tab"] {
        color: #6200ea !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. الدوال المنطقية
def are_similar(str1, str2, threshold=0.75):
    s1 = str(str1).strip().lower().replace("أ", "ا").replace("إ", "ا").replace("ة", "ه")
    s2 = str(str2).strip().lower().replace("أ", "ا").replace("إ", "ا").replace("ة", "ه")
    return SequenceMatcher(None, s1, s2).ratio() > threshold

if 'df' not in st.session_state:
    st.session_state.df = None
if 'history' not in st.session_state:
    st.session_state.history = []

def save_step():
    st.session_state.history.append(st.session_state.df.copy())
    if len(st.session_state.history) > 15: st.session_state.history.pop(0)

# --- الواجهة الرئيسية ---
st.markdown("<h2 style='text-align: center; color: #6200ea;'>المنصة المتكاملة لإدارة البيانات</h2>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("قم برفع ملفك (Excel/CSV)", type=["xlsx", "csv"])

if uploaded_file:
    if st.session_state.df is None:
        st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)
        save_step()

    df = st.session_state.df

    # شريط التحكم العلوي
    col_t1, col_t2, col_t3 = st.columns([1, 1, 2])
    with col_t1:
        if st.button("Undo", icon=":material/undo:"):
            if len(st.session_state.history) > 1:
                st.session_state.history.pop()
                st.session_state.df = st.session_state.history[-1].copy()
                st.rerun()
    with col_t3:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button("تصدير الملف النهائي", data=output.getvalue(), file_name="Cleaned_Data.xlsx", icon=":material/download:")

    # التبويبات التي تجمع كل طلباتك
    tab_manual, tab_smart, tab_view = st.tabs(["⚙️ أدوات يدوية", "🧠 أدوات ذكية", "📋 استعراض وبحث"])

    with tab_manual:
        st.markdown("### الإجراءات اليدوية")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🗑️ حذف أعمدة**")
            cols_to_del = st.multiselect("اختر الأعمدة لحذفها:", df.columns)
            if st.button("تأكيد الحذف", icon=":material/delete_sweep:"):
                save_step()
                st.session_state.df.drop(columns=cols_to_del, inplace=True)
                st.rerun()
        
        with col2:
            st.markdown("**🔄 استبدال قيم**")
            old_v = st.text_input("القيمة القديمة (نص أو رقم)")
            new_v = st.text_input("القيمة الجديدة")
            if st.button("تنفيذ الاستبدال الشامل", icon=":material/find_replace:"):
                save_step()
                # معالجة النصوص والأرقام
                ov = float(old_v) if old_v.replace('.','',1).isdigit() else old_v
                nv = float(new_v) if new_v.replace('.','',1).isdigit() else new_v
                st.session_state.df.replace(ov, nv, inplace=True)
                st.rerun()

    with tab_smart:
        st.markdown("### كشف التشابه الإملائي وتوحيده")
        target_col = st.selectbox("اختر عموداً لفحصه (مثل الكلية):", df.columns)
        
        if st.button("بدء التحليل الذكي", icon=":material/psychology:"):
            unique_vals = df[target_col].dropna().unique().astype(str)
            checked = set()
            found = False
            for i, v1 in enumerate(unique_vals):
                if v1 in checked: continue
                group = [v1] + [v2 for v2 in unique_vals[i+1:] if are_similar(v1, v2)]
                if len(group) > 1:
                    found = True
                    st.markdown(f'<div class="data-card">⚠️ تم كشف تشتت في: <b>{v1}</b><br><small>القيم: {", ".join(group)}</small></div>', unsafe_allow_html=True)
                    c_in, c_btn = st.columns([3, 1])
                    new_val = c_in.text_input(f"توحيد المجموعة إلى:", value=v1, key=f"in_{v1}")
                    if c_btn.button("اعتماد", key=f"btn_{v1}", icon=":material/done_all:"):
                        save_step()
                        st.session_state.df[target_col].replace(group, new_val, inplace=True)
                        st.rerun()
                for item in group: checked.add(item)
            if not found: st.success("لا توجد مسميات مشتتة.")

    with tab_view:
        st.markdown("### البحث والاستعراض")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            search_all = st.text_input("البحث الشامل في الجدول:", icon=":material/search:")
        with col_s2:
            filter_col = st.selectbox("البحث في عمود محدد:", ["كل الأعمدة"] + list(df.columns))
            
        display_df = df
        if search_all:
            mask = df.astype(str).apply(lambda x: x.str.contains(search_all, case=False, na=False)).any(axis=1)
            display_df = display_df[mask]
        
        if filter_col != "كل الأعمدة":
            specific_search = st.text_input(f"بحث خاص داخل {filter_col}:")
            if specific_search:
                display_df = display_df[display_df[filter_col].astype(str).str.contains(specific_search, case=False, na=False)]

        st.dataframe(display_df, use_container_width=True)
