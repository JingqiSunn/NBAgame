# NBA Manager Game

这是一个基于Python和Flask的NBA经理模式游戏，允许多个玩家扮演不同球队的经理，进行选秀、交易和比赛。

## 功能特点

- 30支NBA球队可供选择
- 多人游戏模式
- 球员选秀系统
- 球员交易系统
- 比赛模拟系统
- 赛季排名系统

## 技术栈

- Python 3.8+
- Flask
- PostgreSQL
- SQLAlchemy
- Flask-Login

## 安装步骤

1. 克隆项目到本地：
```bash
git clone [repository_url]
cd NBAgame
```

2. 创建虚拟环境并激活：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置数据库：
- 确保PostgreSQL服务器已启动
- 在`src/app.py`中更新数据库连接信息

5. 初始化数据库：
```bash
python src/init_db.py
```

6. 运行应用：
```bash
python src/app.py
```

## 游戏玩法

1. 注册/登录账号
2. 选择一支球队作为你的经理球队
3. 管理你的球队：
   - 查看球员名单
   - 进行球员交易
   - 参与选秀
   - 安排比赛
4. 与其他玩家竞争，争夺总冠军

## 注意事项

- 确保PostgreSQL服务器正在运行
- 默认数据库连接信息需要根据实际情况修改
- 建议使用虚拟环境运行项目

## 贡献

欢迎提交Issue和Pull Request来帮助改进这个项目。

## 许可证

MIT License
