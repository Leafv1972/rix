"""
textstat_gradio_webui.py - Gradio WebUI前端
文本可读性分析工具 (RIX指数计算器)
"""

import warnings
import re
import math
from collections import Counter
from typing import Union, List, Set
from functools import lru_cache
import gradio as gr
import webbrowser
import threading
import os

warnings.filterwarnings("ignore", category=DeprecationWarning)

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

text_1 ="""

Introduction
'I don't trust you. You are one of them, right? You all just want to sell me like some animal.' This was the first message a young Taiwanese woman named Alice (a pseudonym) sent to us when we reached out to her after she was rescued from a scam compound in Sihanoukville, Cambodia. Like the dozens of other survivors we met in the following months, her harrowing experience had left her unable to trust anyone.
　In the ensuing two weeks, as we continued to exchange messages, Alice was always on edge. Penniless and paperless, she was staying in a safe house in Phnom Penh together with other survivors who mostly came from mainland China, waiting to find a way to return home to the small child she had left behind. It took some time, but eventually someone offered to pay for her journey back to Taiwan. Just a few days before her flight, she agreed to meet with one of us in a public place. It was then that she shared her whole story: 'I feel lucky because I was rescued very quickly, basically in a week. If I had been enslaved for a year or two, I might not be able to believe in humanity anymore. I know some of the victims have been brainwashed, or some have been tortured to the point that they are numb or have developed some mental illness. And at the same time, people outside, including my own family, think that I was trafficked because I am greedy and wanted to get rich overnight. So, I need to tell my story. I need to let them know the real situation.'
　Knowing that she had been tortured and sexually abused in four different scam compounds, it was shocking to hear Alice describing herself as 'lucky'. She had been lured by a bogus job presented to her by a friend whom she trusted, a man in the Philippines who even paid for her visa and flight to Phnom Penh. When she arrived at her supposed new office in Sihanoukville, the supervisor informed her that she had been sold there to conduct online scams and that she would not be allowed to leave until she had earned enough money for the company. Threatening her with a stun gun, he said that if she did not comply, he would lock her up in a room and let several men rape her, which is exactly what happened soon after.
　'At the beginning, they tried to force me to do pig-butchering work,' she said, referring to a type of online scam, called shazhupan in Chinese, in which scammers take on fictional profiles, initiate contact with hapless marks, and then slowly gain their trust before tricking them into fake investments.1
　'I knew it was illegal, so I played dumb and said that I didn't know how to type. So, they assigned me to do cleaning and paperwork. Then they sold me again and again. I was repeatedly raped and almost forced to work in a brothel-like clubhouse in the last company.'
　Alice eventually found a way to post a call for help on Instagram and was rescued before being sold a fifth time. Because of that cry for help, however, everyone in her social circles has come to know what happened to her, which has led to public shaming and is making her reintegration more difficult now that she is back home. As she told us: 'I want you to write about me. I am a victim of modern slavery, but no organisation is helping me. I also want to say it is not a matter of being greedy or stupid. It can really happen to anyone.'

"""


class textstatistics:
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
    def rix(self, text: str) -> tuple:
        words = self.remove_punctuation(text).split()
        sentences_count = self.sentence_count(text)
        
        long_words_count = 0
        long_words_list = []
        
        for wrd in words:
            if len(wrd) >= 7:
                long_words_count += 1
                long_words_list.append(wrd)
                
        try:
            rix = long_words_count / sentences_count
        except ZeroDivisionError:
            rix = 0.00
        
        sweden_grade_rix = ""
        
        if rix >= 7.2:
            sweden_grade_rix = "Sweden RIX College"
        elif rix >= 6.2 and rix < 7.2:
            sweden_grade_rix = "Sweden RIX Grade 12"
        elif rix >= 5.3 and rix < 6.2:
            sweden_grade_rix = "Sweden RIX Grade 11"
        elif rix >= 4.5 and rix < 5.3:
            sweden_grade_rix = "Sweden RIX Grade 10"
        elif rix >= 3.7 and rix < 4.5:
            sweden_grade_rix = "Sweden RIX Grade 09"
        elif rix >= 3.0 and rix < 3.7:
            sweden_grade_rix = "Sweden RIX Grade 08"
        elif rix >= 2.4 and rix < 3.0:
            sweden_grade_rix = "Sweden RIX Grade 07"
        elif rix >= 1.8 and rix < 2.4:
            sweden_grade_rix = "Sweden RIX Grade 06"
        elif rix >= 1.3 and rix < 1.8:
            sweden_grade_rix = "Sweden RIX Grade 05"
        elif rix >= 0.8 and rix < 1.3:
            sweden_grade_rix = "Sweden RIX Grade 04"
        elif rix > 0.5 and rix < 0.8:
            sweden_grade_rix = "Sweden RIX Grade 03"
        elif rix >= 0.2 and rix <= 0.5:
            sweden_grade_rix = "Sweden RIX Grade 02"
        elif rix < 0.2:
            sweden_grade_rix = "Sweden RIX Grade 01" 

        return self._legacy_round(rix, 2), sweden_grade_rix, long_words_count, sentences_count, long_words_list

    @lru_cache(maxsize=128)
    def get_long_words(self, text: str) -> list:
        word_list = self.remove_punctuation(text).split()
        long_words_list = []
        for wrd in word_list:
            if len(wrd) >= 7:
                long_words_list.append(wrd)
        return long_words_list


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
        return "", "Please enter text for analysis", ""
    
    file_path = file if isinstance(file, str) else file.name
    content = detect_and_convert_to_utf8(file_path)
    result_text, long_words_md = analyze_text(content)
    return content, result_text, long_words_md

