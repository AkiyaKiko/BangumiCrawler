# BangumiCrawler

**BangumiCrawler** 是一个用于抓取 Bangumi 动漫数据并进行分析的爬虫与数据处理工具集，集成了数据采集、评论抓取、数据库管理、数据分析与可视化等功能模块。适合用于动漫数据分析、NLP 预训练、情感分析与可视化展示等科研与学习任务。

---

## 🔧 功能概览

- ✅ 动漫目录与详情页数据抓取
- ✅ 评论数据批量采集
- ✅ SQLite 数据库存储与管理
- ✅ 数据分析与可视化（词云、评分分布等）
- ✅ RoBERTa 微调模型情感分类

---

## 📂 项目结构

```
BangumiCrawler/
├── anime_data.db                 # SQLite 数据库文件
├── config.py                    # 配置参数（年份、地区等）
├── failed_animes.txt            # 抓取失败的条目记录
├── main.py                      # 主程序入口：抓取流程调度
├── requirements.txt             # 项目依赖包列表
│
├── EDA/                         # 数据分析与 NLP 相关模块
│   ├── anime_data.csv           # 动漫元数据（CSV 格式）
│   ├── comments.csv             # 评论数据（CSV 格式）
│   ├── EDA.ipynb                # 数据分析 Jupyter Notebook
│   ├── wordclouds/             # 词云图像输出目录
│   └── fine_tuned_roberta/     # 微调后的 RoBERTa 模型文件与词表
│
├── scraper/                     # 网络爬虫模块
│   ├── directory.py             # 动漫列表与分页抓取逻辑
│   ├── fetcher.py               # 动漫详情页面爬取
│   └── comments.py              # 动漫评论抓取器
│
└── utils/                       # 工具类函数与数据库管理
    ├── proxy_manager.py         # 动态代理池管理器
    └── sqldb.py                 # SQLite 数据库操作封装
```

---

## 🚀 快速上手

### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/BangumiCrawler.git
cd BangumiCrawler
```

### 2. 安装依赖

建议使用虚拟环境：

```bash
pip install -r requirements.txt
```

### 3. 配置参数

编辑 `config.py`，设置抓取的起止年份、地区等参数。

### 4. 运行主程序

执行爬虫主程序，自动抓取 Bangumi 动漫数据并写入数据库：

```bash
python main.py
```

### 5. 进行数据分析

在 Jupyter Notebook 中打开：

```bash
EDA/EDA.ipynb
```

可进行数据探索、词云生成、情感分析等操作。

---

## 📌 注意事项

- 本项目仅用于学习、研究目的，**请勿用于商业用途**。
- 若抓取过程中遇到频繁失败，可编辑 `proxy_manager.py` 启用代理功能。
- 抓取失败的条目会记录在 `failed_animes.txt` 中，可用于补抓。
- 若使用微调后的 RoBERTa 模型，请注意使用 Git LFS 管理大文件。

---

## 💻 技术栈与依赖

- **语言**：Python 3.8+
- **网络爬虫**：`aiohttp`, `lxml`, `BeautifulSoup4`
- **数据处理**：`pandas`, `sqlite3`
- **可视化**：`matplotlib`, `seaborn`, `wordcloud`
- **NLP 模型（可选）**：HuggingFace `transformers`, `roberta-base`

详见 [`requirements.txt`](./requirements.txt)

---

## 🤝 致谢

- [Bangumi](https://bangumi.tv/) 动漫社区开放数据接口
- [HuggingFace Transformers](https://huggingface.co/)
- 开源社区中提供支持的开发者与工具

---

## 📬 联系与贡献

欢迎提交 [Issues](https://github.com/你的用户名/BangumiCrawler/issues) 或 [Pull Requests](https://github.com/你的用户名/BangumiCrawler/pulls)。