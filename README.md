

# Rix英语文本分析器

## 介绍

Rix 是一款用于分析英语文本可读性的工具，基于 textstat.py 开源算法库开发，并提供 Gradio Web 用户界面。该工具主要用于计算文本的 RIX（Readability Index）可读性指数，帮助评估英语文本的阅读难度。

RIX（Readability Index）是一种衡量文本难度的指标，通过计算文本中长词（7个字母以上的词）与句子数量的比值来评估文本的可读性。RIX 值越高，表示文本中长词比例越高，阅读难度越大。

## 功能特性

- **RIX 可读性指数计算**：自动分析文本中长词与句子的比例
- **词频统计**：内置多种英语词频数据库（BNC、AME、Collins 等）
- **Gradio Web 界面**：提供友好的图形化分析界面
- **批量文本分析**：支持分析多个预设样本文本
- **文件上传分析**：支持上传txt文件进行分析
- **多维度文本分析**：计算词汇量、句子数、词数等指标

## 软件架构

项目采用前后分离架构：

- **后端算法**：textstat.py 文本可读性分析算法
- **Web 前端**：Gradio 6.10 交互式界面
- **词频数据库**：BNC15000、AME20000、Collins 星級词汇表
- **预设文本库**：包含各类英语新闻和文章样例

## 安装教程

### 环境要求

- Python 3.12.10
- Gradio 6.10
- textstat.py 依赖库

### 安装步骤

1. 安装 Python 3.12.10
2. 安装 Gradio：
   ```
   pip install gradio
   ```
3. 下载或克隆本项目代码
4. 确保词频数据文件（BNC15000.txt、AME20000.txt 等）位于正确目录

### 快速启动

运行项目提供的批处理文件即可启动 Web 界面：

```bash
!!!!!!!gradio_webui - 7860.bat
```

或使用带星级的版本：

```bash
!!!!!!!gradio_webui - 7860 - stars.bat
```

## 使用说明

### 基本使用

1. 启动程序后，浏览器自动打开 Gradio Web 界面
2. 在文本输入框中输入或粘贴待分析的英语文本
3. 点击"分析"按钮获取 RIX 可读性指数及各项指标

### 预设文本

程序内置多个预设样本文本，可通过下拉菜单选择：

- BBC 一代人的记忆 - 中国悼念争议教育影响者突然离世
- 一个告诉中国孩子如何成功的突然离世的人
- dancing robots 等其他样本文本

### 使用示例

默认输入文本示例：

```
Introduction
'I don't trust you. You are one of them, right? 
…… 
I also want to say it is not a matter of being greedy or stupid. It can really happen to anyone.'
```

### 运行结果

分析完成后，将显示以下指标：

- RIX 可读性指数
- 词汇数量
- 句子数量
- 长词（7字母以上）数量
- 可读性评级（基于 Collins 星级）

## 文件说明

### 主要源代码

- `textstat_gradio610_webui.py` - 主程序（基础版）
- `textstat_gradio_webui610_stars.py` - 带星级评分版

### 词频数据

| 文件名 | 说明 |
|--------|------|
| BNC15000.txt | 英国国家语料库高频词 TOP 15000 |
| AME20000.txt | 美国英语高频词 TOP 20000 |
| Collins5Stars.txt |Collins 五星词汇 |
| Collins4Stars.txt | Collins 四星词汇 |
| Collins3Stars.txt | Collins 三星词汇 |
| Collins2Stars.txt | Collins 二星词汇 |
| Collins1Stars.txt | Collins 一星词汇 |
| Collins0Stars.txt | Collins 零星词汇 |

### 预设文本

- `txt/BBC_Memory of a generation_China mourns the sudden death of a controversial education influencerMod0.txt`
- `txt/The Sudden Death of a Man Who Told Chinese Kids How to Succeed_mod0.txt`
- `txt/dancingrobots20260320finished - mod0.txt`
- `txt/textstat-00f1rixliteRacingbTEorgtext.txt`

## 项目结构

```
rix/
│
├── textstat_gradio610_webui.py      # 主程序（基础版）
├── textstat_gradio_webui610_stars.py # 主程序（星级版）
│
├── BNC15000.txt                     # 英国国家语料库词频
├── AME20000.txt                     # 美国词频
├── Collins5Stars.txt                # Collins 5星词
├── Collins4Stars.txt                # Collins 4星词
├── Collins3Stars.txt                # Collins 3星词
├── Collins2Stars.txt                # Collins 2星词
├── Collins1Stars.txt                # Collins 1星词
├── Collins0Stars.txt                # Collins 0星词
│
├── txt/                             # 预设文本目录
│   ├── BBC_Memory of a generation...
│   ├── The Sudden Death of a Man...
│   ├── dancingrobots20260320...
│   └── textstat-00f1rixlite...
│
├── !!!!!!!gradio_webui - 7860.bat   # 启动脚本
├── !!!!!!!gradio_webui - 7860 - stars.bat
└── !!!!!!!7860_clean.bat
```

## 许可

本项目基于 MIT 许可证开源。具体许可信息请参见 LICENSE 文件。