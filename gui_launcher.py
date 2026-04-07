#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from batch_generate_posters import BatchConfig, build_default_config, run_batch


class PosterGui:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("月度之星海报生成器")
        self.root.geometry("860x620")
        self.root.minsize(780, 560)

        self.default_config = build_default_config()
        self.default_config.input_dir.mkdir(parents=True, exist_ok=True)
        self.default_config.output_dir.mkdir(parents=True, exist_ok=True)

        self.input_var = tk.StringVar(value=str(self.default_config.input_dir))
        self.output_var = tk.StringVar(value=str(self.default_config.output_dir))
        self.template_var = tk.StringVar(value=str(self.default_config.template_path))
        self.font_var = tk.StringVar(value=str(self.default_config.font_path))
        self.status_var = tk.StringVar(value="把照片放进输入文件夹后，点击“开始生成”。")
        self.is_running = False

        self._build_ui()

    def _build_ui(self) -> None:
        self.root.configure(bg="#f4f6f8")

        wrapper = ttk.Frame(self.root, padding=18)
        wrapper.pack(fill="both", expand=True)
        wrapper.columnconfigure(0, weight=1)
        wrapper.rowconfigure(2, weight=1)

        title = ttk.Label(wrapper, text="月度之星海报生成器", font=("Microsoft YaHei UI", 18, "bold"))
        title.grid(row=0, column=0, sticky="w")

        subtitle = ttk.Label(
            wrapper,
            text="文件名格式：部门-姓名-YYYYMM，例如：制造部-张三-202603.jpg",
            font=("Microsoft YaHei UI", 10),
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(6, 14))

        form = ttk.LabelFrame(wrapper, text="目录与资源", padding=14)
        form.grid(row=2, column=0, sticky="nsew")
        form.columnconfigure(1, weight=1)

        self._add_path_row(form, 0, "输入图片", self.input_var, self.choose_input_dir)
        self._add_path_row(form, 1, "输出海报", self.output_var, self.choose_output_dir)
        self._add_path_row(form, 2, "模板图片", self.template_var, self.choose_template)
        self._add_path_row(form, 3, "字体文件", self.font_var, self.choose_font)

        actions = ttk.Frame(wrapper)
        actions.grid(row=3, column=0, sticky="ew", pady=(14, 10))
        actions.columnconfigure(4, weight=1)

        self.generate_button = ttk.Button(actions, text="开始生成", command=self.start_generate)
        self.generate_button.grid(row=0, column=0, padx=(0, 8))

        ttk.Button(actions, text="打开输入文件夹", command=self.open_input_dir).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(actions, text="打开输出文件夹", command=self.open_output_dir).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(actions, text="恢复默认目录", command=self.restore_defaults).grid(row=0, column=3, padx=(0, 8))

        self.progress = ttk.Progressbar(actions, mode="indeterminate")
        self.progress.grid(row=0, column=4, sticky="ew")

        log_frame = ttk.LabelFrame(wrapper, text="处理日志", padding=14)
        log_frame.grid(row=4, column=0, sticky="nsew")
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        wrapper.rowconfigure(4, weight=1)

        self.log = scrolledtext.ScrolledText(log_frame, wrap="word", font=("Consolas", 10), height=18)
        self.log.grid(row=0, column=0, sticky="nsew")
        self.log.insert("end", "程序已就绪。\n")
        self.log.configure(state="disabled")

        status = ttk.Label(wrapper, textvariable=self.status_var, anchor="w")
        status.grid(row=5, column=0, sticky="ew", pady=(10, 0))

    def _add_path_row(self, parent: ttk.LabelFrame, row: int, label: str, variable: tk.StringVar, command: callable) -> None:
        ttk.Label(parent, text=label, width=10).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=(0, 8), pady=6)
        ttk.Button(parent, text="浏览", command=command, width=8).grid(row=row, column=2, sticky="e", pady=6)

    def append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def set_running(self, running: bool) -> None:
        self.is_running = running
        state = "disabled" if running else "normal"
        self.generate_button.configure(state=state)
        if running:
            self.progress.start(10)
        else:
            self.progress.stop()

    def choose_input_dir(self) -> None:
        path = filedialog.askdirectory(initialdir=self.input_var.get() or str(Path.home()))
        if path:
            self.input_var.set(path)

    def choose_output_dir(self) -> None:
        path = filedialog.askdirectory(initialdir=self.output_var.get() or str(Path.home()))
        if path:
            self.output_var.set(path)

    def choose_template(self) -> None:
        path = filedialog.askopenfilename(
            initialdir=str(Path(self.template_var.get()).parent),
            filetypes=[("PNG 图片", "*.png"), ("所有文件", "*.*")],
        )
        if path:
            self.template_var.set(path)

    def choose_font(self) -> None:
        path = filedialog.askopenfilename(
            initialdir=str(Path(self.font_var.get()).parent),
            filetypes=[("字体文件", "*.ttf *.ttc *.otf"), ("所有文件", "*.*")],
        )
        if path:
            self.font_var.set(path)

    def open_input_dir(self) -> None:
        self._open_dir(Path(self.input_var.get()))

    def open_output_dir(self) -> None:
        self._open_dir(Path(self.output_var.get()))

    def _open_dir(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        os.startfile(path)  # type: ignore[attr-defined]

    def restore_defaults(self) -> None:
        self.input_var.set(str(self.default_config.input_dir))
        self.output_var.set(str(self.default_config.output_dir))
        self.template_var.set(str(self.default_config.template_path))
        self.font_var.set(str(self.default_config.font_path))
        self.append_log("已恢复默认目录配置。")
        self.status_var.set("默认目录已恢复。")

    def build_config(self) -> BatchConfig:
        return BatchConfig(
            input_dir=Path(self.input_var.get()).expanduser(),
            output_dir=Path(self.output_var.get()).expanduser(),
            template_path=Path(self.template_var.get()).expanduser(),
            font_path=Path(self.font_var.get()).expanduser(),
        )

    def start_generate(self) -> None:
        if self.is_running:
            return

        config = self.build_config()
        self.set_running(True)
        self.status_var.set("正在生成海报，请稍候…")
        self.append_log("开始处理…")

        worker = threading.Thread(target=self._run_generate, args=(config,), daemon=True)
        worker.start()

    def _run_generate(self, config: BatchConfig) -> None:
        try:
            result = run_batch(config, progress=lambda line: self.root.after(0, self.append_log, line))
            self.root.after(0, self._on_success, result.ok_count, result.fail_count, config.output_dir)
        except Exception as exc:  # noqa: BLE001
            self.root.after(0, self._on_error, str(exc))

    def _on_success(self, ok_count: int, fail_count: int, output_dir: Path) -> None:
        self.set_running(False)
        self.status_var.set(f"处理完成：成功 {ok_count}，失败 {fail_count}")
        if fail_count == 0:
            messagebox.showinfo("处理完成", f"海报已生成完成。\n成功 {ok_count} 张\n输出目录：{output_dir}")
        else:
            messagebox.showwarning("处理完成", f"处理结束。\n成功 {ok_count} 张，失败 {fail_count} 张\n请查看日志定位问题。")

    def _on_error(self, message: str) -> None:
        self.set_running(False)
        self.append_log(message)
        self.status_var.set("处理未完成，请查看提示信息。")
        messagebox.showerror("无法继续", message)


def main() -> None:
    root = tk.Tk()
    ttk.Style().theme_use("clam")
    PosterGui(root)
    root.mainloop()


if __name__ == "__main__":
    main()
