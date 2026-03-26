import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import datetime
import json
import requests
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="无人机监控系统",
    page_icon="🚁",
    layout="wide"
)

# 高德地图API配置
AMAP_KEY = "your_amap_api_key"  # 请替换为实际的高德地图API密钥

# 南京科技职业学院坐标（示例）
CAMPUS_LOCATION = {
    "latitude": 32.3904,
    "longitude": 118.7128
}

# 导航菜单
menu = st.sidebar.selectbox(
    "选择功能",
    ["航线规划", "飞行监控", "坐标系转换"]
)

# 界面一：航线规划
if menu == "航线规划":
    st.title("🚁 航线规划")
    st.markdown("---")
    
    # 地图显示区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("3D地图展示")
        
        # 高德地图HTML
        map_html = f'''<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>高德地图3D展示</title>
            <script type="text/javascript" src="https://webapi.amap.com/maps?v=2.0&key={AMAP_KEY}"></script>
            <style>
                #container {{ width: 100%; height: 600px; }}
            </style>
        </head>
        <body>
            <div id="container"></div>
            <script>
                var map = new AMap.Map('container', {{
                    zoom: 16,
                    center: [118.7128, 32.3904],
                    mapStyle: 'amap://styles/whitesmoke',
                    viewMode: '3D'
                }});
                
                // 添加南京科技职业学院标记
                var marker = new AMap.Marker({{
                    position: [118.7128, 32.3904],
                    title: '南京科技职业学院'
                }});
                marker.setMap(map);
                
                // 缩放监听
                map.on('zoomend', function() {{
                    var zoom = map.getZoom();
                    if (zoom > 17) {{
                        map.setViewMode('2D');
                    }} else {{
                        map.setViewMode('3D');
                    }}
                }});
            </script>
        </body>
        </html>
        '''
        
        # 显示地图
        st.components.v1.html(map_html, height=600)
    
    with col2:
        st.subheader("航线设置")
        
        # 起点A
        st.markdown("### 起点 A")
        lat_a = st.number_input("纬度", value=32.3904, min_value=32.0, max_value=33.0, step=0.0001)
        lon_a = st.number_input("经度", value=118.7128, min_value=118.0, max_value=119.0, step=0.0001)
        
        # 终点B
        st.markdown("### 终点 B")
        lat_b = st.number_input("纬度", value=32.3920, min_value=32.0, max_value=33.0, step=0.0001)
        lon_b = st.number_input("经度", value=118.7140, min_value=118.0, max_value=119.0, step=0.0001)
        
        # 计算距离
        def calculate_distance(lat1, lon1, lat2, lon2):
            from math import radians, cos, sin, asin, sqrt
            R = 6371  # 地球半径
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
        obstacle_areas = st.text_area("手动圈选障碍物区域（经纬度列表）")
        
        if st.button("生成航线"):
            st.success("航线生成成功！")
            # 这里可以添加航线生成的逻辑

# 界面二：飞行监控
elif menu == "飞行监控":
    st.title("🚁 飞行监控")
    st.markdown("---")
    
    # 心跳包数据可视化
    st.subheader("心跳包数据监控")
    
    # 模拟心跳包数据
    @st.cache_data(ttl=1)
    def get_heartbeat_data():
        # 模拟数据
        data = []
        now = datetime.now()
        for i in range(50):
            timestamp = now - datetime.timedelta(seconds=50-i)
            data.append({
                "sequence": i,
                "timestamp": timestamp,
                "status": "online" if i % 2 == 0 else "online"
            })
        return pd.DataFrame(data)
    
    df = get_heartbeat_data()
    
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
    
    # 飞行性能监控
    st.subheader("飞行性能监控")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("电池电量", "85%")
        st.metric("飞行高度", "120 米")
    
    with col2:
        st.metric("飞行速度", "15 m/s")
        st.metric("飞行姿态", "水平")
    
    with col3:
        st.metric("GPS信号", "良好")
        st.metric("温度", "25°C")
    
    # 电池电量曲线
    st.subheader("电池电量变化")
    battery_data = pd.DataFrame({
        "time": pd.date_range(start=datetime.now() - pd.Timedelta(minutes=30), periods=30, freq='T'),
        "battery": np.linspace(100, 85, 30)
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

# 界面三：坐标系转换
elif menu == "坐标系转换":
    st.title("🌐 坐标系转换工具")
    st.markdown("---")
    
    # 坐标系转换函数
    def wgs84_to_gcj02(lat, lon):
        """WGS-84转GCJ-02"""
        # 简化版转换算法
        a = 6378245.0
        ee = 0.00669342162296594323
        
        if out_of_china(lat, lon):
            return lat, lon
        
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
        """GCJ-02转WGS-84"""
        # 简化版转换算法
        if out_of_china(lat, lon):
            return lat, lon
        
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
    
    def out_of_china(lat, lon):
        return not (73.66 < lon < 135.05 and 3.86 < lat < 53.55)
    
    # 转换界面
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("WGS-84 → GCJ-02")
        wgs_lat = st.number_input("WGS-84 纬度", value=32.3904, min_value=-90.0, max_value=90.0, step=0.0001)
        wgs_lon = st.number_input("WGS-84 经度", value=118.7128, min_value=-180.0, max_value=180.0, step=0.0001)
        
        if st.button("转换"):
            gcj_lat, gcj_lon = wgs84_to_gcj02(wgs_lat, wgs_lon)
            st.success(f"GCJ-02 坐标: {gcj_lat:.6f}, {gcj_lon:.6f}")
    
    with col2:
        st.subheader("GCJ-02 → WGS-84")
        gcj_lat = st.number_input("GCJ-02 纬度", value=32.3904, min_value=-90.0, max_value=90.0, step=0.0001)
        gcj_lon = st.number_input("GCJ-02 经度", value=118.7128, min_value=-180.0, max_value=180.0, step=0.0001)
        
        if st.button("转换"):
            wgs_lat, wgs_lon = gcj02_to_wgs84(gcj_lat, gcj_lon)
            st.success(f"WGS-84 坐标: {wgs_lat:.6f}, {wgs_lon:.6f}")
    
    # 批量转换
    st.subheader("批量转换")
    batch_input = st.text_area("输入坐标（每行一个，格式：lat,lon）")
    
    if st.button("批量转换"):
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
            
            st.text_area("转换结果", '\n'.join(results), height=200)

# 页脚信息
st.markdown("---")
st.info("💡 系统说明：\n- 航线规划：基于高德地图实现3D地图展示和航线规划\n- 飞行监控：实时监控心跳包和飞行性能参数\n- 坐标系转换：支持WGS-84与GCJ-02坐标系双向转换")
