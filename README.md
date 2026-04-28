https://gitee.com/leafv1972/rix

https://github.com/Leafv1972/rix

 **_Note that Python 3.12.10 cannot be used on Windows 7 or earlier._** 

# Rix 英语文本可读性分析系统：理论、实现与应用综述

## 摘要

本文系统介绍了基于 **Rix（Rate of Long Words Index）** 指数的英语文本可读性分析工具。该工具由 Jonathan Anderson (1983) 提出的经典理论衍生而来，并通过现代 Python 技术栈（特别是 `textstat` 库和 `Gradio` 框架）进行了工程化实现。本文详细阐述了 Rix 指数的数学原理、分级标准，分析了该系统相较于传统公式（Flesch, SMOG, Fry）在低端文本区分度和计算效率上的优势。此外，本文重点描述了该系统的软件架构、核心功能特性（包括多源词频数据库集成、Gradio Web 界面、批量分析能力），并提供了详细的安装与使用说明。研究旨在为教育工作者、出版商及 NLP 研究人员提供一个高效、准确且用户友好的文本难度评估解决方案。

---

## 1. 引言

### 1.1 背景
在语言教育和自然语言处理领域，准确评估文本的阅读难度至关重要。传统的可读性公式如 Flesch-Kincaid、SMOG 和 Fry 图表虽然广泛应用，但往往存在计算繁琐、对低龄段文本区分度低（"触底效应"）或对音节划分依赖过高等问题。

### 1.2 Rix 指数的提出
1983年，Jonathan Anderson 在《Journal of Reading》发表文章，介绍了源自瑞典的 Lix 公式，并提出了其简化版本——**Rix 指数**。Rix 定义为长词（7个字母及以上）数量与句子数量的比值。Anderson 和后续研究者 Joseph Kretschmer (1984) 证明，Rix 不仅计算极速，且在小学低年级文本的难度区分上优于主流公式。

### 1.3 本系统目标
本项目 **"Rix 英语文本分析器"** 旨在将这一经典理论转化为现代化的 Web 应用。通过整合 `textstat` 算法库和 `Gradio` 前端，并引入 BNC、AME 及 Collins 星级词典，系统不仅提供基础的难度评分，还能进行多维度的词汇频率分析，帮助用户深入理解文本的复杂度构成。

---

## 2. Rix 指数理论解析

### 2.1 定义与计算
Rix 指数的核心公式为：

$$ \text{Rix} = \frac{\text{Number of Long Words (≥7 letters)}}{\text{Number of Sentences}} $$

*   **长词 (Long Words)**：定义为长度大于或等于 7 个字母的单词（如 *understand*, *environment*, *necessary*）。
*   **句子 (Sentences)**：通过标点符号（. ! ?）分割的文本单元。

### 2.2 分级标准 (Grade Level Mapping)
根据 Anderson 和 Kretschmer 的研究，Rix 值与教育年级水平的对应关系如下：

| Rix Score Range | Estimated Grade Level | 文本特征描述 |
| :--- | :--- | :--- |
| **< 0.2** | Grade 1 (1st) | 极简单，适合早期阅读者。长词极少。 |
| **0.2 - 0.5** | Grade 2 (2nd) | 简单，初级读物。 |
| **0.5 - 0.8** | Grade 3 (3rd) | 初级，开始引入少量复杂词汇。 |
| **0.8 - 1.3** | Grade 4 (4th) | 中级偏易，典型小学生高年级水平。 |
| **1.3 - 1.8** | Grade 5 (5th) | 中等，正式学习阶段标准难度。 |
| **1.8 - 2.4** | Grade 6 (6th) | 中等偏难，初中低年级水平。 |
| **2.4 - 3.0** | Grade 7 (7th) | 难，初中阶段典型范围。 |
| **3.0 - 3.7** | Grade 8 (8th) | 较难，包含较多专业术语。 |
| **3.7 - 4.5** | Grade 9 (9th) | 困难，高中早期水平。 |
| **4.5 - 5.3** | Grade 10 (10th) | 非常难，高中后期水平。 |
| **5.3 - 6.2** | Grade 11 (11th) | 极难，大学预备级。 |
| **6.2 - 7.2** | Grade 12 (12th) | 高等教育入门级。 |
| **≥ 7.2** | College | 大学及以上，学术或专业文献。 |

