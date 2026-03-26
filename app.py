import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta

# 页面配置
st.set_page_config(
    page_title="无人机监控系统",
    page_icon="🚁",
    layout="wide"
)

# 初始化会话状态
if 'heartbeat_data' not in st.session_state:
    st.session_state.heartbeat_data = []
if 'flight_active' not in st.session_state:
    st.session_state.flight_active = False
if 'drone_position' not in st.session_state:
    st.session_state.drone_position = {'lat': 32.3904, 'lon': 118.7128, 'alt': 0}
if 'battery' not in st.session_state:
    st.session_state.battery = 100
if 'flight_time' not in st.session_state:
    st.session_state.flight_time = 0

# 导航菜单
menu = st.sidebar.selectbox(
    "选择功能",
    ["航线规划", "飞行监控", "飞行控制", "坐标系转换"]
)

# 界面一：航线规划
if menu == "航线规划":
    st.title("🚁 航线规划")
    st.markdown("---")
    
    # 地图显示区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("地图展示")
        
        # 使用Streamlit内置地图
        map_data = pd.DataFrame({
            'lat': [32.3904],
            'lon': [118.7128]
        })
        st.map(map_data, zoom=15)
    
    with col2:
        st.subheader("航线设置")
        
        # 起点A
        st.markdown("### 起点 A")
        lat_a = st.number_input("纬度", value=32.3904, min_value=32.0, max_value=33.0, step=0.0001, key='lat_a')
        lon_a = st.number_input("经度", value=118.7128, min_value=118.0, max_value=119.0, step=0.0001, key='lon_a')
        
        # 终点B
        st.markdown("### 终点 B")
        lat_b = st.number_input("纬度", value=32.3920, min_value=32.0, max_value=33.0, step=0.0001, key='lat_b')
        lon_b = st.number_input("经度", value=118.7140, min_value=118.0, max_value=119.0, step=0.0001, key='lon_b')
        
        # 计算距离
        def calculate_distance(lat1, lon1, lat2, lon2):
            from math import radians, cos, sin, asin, sqrt
            R = 6371
            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)
            a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            distance = R * c
            return distance
        
        distance = calculate_distance(lat_a, lon_a, lat_b, lon_b)
        st.metric("航线距离", f"{distance:.2f} 公里")
        
        # 障碍物管理
        st.markdown("### 障碍物管理")
        obstacle_areas = st.text_area("手动圈选障碍物区域（经纬度列表）", key='obstacle_areas')
        
        if st.button("生成航线"):
            st.success("航线生成成功！")
            st.info(f"从起点 ({lat_a}, {lon_a}) 到终点 ({lat_b}, {lon_b}) 的航线已生成")

