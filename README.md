cursor做的合同生成小工具  contractG发行版公布了！
这个小工具我是做了自己用的，大概做了两天就可以自己用了。

完善功能和做发行版花了近一周的时间。
我自己感觉很好用，分享给有需要的企业朋友。

欢迎大家测试和使用，并推荐给周围有需要朋友。
用的人多会开源！

contractG 使用截图，示例数据由LLM生成：
![20250311181846](https://github.com/user-attachments/assets/d22bcd84-71cc-4a3b-aceb-e5d3e288c604)
![SC-20250311-001209_with_seal_00](https://github.com/user-attachments/assets/d1d2dbd2-2249-4083-bec0-92c375d1fb22)
![报价单-SC-20250311-001209_with_seal_00](https://github.com/user-attachments/assets/201d477b-e6bd-4ab3-87b4-6ad492b526a0)

# 合同生成工具 (contractG)

一个用于生成合同和报价单的桌面应用程序，使用Python和PyQt5开发。

## 功能特点
- 合同和报价支持印章和图片式PDF
- 一分钟生成合同和报价单
- 全部查询支持中文首字母
- 乙方没设置印章，默认只生成excel格式
  


### 1. 合同生成
- 支持选择客户和商品生成合同
- 使用搜索框可以快速查找客户和商品
- 支持新增客户
- 自动计算合同金额（商品总额 + 技术服务费）
- 支持设置合同编号、签订日期、交货日期
- 支持自定义付款方式
- 支持设置报价单有效期
- 自动生成合同和报价单文件
- 合同和报价支持印章和图片式PDF

### 2. 乙方公司管理
- 支持管理多个乙方公司信息
- 可以设置默认乙方公司
- 支持从文本解析导入公司信息（如开票信息、名片等）
- 公司信息包含：公司名称、联系人、电话、地址、开户行、银行账号、税号等
- 支持公司信息的添加、编辑、删除操作
- 
### 3. 客户管理
- 支持从文本解析导入
- 添加、编辑、删除客户信息
- 支持客户信息导入导出
- 客户信息包含：公司名称、联系人、电话、地址、开户行、银行账号、税号等
- 支持客户信息搜索和筛选

### 4. 商品管理
- 支持从文本解析导入
- 使用搜索框可以快速查找
- 添加、编辑、删除商品信息
- 支持商品信息导入导出
- 商品信息包含：商品名称、规格型号、单位、单价等
- 支持商品信息搜索和筛选

### 5. 系统功能
- 支持打开数据目录和输出目录
- 首次运行自动引导配置公司信息
- 支持系统设置管理

## UI设计特点

### 1. 现代化界面
- 采用Material Design设计风格
- 统一的配色方案和视觉元素
- 响应式布局，适应不同屏幕尺寸
- Qt部分使用QSS样式，Vue部分使用标准CSS

### 2. 用户体验优化
- 表格行交替颜色，提高可读性
- 按钮颜色区分功能类型（主要、次要、危险等）
- 表单字段布局合理，操作流程清晰
- 添加提示信息，引导用户操作

### 3. 视觉元素
- 标题和分组清晰，层次分明
- 重要信息突出显示
- 表格样式统一，便于信息浏览
- 按钮样式美观，交互反馈明确

### 4. 性能优化
- 支持高DPI显示
- 优化表格渲染性能
- 减少不必要的UI刷新


## 使用说明

### 1. 首次使用
1. 运行程序后，系统会自动引导您配置乙方公司信息
2. 在"系统"菜单中选择"配置乙方公司"可以随时修改公司信息

### 2. 客户管理
1. 切换到"客户管理"标签页
2. 点击"添加客户"按钮添加新客户
3. 在客户列表中双击客户可以编辑信息
4. 选中客户后点击"删除客户"可以删除客户
5. 使用搜索框可以快速查找客户

### 3. 商品管理
1. 切换到"商品管理"标签页
2. 点击"添加商品"按钮添加新商品
3. 在商品列表中双击商品可以编辑信息
4. 选中商品后点击"删除商品"可以删除商品
5. 使用搜索框可以快速查找商品

### 4. 合同生成
1. 切换到"合同生成"标签页
2. 在客户列表中选择客户
3. 在商品列表中选择商品并添加到合同
4. 设置合同信息（编号、日期、付款方式等）
5. 选择乙方公司
6. 点击"生成合同"按钮生成合同文件

### 5. 乙方公司管理
1. 在"系统"菜单中选择"配置乙方公司"
2. 在对话框中可以：
   - 查看所有乙方公司列表
   - 添加新的乙方公司
   - 编辑现有公司信息
   - 删除公司
   - 设置默认公司
   - 从文本解析导入公司信息
   - 编辑栏可以加入电子印章，注意印章尽量充满图片，PNG格式


## 注意事项

1. 首次使用前请确保已正确配置乙方公司信息（含电子印章）
2. 生成合同前请确保已选择客户和添加商品
3. 合同编号格式为：SC-YYYYMMDD-XXX

## 版本历史

### v1.4.0 (2025-03-11)
- 新增PyInstaller打包支持
- 添加spec文件配置，优化打包过程
- 支持一键打包为可执行文件
- 添加自动创建安装脚本功能
- 优化程序启动方式
- 修复中文路径和文件名问题
- 新增PDF盖章文件转图片式功能，提高文件兼容性
- 支持自动识别印章位置并应用到PDF文件

### v1.3.0 (2025-03-05)
- 新增多乙方公司管理功能
- 支持设置默认乙方公司
- 支持从文本解析导入公司信息
- 优化合同生成界面
- 改进用户界面交互体验
- 全面优化UI设计，采用Material Design风格

### v1.2.0 (2025-02-20)
- 新增客户和商品管理功能
- 支持数据导入导出
- 优化合同生成流程
- 改进用户界面设计

### v1.1.0 (2025-02-13)
- 新增报价单生成功能
- 支持合同草稿模式
- 优化文件保存路径
- 改进错误处理机制

### v1.0.0 (2025-02-12)
- 初始版本发布
- 实现基本的合同生成功能
- 支持客户和商品选择
- 支持合同金额计算

## 开发计划

1. 添加合同模板自定义功能
3. 添加合同历史记录管理
4. 支持数据备份和恢复
5. 添加用户权限管理
6. 优化性能和用户体验

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证

本项目采用 MIT 许可证。


### 安装程序
1. 运行打包后生成的安装脚本`install.bat`
2. 安装程序会自动：
   - 将程序安装到Program Files目录
   - 创建必要的数据目录
   - 创建桌面快捷方式
   - 创建开始菜单快捷方式

### 注意事项
1. 如果遇到杀毒软件报警，请将程序添加到白名单
2. 建议将程序安装在非系统盘，并关闭杀毒软件对程序目录的实时监控
3. 首次运行时请确保已正确配置公司信息


