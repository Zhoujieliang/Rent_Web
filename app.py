import streamlit as st
import json
import os
import datetime
import math
from utils import generate_receipt_image

# 设置页面配置
st.set_page_config(page_title="房屋水电收据", layout="centered")

# CSS 优化紧凑布局
st.markdown("""
    <style>
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        min-height: 40px;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# 文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(BASE_DIR, "receipt_template.png")
OUTPUT_DIR = os.path.join(BASE_DIR, "receipts")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- 登录验证 ---
def check_password():
    if "password" not in st.secrets:
        st.error("未配置密码")
        return False
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    
    if not st.session_state["password_correct"]:
        pwd = st.text_input("请输入访问密码", type="password")
        if pwd == st.secrets["password"]:
            st.session_state["password_correct"] = True
            st.rerun()
        elif pwd:
            st.error("密码错误")
        return False
    return True

if not check_password():
    st.stop()

# --- 数据加载 ---
def load_data(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def main():
    st.title("🏠 房屋水电收据助手")

    # --- 第一行：基础信息 (地点 | 月份 | 日期 | 房间) ---
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 1.5, 2])
    
    with c1:
        location = st.selectbox("地点", ["马安", "吴栏"], key="loc_select")
        json_filename = "rooms_maan.json" if location == "马安" else "rooms_wulan.json"
        data_file = os.path.join(BASE_DIR, json_filename)
        data = load_data(data_file)
        
    with c2:
        today = datetime.date.today()
        # 默认选当前月
        bill_month_str = st.selectbox("账单月份", [f"{today.year}-{m}" for m in range(1, 13)], index=today.month-1)
        # Parse selected month
        sel_year, sel_month = map(int, bill_month_str.split('-'))
        
    with c3:
        invoice_date = st.date_input("开单日期", today)
        
    with c4:
        room_list = list(data.keys())
        # 保持房间选择状态
        if 'last_room' not in st.session_state:
            st.session_state['last_room'] = room_list[0] if room_list else None
            
        selected_room = st.selectbox("房间号", room_list, index=room_list.index(st.session_state['last_room']) if st.session_state['last_room'] in room_list else 0)
        st.session_state['last_room'] = selected_room

    if not selected_room:
        st.warning("无房间数据")
        return

    # 获取数据
    room_info = data[selected_room]
    history = room_info.get('history', {})
    
    # Key Calculation
    current_key = f"{sel_year}-{sel_month}"
    # Calculate prev key
    if sel_month == 1:
        prev_key = f"{sel_year-1}-12"
    else:
        prev_key = f"{sel_year}-{sel_month-1}"
        
    # Get Records
    prev_record = history.get(prev_key, {'water': 0.0, 'elec': 0.0})
    curr_record = history.get(current_key, None)
    
    last_water = float(prev_record['water'])
    last_elec = float(prev_record['elec'])
    
    # Defaults for inputs
    def_cw = float(curr_record['water']) if curr_record else 0.0
    def_ce = float(curr_record['elec']) if curr_record else 0.0
    
    # Form Layout
    with st.container():
        st.markdown("---")
        
        # --- 第二行：水费 ---
        cw1, cw2, cw3, cw4 = st.columns([1, 1, 1, 1])
        with cw1:
            st.markdown(f"**💧 水费**")
        with cw2:
            st.number_input("上月水", value=last_water, disabled=True, key=f"dis_lw_{location}_{selected_room}_{prev_key}")
        with cw3:
            curr_water = st.number_input("本月水", value=def_cw, step=1.0, key=f"in_cw_{location}_{selected_room}_{current_key}")
        with cw4:
            # Price (Editable, dynamic key)
            price_w = st.number_input("水单价", value=float(room_info.get('water_price', 4.0)), step=0.1, key=f"in_pw_{location}_{selected_room}")

        # --- 第三行：电费 ---
        ce1, ce2, ce3, ce4 = st.columns([1, 1, 1, 1])
        with ce1:
            st.markdown(f"**⚡ 电费**")
        with ce2:
            st.number_input("上月电", value=last_elec, disabled=True, key=f"dis_le_{location}_{selected_room}_{prev_key}")
        with ce3:
            curr_elec = st.number_input("本月电", value=def_ce, step=1.0, key=f"in_ce_{location}_{selected_room}_{current_key}")
        with ce4:
            price_e = st.number_input("电单价", value=float(room_info.get('elec_price', 1.3)), step=0.1, key=f"in_pe_{location}_{selected_room}")

        # --- 第四行：房租 & 计算 ---
        st.markdown("---")
        cr1, cr2 = st.columns([2, 2])
        with cr1:
            rent_val = st.number_input("🏠 房租", value=float(room_info['rent']), step=100.0, key=f"in_rent_{location}_{selected_room}")
        
        with cr2:
            st.write("") # Spacer
            st.write("") 
            # Submit Button acts as Generate
            if st.button("🚀 生成收据", type="primary", use_container_width=True):
                 # Save Data logic
                if curr_water < last_water or curr_elec < last_elec:
                    st.toast("⚠️ 注意：本月读数小于上月", icon="⚠️")
                
                # Update Data Object
                if 'history' not in data[selected_room]:
                    data[selected_room]['history'] = {}
                
                data[selected_room]['history'][current_key] = {
                    "water": curr_water,
                    "elec": curr_elec
                }
                # Optional: Update prices/rent if changed?
                data[selected_room]['rent'] = rent_val
                data[selected_room]['water_price'] = price_w
                data[selected_room]['elec_price'] = price_e
                
                save_data(data_file, data)
                
                # Calcs
                w_usage = curr_water - last_water
                e_usage = curr_elec - last_elec
                w_cost = math.floor(w_usage * price_w)
                e_cost = math.floor(e_usage * price_e)
                total = rent_val + w_cost + e_cost
                
                # Receipt Data
                r_data = {
                    "location_name": location,
                    "room_id": selected_room,
                    "year": invoice_date.year,
                    "month": invoice_date.month,
                    "day": invoice_date.day,
                    "water_last": int(last_water),
                    "water_current": int(curr_water),
                    "water_usage": f"{w_usage:.1f}",
                    "water_cost": f"{w_cost:.2f}",
                    "water_price": str(price_w),
                    "elec_last": int(last_elec),
                    "elec_current": int(curr_elec),
                    "elec_usage": f"{e_usage:.0f}",
                    "elec_cost": f"{e_cost:.2f}",
                    "elec_price": str(price_e),
                    "rent": f"{rent_val:.2f}",
                    "total": f"{total:.2f}"
                }
                
                # Generate
                out_name = f"{location}_{selected_room}_{current_key}.png"
                out_path = os.path.join(OUTPUT_DIR, out_name)
                success, msg = generate_receipt_image(TEMPLATE_FILE, out_path, r_data)
                
                if success:
                    st.session_state['receipt_img'] = out_path
                    st.session_state['receipt_name'] = out_name
                    st.toast("收据生成成功！", icon="✅")
                else:
                    st.error(f"生成失败: {msg}")

    # --- 预览 & 下载 (Always visible if exists) ---
    if 'receipt_img' in st.session_state and os.path.exists(st.session_state['receipt_img']):
        st.markdown("---")
        path = st.session_state['receipt_img']
        name = st.session_state['receipt_name']
        
        c_img, c_btn = st.columns([3, 1])
        with c_img:
            st.image(path, caption="收据预览", width=500)
        with c_btn:
            with open(path, "rb") as f:
                st.download_button(
                    label="📥 下载图片",
                    data=f,
                    file_name=name,
                    mime="image/png",
                    type="primary",
                    use_container_width=True
                )

if __name__ == "__main__":
    main()
