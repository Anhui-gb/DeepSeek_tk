import os
import sys
import json
import time
import threading
import urllib.request
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk, scrolledtext
import re

# ================= 配置 =================
CONFIG_FILE = "client_config.json"
OLLAMA_URL = "http://localhost:11434"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"mode": "", "api_key": "", "url": DEEPSEEK_API_URL, "model": "deepseek-chat"}

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

# ================= 暴躁下载器模块 =================
def download_cmd_with_progress(root):
    download_url = "https://release-assets.githubusercontent.com/github-production-release-asset/1429822521/97eb52ee-baa0-42d6-8eb5-ec00eca9df80?sp=r&sv=2018-11-09&sr=b&spr=https&se=2026-10-22T15%3A31%3A56Z&rscd=attachment%3B+filename%3DDeepSeek_cmd.exe&rsct=application%2Foctet-stream&skoid=96c2d410-5711-43a1-aedd-ab1947aa7ab0&sktid=398a6654-997b-47e9-b12b-9515b896b4de&skt=2026-10-22T14%3A30%3A57Z&ske=2026-10-22T15%3A31%3A56Z&sks=b&skv=2018-11-09&sig=WQpej1xw6S6azJqF7oZN3gqZXG%2FhrKNAMWFRDF%2FFtMo%3D&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmVsZWFzZS1hc3NldHMuZ2l0aHVidXNlcmNvbnRlbnQuY29tIiwia2V5Ijoia2V5MSIsImV4cCI6MTc5MjY3OTc1NywibmJmIjoxNzkyNjc5NDU3LCJwYXRoIjoicmVsZWFzZWFzc2V0cHJvZHVjdGlvbi5ibG9iLmNvcmUud2luZG93cy5uZXQifQ.McqkQqWBvWJvUMvKYKEl4V1ojU_7w4pyOdkotMXO2So&response-content-disposition=attachment%3B%20filename%3DDeepSeek_cmd.exe&response-content-type=application%2Foctet-stream"
    
    win = tk.Toplevel(root)
    win.title("下载 DeepSeek_cmd")
    win.geometry("400x180")
    win.configure(bg="#0a0e1a")
    win.resizable(False, False)
    win.update_idletasks()
    x = (win.winfo_screenwidth() - 400) // 2
    y = (win.winfo_screenheight() - 180) // 2
    win.geometry(f"400x180+{x}+{y}")
    win.protocol("WM_DELETE_WINDOW", lambda: None)

    tk.Label(win, text="正在从 GitHub 拉取极简版...", font=("微软雅黑", 11), bg="#0a0e1a", fg="white").pack(pady=10)
    progress = ttk.Progressbar(win, orient="horizontal", length=320, mode="determinate")
    progress.pack(pady=5)
    status_label = tk.Label(win, text="准备连接...", font=("微软雅黑", 9), bg="#0a0e1a", fg="#00ff00")
    status_label.pack(pady=5)

    def run_download():
        try:
            req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=10)
            total_size = int(response.getheader('Content-Length', 0))
            block_size = 8192 
            
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            save_path = os.path.join(desktop, "DeepSeek_cmd.exe")
            
            downloaded = 0
            start_time = time.time()
            
            with open(save_path, 'wb') as f:
                while True:
                    buffer = response.read(block_size)
                    if not buffer: break
                    f.write(buffer)
                    downloaded += len(buffer)
                    
                    if total_size > 0:
                        progress['value'] = (downloaded / total_size) * 100
                        elapsed_time = time.time() - start_time
                        if elapsed_time > 0:
                            speed = downloaded / elapsed_time / 1024 
                            if speed > 0:
                                remaining = (total_size - downloaded) / (speed * 1024)
                                if speed < 50 or remaining > 600:
                                    status_label.config(text=f"下载过慢！{progress['value']:.1f}% | 建议复制链接", fg="#ff5555")
                                else:
                                    status_label.config(text=f"下载中... {progress['value']:.1f}% | 剩余: {int(remaining)}秒 | {int(speed)} KB/s")
                    win.update()

            win.destroy()
            messagebox.showinfo("下载成功", "✅ DeepSeek_cmd.exe 已成功下载到您的桌面！\n\n双击即可开始使用。")
        except Exception as e:
            win.destroy()
            show_network_error(root, download_url, str(e))

    threading.Thread(target=run_download, daemon=True).start()

