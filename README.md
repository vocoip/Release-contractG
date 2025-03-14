# 合同生成工具 (contractG)

![合同生成界面](https://github.com/user-attachments/assets/d22bcd84-71cc-4a3b-aceb-e5d3e288c604)

## 📢 最新发布 - R1.1 (2025年3月14日)

- **PDF优化**：文件大小从12M缩减至200K
- **新增功能**：拖曳Excel转PDF功能
- **界面优化**：更简洁直观的用户界面
- **Bug修复**：修复多个已知问题

![新版界面](https://github.com/user-attachments/assets/0e2f1a21-181e-46bf-9e40-b8937e33387e)
![微信图片](https://github.com/user-attachments/assets/e6dee3d5-e840-4db0-990d-0ba4ee5fa4d4)

**下载地址**：[https://codeload.github.com/vocoip/Release-contractG/zip/refs/heads/main](https://codeload.github.com/vocoip/Release-contractG/zip/refs/heads/main)

## 📋 项目简介

contractG是一款专为企业设计的合同生成工具，使用Python和PyQt5开发。它能帮助您在短短一分钟内生成专业的合同和报价单，支持电子印章和图片式PDF，大幅提高工作效率。

本工具最初是为个人使用而开发，经过完善后决定免费分享给有需要的企业用户。欢迎测试使用并推荐给周围有需要的朋友。

## 🖼️ 功能展示

![合同示例](https://github.com/user-attachments/assets/d1d2dbd2-2249-4083-bec0-92c375d1fb22)
![报价单示例](https://github.com/user-attachments/assets/201d477b-e6bd-4ab3-87b4-6ad492b526a0)

## 🚀 快速开始

### 安装与运行

1. 从GitHub下载最新版本
2. 解压到本地目录（建议非系统盘）
3. 双击`启动合同生成工具.bat`或`contractG.exe`运行程序

### 初始设置

1. **公司信息设置**：
   - 进入设置，找到公司设置
   - 在解析栏输入开票信息，系统会自动解析
   - 设置为默认公司
   - 上传公司印章（PNG格式，建议印章图像充满整个图片）

2. **数据导入**：
   - 客户和商品数据可通过导出模板，填写后再导入
   - 也可手动添加或从文本解析导入

3. **新客户添加**：
   - 在合同生成页面，点击"新增客户"
   - 输入开票资料，系统会自动解析

## 💡 主要功能

### 1. 合同生成

- 快速选择客户和商品生成合同
- 支持中文首字母快速搜索
- 自动计算合同金额（商品总额+技术服务费）
- 自定义合同编号、签订日期、交货日期
- 自定义付款方式
- 设置报价单有效期
- 支持电子印章和图片式PDF

### 2. 乙方公司管理

- 支持管理多个乙方公司信息
- 设置默认乙方公司
- 从文本解析导入公司信息
- 完整公司信息管理（名称、联系人、电话、地址、银行账户等）
- 支持上传电子印章

### 3. 客户管理

- 添加、编辑、删除客户信息
- 支持从文本解析导入
- 客户信息导入导出功能
- 快速搜索和筛选

### 4. 商品管理

- 添加、编辑、删除商品信息
- 支持从文本解析导入
- 商品信息导入导出功能
- 快速搜索和筛选

### 5. 系统功能

- 打开数据目录和输出目录
- 首次运行自动引导配置
- 系统设置管理

## 🎨 界面特点

- 采用Material Design设计风格
- 统一配色方案和视觉元素
- 响应式布局，适应不同屏幕尺寸
- 表格行交替颜色，提高可读性
- 按钮颜色区分功能类型
- 支持高DPI显示

## 📝 使用指南

### 合同生成流程

1. 切换到"合同生成"标签页
2. 选择客户（或添加新客户）
3. 选择商品并添加到合同
4. 设置合同信息（编号、日期、付款方式等）
5. 选择乙方公司
6. 点击"生成合同"按钮

### 注意事项

1. 首次使用前请确保已正确配置乙方公司信息（含电子印章）
2. 如遇杀毒软件报警，请将程序添加到白名单
3. 建议将程序安装在非系统盘，并关闭杀毒软件对程序目录的实时监控
4. 合同编号格式为：SC-YYYYMMDD-XXX
5. 乙方未设置印章时，默认只生成Excel格式

## 🔜 开发计划

1. **合同条款自定义**：即将添加，同时修复已发现的小Bug
2. **合同模板自定义**：重要但有难度，正在解决单元格合并、样式等问题
3. **文件转换增强**：支持选择Excel和PDF文件，转换为带印章的图片式PDF
4. **数据备份与恢复**：增加数据备份和恢复功能
5. **用户体验优化**：持续改进界面和操作流程

## 📜 版本历史

### v1.1.0 (2025-03-14)
- **新增功能**：
  - Excel转PDF工具，支持拖放转换
  - 图片式PDF选项，提高PDF兼容性
  - 状态反馈和进度显示
  - 公司管理功能（添加、编辑、删除和设置默认公司）
  - 自定义图标系统
  - 报价单印章处显示"报价方签章处"文字
- **改进**：
  - 优化界面布局和交互体验
  - 改进文件命名规则，添加随机后缀避免重名
  - 完善错误处理和提示信息
  - 添加拖放功能，简化文件操作
- **修复**：
  - 印章添加时的文字对齐问题
  - 文件生成时的随机后缀缺失问题

### v1.0.0 (2024-03-12)
- 初始版本发布
- 基础功能：
  - 合同管理
  - 报价单生成
  - 印章添加
  - 数据导出

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献指南

欢迎提交Issue和Pull Request来帮助改进这个项目。
