# Streamlit 无人机监控系统部署指南

## 一、GitHub 仓库设置

### 1. 创建 GitHub 仓库
1. 登录 GitHub 账号
2. 点击右上角的 "+", 选择 "New repository"
3. 填写仓库信息：
   - Repository name: `drone-monitoring-system`
   - Description: `Streamlit-based drone monitoring system with route planning and flight monitoring`
   - Visibility: 选择 "Public" 或 "Private"
   - 勾选 "Add a README file"
   - 点击 "Create repository"

### 2. 配置本地 Git 仓库
1. 打开命令行终端（PowerShell）
2. 导航到项目目录：
   ```powershell
   cd D:\Trae CN\weikun
   ```
3. 检查当前 Git 配置：
   ```powershell
   git remote -v
   ```
4. 更新远程仓库 URL（替换为你实际的 GitHub 用户名）：
   ```powershell
   git remote set-url origin https://github.com/你的GitHub用户名/drone-monitoring-system.git
   ```
5. 验证远程仓库配置：
   ```powershell
   git remote -v
   ```

### 3. 推送代码到 GitHub
1. 检查当前代码状态：
   ```powershell
   git status
   ```
2. 推送代码到 GitHub：
   ```powershell
   git push -u origin master
   ```
3. 输入 GitHub 用户名和密码（或使用 SSH 密钥）

## 二、Streamlit Cloud 部署

### 1. 登录 Streamlit Cloud
1. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
2. 点击 "Sign in with GitHub"
3. 授权 Streamlit 访问你的 GitHub 账号

### 2. 部署应用
1. 点击 "New app"
2. 在 "Deploy an app" 页面：
   - **Repository**: 选择 `你的GitHub用户名/drone-monitoring-system`
   - **Branch**: 选择 `master`
   - **Main file path**: 输入 `app.py`
   - **App name**: 输入 `drone-monitoring-system`
   - 点击 "Deploy"

### 3. 配置环境变量（可选）
如果需要高德地图 API 密钥：
1. 在 Streamlit Cloud 应用页面，点击 "Settings"
2. 在 "Secrets" 部分，添加：
   ```toml
   [general]
   AMAP_KEY = "你的高德地图API密钥"
   ```
3. 然后在 `app.py` 中修改：
   ```python
   import streamlit as st
   AMAP_KEY = st.secrets["general"]["AMAP_KEY"]
   ```

## 三、使用说明

### 1. 访问应用
部署完成后，Streamlit Cloud 会提供一个 URL，例如：
`https://drone-monitoring-system.streamlit.app`

### 2. 功能使用
- **航线规划**：在左侧菜单选择 "航线规划"，设置起点和终点坐标，查看3D地图
- **飞行监控**：选择 "飞行监控"，查看心跳包数据和飞行性能参数
- **坐标系转换**：选择 "坐标系转换"，进行 WGS-84 和 GCJ-02 坐标系的转换

### 3. 高德地图 API 密钥获取
1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册并登录账号
3. 创建应用，获取 API 密钥
4. 在 `app.py` 中替换 `AMAP_KEY` 为实际密钥

## 四、故障排查

### 1. 部署失败
- 检查 `requirements.txt` 是否包含所有必要的依赖
- 确保 `app.py` 没有语法错误
- 检查 Streamlit Cloud 日志获取详细错误信息

### 2. 地图不显示
- 检查高德地图 API 密钥是否正确
- 确保网络连接正常

### 3. 数据更新问题
- 检查 `st.cache_data` 装饰器的设置
- 确保数据缓存时间设置合理

## 五、项目结构
```
drone-monitoring-system/
├── app.py              # 主应用文件
├── requirements.txt    # 依赖库配置
├── .gitignore          # Git 忽略文件
└── README.md           # 项目说明
```

## 六、技术栈
- Python 3.8+
- Streamlit 1.28.0+
- Plotly 5.17.0+
- Pandas 2.0.0+
- Matplotlib 3.7.0+
- NumPy 1.24.0+
- Requests 2.31.0+

## 七、联系信息
如果遇到部署问题，请参考 Streamlit Cloud 官方文档或联系技术支持。
