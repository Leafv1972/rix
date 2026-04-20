"""
================================================================================
textstat_gradio_webui.py - RIX指数分析器 Gradio WebUI (完整版)
================================================================================

【模块概述】
本模块实现文本可读性分析功能，主要计算RIX指数(Readability Index)，
并提供Gradio Web界面用于在线分析。

【RIX指数原理】
RIX = 长单词数(≥7个字母) / 句子数
RIX值越高，文本越难阅读；RIX值越低，文本越容易阅读。

【功能】
- 输入文本进行分析
- 上传txt文件（自动转换为UTF-8编码）
- 显示RIX指数和美国年级等级
- 显示长单词列表（含词频排名）
- 显示统计信息

【依赖库】
1. warnings  - Python标准库，警告控制
2. re        - Python标准库，正则表达式
3. math      - Python标准库，数学运算
4. collections.Counter - Python标准库，计数器
5. typing    - Python标准库，类型提示
6. functools.lru_cache - Python标准库，缓存装饰器
7. gradio    - Web界面框架

【作者】textstat项目
【版本】3.0 (合并版)
================================================================================
"""

text_1 ="""

Introduction
'I don't trust you. You are one of them, right? You all just want to sell me like some animal.' This was the first message a young Taiwanese woman named Alice (a pseudonym) sent to us when we reached out to her after she was rescued from a scam compound in Sihanoukville, Cambodia. Like the dozens of other survivors we met in the following months, her harrowing experience had left her unable to trust anyone.
　In the ensuing two weeks, as we continued to exchange messages, Alice was always on edge. Penniless and paperless, she was staying in a safe house in Phnom Penh together with other survivors who mostly came from mainland China, waiting to find a way to return home to the small child she had left behind. It took some time, but eventually someone offered to pay for her journey back to Taiwan. Just a few days before her flight, she agreed to meet with one of us in a public place. It was then that she shared her whole story: 'I feel lucky because I was rescued very quickly, basically in a week. If I had been enslaved for a year or two, I might not be able to believe in humanity anymore. I know some of the victims have been brainwashed, or some have been tortured to the point that they are numb or have developed some mental illness. And at the same time, people outside, including my own family, think that I was trafficked because I am greedy and wanted to get rich overnight. So, I need to tell my story. I need to let them know the real situation.'
　Knowing that she had been tortured and sexually abused in four different scam compounds, it was shocking to hear Alice describing herself as 'lucky'. She had been lured by a bogus job presented to her by a friend whom she trusted, a man in the Philippines who even paid for her visa and flight to Phnom Penh. When she arrived at her supposed new office in Sihanoukville, the supervisor informed her that she had been sold there to conduct online scams and that she would not be allowed to leave until she had earned enough money for the company. Threatening her with a stun gun, he said that if she did not comply, he would lock her up in a room and let several men rape her, which is exactly what happened soon after.
　'At the beginning, they tried to force me to do pig-butchering work,' she said, referring to a type of online scam, called shazhupan in Chinese, in which scammers take on fictional profiles, initiate contact with hapless marks, and then slowly gain their trust before tricking them into fake investments.1
　'I knew it was illegal, so I played dumb and said that I didn't know how to type. So, they assigned me to do cleaning and paperwork. Then they sold me again and again. I was repeatedly raped and almost forced to work in a brothel-like clubhouse in the last company.'
　Alice eventually found a way to post a call for help on Instagram and was rescued before being sold a fifth time. Because of that cry for help, however, everyone in her social circles has come to know what happened to her, which has led to public shaming and is making her reintegration more difficult now that she is back home. As she told us: 'I want you to write about me. I am a victim of modern slavery, but no organisation is helping me. I also want to say it is not a matter of being greedy or stupid. It can really happen to anyone.'

"""

import warnings
import re
import math
from collections import Counter
from typing import Union, List, Set
from functools import lru_cache
import gradio as gr
import os
import webbrowser
import threading

warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*theme.*parameter.*")
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*css.*parameter.*")


