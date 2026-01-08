# 房屋水电收据生成器 (Rent Receipt Generator)

这是一个用于管理简易房屋出租、水电费计算及收据生成的 Streamlit 网页应用。

## 📁 目录结构

*   `app.py`: 应用程序入口文件，包含主要的界面和逻辑。
*   `utils.py`: 工具库，包含图片生成、绘图辅助函数。
*   `rooms_maan.json`: **马安** 地区的房间数据（房租、水电费率、历史读数）。
*   `rooms_wulan.json`: **吴栏** 地区的房间数据。
*   `receipt_template.png`: 收据背景模板图片。
*   `requirements.txt`: Python 依赖库列表。
*   `receipts/`: (文件夹) 存放生成的收据图片。

## 🚀 快速开始

1.  **安装依赖**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **运行应用**:
    ```bash
    streamlit run app.py
    ```

## 🛠️ 功能说明

1.  **多地点管理**: 支持“马安”和“吴栏”两个地点，数据独立存储。
2.  **历史数据**: 支持 2026-2036 年的历史读数记录，自动调取上月读数作为基准。
3.  **收据生成**: 根据录入的水电读数，自动计算费用并生成 JPG/PNG 格式收据。
4.  **数据管理**: 支持在侧边栏修改房间基础信息（租金、单价）或修正历史读数。

## 🔐 部署与密码设置

为了保护您的数据，本项目启用了简单的密码验证。

### 本地运行
默认密码为 `admin`。您可以在 `.streamlit/secrets.toml` 文件中修改：
```toml
password = "您的密码"
```

### 部署到 Streamlit Cloud
在将代码上传到 GitHub 并部署到 Streamlit Cloud 时，如果不配置密码，应用将报错。
请在 Streamlit Cloud 的应用仪表盘中：
1.  点击 App 右下角的 **Settings** -> **Secrets**。
2.  在编辑框中粘贴以下内容并保存：
    ```toml
    password = "您想设置的复杂密码"
    ```
3.  重启应用即可生效。

## 📝 注意事项

*   请定期备份 `.json` 数据文件，以防丢失。
*   生成的收据图片会保存在 `receipts` 文件夹中，文件名为 `地点_房号_年月.png`。