### 2.3 优势与局限性
*   **优势**：
    1.  **极速计算**：无需音节计数，仅需字母计数和句子分割。
    2.  **低端敏感**：在 1-3 年级文本中，Rix 能有效区分细微难度差异，而 SMOG/Fry 往往无法区分（均显示为 1 或 2 年级）。
    3.  **客观性**：避免了人工划分音节的 subjective errors。
*   **局限性**：
    1.  **短难词忽略**：如 *anxiety*, *oblique* 等短而难词未被捕捉。*(本系统通过 Collins 星级数据部分弥补此缺陷)*
    2.  **长度偏见**：长词未必难（如 *banana*），短词未必易。*(本系统通过 AME/BNC 词频数据提供额外参考)*

---

## 3. 系统架构与设计

本系统采用前后端分离架构，基于 Python 生态构建，确保高性能、可扩展性和用户友好性。

### 3.1 软件架构图

```mermaid
graph TD
    User[用户] --> WebUI[Gradio Web Interface]
    WebUI --> Core[Core Analysis Engine]
    
    subgraph "Backend Logic (Python)"
        Core --> TextStats[TextStatistics Class]
        TextStats --> Preprocessing[Text Preprocessing]
        Preprocessing --> CleanText[Cleaned Text]
        CleanText --> RixCalc[Rix Calculation]
        RixCalc --> Metrics[Metrics Generation]
    end
    
    subgraph "Data Layer"
        Metrics --> WordFreqDB[Word Frequency DBs]
        WordFreqDB --> AME[AME20000.txt]
        WordFreqDB --> BNC[BNC15000.txt]
        WordFreqDB --> Collins[Collins Stars Data]
        
        Metrics --> SampleDB[Sample Texts]
        SampleDB --> TXT_Folder[txt/ Directory]
    end
    
    WebUI --> Output[Markdown Results & Tables]
```

### 3.2 技术栈

 **_Note that Python 3.12.10 cannot be used on Windows 7 or earlier._** 

*   **后端**：Python 3.12+
    *   `textstat`：提供底层文本统计支持。
    *   `re` (Regex)：用于高性能的正则表达式清洗和分句。
    *   `collections.Counter`：用于高效词频统计。
*   **前端**：Gradio 6.10
    *   提供交互式 Web UI，支持实时分析、文件上传和可视化展示。
*   **数据源**：
    *   **BNC15000.txt**：英国国家语料库前 15,000 高频词。
    *   **AME20000.txt**：美国英语高频词前 20,000。
    *   **Collins Star Files**：Collins Dictionary 星级词汇表（0-5 星），用于评估词汇常见度。

---

## 4. 功能特性详解

### 4.1 核心分析能力
1.  **Rix 指数计算**：自动统计长词数量和句子数量，计算 Rix 值并映射到对应的年级水平。
2.  **多维度统计**：
    *   总词数 (Total Words)
    *   句子数 (Sentences)
    *   长词数量 (Long Words ≥7 chars)
3.  **词汇频率增强分析**：
    *   对于识别出的每个长词，系统查询 AME 和 BNC 排名。
    *   匹配 Collins 星级（1-5 星），帮助用户判断词汇是“长但常见”还是“长且罕见”。
4.  **实时反馈**：Gradio 界面支持用户输入时实时显示分析结果（通过 `input_text.change` 事件绑定）。

### 4.2 用户交互界面
*   **文本输入**：支持直接粘贴文本或上传 `.txt` 文件。
*   **文件上传**：内置自动编码检测（UTF-8, GBK, Big5 等），确保跨平台文件兼容性。
*   **预设样本库**：内置多个示例文本（如 BBC 新闻、科幻片段等），方便用户快速测试系统功能。
*   **结果展示**：
    *   **概览表格**：清晰展示 Rix 值、对应年级、关键统计指标。
    *   **长词清单**：以 Markdown 表格形式列出所有长词，附带频率和星级信息，便于编辑者识别难点词汇。

