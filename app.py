# 이미지 크롤러 애플리케이션 - 메인 클래스 / last update : 20250521
from tkinter import *
from tkinter import filedialog
from ui.frames import SearchFrame, QuantityFrame, ButtonFrame, LogFrame

class ImageCrawlerApp:
    # 이미지 크롤러 애플리케이션의 메인 클래스
    
    def __init__(self, root):
        """
        애플리케이션 초기화
        Args:
            root: tkinter의 루트 윈도우
        """
        self.root = root
        self.root.title("이미지 크롤러 0.1v") 
        self.root.geometry("1000x800") 
        
        # UI 구성요소 생성
        self.create_frames()
        
        self.log_frame.add_log("프로그램이 시작되었습니다.")

    def create_frames(self):
        # UI의 각 프레임들을 생성하고 배치
        # 검색 프레임 생성 (검색창과 검색 버튼)
        self.search_frame = SearchFrame(self.root)
        
        # 매수 입력 프레임 생성 (매수 입력과 저장 위치 선택)
        self.quantity_frame = QuantityFrame(
            self.root,
            self.on_validate,  # 입력값 검증 함수
            self.on_key_press,  # 키 입력 처리 함수
            self.validate_spinbox,  # Spinbox 값 검증 함수
            self.select_save_location  # 저장 위치 선택 함수
        )
        
        # 로그 표시 프레임 생성
        self.log_frame = LogFrame(self.root)
        
        # 검색 버튼 프레임 생성 (구글/Bing 검색 버튼)
        self.button_frame = ButtonFrame(
            self.root, 
            self.log_frame,
            self.search_frame,  # 검색 프레임 전달
            self.quantity_frame  # 매수 프레임 전달
        )

    def on_validate(self, P):
        """
        Spinbox 입력값 검증
        Args:
            P: 입력하려는 값
        Returns:
            bool: 입력값이 유효하면 True, 아니면 False
        """
        if P == "":  # 빈 문자열은 허용 (삭제할 때)
            return True
        try:
            int(P)  # 숫자로 변환 가능한지 확인
            return True
        except ValueError:
            return False

    def on_key_press(self, event):
        """
        키 입력 처리
        Args:
            event: 키보드 이벤트
        Returns:
            str: "break"를 반환하여 기본 입력 동작 방지
        """
        widget = event.widget
        char = event.char

        if event.keysym in ('BackSpace', 'Delete'):
            return

        # 숫자가 아닌 입력은 무시
        if not char.isdigit():
            return "break"

        current = widget.get()

        # 현재 값이 "0"이면 새 숫자로 대체
        if current == "0":
            widget.delete(0, END)
            widget.insert(END, char)
        else:
            # 그 외의 경우 기존 값에 추가
            widget.insert(END, char)

        return "break"

    def validate_spinbox(self):
        # pinbox의 값이 유효한지 검증하고 필요시 초기화
        try:
            value = int(self.quantity_frame.spinbox.get())
            if value < 0:  # 음수는 0으로 초기화
                self.quantity_frame.spinbox.delete(0, END)
                self.quantity_frame.spinbox.insert(0, "0")
        except ValueError:  # 숫자가 아닌 값은 0으로 초기화
            self.quantity_frame.spinbox.delete(0, END)
            self.quantity_frame.spinbox.insert(0, "0")

    def select_save_location(self):
        # 저장 위치 선택 다이얼로그를 표시하고 선택된 경로를 저장
        folder_path = filedialog.askdirectory()
        if folder_path:
            # Entry 위젯을 수정 가능하게 변경
            self.quantity_frame.save_path_entry.config(state='normal')
            self.quantity_frame.save_path_entry.delete(0, END)
            self.quantity_frame.save_path_entry.insert(0, folder_path)
            self.quantity_frame.save_path_entry.config(state='readonly')
            self.log_frame.add_log(f"저장 위치가 선택되었습니다: {folder_path}") 