def load_sample_text(sample_name):
    if sample_name not in SAMPLE_TEXTS:
        return "", "Please enter text for analysis", ""
    text = SAMPLE_TEXTS[sample_name]
    result_text, long_words_md = analyze_text(text)
    return text, result_text, long_words_md

def analyze_text(text: str) -> tuple:
    load_word_frequency()
    ts = textstatistics()
    rix_value, grade, long_count, sent_count, long_words = ts.rix(text)
    total_words = ts.lexicon_count(text)
    
    result_text = f"""## RIX Analysis Results

| Metric | Value |
|--------|-------|
| **RIX Index** | {rix_value} |
| **Reading Level** | {grade} |
| **Total Words** | {total_words} |
| **Sentences** | {sent_count} |
| **Long Words (≥7 chars)** | {long_count} |

### RIX Formula
**RIX = Long Words / Sentences = {long_count} / {sent_count} = {rix_value}**

### RIX Grade Scale
| RIX Range | Grade Level |
|-----------|-------------|
| < 0.2 | Grade 01 |
| 0.2 - 0.5 | Grade 02 |
| 0.5 - 0.8 | Grade 03 |
| 0.8 - 1.3 | Grade 04 |
| 1.3 - 1.8 | Grade 05 |
| 1.8 - 2.4 | Grade 06 |
| 2.4 - 3.0 | Grade 07 |
| 3.0 - 3.7 | Grade 08 |
| 3.7 - 4.5 | Grade 09 |
| 4.5 - 5.3 | Grade 10 |
| 5.3 - 6.2 | Grade 11 |
| 6.2 - 7.2 | Grade 12 |
| ≥ 7.2 | College |
"""
    
    word_freq = Counter(long_words)
    sorted_words = sorted(word_freq.items(), key=lambda x: (-x[1], x[0]))
    
    long_words_md = "## Long Words List (≥7 letters)\n\n| No. | Word | Count | AME | BNC | Collins |\n|-----|------|-------|-----|-----|----------|\n"
    for idx, (word, count) in enumerate(sorted_words, 1):
        word_lower = word.lower()
        ame_rank = WORD_FREQUENCY_AME.get(word_lower, "-")
        bnc_rank = WORD_FREQUENCY_BNC.get(word_lower, "-")
        
        collins_stars = ""
        if word_lower in COLLINS_5STARS:
            collins_stars = "★★★★★"
        elif word_lower in COLLINS_4STARS:
            collins_stars = "★★★★☆"
        elif word_lower in COLLINS_3STARS:
            collins_stars = "★★★☆☆"
        elif word_lower in COLLINS_2STARS:
            collins_stars = "★★☆☆☆"
        elif word_lower in COLLINS_1STARS:
            collins_stars = "★☆☆☆☆"
        elif word_lower in COLLINS_0STARS:
            collins_stars = "☆☆☆☆☆"
        else:
            collins_stars = "-"
        
        long_words_md += f"| {idx:05d} | {word} | {count} | {ame_rank} | {bnc_rank} | {collins_stars} |\n"
    
    return result_text, long_words_md


def create_interface():
    with gr.Blocks(
        title="RIX Text Readability Analyzer"
    ) as demo:
        gr.Markdown(
            """
            # RIX Text Readability Analyzer
            ### Readability Index Calculator
            
            **RIX Formula**: RIX = Long Words (≥7 letters) / Sentences
            - Higher RIX value = More difficult text
            - Lower RIX value = Easier text
            """
        )
        
        with gr.Row():
            with gr.Column(scale=2):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Upload TXT File")
                        file_upload = gr.File(
                            label="Upload TXT File",
                            file_types=[".txt"],
                            type="filepath"
                        )
                        gr.Markdown(
                            """
                            **Note**: 
                            - Supports .txt plain text files
                            - Auto-detects file encoding and converts to UTF-8
                            - Supported encodings: UTF-8, GBK, GB2312, Big5, Shift-JIS, etc.
                            """
                        )
                    
                    with gr.Column(scale=1):
                        gr.Markdown("### Sample Texts")
                        sample_dropdown = gr.Dropdown(
                            choices=list(SAMPLE_TEXTS.keys()),
                            label="Select Sample Text",
                            value=list(SAMPLE_TEXTS.keys())[0] if SAMPLE_TEXTS else None
                        )
                        gr.Markdown(
                            """
                            ### Grade Level Conversion Table
                            | RIX Range | Grade Level | RIX Range | Grade Level |
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
                
                gr.Markdown("### Input Text")
                input_text = gr.Textbox(
                    label="Text Content",
                    placeholder="Enter or edit text...",
                    lines=10,
                    max_lines=20,
                    interactive=True
                )
            
            with gr.Column(scale=1):
                result_output = gr.Markdown(
                    label="Analysis Results",
                    elem_classes=["output-box"]
                )
        
        with gr.Row():
            long_words_output = gr.Markdown(
                label="Long Words List (≥7 letters)",
                elem_classes=["output-box"]
            )
        
        file_upload.change(
            fn=process_uploaded_file,
            inputs=[file_upload],
            outputs=[input_text, result_output, long_words_output]
        )
        
        sample_dropdown.change(
            fn=load_sample_text,
            inputs=[sample_dropdown],
            outputs=[input_text, result_output, long_words_output]
        )
        
        input_text.change(
            fn=analyze_text,
            inputs=[input_text],
            outputs=[result_output, long_words_output]
        )
        
        input_text.submit(
            fn=analyze_text,
            inputs=[input_text],
            outputs=[result_output, long_words_output]
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