### 4.3 数据处理流程
1.  **加载**：启动时加载 AME、BNC 和 Collins 数据到内存（`dict` 和 `set`），确保后续查询的 O(1) 时间复杂度。
2.  **清洗**：移除标点符号（保留撇号以维持单词完整性）。
3.  **分句**：使用正则表达式 `\b[^.!?]+[.!?]*` 分割句子。
4.  **分词**：按空格分割文本。
5.  **统计**：
    *   计算句子总数。
    *   筛选长度 ≥7 的单词。
    *   查询数据库获取频率信息。
6.  **渲染**：生成 Markdown 格式的 HTML 返回给前端。

---

## 5. 安装与使用指南

### 5.1 环境要求
*   **操作系统**：Windows / macOS / Linux
*   **Python 版本**：3.12.10 或更高
*   **依赖库**：
    ```bash
    pip install gradio textstat
    ```

### 5.2 项目结构
```text
rix/
├── textstat_gradio610_webui.py      # 基础版主程序
├── textstat_gradio_webui610_stars.py # 带星级评分版主程序
├── BNC15000.txt                     # BNC 词频数据
├── AME20000.txt                     # AME 词频数据
├── Collins5Stars.txt ~ Collins0Stars.txt # Collins 星级数据
├── txt/                             # 预设样本文本目录
│   ├── BBC_Memory of a generation...txt
│   ├── The Sudden Death of a Man...txt
│   └── ...
├── !!!!!!!gradio_webui - 7860.bat   # Windows 启动脚本 (基础版)
├── !!!!!!!gradio_webui - 7860 - stars.bat # Windows 启动脚本 (星级版)
└── !!!!!!!7860_clean.bat            # 清理缓存启动脚本
```

### 5.3 快速启动
1.  **克隆/下载**项目代码。
2.  **确保数据文件**位于项目根目录或正确路径。
3.  **运行启动脚本**：
    *   双击 `!!!!!!!gradio_webui - 7860.bat` (基础版)
    *   或 `!!!!!!!gradio_webui - 7860 - stars.bat` (星级版)
4.  **浏览器访问**：程序将自动在 `http://127.0.0.1:7860` 打开 Web 界面。

### 5.4 使用示例
1.  **输入文本**：
    > "The environmental impact of industrialization is profound. Scientists argue that sustainable practices are necessary for future generations."
2.  **分析结果**：
    *   **RIX Index**: ~1.5 (假设句子数为 2, 长词为 *environmental, industrialization, sustainable, generations* -> 4/2 = 2.0, 具体值取决于分句)
    *   **Reading Level**: Grade 6-7 范围
    *   **Long Words**: *environmental* (AME Rank: 5000, Collins: ★★★★☆), *industrialization* (AME Rank: 15000, Collins: ★★★☆☆) ...

---

## 6. 讨论与比较

### 6.1 与传统公式的比较

| 特性 | Flesch-Kincaid | SMOG | Fry Graph | **本 Rix 系统** |
| :--- | :--- | :--- | :--- | :--- |
| **计算复杂度** | 高 (需音节) | 中 (查表/公式) | 中 (图表查找) | **极低 (仅长度+分句)** |
| **低端区分度** | 差 (触底) | 差 (触底) | 差 (触底) | **优 (0.2-0.5 区分 G1-G2)** |
| **词汇洞察** | 无 | 无 | 无 | **强 (AME/BNC/Collins)** |
| **实现难度** | 高 | 中 | 高 | **低 (Python 脚本)** |
| **适用场景** | 通用 | 学术/正式 | 教育出版 | **实时编辑/批量处理** |