def show_network_error(root, url, error_msg):
    win = tk.Toplevel(root)
    win.title("下载失败")
    win.geometry("500x250")
    win.configure(bg="#0a0e1a")
    tk.Label(win, text="❌ 下载连接中断或极度缓慢", font=("微软雅黑", 12, "bold"), bg="#0a0e1a", fg="#ff5555").pack(pady=10)
    
    if "timeout" in error_msg.lower():
        msg = "连接超时，该网站拒绝访问。\n你需要开启加速器（如 Watt Toolkit）或者检查网络是否通畅。"
    else:
        msg = f"网络异常：{error_msg}"
        
    tk.Label(win, text=msg, font=("微软雅黑", 10), bg="#0a0e1a", fg="white", justify="center").pack(pady=5)
    
    link_entry = tk.Entry(win, font=("Consolas", 9), width=60, bg="#222", fg="#00ff00", insertbackground="white")
    link_entry.insert(0, url)
    link_entry.config(state="readonly")
    link_entry.pack(pady=5)
    
    def copy_link():
        win.clipboard_clear()
        win.clipboard_append(url)
        messagebox.showinfo("复制成功", "链接已复制到剪贴板。", parent=win)
        
    tk.Button(win, text="📋 复制链接", bg="#4CAF50", fg="white", font=("微软雅黑", 10, "bold"), command=copy_link).pack(pady=10)

# ================= 欢迎弹窗 =================
def show_welcome():
    cfg = load_config()
    win = tk.Tk()
    win.title("欢迎")
    win.geometry("440x240")
    win.configure(bg="#1e88e5")
    win.update_idletasks()
    win.geometry(f"440x240+{(win.winfo_screenwidth()-440)//2}+{(win.winfo_screenheight()-240)//2}")
    result = {"mode": ""}

    def choose_api():
        key = simpledialog.askstring("API Key", "请输入 Key：", parent=win, show="*")
        if key:
            cfg.update({"mode": "api", "api_key": key.strip()})
            save_config(cfg)
            result["mode"] = "api"
            win.destroy()

    def choose_custom():
        url = simpledialog.askstring("自定义 URL", "请输入 API URL (例如千问)：", parent=win)
        if not url: return
        key = simpledialog.askstring("API Key", "请输入 Key：", parent=win, show="*")
        if not key: return
        model = simpledialog.askstring("模型名", "请输入模型名称(如 qwen-turbo)：", parent=win)
        if not model: return
        
        cfg.update({"mode": "api", "url": url.strip(), "api_key": key.strip(), "model": model.strip()})
        save_config(cfg)
        result["mode"] = "api"
        win.destroy()

    def choose_local():
        cfg.update({"mode": "local", "model": "deepseek-r1:1.5b"})
        save_config(cfg)
        result["mode"] = "local"
        win.destroy()

    tk.Label(win, text="欢迎使用 DeepSeek 电脑端", font=("微软雅黑", 14, "bold"), bg="#1e88e5", fg="white").pack(pady=20)
    tk.Button(win, text="1. DeepSeek 官方 API", font=("微软雅黑", 10), bg="#4CAF50", fg="white", command=choose_api).pack(pady=5)
    tk.Button(win, text="2. 自定义 API (阿里千问等)", font=("微软雅黑", 10), bg="#FF9800", fg="white", command=choose_custom).pack(pady=5)
    tk.Button(win, text="3. 本地 Ollama 模式", font=("微软雅黑", 10), bg="#2196F3", fg="white", command=choose_local).pack(pady=5)

    win.mainloop()
    return result["mode"]