class textstatistics:
    """
    文本统计分析类
    
    该类提供文本可读性分析功能，包括：
    - RIX指数计算（英语可读性指数）
    - 词汇统计
    - 句子计数
    - 长单词统计
    """
    
    __lang = "en_US"
    __easy_word_sets = {}
    __round_outputs = True
    __round_points = None
    __rm_apostrophe = True
    text_encoding = "utf-8"

    def _cache_clear(self) -> None:
        caching_methods = [
            method for method in dir(self)
            if callable(getattr(self, method))
            and hasattr(getattr(self, method), "cache_info")
        ]
        for method in caching_methods:
            getattr(self, method).cache_clear()

    def _legacy_round(self, number: float, points: int = 0) -> float:
        points = self.__round_points if (
            self.__round_points is not None) else points
        if self.__round_outputs:
            p = 10 ** points
            return float(
                math.floor((number * p) + math.copysign(0.5, number))) / p
        else:
            return number

    def set_rounding(
        self, rounding: bool, points: Union[int, None] = None
    ) -> None:
        self.__round_outputs = rounding
        self.__round_points = points

    def set_rm_apostrophe(self, rm_apostrophe: bool) -> None:
        self.__rm_apostrophe = rm_apostrophe

    @lru_cache(maxsize=128)
    def remove_punctuation(self, text: str) -> str:
        if self.__rm_apostrophe:
            punctuation_regex = r"[^\w\s]"
        else:
            text = re.sub(r"\'(?![tsd]\b|ve\b|ll\b|re\b)", '"', text)
            punctuation_regex = r"[^\w\s\']"
        text = re.sub(punctuation_regex, '', text)
        return text

    @lru_cache(maxsize=128)
    def lexicon_count(self, text: str, removepunct: bool = True) -> int:
        if removepunct:
            text = self.remove_punctuation(text)
        count = len(text.split())
        return count

    @lru_cache(maxsize=128)
    def sentence_count(self, text: str) -> int:
        ignore_count = 0
        sentences = re.findall(r'\b[^.!?]+[.!?]*', text, re.UNICODE)
        for sentence in sentences:
            if self.lexicon_count(sentence) <= 2:
                ignore_count += 1
        return max(1, len(sentences) - ignore_count)

    @lru_cache(maxsize=128)
    def rix(self, text: str) -> float:
        words = self.remove_punctuation(text).split()
        sentences_count = self.sentence_count(text)
        
        long_words_count = 0
        for wrd in words:
            if len(wrd) >= 7:
                long_words_count += 1
                
        try:
            rix = long_words_count / sentences_count
        except ZeroDivisionError:
            rix = 0.00
        
        sweden_grade_rix = ""
        
        if rix >= 7.2:
            sweden_grade_rix = "College"
        elif rix >= 6.2:
            sweden_grade_rix = "Grade 12"
        elif rix >= 5.3:
            sweden_grade_rix = "Grade 11"
        elif rix >= 4.5:
            sweden_grade_rix = "Grade 10"
        elif rix >= 3.7:
            sweden_grade_rix = "Grade 09"
        elif rix >= 3.0:
            sweden_grade_rix = "Grade 08"
        elif rix >= 2.4:
            sweden_grade_rix = "Grade 07"
        elif rix >= 1.8:
            sweden_grade_rix = "Grade 06"
        elif rix >= 1.3:
            sweden_grade_rix = "Grade 05"
        elif rix >= 0.8:
            sweden_grade_rix = "Grade 04"
        elif rix > 0.5:
            sweden_grade_rix = "Grade 03"
        elif rix >= 0.2:
            sweden_grade_rix = "Grade 02"
        else:
            sweden_grade_rix = "Grade 01"

        return self._legacy_round(rix, 2), sweden_grade_rix, long_words_count, sentences_count


ts = textstatistics()

WORD_FREQUENCY_AME = {}
WORD_FREQUENCY_BNC = {}
COLLINS_5STARS = set()
COLLINS_4STARS = set()
COLLINS_3STARS = set()
COLLINS_2STARS = set()
COLLINS_1STARS = set()
COLLINS_0STARS = set()
WORD_FREQ_LOADED = False