### 6.2 多源词频数据的重要性
传统 Rix 仅看长度。本系统通过集成：
*   **BNC (British)** 和 **AME (American)**：区分英式与美式英语的难度感知。例如，某些词在英式英语中高频（易读），但在美式英语中低频（难读）。
*   **Collins Stars**：提供词汇的“通用性”评级。一个长词如果是 5 星（如 *understand*），其实际阅读障碍远小于 0 星（如 *pneumonoultramicroscopicsilicovolcanoconiosis*）。

### 6.3 局限性
*   **中文不适用**：Rix 基于字母长度，中文无字母概念，需使用笔画数或字频。
*   **上下文缺失**：无法识别“看起来简单但语境复杂”的词汇（如 *bank* 在金融 vs. 河流语境下的难度差异）。

---

## 7. 结论

本系统成功地将 Jonathan Anderson 提出的 Rix 指数理论转化为一个功能强大、用户友好的现代 Web 应用。通过整合 `textstat` 算法库和 `Gradio` 前端，并引入多维词频数据，系统不仅保留了 Rix 指数**计算极速、低端敏感**的核心优势，还通过**词汇频率和星级分析**弥补了其单一维度的不足。

对于教育工作者、出版商和内容创作者而言，该系统提供了一个比传统公式更精细、比复杂 NLP 模型更透明的文本难度评估工具。未来工作可包括支持更多语言、集成上下文感知模型以及扩展为 API 服务。

---

## 参考文献

1.  Anderson, J. (1983). Lix and Rix: Variations on a Little-known Readability Index. *Journal of Reading*, 26(6), 490-496.
2.  Kretschmer, J. C. (1984). Computerizing and Comparing the Rix Readability Index. *Journal of Reading*, 27(6), 490-499.
3.  Björnsson, C. H. (1968). *Läsbarhet*. Stockholm: Bokförlaget Liber.
4.  McLaughlin, G. H. (1969). SMOG Grading—A New Readability Formula. *Journal of Reading*, 12(8), 639-646.
5.  Fry, E. (1968). A Readability Formula that Saves Time. *Journal of Reading*, 11(7), 513-516.
6.  Harrison, C. (1980). *Readability in the Classroom*. Cambridge: Cambridge University Press.
7.  Rudolf Flesch, The Art of Readable Writing.
8.  John Maguire, THE READABLE WRITING GUIDE. https://www.youtube.com/watch?v=TUz4tjSVn4w
9.  Gradio Documentation. https://www.gradio.app/
10.  Textstat Library. https://github.com/fnl/textstat

---

**许可信息**
本项目基于 `textstat.py` 开源算法库许可证开源。具体许可信息请参见文本统计模块的文件头或项目根目录的 LICENSE 文件。词频数据（BNC, AME, Collins）受各自来源版权保护，仅供研究和教育使用。

---
**附录1：Rix 分级快速参考表 (基于 Kretschmer, 1984)**

| Rix Score Range | Estimated Grade Level |
| :--- | :--- |
| < 0.20 | 1st Grade |
| 0.20 - 0.49 | 2nd Grade |
| 0.50 - 0.79 | 3rd Grade |
| 0.80 - 1.29 | 4th Grade |
| 1.30 - 1.79 | 5th Grade |
| 1.80 - 2.39 | 6th Grade |
| 2.40 - 2.99 | 7th Grade |
| 3.00 - 3.69 | 8th Grade |
| 3.70 - 4.49 | 9th Grade |
| 4.50 - 5.29 | 10th Grade |
| 5.30 - 6.19 | 11th Grade |
| 6.20 - 7.19 | 12th Grade |
| >= 7.20 | College |

*(注：此表为基于原始文档逻辑的近似映射，实际应用中建议结合具体文本语境判断。)*

**附录2：将 Joseph C. Kretschmer 文档中提供的 **RIXRATE** (BASIC程序) 转换为现代 **Python** 程序**

Python 脚本保留了原版 BASIC 程序的核心逻辑：
1.  **实时统计**：逐句输入，实时显示统计结果。
2.  **长词定义**：单词长度 > 6 (即 7 个字母及以上)。
3.  **Rix 公式**：`Rix = 长词总数 / 句子总数`。
4.  **年级映射**：根据 Rix 值映射到对应的年级水平。