# ================= 主界面 =================
class ChatApp:
    def __init__(self, root, cfg):
        self.root = root
        self.cfg = cfg
        self.mode = cfg["mode"]
        self.api_key = cfg.get("api_key", "")
        self.url = cfg.get("url", DEEPSEEK_API_URL)
        self.model = cfg.get("model", "deepseek-chat")
        
        self.messages = []
        self.c = {"bg": "#0a0e1a", "chat_bg": "#0f1420", "user_bubble": "#005c4b", "ai_bubble": "#202c33", "text": "#e0e0e0", "input_bg": "#1a1f2e"}
        
        self.root.title("DeepSeek Tk 客户端")
        self.root.geometry("900x700")
        self.build_ui()

    def build_ui(self):
        self.root.configure(bg=self.c["bg"])
        
        # === 顶部栏 ===
        top = tk.Frame(self.root, bg=self.c["bg"])
        top.pack(fill="x", padx=15, pady=10)
        mode_text = f"🌐 {self.mode.upper()} 模式 | 模型: {self.model}"
        tk.Label(top, text=mode_text, font=("Microsoft YaHei", 11, "bold"), bg=self.c["bg"], fg="#00bcd4").pack(side="left")
        
        tk.Button(top, text="⚙ 设置", bg="#444", fg="white", relief="flat", command=self.open_settings).pack(side="right", padx=5)
        tk.Button(top, text="🗑 清空", bg="#e74c3c", fg="white", relief="flat", command=self.clear_chat).pack(side="right", padx=5)

        # === 聊天滚动区 ===
        self.canvas_frame = tk.Frame(self.root, bg=self.c["chat_bg"])
        self.canvas_frame.pack(fill="both", expand=True, padx=15, pady=5)
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.c["chat_bg"], highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.chat_frame = tk.Frame(self.canvas, bg=self.c["chat_bg"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.chat_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        # === 输入区 ===
        input_frame = tk.Frame(self.root, bg=self.c["bg"])
        input_frame.pack(fill="x", padx=15, pady=10)
        self.input_border = tk.Frame(input_frame, bg="#333", bd=1)
        self.input_border.pack(fill="x")
        self.input_box = tk.Text(self.input_border, height=3, font=("Microsoft YaHei", 11), bg=self.c["input_bg"], fg=self.c["text"], insertbackground=self.c["text"], relief="flat", padx=10, pady=8)
        self.input_box.pack(fill="x", padx=1, pady=1)
        self.input_box.bind("<Control-Return>", lambda e: self.send_message())

        btn_frame = tk.Frame(input_frame, bg=self.c["bg"])
        btn_frame.pack(fill="x", pady=(5, 0))
        tk.Button(btn_frame, text="发送 (Ctrl+Enter)", font=("Microsoft YaHei", 10, "bold"), bg="#1e88e5", fg="white", relief="flat", padx=20, command=self.send_message).pack(side="right")

    # ============ 气泡渲染 ============
    def add_bubble(self, role, text):
        is_user = (role == "user")
        row_frame = tk.Frame(self.chat_frame, bg=self.c["chat_bg"])
        row_frame.pack(fill="x", pady=8, padx=10)

        bg_color = self.c["user_bubble"] if is_user else self.c["ai_bubble"]
        fg_color = self.c["text"]

        bubble = tk.Frame(row_frame, bg=bg_color, padx=12, pady=10)

        # 解析代码块
        if "```" in text and not is_user:
            parts = re.split(r"(```.*?```)", text, flags=re.DOTALL)
            for part in parts:
                if not part.strip(): continue
                if part.startswith("```"):
                    code_content = part.strip("`").strip()
                    if "\n" in code_content: code_content = code_content.split("\n", 1)[1]
                    code_frame = tk.Frame(bubble, bg="#1e1e1e", bd=1, relief="solid")
                    code_frame.pack(fill="x", pady=5)
                    tool_bar = tk.Frame(code_frame, bg="#2d2d2d")
                    tool_bar.pack(fill="x")
                    tk.Button(tool_bar, text="📋 复制", font=("Microsoft YaHei", 8), bg="#2d2d2d", fg="#00bcd4", relief="flat", command=lambda c=code_content: self.copy_text(c)).pack(side="right", padx=5)
                    code_text = tk.Text(code_frame, height=min(15, code_content.count("\n")+1), font=("Consolas", 10), bg="#1e1e1e", fg="#d4d4d4", relief="flat")
                    code_text.insert("1.0", code_content)
                    code_text.config(state="disabled")
                    code_text.pack(fill="x")
                else:
                    tk.Label(bubble, text=part, font=("Microsoft YaHei", 11), bg=bg_color, fg=fg_color, wraplength=600, justify="left").pack(anchor="w", pady=2)
        else:
            tk.Label(bubble, text=text, font=("Microsoft YaHei", 11), bg=bg_color, fg=fg_color, wraplength=600, justify="left").pack(anchor="w")

        bubble.pack(side="right" if is_user else "left")
        self.root.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def copy_text(self, txt):
        self.root.clipboard_clear()
        self.root.clipboard_append(txt)
        messagebox.showinfo("成功", "已复制！")

    # ============ 发送与网络请求 ============
    def send_message(self):
        msg = self.input_box.get("1.0", tk.END).strip()
        if not msg: return
        self.input_box.delete("1.0", tk.END)
        
        self.add_bubble("user", msg)
        self.messages.append({"role": "user", "content": msg})
        self.input_box.config(state="disabled")
        
        threading.Thread(target=self.call_api, daemon=True).start()

    def call_api(self):
        try:
            data = {"model": self.model, "messages": self.messages, "stream": True}
            req = urllib.request.Request(self.url, data=json.dumps(data).encode("utf-8"), 
                                         headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})
            
            reply = ""
            with urllib.request.urlopen(req, timeout=120) as resp:
                for line in resp:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data: "):
                        d = line[6:]
                        if d == "[DONE]": break
                        try:
                            chunk = json.loads(d)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            if "content" in delta and delta["content"]: reply += delta["content"]
                        except: pass

            self.messages.append({"role": "assistant", "content": reply})
            self.root.after(0, lambda: self.add_bubble("assistant", reply))
        except Exception as e:
            self.root.after(0, lambda: self.add_bubble("system", f"请求失败：{e}"))
        finally:
            self.root.after(0, lambda: self.input_box.config(state="normal"))

    def clear_chat(self):
        self.messages = []
        for w in self.chat_frame.winfo_children(): w.destroy()

    # ============ 设置界面 ============
    def open_settings(self):
        set_win = tk.Toplevel(self.root)
        set_win.title("设置与关于")
        set_win.geometry("550x350")
        set_win.resizable(False, False)
        set_win.configure(bg="#2b2b2b")

        nav_frame = tk.Frame(set_win, bg="#000000", width=150)
        nav_frame.pack(side="left", fill="y")
        nav_frame.pack_propagate(False)
        content_frame = tk.Frame(set_win, bg="#2b2b2b")
        content_frame.pack(side="right", fill="both", expand=True)

        def show_settings():
            for widget in content_frame.winfo_children(): widget.destroy()
            tk.Label(content_frame, text="⚙️ 基本设置", font=("微软雅黑", 14, "bold"), bg="#2b2b2b", fg="white").pack(pady=15)
            
            # 暴躁下载器按钮
            tk.Button(content_frame, text="📥 下载 DeepSeek_cmd", font=("微软雅黑", 11, "bold"), 
                      bg="#00aa00", fg="white", padx=20, pady=8, 
                      command=lambda: download_cmd_with_progress(self.root)).pack(pady=10)

        def show_about():
            for widget in content_frame.winfo_children(): widget.destroy()
            tk.Label(content_frame, text="👨‍💻 关于作者", font=("微软雅黑", 14, "bold"), bg="#2b2b2b", fg="white").pack(pady=20)
            def open_github():
                import webbrowser
                webbrowser.open("https://github.com/Anhui-gb")
            tk.Button(content_frame, text="🌐 访问我的 GitHub 主页", font=("微软雅黑", 11), bg="#2196F3", fg="white", command=open_github).pack(pady=10)

        tk.Button(nav_frame, text="⚙️ 设置", font=("Consolas", 11, "bold"), bg="#000000", fg="#00ff00", relief="flat", anchor="w", command=show_settings).pack(fill="x", pady=5)
        tk.Button(nav_frame, text="👨‍💻 关于作者", font=("Consolas", 11, "bold"), bg="#000000", fg="#00ff00", relief="flat", anchor="w", command=show_about).pack(fill="x", pady=5)
        show_settings()

# ================= 启动 =================
if __name__ == "__main__":
    cfg = load_config()
    if not cfg.get("mode"):
        if not show_welcome(): sys.exit()
        cfg = load_config()

    root = tk.Tk()
    app = ChatApp(root, cfg)
    root.mainloop()