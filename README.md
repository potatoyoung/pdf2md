# Literature Preprocessor

轻量级科研论文 PDF 批量预处理工具，用于把 PDF 转换为适合后续文献综述和 LLM 分析的 Markdown。核心解析库为 `pymupdf4llm`，默认单进程顺序处理，优先兼容 CPU 环境、低资源占用和稳定性。

## 项目结构

```text
literature-preprocessor/
├── pyproject.toml
├── README.md
├── .gitignore
├── src/
│   └── literature_preprocessor/
│       ├── __init__.py
│       ├── cli.py
│       ├── converter.py
│       ├── scanner.py
│       ├── logger.py
│       └── utils.py
├── scripts/
│   └── convert_papers.py
├── data/
│   ├── pdf/
│   └── markdown/
└── logs/
```

## 安装

本项目使用 `uv` 管理 Python 环境和依赖，要求 Python 3.11+。

```bash
uv venv
uv sync
```

Windows PowerShell 中如需手动激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

## 批量转换

把 PDF 放入 `data/pdf/`，然后运行：

```bash
uv run python scripts/convert_papers.py
```

也可以使用安装后的命令行入口：

```bash
uv run convert-papers
```

指定输入和输出目录：

```bash
uv run python scripts/convert_papers.py --input-dir data/pdf --output-dir data/markdown
```

默认会递归扫描子目录，并尽量保留原始目录结构。例如：

```text
data/pdf/topic-a/paper.pdf
```

会输出为：

```text
data/markdown/topic-a/paper.md
```

如果 Markdown 文件已经存在且非空，默认会跳过，方便断点续跑。需要强制重新转换时使用：

```bash
uv run python scripts/convert_papers.py --overwrite
```

只扫描输入目录第一层，不递归子目录：

```bash
uv run python scripts/convert_papers.py --no-recursive
```

## 日志和报告

每次运行会在 `logs/` 下生成：

- `convert_YYYYMMDD_HHMMSS.log`：运行日志。
- `conversion_report_YYYYMMDD_HHMMSS.csv`：结构化转换报告。

CSV 报告字段：

- `pdf_path`：PDF 文件路径。
- `markdown_path`：Markdown 输出路径。
- `success`：是否成功。
- `skipped`：是否因已有输出而跳过。
- `error`：失败错误信息。
- `elapsed_seconds`：单篇转换耗时。

单篇 PDF 转换失败不会中断整个批处理流程，错误会写入日志和 CSV 报告。

## 最小可运行示例

```bash
mkdir -p data/pdf
# 将 example.pdf 放入 data/pdf/
uv run python scripts/convert_papers.py -i data/pdf -o data/markdown
```

转换完成后查看：

```text
data/markdown/example.md
logs/conversion_report_*.csv
```

## 常见失败情况

- PDF 文件损坏、加密或权限受限。
- PDF 主要由扫描图片构成，没有可提取文本。本项目当前不做 OCR。
- 文件路径过长或包含特殊字符。程序会对输出路径组件做基础清理，但仍建议避免极端长路径。
- `pymupdf4llm` 或底层 PyMuPDF 无法解析某些复杂版式 PDF。

当前版本只做稳定的 PDF 到 Markdown 批量转换，暂不包含 LLM API、RAG、向量数据库、Embedding、GUI、Web 服务或 Zotero API。

