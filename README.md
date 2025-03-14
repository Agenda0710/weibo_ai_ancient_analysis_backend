
# 项目名称  
## 智汇古今——面向中华自然科学与优秀文化可视化分析平台  

---
### **分支说明**  
1. **`master` 分支**  
   - **项目名称**：面向人工智能行业的数据洞察与可视化分析  
   - **状态**：已完结，功能稳定，可直接部署。  
   - **内容**：  
     - 基于 Django 的后端服务。  
     - 数据可视化核心功能（AI 行业数据）。  
     - 完整的接口文档和规范代码。  

2. **`new_project` 分支**  
   - **项目名称**：智汇古今——面向中华自然科学与优秀文化可视化分析平台  
   - **状态**：开发中，功能迭代中。  
   - **内容**：  
     - 基于 `master` 分支的代码框架扩展。  
     - 新增中华自然科学与优秀文化数据模块。  
     - **注意**：部分函数、接口名称尚未规范化（后续逐步优化）。  

---

### **功能特性**  
#### **`master` 分支**  
- 数据洞察：AI 行业数据清洗、分析与可视化。  
- 后端接口：Django 提供 RESTful API，支持前端数据交互。  
- 可视化图表：集成 ECharts/Pyecharts，动态展示分析结果。  

#### **`new_project` 分支**  
- 文化数据扩展：新增中华古籍、历史事件、传统工艺等数据集。  
- 可视化优化：适配文化数据的特殊展示需求（如时间轴、地理分布）。  
- 模型适配：部分预训练模型（NLP）用于文化内容分析。  

---

### **环境要求**  
- Python 3.8+  
- Django 4.0+  
- MySQL/PostgreSQL（根据实际配置）  
- 依赖库：`requirements.txt`（分支独立配置）  

---

### **快速开始**  
#### **1. 克隆项目**  
```bash  
git clone https://github.com/Agenda0710/weibo_ai_ancient_analysis_backend.git  
cd weibo_ai_ancient_analysis_backend  
```  

#### **2. 切换分支**  
- **稳定版（`master`）**：  
  ```bash  
  git checkout master  
  ```  
- **开发版（`new_project`）**：  
  ```bash  
  git checkout new_project  
  ```  

#### **3. 安装依赖**  
```bash  
pip install -r requirements.txt  
```  

#### **4. 配置数据库**  
- 修改 `settings.py` 中的数据库配置（路径：`your_project_name/settings.py`）：  
  ```python  
  DATABASES = {  
      'default': {  
          'ENGINE': 'django.db.backends.mysql',  
          'NAME': 'your_database_name',  
          'USER': 'your_username',  
          'PASSWORD': 'your_password',  
          'HOST': 'localhost',  
          'PORT': '3306',  
      }  
  }  
  ```  

#### **5. 运行迁移**  
```bash  
python manage.py makemigrations  
python manage.py migrate  
```  

#### **6. 启动服务**  
```bash  
python manage.py runserver  
```  

---

### **注意事项**  
1. **模型文件缺失**  
   - 由于模型文件过大，未提交到 Git 仓库。  
   - **解决方案**：  
     - 联系作者获取预训练模型文件。  
     - 按路径 `your_app/models/` 放置模型文件。  

2. **路径问题**  
   - 部分路径（如静态文件、数据集）需手动配置。  
   - **修改位置**：  
     - `settings.py` 中的 `STATIC_URL`、`MEDIA_ROOT`。  
     - 数据接口路径（`views.py` 中的文件读取逻辑）。  

3. **代码规范**  
   - `new_project` 分支的函数、接口名称正在优化中，部分代码可能与 `master` 分支存在差异。  



### **附：分支切换命令速查**  
```bash  
# 查看所有分支  
git branch -a  

# 切换到 master 分支  
git checkout master  

# 切换到 new_project 分支  
git checkout new_project  

# 拉取远程分支更新  
git pull origin <branch_name>  