### Python 代码实现

```python
import sys
import os

class RixAnalyzer:
    def __init__(self):
        # 初始化统计变量
        self.total_words = 0
        self.num_sentences = 0
        self.num_long_words = 0
        self.current_word_len = 0
        self.running_text_title = ""
        
        # Rix 到 Grade Level 的映射表 (基于原始文档中的 BASIC 逻辑)
        # 原始逻辑: 
        # RX < .2 -> G=1
        # RX < .5 -> G=2
        # ...
        # RX > 7.2 -> G=13 (College)
        self.grade_levels = [
            {"max_rx": 0.2, "grade": 1},
            {"max_rx": 0.5, "grade": 2},
            {"max_rx": 0.8, "grade": 3},
            {"max_rx": 1.3, "grade": 4},
            {"max_rx": 1.8, "grade": 5},
            {"max_rx": 2.4, "grade": 6},
            {"max_rx": 3.0, "grade": 7},
            {"max_rx": 3.7, "grade": 8},
            {"max_rx": 4.5, "grade": 9},
            {"max_rx": 5.3, "grade": 10},
            {"max_rx": 6.2, "grade": 11},
            {"max_rx": 7.2, "grade": 12},
            {"max_rx": float('inf'), "grade": "College"}
        ]

    def clear_screen(self):
        """跨平台清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_grade_from_rix(self, rix_value):
        """根据 Rix 值查找对应的年级"""
        for level in self.grade_levels:
            if rix_value < level["max_rx"]:
                return level["grade"]
        return "College"

    def update_stats_and_print(self):
        """更新状态并打印当前统计信息"""
        if self.num_sentences == 0:
            avg_sentence_len = 0
        else:
            avg_sentence_len = self.total_words / self.num_sentences
            
        # 计算 Rix 值
        if self.num_sentences == 0:
            rix_val = 0
        else:
            rix_val = self.num_long_words / self.num_sentences
            
        current_grade = self.get_grade_from_rix(rix_val)
        
        # 格式化输出，尽量模拟原 BASIC 程序的屏幕布局
        print("-" * 50)
        print(f"TEXT: {self.running_text_title}")
        print(f"TOTAL WORDS: {self.total_words}")
        print(f"NO. SENTENCES: {self.num_sentences}")
        print(f"NO. LONG WORDS (>6 chars): {self.num_long_words}")
        print(f"AV. SENT. LENGTH: {avg_sentence_len:.1f}")
        print(f"Rix SCORE: {rix_val:.2f}")
        print(f"ESTIMATED GRADE LEVEL: {current_grade}")
        print("-" * 50)
        
        # 模拟原程序中的小延迟，让更新更清晰
        # time.sleep(0.5) 

    def run(self):
        """主程序循环"""
        self.clear_screen()
        print("RIXRATE READABILITY PROGRAM")
        print("BASED ON THE RIX FORMULA")
        print("BY J. ANDERSON")
        print("PYTHON PORT BY ASSISTANT")
        print()
        
        # 获取文本标题
        try:
            title = input("Enter a short title for the text (9 chars max): ")
        except EOFError:
            return
            
        # 限制标题长度以匹配原程序逻辑 (虽然Python中不需要，但为了忠实还原)
        self.running_text_title = title[:9]
        
        self.clear_screen()
        print("Instructions:")
        print("1. Type sentences one by one.")
        print("2. Press ENTER to finish a sentence.")
        print("3. Use spaces between words.")
        print("4. Omit punctuation except apostrophes and hyphens.")
        print("5. Press Ctrl+C to exit.")
        print("-" * 50)
        
        try:
            while True:
                # 获取用户输入
                try:
                    sentence = input(">> Enter sentence: ")
                except EOFError:
                    break
                
                if not sentence:
                    continue

                # 处理输入：转换为大写以符合原程序逻辑，并去除首尾空白
                sentence = sentence.upper().strip()
                
                # 简单的分词处理
                # 原 BASIC 程序通过检查空格 CHR$(32) 来分割单词
                # 这里我们模拟同样的逻辑：按空格分割
                words = sentence.split(' ')
                
                for word in words:
                    if word:
                        self.total_words += 1
                        # 计算单词长度
                        # 原程序逻辑: L = L + 1; IF L > 6 THEN LW = LW + 1; L = -30
                        # 这意味着只要单词长度 >= 7 就算长词
                        if len(word) > 6:
                            self.num_long_words += 1
                
                # 每输入一行（按回车），视为一个句子结束
                self.num_sentences += 1
                
                # 更新显示
                self.update_stats_and_print()
                
        except KeyboardInterrupt:
            print("\n\nProgram interrupted.")
        except Exception as e:
            print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    analyzer = RixAnalyzer()
    analyzer.run()
```