def load_word_frequency():
    global WORD_FREQUENCY_AME, WORD_FREQUENCY_BNC, WORD_FREQ_LOADED
    global COLLINS_5STARS, COLLINS_4STARS, COLLINS_3STARS, COLLINS_2STARS, COLLINS_1STARS, COLLINS_0STARS
    if WORD_FREQ_LOADED:
        return
    
    base_path = os.path.dirname(__file__)
    
    ame_path = os.path.join(base_path, "AME20000.txt")
    if os.path.exists(ame_path):
        try:
            with open(ame_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        try:
                            rank = int(parts[0])
                            word = parts[1].lower().strip()
                            if word and word not in WORD_FREQUENCY_AME:
                                WORD_FREQUENCY_AME[word] = rank
                        except ValueError:
                            continue
        except Exception:
            pass
    
    bnc_path = os.path.join(base_path, "BNC15000.txt")
    if os.path.exists(bnc_path):
        try:
            with open(bnc_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            rank = int(parts[0])
                            word = parts[1].lower().strip()
                            if word and word not in WORD_FREQUENCY_BNC:
                                WORD_FREQUENCY_BNC[word] = rank
                        except ValueError:
                            continue
        except Exception:
            pass
    
    collins_files = {
        "1_Collins5Stars.txt": COLLINS_5STARS,
        "2_Collins4Stars.txt": COLLINS_4STARS,
        "3_Collins3Stars.txt": COLLINS_3STARS,
        "4_Collins2Stars.txt": COLLINS_2STARS,
        "5_Collins1Stars.txt": COLLINS_1STARS,
        "6_Collins0Stars.txt": COLLINS_0STARS,
    }
    
    for filename, word_set in collins_files.items():
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        word = line.strip().lower()
                        if word:
                            word_set.add(word)
            except Exception:
                pass
    
    WORD_FREQ_LOADED = True

load_word_frequency()

ENCODING_LIST = [
    'utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030',
    'big5', 'shift_jis', 'euc-jp', 'euc-kr',
    'iso-8859-1', 'iso-8859-2', 'iso-8859-15',
    'windows-1250', 'windows-1251', 'windows-1252',
    'ascii', 'latin-1'
]

def detect_and_convert_to_utf8(file_path: str) -> str:
    if not file_path or not os.path.exists(file_path):
        return ""
    
    for encoding in ENCODING_LIST:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return content
        except (UnicodeDecodeError, UnicodeError):
            continue
    
    try:
        with open(file_path, 'rb') as f:
            raw_bytes = f.read()
        content = raw_bytes.decode('utf-8', errors='replace')
        return content
    except Exception:
        return ""

def load_sample_texts():
    base_path = os.path.dirname(__file__)
    txt_folder = os.path.join(base_path, "txt")
    
    sample_texts = {}
    
    if os.path.exists(txt_folder):
        for filename in os.listdir(txt_folder):
            if filename.endswith('.txt'):
                filepath = os.path.join(txt_folder, filename)
                try:
                    content = detect_and_convert_to_utf8(filepath)
                    if content:
                        file_name = os.path.splitext(filename)[0]
                        sample_texts[file_name] = content
                except Exception:
                    pass
    
    return sample_texts

SAMPLE_TEXTS = load_sample_texts()

def process_uploaded_file(file):
    if file is None:
        return "", "请输入文本进行分析", "", "", ""
    
    file_path = file if isinstance(file, str) else file.name
    content = detect_and_convert_to_utf8(file_path)
    rix_result, grade_result, stats_result, long_words_result = analyze_text(content)
    return content, rix_result, grade_result, stats_result, long_words_result

def load_sample_text(sample_name):
    if sample_name not in SAMPLE_TEXTS:
        return "", "请输入文本进行分析", "", "", ""
    text = SAMPLE_TEXTS[sample_name]
    rix_result, grade_result, stats_result, long_words_result = analyze_text(text)
    return text, rix_result, grade_result, stats_result, long_words_result

def analyze_text(text: str):
    if not text or text.strip() == "":
        return "请输入文本进行分析", "", "", ""
    
    ts._cache_clear()
    
    rix_value, grade_level, long_words_count, sentences_count = ts.rix(text)
    word_count = ts.lexicon_count(text)
    
    words = ts.remove_punctuation(text).split()
    long_words = [wrd for wrd in words if len(wrd) >= 7]
    
    if long_words:
        long_words_table = "| 序号 | 长单词 | 字母数 | 美国词频 | 英国词频 | 5星 | 4星 | 3星 | 2星 | 1星 | 0星 |\n"
        long_words_table += "|------|--------|--------|----------|----------|-----|-----|-----|-----|-----|-----|\n"
        for idx, word in enumerate(long_words, 1):
            word_lower = word.lower()
            ame_rank = WORD_FREQUENCY_AME.get(word_lower, "-")
            bnc_rank = WORD_FREQUENCY_BNC.get(word_lower, "-")
            c5 = "✓" if word_lower in COLLINS_5STARS else "-"
            c4 = "✓" if word_lower in COLLINS_4STARS else "-"
            c3 = "✓" if word_lower in COLLINS_3STARS else "-"
            c2 = "✓" if word_lower in COLLINS_2STARS else "-"
            c1 = "✓" if word_lower in COLLINS_1STARS else "-"
            c0 = "✓" if word_lower in COLLINS_0STARS else "-"
            long_words_table += f"| {idx} | {word} | {len(word)} | {ame_rank} | {bnc_rank} | {c5} | {c4} | {c3} | {c2} | {c1} | {c0} |\n"
    else:
        long_words_table = "无长单词"
    
    stats_info = f"""文本统计信息:
- 总单词数: {word_count}
- 句子数: {sentences_count}
- 长单词数(≥7字母): {long_words_count}
- RIX指数: {rix_value}
- 美国年级等级: {grade_level}"""
    
    rix_result = f"RIX指数: {rix_value}"
    grade_result = f"年级等级: {grade_level}"
    
    return rix_result, grade_result, stats_info, long_words_table

def create_interface():
    with gr.Blocks(
        title="RIX文本可读性分析器"
    ) as demo:
        gr.Markdown(
            """
            # RIX文本可读性分析器
            ### 英语可读性指数 (Readability Index) 计算工具
            
            **RIX指数原理**: RIX = 长单词数(≥7个字母) / 句子数
            - RIX值越高，文本越难阅读
            - RIX值越低，文本越容易阅读
            """
        )
        
        with gr.Row():
            with gr.Column(scale=2):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 上传TXT文件")
                        file_upload = gr.File(
                            label="上传TXT纯文本文件",
                            file_types=[".txt"],
                            type="filepath"
                        )
                        gr.Markdown(
                            """
                            **说明**: 
                            - 支持上传 .txt 纯文本文件
                            - 自动检测文件编码并转换为UTF-8
                            - 支持的编码: UTF-8, GBK, GB2312, Big5, Shift-JIS等
                            """
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### 示例文本")
                        sample_dropdown = gr.Dropdown(
                            choices=list(SAMPLE_TEXTS.keys()),
                            label="选择示例文本",
                            value=list(SAMPLE_TEXTS.keys())[0] if SAMPLE_TEXTS else None
                        )
                        gr.Markdown(
                            """
                            ### 美国年级等级对照表
                            | RIX范围 | 年级等级 | RIX范围 | 年级等级 |
                            |---------|----------|---------|----------|
                            | < 0.2 | Grade 01 | 3.0-3.7 | Grade 08 |
                            | 0.2-0.5 | Grade 02 | 3.7-4.5 | Grade 09 |
                            | 0.5-0.8 | Grade 03 | 4.5-5.3 | Grade 10 |
                            | 0.8-1.3 | Grade 04 | 5.3-6.2 | Grade 11 |
                            | 1.3-1.8 | Grade 05 | 6.2-7.2 | Grade 12 |
                            | 1.8-2.4 | Grade 06 | ≥ 7.2 | College |
                            | 2.4-3.0 | Grade 07 | | |
                            """
                        )
                
                gr.Markdown("### 输入文本内容")
                input_text = gr.Textbox(
                    label="文本内容",
                    placeholder="请输入或编辑文本...",
                    lines=10,
                    max_lines=20,
                    interactive=True
                )
            
            with gr.Column(scale=1):
                rix_output = gr.Textbox(
                    label="RIX指数",
                    interactive=False,
                    elem_classes=["output-box"]
                )
                grade_output = gr.Textbox(
                    label="年级等级",
                    interactive=False,
                    elem_classes=["output-box"]
                )
                stats_output = gr.Textbox(
                    label="统计信息",
                    interactive=False,
                    lines=6,
                    elem_classes=["output-box"]
                )
        
        with gr.Row():
            long_words_output = gr.Markdown(
                label="长单词列表 (≥7字母)",
                elem_classes=["output-box"]
            )
        
        file_upload.change(
            fn=process_uploaded_file,
            inputs=[file_upload],
            outputs=[input_text, rix_output, grade_output, stats_output, long_words_output]
        )
        
        sample_dropdown.change(
            fn=load_sample_text,
            inputs=[sample_dropdown],
            outputs=[input_text, rix_output, grade_output, stats_output, long_words_output]
        )
        
        input_text.change(
            fn=analyze_text,
            inputs=[input_text],
            outputs=[rix_output, grade_output, stats_output, long_words_output]
        )
        
        input_text.submit(
            fn=analyze_text,
            inputs=[input_text],
            outputs=[rix_output, grade_output, stats_output, long_words_output]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    
    def open_browser():
        webbrowser.open("http://127.0.0.1:7860/?__theme=dark")
    
    threading.Timer(2.0, open_browser).start()
    
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {max-width: 1200px !important;}
        .output-box {min-height: 100px;}
        """
    )
