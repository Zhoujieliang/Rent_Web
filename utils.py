import os
from PIL import Image, ImageDraw, ImageFont
import datetime

def get_font():
    """尝试获取系统中支持中文的字体"""
    
    # 1. 优先检查当前目录下是否有字体文件 (适合云端部署)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    local_fonts = ["SimHei.ttf", "simhei.ttf", "font.ttf", "msyh.ttc", "simsun.ttc"]
    
    for f_name in local_fonts:
        f_path = os.path.join(base_dir, f_name)
        if os.path.exists(f_path):
            return f_path

    # 2. Windows 常见中文字体路径 (本地开发备用)
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf", # 黑体
        "C:/Windows/Fonts/simsun.ttc", # 宋体
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf", # Linux 备选
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            return path
    
    return None # 如果没找到，PIL会使用默认字体（可能不支持中文）



def num_to_cn_simple(num):
    """
    数字转中文汉字 (不带单位)
    123 -> 壹贰叁
    """
    try:
        num = int(num)
    except:
        return ""
    
    CN_MAP = dict(zip("0123456789", "零壹贰叁肆伍陆柒捌玖"))
    s = str(num)
    return "".join([CN_MAP[c] for c in s])

def get_digits_map(amount):
    """
    将金额分解为：万 千 百 十 元 角
    返回字典 {'wan': 'x', 'qian': 'x', ...}
    """
    try:
        # 向下取整逻辑在传入 amount 之前处理，或者在这里处理
        # 假设传入的 amount 已经是 float
        # 格式化为 2 位小数
        s = "{:.2f}".format(float(amount))
        parts = s.split('.')
        integer = parts[0]
        decimal = parts[1]
        
        digits = {}
        
        # 角 (小数第1位)
        if len(decimal) >= 1:
            digits['jiao'] = decimal[0]
        else:
            digits['jiao'] = '0'
            
        # 倒序处理整数
        rev_int = integer[::-1]
        units = ['yuan', 'shi', 'bai', 'qian', 'wan']
        
        for i, unit in enumerate(units):
            if i < len(rev_int):
                digits[unit] = rev_int[i]
            else:
                digits[unit] = "" # 默认留空
                
        return digits
    except Exception as e:
        print(f"Error parsing amount {amount}: {e}")
        return {}


def generate_receipt_image(template_path, output_path, data):
    """
    生成收据图片 (Grid 版)
    """
    
    
    try:
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
        
        # 字体
        font_path = get_font()
        # [NEW] 双字号支持
        font_size_norm = 20
        font_size_big = 30 # 大写金额字号
        
        if font_path:
            font_norm = ImageFont.truetype(font_path, font_size_norm)
            font_big = ImageFont.truetype(font_path, font_size_big)
        else:
            font_norm = ImageFont.load_default()
            font_big = ImageFont.load_default()

        fill_color = (0, 0, 0)
        
        # ==========================================
        # 坐标配置 (User Final Version)
        # ==========================================
        # 1. 标题/日期
        pos_date = (654, 33)
        date_fmt = "{y} 年 {m} 月 {d} 日"
        pos_room = (140, 33)

        # 2. 列表
        col_read_x = 200
        col_last_x = 290
        col_usage_x = 380
        
        pos_water_price = (480, 103)
        pos_elec_price = (480, 127)
        
        y_water = 103
        y_elec = 127
        y_rent = 150
        
        pos_rent_text = (290, 150) # 房租文本位置
        
        # 3. Grid 配置 (独立坐标)
        grid_x_map = {
            'wan': 550,
            'qian': 585,
            'bai': 620,
            'shi': 657,
            'yuan': 693,
            'jiao': 728
        }
        
        # 4. 大写配置
        y_cap = 230
        cap_pos_map = {
            'wan': 280,
            'qian': 302,
            'bai': 372,
            'shi': 460,
            'yuan': 540
        }
        
        # 5. 合计
        pos_total = (660, 236)


        # ==========================================
        # 绘制
        # ==========================================
        
        # 日期
        date_str = date_fmt.format(y=data['year'], m=data['month'], d=data['day'])
        draw.text(pos_date, date_str, font=font_norm, fill=fill_color)
        
        # 房号
        # 动态地点前缀
        loc_name = data.get('location_name', '')
        if loc_name:
            room_text = f"{loc_name} {data['room_id']}"
        else:
            room_text = str(data['room_id'])
            
        draw.text(pos_room, room_text, font=font_norm, fill=fill_color)
        
        # 读数 (水)
        draw.text((col_read_x, y_water), str(data['water_current']), font=font_norm, fill=fill_color)
        draw.text((col_last_x, y_water), str(data['water_last']), font=font_norm, fill=fill_color)
        draw.text((col_usage_x, y_water), str(data['water_usage']), font=font_norm, fill=fill_color)
        draw.text(pos_water_price, f"{data.get('water_price', '2.5')}", font=font_norm, fill=fill_color)
        
        # 读数 (电)
        draw.text((col_read_x, y_elec), str(data['elec_current']), font=font_norm, fill=fill_color)
        draw.text((col_last_x, y_elec), str(data['elec_last']), font=font_norm, fill=fill_color)
        draw.text((col_usage_x, y_elec), str(data['elec_usage']), font=font_norm, fill=fill_color)
        draw.text(pos_elec_price, f"{data.get('elec_price', '1.3')}", font=font_norm, fill=fill_color)

        # 房租 (文本 - 整数显示)
        # 转为float后转int再转str，去掉小数
        try:
            rent_val = int(float(data['rent']))
            draw.text(pos_rent_text, str(rent_val), font=font_norm, fill=fill_color)
        except:
            draw.text(pos_rent_text, str(data['rent']), font=font_norm, fill=fill_color)
        
        # --- Grid 金额绘制 (使用独立坐标) ---
        amounts = [
            (data['water_cost'], y_water),
            (data['elec_cost'], y_elec),
            (data['rent'], y_rent)
        ]
        
        for amt_str, y_pos in amounts:
            digits_map = get_digits_map(amt_str)
            for unit, digit in digits_map.items():
                x_pos = grid_x_map.get(unit)
                if x_pos is not None and digit != "":
                    draw.text((x_pos, y_pos), digit, font=font_norm, fill=fill_color)
                    
        # --- 合计 (小写) ---
        draw.text(pos_total, str(data['total']), font=font_norm, fill=fill_color)
        
        # --- 合计 (大写) ---
        total_float = float(data['total'])
        total_int = int(total_float)
        
        cap_val_map = {
            'wan': (total_int // 10000) % 10,
            'qian': (total_int // 1000) % 10,
            'bai': (total_int // 100) % 10,
            'shi': (total_int // 10) % 10,
            'yuan': total_int % 10
        }
        
        has_started = False
        order = ['wan', 'qian', 'bai', 'shi', 'yuan']
        
        for k in order:
            val = cap_val_map[k]
            if val > 0: has_started = True
            
            if has_started or k == 'yuan': 
                 txt = num_to_cn_simple(val)
                 draw.text((cap_pos_map[k], y_cap), txt, font=font_big, fill=fill_color)

        img.save(output_path)
        return True, "收据生成成功！"
        
    except Exception as e:
        import traceback
        return False, f"生成收据失败: {str(e)} \n {traceback.format_exc()}"
    except Exception as e:
        return False, f"生成收据失败: {str(e)}"
