# 이미지 크롤러 프레임 - 프레임 설정 / last update : 20250521
from tkinter import *
from tkinter import scrolledtext, filedialog
from google.image_download import image_download
import logging
import threading
import queue
import os

class SearchFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='x', padx=50, pady=(50,0))

        
        self.label = Label(self, text="이미지 크롤러")
        self.label.pack(side='top', padx=(0, 5))
        
        # 검색창
        self.entry = Entry(self)
        self.entry.pack(side='left', fill='x', expand=True)
        
        # # 검색 버튼
        # self.search_button = Button(self, text="검색", width=10)
        # self.search_button.pack(side='right', padx=(10,0))

    def get_search_term(self):
        """검색어를 반환하는 메서드"""
        return self.entry.get() or "헤어모델"  # 검색어가 없으면 기본값 "헤어모델" 반환

class QuantityFrame(Frame):
    def __init__(self, parent, on_validate, on_key_press, validate_spinbox, select_save_location):
        super().__init__(parent)
        self.pack(fill='x', pady=(10), padx=(300,50))
        
        # 왼쪽: 매수 입력
        self.left_frame = Frame(self)
        self.left_frame.pack(side='left')
        
        self.label = Label(self.left_frame, text="매수")
        self.label.pack(side='left', padx=(0, 5))
        
        # Spinbox 설정 변경
        self.spinbox = Spinbox(self.left_frame, from_=1, to=999999, increment=1, width=10)
        self.spinbox.delete(0, END)
        self.spinbox.insert(0, "5")  # 기본값을 5로 설정
        self.spinbox.pack(side='left')
        
        # 키 이벤트 바인딩
        self.spinbox.bind('<KeyPress>', self.on_key_press)
        self.spinbox.bind('<KeyRelease>', lambda e: validate_spinbox())
        
        # 오른쪽: 저장 경로 선택
        self.right_frame = Frame(self)
        self.right_frame.pack(side='right')
        
        self.path_label = Label(self.right_frame, text="저장 경로:")
        self.path_label.pack(side='left', padx=(0, 5))
        
        self.path_entry = Entry(self.right_frame, width=30, state='readonly')
        self.path_entry.pack(side='left', padx=(0, 5))
        self.path_entry.config(state='normal')
        self.path_entry.insert(0, os.path.join(os.getcwd(), "다운로드된_이미지"))
        self.path_entry.config(state='readonly')
        
        self.path_button = Button(self.right_frame, text="찾아보기", command=self.select_save_location)
        self.path_button.pack(side='left')

    def on_key_press(self, event):
        """키 입력 처리"""
        if event.char.isdigit():
            current = self.spinbox.get()
            if current == "0":
                self.spinbox.delete(0, END)
                self.spinbox.insert(0, event.char)
            return None
        elif event.keysym in ('BackSpace', 'Delete'):
            return None
        return "break"

    def select_save_location(self):
        """저장 경로를 선택하는 메서드"""
        directory = filedialog.askdirectory()
        if directory:
            self.path_entry.config(state='normal')
            self.path_entry.delete(0, END)
            self.path_entry.insert(0, directory)
            self.path_entry.config(state='readonly')

    def get_save_location(self):
        """저장 경로를 반환하는 메서드"""
        path = self.path_entry.get()
        if not path:
            path = os.path.join(os.getcwd(), "다운로드된_이미지")
        return path

    def get_quantity(self):
        """매수 값을 반환하는 메서드"""
        try:
            value = int(self.spinbox.get())
            return max(1, min(value, 999999))  # 1에서 999999 사이의 값으로 제한
        except ValueError:
            return 5  # 기본값 5 반환