### 代码说明与对照

1.  **变量对应关系**：
    *   BASIC `W` (Total Words) -> Python `self.total_words`
    *   BASIC `S` (Number of Sentences) -> Python `self.num_sentences`
    *   BASIC `LW` (Long Words) -> Python `self.num_long_words`
    *   BASIC `L` (Current Word Length Counter) -> Python 内部通过 `len(word)` 直接处理，效果等同于原程序中的累加判断 `IF L > 6 THEN...`。

2.  **长词定义**：
    *   原 BASIC 代码：`IF L > 6 THEN LW = LW + 1`。这意味着当字母计数超过 6（即第 7 个字母存在时），计数器增加。因此，**7个或更多字母**的单词被定义为长词。
    *   Python 代码：`if len(word) > 6:` 完全实现了这一逻辑。

3.  **分级映射 (Grade Level Mapping)**：
    *   原 BASIC 代码使用了一系列 `IF RX < x THEN G = y` 的语句。
    *   Python 代码将其重构为 `self.grade_levels` 列表，逻辑完全一致：
        *   `RX < 0.2` -> Grade 1
        *   `RX < 0.5` -> Grade 2
        *   ...
        *   `RX > 7.2` -> College

4.  **交互方式**：
    *   原程序是字符流式的（逐字符读取）。
    *   Python 程序采用行式输入（逐行读取），这在现代终端交互中更自然。由于原程序的核心统计单元是“句子”，而用户通常以行为单位输入句子，因此这种映射是安全的。每按一次回车，程序就更新一次统计，这与原程序“Press ENTER... statistics... are immediately updated”的行为一致。

### 如何使用

1.  确保你安装了 Python 3。
2.  将上述代码保存为 `rixrate.py`。
3.  在终端或命令提示符中运行：
    ```bash
    python rixrate.py
    ```
4.  按照提示输入文本标题，然后逐句输入你想分析的文本。每按一次 Enter，屏幕会刷新显示当前的 Rix 分数和预估年级。
5.  按 `Ctrl+C` 退出程序。

### 与原程序的主要区别（现代化改进）

*   **标点处理**：原 BASIC 程序要求用户手动省略标点（除了撇号和连字符），因为它没有内置的正则表达式解析器。这个 Python 版本使用 `split(' ')` 进行简单分词，如果你输入了标点（如 "hello,"），它会被算作文本的一部分（长度变为 6，不算长词；如果变成 "hello,!"，长度为 7，就算长词）。**为了获得与原始研究完全一致的结果，建议输入时去掉标点，或者在代码中增加 `strip()` 和标点移除逻辑。**
    *   *可选改进*：如果需要更精确的匹配，可以在 `for word in words:` 循环中加入：
        ```python
        word = word.strip(".,!?;:\"'")
        if not word: continue
        ```
*   **屏幕刷新**：原程序在 TRS-80 上通过 `PRINT@` 精确定位光标。Python 版本使用简单的多行打印。如果你希望在终端中实现类似“原地更新”的效果，可以使用 ANSI 转义序列，但对于学术研究和日常分析，多行打印更清晰且不易出错。