# 界面二：飞行监控
elif menu == "飞行监控":
    st.title("🚁 飞行监控")
    st.markdown("---")
    
    # 心跳包数据可视化
    st.subheader("心跳包数据监控")
    
    # 添加自动刷新按钮
    auto_refresh = st.checkbox("自动刷新数据", value=True)
    
    # 生成实时心跳包数据
    if auto_refresh:
        now = datetime.now()
        new_heartbeat = {
            "sequence": len(st.session_state.heartbeat_data),
            "timestamp": now,
            "status": "online"
        }
        st.session_state.heartbeat_data.append(new_heartbeat)
        
        # 保持最近100条数据
        if len(st.session_state.heartbeat_data) > 100:
            st.session_state.heartbeat_data = st.session_state.heartbeat_data[-100:]
    
    # 显示心跳包数据
    if st.session_state.heartbeat_data:
        df = pd.DataFrame(st.session_state.heartbeat_data)
        
        # 折线图
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['sequence'],
            mode='lines+markers',
            name='心跳包序号',
            line=dict(color='#00CC96', width=2)
        ))
        fig.update_layout(
            title="心跳包序号随时间变化",
            xaxis_title="时间",
            yaxis_title="序号",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 显示最新心跳包信息
        latest = df.iloc[-1]
        st.info(f"最新心跳包: 序号 {latest['sequence']}, 时间 {latest['timestamp'].strftime('%H:%M:%S')}, 状态 {latest['status']}")
    else:
        st.warning("暂无心跳包数据，请开启自动刷新")
    
    # 飞行性能监控
    st.subheader("飞行性能监控")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("电池电量", f"{st.session_state.battery:.1f}%")
        st.metric("飞行高度", f"{st.session_state.drone_position['alt']:.1f} 米")
    
    with col2:
        st.metric("飞行速度", f"{0 if not st.session_state.flight_active else 15} m/s")
        st.metric("飞行姿态", "水平")
    
    with col3:
        st.metric("GPS信号", "良好")
        st.metric("温度", "25°C")
    
    # 电池电量曲线
    st.subheader("电池电量变化")
    battery_data = pd.DataFrame({
        "time": pd.date_range(start=datetime.now() - timedelta(minutes=30), periods=30, freq='T'),
        "battery": np.linspace(100, st.session_state.battery, 30)
    })
    
    battery_fig = go.Figure()
    battery_fig.add_trace(go.Scatter(
        x=battery_data['time'],
        y=battery_data['battery'],
        mode='lines',
        name='电池电量',
        line=dict(color='#FF6B6B', width=2)
    ))
    battery_fig.update_layout(
        title="电池电量变化曲线",
        xaxis_title="时间",
        yaxis_title="电量 (%)",
        height=300
    )
    st.plotly_chart(battery_fig, use_container_width=True)
    
    # 导航通信日志
    st.subheader("导航通信日志")
    log_data = [
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 导航信号正常",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 高度保持稳定",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 电池电压正常",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 航线偏差: 0.5米",
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - GPS定位精度: 2米"
    ]
    
    for log in log_data:
        st.info(log)
    
    # 自动刷新
    if auto_refresh:
        time.sleep(1)
        st.rerun()

# 界面三：飞行控制
elif menu == "飞行控制":
    st.title("🚁 飞行控制")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("飞行状态")
        
        # 飞行控制按钮
        st.markdown("### 飞行操作")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("起飞", disabled=st.session_state.flight_active):
                st.session_state.flight_active = True
                st.success("无人机已起飞！")
        
        with col_b:
            if st.button("降落", disabled=not st.session_state.flight_active):
                st.session_state.flight_active = False
                st.session_state.drone_position['alt'] = 0
                st.success("无人机已降落！")
        
        with col_c:
            if st.button("紧急停止"):
                st.session_state.flight_active = False
                st.session_state.drone_position['alt'] = 0
                st.error("紧急停止已执行！")
        
        # 方向控制
        st.markdown("### 方向控制")
        col_up, col_down, col_left, col_right = st.columns(4)
        
        with col_up:
            if st.button("↑ 前进"):
                if st.session_state.flight_active:
                    st.session_state.drone_position['lat'] += 0.0001
                    st.success("无人机向前移动")
        
        with col_down:
            if st.button("↓ 后退"):
                if st.session_state.flight_active:
                    st.session_state.drone_position['lat'] -= 0.0001
                    st.success("无人机向后移动")
        
        with col_left:
            if st.button("← 左转"):
                if st.session_state.flight_active:
                    st.session_state.drone_position['lon'] -= 0.0001
                    st.success("无人机向左移动")
        
        with col_right:
            if st.button("→ 右转"):
                if st.session_state.flight_active:
                    st.session_state.drone_position['lon'] += 0.0001
                    st.success("无人机向右移动")
        
        # 高度控制
        st.markdown("### 高度控制")
        col_up_alt, col_down_alt = st.columns(2)
        
        with col_up_alt:
            if st.button("↑ 上升"):
                if st.session_state.flight_active:
                    st.session_state.drone_position['alt'] += 10
                    st.success(f"无人机上升至 {st.session_state.drone_position['alt']} 米")
        
        with col_down_alt:
            if st.button("↓ 下降"):
                if st.session_state.flight_active and st.session_state.drone_position['alt'] > 0:
                    st.session_state.drone_position['alt'] -= 10
                    st.success(f"无人机下降至 {st.session_state.drone_position['alt']} 米")
        
        # 显示当前位置
        st.markdown("### 当前位置")
        st.info(f"纬度: {st.session_state.drone_position['lat']:.6f}, 经度: {st.session_state.drone_position['lon']:.6f}, 高度: {st.session_state.drone_position['alt']:.1f} 米")
    
    with col2:
        st.subheader("飞行信息")
        
        # 飞行状态指示
        if st.session_state.flight_active:
            st.success("✈️ 飞行中")
        else:
            st.warning("🛬 已降落")
        
        # 飞行参数
        st.markdown("### 飞行参数")
        st.metric("飞行时间", f"{st.session_state.flight_time} 秒")
        st.metric("电池电量", f"{st.session_state.battery:.1f}%")
        st.metric("飞行高度", f"{st.session_state.drone_position['alt']:.1f} 米")
        st.metric("飞行速度", f"{15 if st.session_state.flight_active else 0} m/s")
        
        # 模拟电池消耗
        if st.session_state.flight_active:
            st.session_state.flight_time += 1
            st.session_state.battery = max(0, st.session_state.battery - 0.01)
            time.sleep(0.1)
            st.rerun()

# 界面四：坐标系转换
elif menu == "坐标系转换":
    st.title("🌐 坐标系转换工具")
    st.markdown("---")
    
    # 坐标系转换函数
    def wgs84_to_gcj02(lat, lon):
        a = 6378245.0
        ee = 0.00669342162296594323
        
        if not (73.66 < lon < 135.05 and 3.86 < lat < 53.55):
            return lat, lon
        
        def transformLat(x, y):
            ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * np.sqrt(np.fabs(x))
            ret += (20.0 * np.sin(6.0 * x * np.pi) + 20.0 * np.sin(2.0 * x * np.pi)) * 2.0 / 3.0
            ret += (20.0 * np.sin(y * np.pi) + 40.0 * np.sin(y / 3.0 * np.pi)) * 2.0 / 3.0
            ret += (160.0 * np.sin(y / 12.0 * np.pi) + 320 * np.sin(y * np.pi / 30.0)) * 2.0 / 3.0
            return ret
        
        def transformLon(x, y):
            ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * np.sqrt(np.fabs(x))
            ret += (20.0 * np.sin(6.0 * x * np.pi) + 20.0 * np.sin(2.0 * x * np.pi)) * 2.0 / 3.0
            ret += (20.0 * np.sin(x * np.pi) + 40.0 * np.sin(x / 3.0 * np.pi)) * 2.0 / 3.0
            ret += (150.0 * np.sin(x / 12.0 * np.pi) + 300.0 * np.sin(x / 30.0 * np.pi)) * 2.0 / 3.0
            return ret
        
        dLat = transformLat(lon - 105.0, lat - 35.0)
        dLon = transformLon(lon - 105.0, lat - 35.0)
        radLat = lat / 180.0 * np.pi
        magic = np.sin(radLat)
        magic = 1 - ee * magic * magic
        sqrtMagic = np.sqrt(magic)
        dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * np.pi)
        dLon = (dLon * 180.0) / (a / sqrtMagic * np.cos(radLat) * np.pi)
        mgLat = lat + dLat
        mgLon = lon + dLon
        return mgLat, mgLon
    
    def gcj02_to_wgs84(lat, lon):
        if not (73.66 < lon < 135.05 and 3.86 < lat < 53.55):
            return lat, lon
        
        def transformLat(x, y):
            ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * np.sqrt(np.fabs(x))
            ret += (20.0 * np.sin(6.0 * x * np.pi) + 20.0 * np.sin(2.0 * x * np.pi)) * 2.0 / 3.0
            ret += (20.0 * np.sin(y * np.pi) + 40.0 * np.sin(y / 3.0 * np.pi)) * 2.0 / 3.0
            ret += (160.0 * np.sin(y / 12.0 * np.pi) + 320 * np.sin(y * np.pi / 30.0)) * 2.0 / 3.0
            return ret
        
        def transformLon(x, y):
            ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * np.sqrt(np.fabs(x))
            ret += (20.0 * np.sin(6.0 * x * np.pi) + 20.0 * np.sin(2.0 * x * np.pi)) * 2.0 / 3.0
            ret += (20.0 * np.sin(x * np.pi) + 40.0 * np.sin(x / 3.0 * np.pi)) * 2.0 / 3.0
            ret += (150.0 * np.sin(x / 12.0 * np.pi) + 300.0 * np.sin(x / 30.0 * np.pi)) * 2.0 / 3.0
            return ret
        
        dLat = transformLat(lon - 105.0, lat - 35.0)
        dLon = transformLon(lon - 105.0, lat - 35.0)
        radLat = lat / 180.0 * np.pi
        magic = np.sin(radLat)
        magic = 1 - 0.00669342162296594323 * magic * magic
        sqrtMagic = np.sqrt(magic)
        dLat = (dLat * 180.0) / ((6378245.0 * (1 - 0.00669342162296594323)) / (magic * sqrtMagic) * np.pi)
        dLon = (dLon * 180.0) / (6378245.0 / sqrtMagic * np.cos(radLat) * np.pi)
        mgLat = lat + dLat
        mgLon = lon + dLon
        return lat * 2 - mgLat, lon * 2 - mgLon
    
    # 转换界面
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("WGS-84 → GCJ-02")
        wgs_lat = st.number_input("WGS-84 纬度", value=32.3904, min_value=-90.0, max_value=90.0, step=0.0001, key='wgs_lat')
        wgs_lon = st.number_input("WGS-84 经度", value=118.7128, min_value=-180.0, max_value=180.0, step=0.0001, key='wgs_lon')
        
        if st.button("转换", key='convert_wgs_to_gcj'):
            gcj_lat, gcj_lon = wgs84_to_gcj02(wgs_lat, wgs_lon)
            st.success(f"GCJ-02 坐标: {gcj_lat:.6f}, {gcj_lon:.6f}")
    
    with col2:
        st.subheader("GCJ-02 → WGS-84")
        gcj_lat = st.number_input("GCJ-02 纬度", value=32.3904, min_value=-90.0, max_value=90.0, step=0.0001, key='gcj_lat')
        gcj_lon = st.number_input("GCJ-02 经度", value=118.7128, min_value=-180.0, max_value=180.0, step=0.0001, key='gcj_lon')
        
        if st.button("转换", key='convert_gcj_to_wgs'):
            wgs_lat, wgs_lon = gcj02_to_wgs84(gcj_lat, gcj_lon)
            st.success(f"WGS-84 坐标: {wgs_lat:.6f}, {wgs_lon:.6f}")
    
    # 批量转换
    st.subheader("批量转换")
    batch_input = st.text_area("输入坐标（每行一个，格式：lat,lon）", key='batch_input')
    
    if st.button("批量转换", key='batch_convert'):
        if batch_input:
            lines = batch_input.strip().split('\n')
            results = []
            for line in lines:
                try:
                    lat, lon = map(float, line.strip().split(','))
                    gcj_lat, gcj_lon = wgs84_to_gcj02(lat, lon)
                    results.append(f"{lat:.6f},{lon:.6f} → {gcj_lat:.6f},{gcj_lon:.6f}")
                except:
                    results.append(f"{line} - 格式错误")
            
            st.text_area("转换结果", '\n'.join(results), height=200, key='batch_results')

# 页脚信息
st.markdown("---")
st.info("💡 系统说明：\n- 航线规划：基于地图实现航线规划和障碍物管理\n- 飞行监控：实时监控心跳包和飞行性能参数\n- 飞行控制：控制无人机起飞、降落和方向移动\n- 坐标系转换：支持WGS-84与GCJ-02坐标系双向转换")
