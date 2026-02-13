import streamlit as st
import pandas as pd
import io
from difflib import SequenceMatcher

# 1. إعدادات الصفحة الاحترافية
st.set_page_config(page_title="Data Processor Pro", page_icon="📊", layout="wide")

# 2. تصميم CSS متقدم (بدون إيموجي، تركيز على الحدود والألوان الرصينة)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    
    /* تصميم الأزرار الاحترافي */
    .stButton>button { 
        background: #6200ea;
        color: white; border-radius: 8px; border: none;
        padding: 0.5rem 1rem; font-weight: 600; width: 100%;
    }
    .stButton>button:hover { background: #3700b3; border: none; }
    
    /* صناديق البيانات */
    .data-card {
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 10px;
        background-color: #ffffff;
        margin-bottom: 10px;
    }
    
    /* إخفاء الإيموجي الافتراضي من التبويبات */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
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
    if len(st.session_state.history) > 10: st.session_state.history.pop(0)

# --- الواجهة الرئيسية ---
st.markdown("<h2 style='text-align: center; color: #4527a0;'>منصة معالجة وتنظيف البيانات</h2>", unsafe_allow_html=True)

# منطقة الرفع
with st.container():
    uploaded_file = st.file_uploader("قم بسحب وإفلات الملف هنا", type=["xlsx", "csv"], help="يدعم ملفات Excel و CSV")

if uploaded_file:
    if st.session_state.df is None:
        try:
            st.session_state.df = pd.read_excel(uploaded_file) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file)
            save_step()
        except Exception as e:
            st.error(f"حدث خطأ أثناء تحميل الملف: {e}")

    if st.session_state.df is not None:
        df = st.session_state.df

        # شريط الأدوات العلوي (Toolbar)
        col_tool1, col_tool2, col_tool3 = st.columns([1, 1, 2])
        with col_tool1:
            if st.button("Undo", icon=":material/undo:"):
                if len(st.session_state.history) > 1:
                    st.session_state.history.pop()
                    st.session_state.df = st.session_state.history[-1].copy()
                    st.rerun()
        with col_tool3:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False)
            st.download_button("Export Excel", data=output.getvalue(), file_name="Cleaned_Data.xlsx", icon=":material/download:")

        # التبويبات الرئيسية بأيقونات مادية
        tab_clean, tab_view = st.tabs(["Smart Cleaning", "Data Explorer"])

        with tab_clean:
            st.markdown("#### فحص وتوحيد البيانات المتكررة")
            st.info("سيقوم النظام بمقارنة النصوص المكتوبة بأشكال مختلفة واقتراح تصحيح موحد لها.", icon=":material/info:")
            
            target_col = st.selectbox("اختر العمود المستهدف للفحص:", df.columns)
            
            if st.button("Start Analysis", icon=":material/analytics:"):
                unique_vals = df[target_col].dropna().unique().astype(str)
                checked = set()
                found_issues = False

                for i, v1 in enumerate(unique_vals):
                    if v1 in checked: continue
                    group = [v1]
                    for v2 in unique_vals[i+1:]:
                        if are_similar(v1, v2):
                            group.append(v2)
                            checked.add(v2)
                    
                    if len(group) > 1:
                        found_issues = True
                        with st.container():
                            st.markdown(f"""
                            <div class="data-card">
                                <strong>تنبيه: مسميات مشتتة مكتشفة</strong><br>
                                <small>القيم الحالية: {', '.join(group)}</small>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            c_in, c_btn = st.columns([3, 1])
                            new_val = c_in.text_input("الاسم الموحد المعتمد:", value=v1, key=f"in_{v1}")
                            if c_btn.button("Confirm", key=f"btn_{v1}", icon=":material/check_circle:"):
                                save_step()
                                st.session_state.df[target_col] = st.session_state.df[target_col].replace(group, new_val)
                                st.rerun()
                    checked.add(v1)
                
                if not found_issues:
                    st.success("البيانات في هذا العمود تبدو موحدة بشكل سليم.", icon=":material/verified:")

        with tab_view:
            # فلترة البحث
            search_query = st.text_input("بحث سريع في الجدول:", placeholder="اكتب للبحث في جميع الحقول...", icon=":material/search:")
            
            display_df = df
            if search_query:
                mask = df.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
                display_df = df[mask]

            st.markdown(f"**عدد الصفوف المستعرضة:** {len(display_df)}")
            st.dataframe(display_df, use_container_width=True)

