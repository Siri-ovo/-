# 大学生职业匹配与发展建议系统

本项目是“微专业大作业”的垂直领域大模型应用，面向大学生职业规划场景，使用真实岗位数据、RAG 检索和本地大模型生成职业匹配与发展建议。

## 功能概览

- 职业画像填写：专业、年级、学历、技能、兴趣方向、期望城市、行业偏好和岗位类型。
- 简历上传：支持从简历文本中补充用户能力信息。
- 目标岗位输入：支持岗位链接和岗位描述，用于单岗位分析。
- 真实岗位库检索：基于 NCSS 岗位数据构建岗位库。
- RAG 证据展示：生成报告前先展示召回的真实岗位证据。
- 可解释评分：展示匹配分来源、分项权重、技能差距和学习路径。
- 本地大模型生成：通过 Ollama 调用 `qwen3:4b`，并支持备用模型兜底。
- 历史报告和导出：支持查看历史报告，并下载 JSON / Markdown 报告。

## 技术栈

- Python 3.10+
- Streamlit
- scikit-learn TF-IDF
- pandas / joblib
- Ollama 本地大模型
- pytest

## 项目结构

```text
.
├── app.py
├── data/
│   ├── import/
│   ├── processed/
│   └── raw/
├── scripts/
├── src/
│   ├── analytics/
│   ├── crawler/
│   ├── importers/
│   ├── inputs/
│   ├── llm/
│   ├── rag/
│   ├── scoring/
│   ├── storage/
│   ├── ui/
│   └── utils/
├── tests/
├── vector_store/
├── requirements.txt
└── README.md
```

## 本地运行

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

如果需要重新采集和构建岗位索引，可以依次运行：

```bash
python -m src.crawler.ncss_crawler --pages 10 --limit 20 --delay 1.0
python -m src.crawler.clean_jobs
python -m src.rag.build_index
```

## 服务器运行方式

服务器部署路径示例：

```text
/path/to/career_app
```

服务器启动命令：

```bash
cd /path/to/career_app
.venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1
```

如果部署在远程服务器，本机访问时可以开启 SSH 端口转发：

```bash
ssh -p <ssh_port> -N -L 127.0.0.1:8502:127.0.0.1:8501 <user>@<server_host>
```

然后打开：

```text
http://127.0.0.1:8502
```

## 测试

```bash
PYTHONPATH=. python -m pytest -q
```

服务器 `.venv` 环境中已用于完整测试验证。

## 说明

本项目重点不是让大模型凭空生成职业建议，而是先从真实岗位库中检索证据，再基于岗位证据和用户画像生成可解释的职业匹配报告。这样可以降低幻觉风险，并让推荐理由、技能短板和学习路径更容易追溯。