class ButtonFrame(Frame):
    def __init__(self, parent, log_frame, search_frame, quantity_frame):
        super().__init__(parent)
        self.pack(fill='x', pady=20, before=log_frame)
        self.log_frame = log_frame
        self.current_thread = None
        self.is_cancelled = False
        
        # 중앙 정렬을 위한 프레임
        self.center_frame = Frame(self)
        self.center_frame.pack(expand=True)
        
        # 구글 검색 버튼
        self.google_button = Button(
            self.center_frame, 
            text="구글 검색", 
            width=15, 
            height=2, 
            font=('Arial', 10, 'bold'),
            command=lambda: self.perform_google_search(search_frame, quantity_frame)
        )
        self.google_button.pack(side='left', padx=10)
        
        # 취소 검색 버튼
        self.bing_button = Button(
            self.center_frame, 
            text="취소", 
            width=15, 
            height=2, 
            font=('Arial', 10, 'bold'),
            command=self.cancel_search
        )
        self.bing_button.pack(side='left', padx=(10))

    def perform_google_search(self, search_frame, quantity_frame):
        """구글 검색을 수행하는 메서드"""
        search_term = search_frame.get_search_term()
        quantity = quantity_frame.get_quantity()
        save_location = quantity_frame.get_save_location()
        url = f"https://www.google.com/search?q={search_term}&tbm=isch&tbs=isz:l"
        
        # 취소 상태 초기화
        self.is_cancelled = False
        
        # 버튼 상태 변경
        self.google_button.config(state='disabled')
        self.bing_button.config(state='normal')
        
        # 별도 스레드에서 검색 실행
        def search_thread():
            try:
                image_download(url, "YQ4gaf", quantity, save_location, self)
            finally:
                # 메인 스레드에서 버튼 다시 활성화
                self.after(0, lambda: self.google_button.config(state='normal'))
                self.after(0, lambda: self.bing_button.config(state='disabled'))
                self.current_thread = None
        
        self.current_thread = threading.Thread(target=search_thread)
        self.current_thread.daemon = True
        self.current_thread.start()

    def cancel_search(self):
        """검색을 취소하는 메서드"""
        if self.current_thread and self.current_thread.is_alive():
            self.is_cancelled = True
            logging.info("검색이 취소되었습니다.")
            self.google_button.config(state='normal')
            self.bing_button.config(state='disabled')

class LogFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill='both', expand=True, padx=50, pady=(10,50))
        
        self.log_label = Label(self, text="로그")
        self.log_label.pack(anchor='w')
        
        self.log_text = scrolledtext.ScrolledText(self, height=10, width=100)
        self.log_text.pack(fill='both', expand=True)
        self.log_text.config(state='disabled')

        self.label = Label(self, text="이 이미지 크롤러는 자기학습용으로 개발하였습니다.")
        self.label.pack(side='bottom', padx=(0, 5), pady=(30,0))
        
        # 로그 메시지를 저장할 큐
        self.log_queue = queue.Queue()
        
        # 로깅 핸들러 설정
        self.setup_logging()
        
        # 주기적으로 로그 메시지 처리
        self.process_log_queue()
    
    def setup_logging(self):
        """로깅 핸들러를 설정하는 메서드"""
        class QueueHandler(logging.Handler):
            def __init__(self, log_queue):
                logging.Handler.__init__(self)
                self.log_queue = log_queue

            def emit(self, record):
                msg = self.format(record)
                self.log_queue.put(msg)

        # 로거 설정
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # 기존 핸들러 제거
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # 큐 핸들러 추가
        queue_handler = QueueHandler(self.log_queue)
        queue_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(queue_handler)
    
    def process_log_queue(self):
        """로그 큐의 메시지를 처리하는 메서드"""
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.config(state='normal')
                self.log_text.insert(END, msg + '\n')
                self.log_text.see(END)
                self.log_text.config(state='disabled')
        except queue.Empty:
            pass
        
        # 100ms 후에 다시 체크
        self.after(100, self.process_log_queue)
    
    def add_log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(END, f"{message}\n")
        self.log_text.see(END)
        self.log_text.config(state='disabled') 