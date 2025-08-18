#!/usr/bin/env python3
"""
ゲームクラブ自動出品ツール - GUI版
使用方法: python run_tool.py
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import signal
import sys
from datetime import datetime
from auto_listing_tool import GameClubListingTool

class GameClubToolGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ゲームクラブ自動出品ツール")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # ツールインスタンス
        self.tool = None
        self.is_running = False
        
        # GUI要素の作成
        self.create_widgets()
        
        # シグナルハンドラー設定
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def create_widgets(self):
        """GUI要素を作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = ttk.Label(main_frame, text="🎮 GameClub自動出品ツール", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 説明
        info_text = """
📋 使用方法:
1. 「開始」ボタンをクリック
2.  ログイン確認ウィンドウが表示されます
3.  手動でログインとロボット認証を完了
4.  自動的にスプレッドシートのデータを処理
5. 「停止」ボタンで処理を停止
        """
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.grid(row=1, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        # 開始ボタン
        self.start_button = ttk.Button(button_frame, text="🚀 開始", 
                                      command=self.start_processing, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 停止ボタン
        self.stop_button = ttk.Button(button_frame, text="⏹️ 停止", 
                                     command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT)
        
        # ログ表示エリア
        log_frame = ttk.LabelFrame(main_frame, text="📝 実行ログ", padding="5")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # スクロール可能なテキストエリア
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80, 
                                                 font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # ステータスバー
        self.status_var = tk.StringVar(value="待機中...")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # グリッドの重み設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
    def log_message(self, message):
        """ログメッセージを表示"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # GUIスレッドでログを更新
        self.root.after(0, self._update_log, log_entry)
        
    def _update_log(self, message):
        """ログテキストを更新（GUIスレッド用）"""
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        
    def start_processing(self):
        """処理を開始"""
        if self.is_running:
            return
            
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("処理中...")
        
        # 別スレッドで処理を実行
        self.processing_thread = threading.Thread(target=self._run_processing)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
    def _run_processing(self):
        """バックグラウンドで処理を実行"""
        try:
            self.log_message("🎮 ゲームクラブ自動出品ツールを開始します")
            self.log_message("=" * 50)
            
            # ツールインスタンスを作成
            self.tool = GameClubListingTool()
            
            # ログ出力をリダイレクト
            self._redirect_print()
            
            # 処理を開始
            self.tool.start_continuous_processing()
            
        except Exception as e:
            self.log_message(f"❌ エラーが発生しました: {e}")
            self.root.after(0, self._handle_error, str(e))
            
    def _redirect_print(self):
        """print文をログにリダイレクト"""
        import builtins
        original_print = builtins.print
        
        def custom_print(*args, **kwargs):
            message = " ".join(str(arg) for arg in args)
            self.log_message(message)
            original_print(*args, **kwargs)
            
        builtins.print = custom_print
        
    def stop_processing(self):
        """処理を停止"""
        if not self.is_running:
            return
            
        self.is_running = False
        self.status_var.set("停止中...")
        
        if self.tool:
            self.tool.stop_processing()
            
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("停止済み")
        self.log_message("⚠️ 処理が停止されました")
        
    def _handle_error(self, error_message):
        """エラーハンドリング"""
        messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{error_message}")
        self.stop_processing()
        
    def signal_handler(self, sig, frame):
        """シグナルハンドラー"""
        self.log_message("⚠️ プログラムが中断されました")
        self.stop_processing()
        self.root.quit()
        
    def run(self):
        """GUIを実行"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.signal_handler(None, None)

def main():
    """メイン関数"""
    app = GameClubToolGUI()
    app.run()

if __name__ == "__main__":
    main()