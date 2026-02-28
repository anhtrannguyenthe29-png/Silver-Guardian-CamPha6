import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import winsound
import threading
from datetime import datetime

# =====================================================
# 1. DANH SÁCH TỪ KHÓA CHIẾN LƯỢC (Cập nhật cho năm 2026)
# =====================================================
KICH_BAN_XAU = {
    "TÀI CHÍNH": ["chuyển tiền", "mã otp", "số thẻ", "ngân hàng", "tài khoản", "nộp tiền", "thanh toán", "tiền", "otp", "nộp thuế", "tiền điện", "tiền nước"],
    "GIẢ DANH": ["công an", "viện kiểm sát", "bưu điện", "định danh", "vneid", "phạt nguội", "cán bộ"],
    "DỤ DỖ": ["trúng thưởng", "quà tặng", "miễn phí", "việc nhẹ", "lương cao", "shopee", "tiki", "mật khẩu"]
}

running = False 

# =====================================================
# 2. HÀM XỬ LÝ NHẬN DIỆN VÀ PHÂN TÍCH
# =====================================================

def am_thanh_canh_bao(nhom):
    """Phát âm thanh khác nhau cho từng loại nguy hiểm"""
    if nhom == "TÀI CHÍNH":
        # Tiếng Bíp dồn dập, cảnh báo cao độ
        for _ in range(3): winsound.Beep(2500, 300) 
    else:
        # Tiếng Bíp dài, cảnh báo chú ý
        winsound.Beep(1200, 1000)

def monitoring_loop():
    global running
    r = sr.Recognizer()
    
    # TINH CHỈNH ĐỂ SIÊU NHẠY
    r.energy_threshold = 100       # Rất nhạy, nghe được cả tiếng nói nhỏ
    r.dynamic_energy_threshold = True 
    r.phrase_threshold = 0.5
    r.pause_threshold = 1.2        # Kiên nhẫn đợi người già nói hết câu
    r.operation_timeout = 5        # Giới hạn thời gian kết nối server
    
    with sr.Microphone() as source:
        # Thay vì adjust 0.5s, ta tăng lên 1s để máy hiểu môi trường tốt hơn
        lbl_status.config(text="🛡️ Đang cân chỉnh Micro...", fg="#d35400")
        r.adjust_for_ambient_noise(source, duration=1) 
        
        while running:
            # ... phần còn lại của code
            lbl_status.config(text="🛡️ ĐANG GIÁM SÁT TRỰC TIẾP...", fg="#27ae60")
            try:
                # Nghe câu thoại ngắn (tối đa 10s một lần)
                audio = r.listen(source, timeout=None, phrase_time_limit=10)
                text = r.recognize_google(audio, language="vi-VN").lower()
                
                # Ghi nội dung lên màn hình
                txt_log.insert(tk.END, f"➤ {text}\n")
                txt_log.see(tk.END)
                
                # Thuật toán tìm kiếm từ khóa
                phat_hien_nhom = None
                for nhom, tu_khoa in KICH_BAN_XAU.items():
                    if any(tu in text for tu in tu_khoa):
                        phat_hien_nhom = nhom
                        break
                
                if phat_hien_nhom:
                    lbl_status.config(text=f"⚠️ CẢNH BÁO: {phat_hien_nhom}", fg="#c0392b")
                    txt_log.insert(tk.END, f"!!! PHÁT HIỆN DẤU HIỆU LỪA ĐẢO [{phat_hien_nhom}] !!!\n", 'warning')
                    am_thanh_canh_bao(phat_hien_nhom)
                    
            except sr.UnknownValueError:
                continue # Nếu không nghe rõ, tự động nghe tiếp câu sau
            except Exception as e:
                continue

def toggle_monitoring():
    global running
    if not running:
        running = True
        btn_start.config(text="DỪNG BẢO VỆ", bg="#c0392b")
        threading.Thread(target=monitoring_loop, daemon=True).start()
    else:
        running = False
        btn_start.config(text="BẮT ĐẦU GIÁM SÁT", bg="#27ae60")
        lbl_status.config(text="Trạng thái: Đã dừng", fg="#7f8c8d")

# =====================================================
# 3. GIAO DIỆN NGƯỜI DÙNG CHUYÊN NGHIỆP
# =====================================================

root = tk.Tk()
root.title("Silver Guardian v2026")
root.geometry("500x600")
root.configure(bg="#f4f7f6")

# Tiêu đề chính
tk.Label(root, text="🛡️ SILVER GUARDIAN", font=("Segoe UI", 26, "bold"), fg="#2c3e50", bg="#f4f7f6").pack(pady=20)

# Trạng thái hiển thị
lbl_status = tk.Label(root, text="Trạng thái: Sẵn sàng bảo vệ", font=("Segoe UI", 12), bg="#f4f7f6", fg="#7f8c8d")
lbl_status.pack(pady=5)

# Nút bấm trung tâm
btn_start = tk.Button(root, text="BẮT ĐẦU GIÁM SÁT", command=toggle_monitoring, 
                      bg="#27ae60", fg="white", font=("Segoe UI", 14, "bold"), 
                      width=20, height=2, bd=0, cursor="hand2")
btn_start.pack(pady=20)

# Khung nhật ký nội dung
tk.Label(root, text="Phân tích hội thoại thời gian thực:", font=("Segoe UI", 10, "bold"), bg="#f4f7f6", fg="#34495e").pack(anchor="w", padx=35)
txt_log = scrolledtext.ScrolledText(root, height=15, width=52, font=("Consolas", 11), bg="white", bd=2, relief="groove")