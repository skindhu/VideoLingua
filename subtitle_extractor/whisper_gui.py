#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Whisper字幕提取工具的图形用户界面
"""

import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinter.scrolledtext import ScrolledText
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config import get_default_settings, get_api_key

class WhisperGUI:
    def __init__(self, root):
        # 获取默认设置
        self.default_settings = get_default_settings()

        self.root = root
        self.root.title("字幕提取与翻译工具")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 创建文件选择框架
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=5)

        # 视频文件选择
        ttk.Label(file_frame, text="视频文件:").pack(side=tk.LEFT)
        self.video_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.video_path_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(file_frame, text="浏览", command=self.browse_file).pack(side=tk.LEFT)

        # 输出目录选择
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=5)

        ttk.Label(output_frame, text="输出目录:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar(value=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output"))
        ttk.Entry(output_frame, textvariable=self.output_dir_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="浏览", command=self.browse_output_dir).pack(side=tk.LEFT)

        # 选项框架
        options_frame = ttk.LabelFrame(main_frame, text="选项")
        options_frame.pack(fill=tk.X, pady=5)

        # 模型选择
        model_frame = ttk.Frame(options_frame)
        model_frame.pack(fill=tk.X, pady=5)

        ttk.Label(model_frame, text="Whisper模型:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value=self.default_settings['model'])
        models = [("Tiny", "tiny"), ("Base", "base"), ("Small", "small"), ("Medium", "medium"), ("Large", "large")]

        for text, value in models:
            ttk.Radiobutton(model_frame, text=text, value=value, variable=self.model_var).pack(side=tk.LEFT, padx=10)

        # 语言选择
        lang_frame = ttk.Frame(options_frame)
        lang_frame.pack(fill=tk.X, pady=5)

        ttk.Label(lang_frame, text="源语言:").pack(side=tk.LEFT)
        self.lang_var = tk.StringVar(value=self.default_settings['language'])
        self.lang_entry = ttk.Entry(lang_frame, textvariable=self.lang_var, width=5)
        self.lang_entry.pack(side=tk.LEFT, padx=5)

        # 字幕类型
        subtitle_type_frame = ttk.Frame(options_frame)
        subtitle_type_frame.pack(fill=tk.X, pady=5)

        ttk.Label(subtitle_type_frame, text="字幕类型:").pack(side=tk.LEFT)
        self.subtitle_type_var = tk.StringVar(value=self.default_settings['subtitle_type'])
        types = [("原始语言", "original"), ("翻译后", "translated"), ("双语", "bilingual")]

        for text, value in types:
            ttk.Radiobutton(subtitle_type_frame, text=text, value=value, variable=self.subtitle_type_var).pack(side=tk.LEFT, padx=10)

        # 目标语言
        dest_lang_frame = ttk.Frame(options_frame)
        dest_lang_frame.pack(fill=tk.X, pady=5)

        ttk.Label(dest_lang_frame, text="目标语言:").pack(side=tk.LEFT)
        self.dest_lang_var = tk.StringVar(value=self.default_settings['dest_language'])
        self.dest_lang_entry = ttk.Entry(dest_lang_frame, textvariable=self.dest_lang_var, width=10)
        self.dest_lang_entry.pack(side=tk.LEFT, padx=5)

        # 字幕烧录选项
        burn_frame = ttk.LabelFrame(options_frame, text="字幕烧录")
        burn_frame.pack(fill=tk.X, pady=5)

        # 是否烧录字幕
        burn_check_frame = ttk.Frame(burn_frame)
        burn_check_frame.pack(fill=tk.X, pady=5)

        self.burn_subtitles_var = tk.BooleanVar(value=self.default_settings['burn_subtitles'])
        ttk.Checkbutton(burn_check_frame, text="将字幕烧录到视频中", variable=self.burn_subtitles_var).pack(side=tk.LEFT)

        # 字体大小
        font_size_frame = ttk.Frame(burn_frame)
        font_size_frame.pack(fill=tk.X, pady=5)

        ttk.Label(font_size_frame, text="字体大小:").pack(side=tk.LEFT)

        self.font_size_var = tk.IntVar(value=self.default_settings['subtitle_font_size'])
        font_size_spinner = ttk.Spinbox(font_size_frame, from_=12, to=48, increment=2, textvariable=self.font_size_var, width=5)
        font_size_spinner.pack(side=tk.LEFT, padx=5)

        # 字幕位置
        position_frame = ttk.Frame(burn_frame)
        position_frame.pack(fill=tk.X, pady=5)

        ttk.Label(position_frame, text="字幕位置:").pack(side=tk.LEFT)

        self.subtitle_position_var = tk.StringVar(value=self.default_settings['subtitle_position'])
        positions = [("底部", "bottom"), ("顶部", "top"), ("中间", "middle")]

        for text, value in positions:
            ttk.Radiobutton(position_frame, text=text, value=value,
                           variable=self.subtitle_position_var).pack(side=tk.LEFT, padx=10)

        # 字体颜色
        font_color_frame = ttk.Frame(burn_frame)
        font_color_frame.pack(fill=tk.X, pady=5)

        ttk.Label(font_color_frame, text="字体颜色:").pack(side=tk.LEFT)

        self.font_color_var = tk.StringVar(value=self.default_settings['subtitle_font_color'])
        colors = [("白色", "white"), ("黄色", "yellow"), ("绿色", "green"),
                 ("青色", "cyan"), ("蓝色", "blue"), ("品红", "magenta"), ("红色", "red")]

        for text, value in colors:
            ttk.Radiobutton(font_color_frame, text=text, value=value,
                           variable=self.font_color_var).pack(side=tk.LEFT, padx=5)

        # 轮廓颜色
        outline_color_frame = ttk.Frame(burn_frame)
        outline_color_frame.pack(fill=tk.X, pady=5)

        ttk.Label(outline_color_frame, text="轮廓颜色:").pack(side=tk.LEFT)

        self.outline_color_var = tk.StringVar(value=self.default_settings['subtitle_outline_color'])
        outline_colors = [("黑色", "black"), ("白色", "white"), ("黄色", "yellow"),
                         ("绿色", "green"), ("青色", "cyan"), ("蓝色", "blue"),
                         ("品红", "magenta"), ("红色", "red")]

        # 使用下拉菜单来节省空间
        outline_color_combo = ttk.Combobox(outline_color_frame, textvariable=self.outline_color_var,
                                          values=[color[1] for color in outline_colors], state="readonly", width=10)
        outline_color_combo.pack(side=tk.LEFT, padx=5)

        # 添加颜色名称映射，用于显示
        color_names = {color[1]: color[0] for color in outline_colors}

        def update_outline_color_text(event):
            selected = self.outline_color_var.get()
            outline_color_combo.set(f"{color_names.get(selected, '')} ({selected})")

        outline_color_combo.bind("<<ComboboxSelected>>", update_outline_color_text)
        # 设置初始显示
        outline_color_combo.set(f"{color_names.get(self.outline_color_var.get(), '')} ({self.outline_color_var.get()})")

        # Gemini API密钥
        api_key_frame = ttk.Frame(options_frame)
        api_key_frame.pack(fill=tk.X, pady=5)

        ttk.Label(api_key_frame, text="Gemini API密钥:").pack(side=tk.LEFT)

        self.api_key_var = tk.StringVar(value=get_api_key() or "")
        self.api_key_entry = ttk.Entry(api_key_frame, textvariable=self.api_key_var, width=40, show="*")
        self.api_key_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.show_key_var = tk.BooleanVar(value=False)
        self.show_key_cb = ttk.Checkbutton(api_key_frame, text="显示",
                                         variable=self.show_key_var,
                                         command=self.toggle_api_key_visibility)
        self.show_key_cb.pack(side=tk.LEFT, padx=5)

        # 更新字幕类型变化时的UI状态
        self.subtitle_type_var.trace_add("write", self.update_translation_ui_state)

        # 输出格式
        format_frame = ttk.Frame(options_frame)
        format_frame.pack(fill=tk.X, pady=5)

        ttk.Label(format_frame, text="输出格式:").pack(side=tk.LEFT)

        self.srt_var = tk.BooleanVar(value=True)
        self.vtt_var = tk.BooleanVar(value=True)
        self.txt_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(format_frame, text="SRT", variable=self.srt_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(format_frame, text="VTT", variable=self.vtt_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(format_frame, text="TXT", variable=self.txt_var).pack(side=tk.LEFT, padx=5)

        # 保留音频选项
        keep_audio_frame = ttk.Frame(options_frame)
        keep_audio_frame.pack(fill=tk.X, pady=5)

        self.keep_audio_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(keep_audio_frame, text="保留提取的音频文件", variable=self.keep_audio_var).pack(side=tk.LEFT)

        # 开始按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        self.start_button = ttk.Button(button_frame, text="开始提取字幕", command=self.start_extraction)
        self.start_button.pack(side=tk.RIGHT)

        # 日志输出区域
        log_frame = ttk.LabelFrame(main_frame, text="日志")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.log_text = ScrolledText(log_frame, wrap=tk.WORD, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

        # 进度条
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=100, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=10)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 初始化
        self.extraction_thread = None
        self.is_extracting = False

    def browse_file(self):
        """浏览选择视频文件"""
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            filetypes=[
                ("视频文件", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.video_path_var.set(file_path)
            # 如果未设置输出目录，默认使用默认输出目录
            if not self.output_dir_var.get():
                default_output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
                os.makedirs(default_output_dir, exist_ok=True)
                self.output_dir_var.set(default_output_dir)

    def browse_output_dir(self):
        """浏览选择输出目录"""
        dir_path = filedialog.askdirectory(title="选择输出目录")
        if dir_path:
            self.output_dir_var.set(dir_path)

    def log(self, message):
        """向日志区域添加消息"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def start_extraction(self):
        """开始提取字幕"""
        if self.is_extracting:
            messagebox.showwarning("警告", "正在处理中，请等待当前任务完成")
            return

        # 检查视频文件
        video_path = self.video_path_var.get().strip()
        if not video_path:
            messagebox.showerror("错误", "请选择视频文件")
            return

        if not os.path.exists(video_path):
            messagebox.showerror("错误", f"视频文件不存在: {video_path}")
            return

        # 检查输出目录
        output_dir = self.output_dir_var.get().strip()
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                messagebox.showerror("错误", f"无法创建输出目录: {e}")
                return

        # 准备命令行参数
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "whisper_subtitle_extractor.py")

        cmd = [sys.executable, script_path, video_path]

        # 添加模型参数
        cmd.extend(["--model", self.model_var.get()])

        # 添加语言参数
        cmd.extend(["--language", self.lang_var.get().strip() or "en"])

        # 添加输出格式
        formats = []
        if self.srt_var.get():
            formats.append("srt")
        if self.vtt_var.get():
            formats.append("vtt")
        if self.txt_var.get():
            formats.append("txt")

        if not formats:
            messagebox.showerror("错误", "请至少选择一种输出格式")
            return

        cmd.extend(["--formats", ",".join(formats)])

        # 添加保留音频选项
        if self.keep_audio_var.get():
            cmd.append("--keep-audio")

        # 添加字幕类型
        cmd.extend(["--subtitle-type", self.subtitle_type_var.get()])

        # 添加目标语言
        cmd.extend(["--dest-language", self.dest_lang_var.get().strip() or "zh-CN"])

        # 添加字幕烧录选项
        if self.burn_subtitles_var.get():
            cmd.append("--burn-subtitles")
            cmd.extend(["--font-size", str(self.font_size_var.get())])
            cmd.extend(["--subtitle-position", self.subtitle_position_var.get()])
            cmd.extend(["--font-color", self.font_color_var.get()])
            cmd.extend(["--outline-color", self.outline_color_var.get()])

        # 添加API密钥（如果有）
        if self.api_key_var.get().strip():
            cmd.extend(["--api-key", self.api_key_var.get().strip()])

        # 添加输出路径
        if output_dir:
            output_base = os.path.join(output_dir, os.path.splitext(os.path.basename(video_path))[0])
            cmd.extend(["--output", output_base])

        # 清空日志
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

        # 更新UI状态
        self.is_extracting = True
        self.start_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("正在处理...")

        # 记录命令
        self.log(f"执行命令: {' '.join(cmd)}")

        # 在新线程中执行
        self.extraction_thread = threading.Thread(target=self.run_extraction, args=(cmd,))
        self.extraction_thread.daemon = True
        self.extraction_thread.start()

    def run_extraction(self, cmd):
        """在单独的线程中运行提取过程"""
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # 读取输出
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log(line.strip())

            process.stdout.close()
            return_code = process.wait()

            if return_code == 0:
                self.log("字幕提取成功完成！")
                messagebox.showinfo("完成", "字幕提取已完成")
            else:
                self.log(f"字幕提取失败，返回代码: {return_code}")
                messagebox.showerror("错误", f"字幕提取失败，返回代码: {return_code}")

        except Exception as e:
            self.log(f"发生错误: {e}")
            messagebox.showerror("错误", f"发生错误: {e}")

        finally:
            # 恢复UI状态
            self.root.after(0, self.reset_ui)

    def reset_ui(self):
        """重置UI状态"""
        self.is_extracting = False
        self.start_button.config(state=tk.NORMAL)
        self.progress.stop()
        self.status_var.set("就绪")

    def toggle_api_key_visibility(self):
        """切换API密钥的可见性"""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")

    def update_translation_ui_state(self, *args):
        """根据字幕类型更新翻译相关UI的状态"""
        needs_translation = self.subtitle_type_var.get() in ["translated", "bilingual"]

        # 启用/禁用目标语言和API密钥输入
        state = "normal" if needs_translation else "disabled"
        self.dest_lang_entry.config(state=state)
        self.api_key_entry.config(state=state)
        self.show_key_cb.config(state=state)

def run_gui():
    """
    启动GUI应用程序
    """
    root = tk.Tk()
    app = WhisperGUI(root)
    root.mainloop()
    return app

def main():
    run_gui()

if __name__ == "__main__":
    main()
