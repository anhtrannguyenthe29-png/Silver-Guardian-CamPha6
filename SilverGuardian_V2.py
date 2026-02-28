import tkinter as tk
from tkinter import scrolledtext
import speech_recognition as sr
import winsound
import threading
from datetime import datetime

# =====================================================
# 1. CẤU HÌNH DỮ LIỆU LỪA ĐẢO
# =====================================================
KICH_BAN_XAU = {
    "TÀI CHÍNH": ["chuyển tiền", "tài khoản", "mã otp", "nợ cước", "phạt nguội", "số thẻ", "ngân hàng", "nộp thuế", "tiền điện", "tiền nước"],
    "GIẢ DANH": ["công an", "viện kiểm sát", "bưu điện", "tòa án", "cán bộ", "định danh", "vneid"],
    "DỤ DỖ": ["trúng thưởng", "quà tặng", "miễn phí", "việc nhẹ lương cao", "nhận quà"]
}

running = False 

# =====================================================
# 2. CÁC HÀM XỬ LÝ CHÍNH
# =====================================================

def ghi_nhat_ky(text, trang_thai):
    """Lưu lại nội dung cuộc gọi vào file txt để đối chiếu sau này"""
    with open("nhat_ky_bao_ve.txt", "a", encoding="utf-8") as f:
        thoigian = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        f.write(f"[{thoigian}] [{trang_thai}] Nội dung: {text}\n")

def phat_am_thanh_canh_bao(level):
    """Phát tiếng bíp tùy theo mức độ nguy hiểm"""
    if level == "TÀI CHÍNH":
        for _ in range(3): winsound.Beep(2000, 400) # Tiếng cao, dồn dập
    else:
        winsound.Beep(1000, 1000) # Tiếng dài, cảnh báo

def monitoring_loop():
    global running
    r = sr.Recognizer()
    
    # Cấu hình "tai nghe" tối ưu cho AI
    r.energy_threshold = 300       # Ngưỡng âm thanh tối thiểu
    r.dynamic_energy_threshold = False # Cố định ngưỡng để không phải đợi lâu
    r.pause_threshold = 1.0        # Đợi 1 giây sau khi nói mới dịch
    
    with sr.Microphone() as source:
        # Lọc nhiễu siêu nhanh (chỉ 0.5 giây) để không gây bất tiện
        lbl_status.config(text="🛡️ Đang khởi tạo lá chắn...", fg="#f39c12")
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        while running:
            lbl_status.config(text="🛡️ HỆ THỐNG ĐANG GIÁM SÁT...", fg="#27ae60")
            try:
                # Nghe câu nói trong tối đa 10 giây
                audio = r.listen(source, timeout=None, phrase_time_limit=10)
                text = r.recognize_google(audio, language="vi-VN").lower()
                
                # Hiển thị nội dung lên màn hình
                txt_log.insert(tk.END, f"➤ {text}\n")
                txt_log.see(tk.END)
                
                # Phân tích kịch bản lừa đảo
                phat_hien = False
                for nhom, tu_khoa in KICH_BAN_XAU.items():
                    for tu in tu_khoa:
                        if tu in text:
                            lbl_status.config(text=f"⚠️ CẢNH BÁO: {nhom}", fg="#e74c3c")
                            txt_log.insert(tk.END, f"!!! PHÁT HIỆN LỪA ĐẢO: {tu.upper()} !!!\n", 'warning')
                            phat_am_thanh_canh_bao(nhom)
                            ghi_nhat_ky(text, f"CẢNH BÁO: {nhom}")
                            phat_hien = True
                            break
                
                if not phat_hien:
                    ghi_nhat_ky(text, "AN TOÀN")

            except sr.UnknownValueError:
                continue # Không nghe rõ thì nghe tiếp
            except Exception as e:
                print(f"Lỗi: {e}")
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
# 3. GIAO DIỆN NGƯỜI DÙNG (UI)
# =====================================================

root.title("Silver Guardian - Bảo vệ người cao tuổi")
root.geometry("500x600")
root.configure(bg="#ecf0f1")

# Tiêu đề
tk.Label(root, text="🛡️ SILVER GUARDIAN", font=("Helvetica", 24, "bold"), fg="#2c3e50", bg="#ecf0f1").pack(pady=20)

# Trạng thái
lbl_status = tk.Label(root, text="Trạng thái: Sẵn sàng", font=("Helvetica", 14, "italic"), bg="#ecf0f1", fg="#7f8c8d")
lbl_status.pack(pady=5)

# Nút bấm chính
btn_start = tk.Button(root, text="BẮT ĐẦU GIÁM SÁT", command=toggle_monitoring, 
                      bg="#27ae60", fg="white", font=("Helvetica", 16, "bold"), 
                      width=20, height=2, relief="flat")
btn_start.pack(pady=20)

# Khung hiển thị nội dung (Nhật ký thời gian thực)
tk.Label(root, text="Nội dung cuộc gọi đang phân tích:", font=("Helvetica", 10), bg="#ecf0f1").pack(anchor="w", padx=40)
txt_log = scrolledtext.ScrolledText(root, height=15, width=55, font=("Segoe UI", 11), bg="white")
txt_log.tag_config('warning', background="#f1c40f", foreground="#c0392b", font=("Segoe UI", 12, "bold"))
txt_log.pack(pady=10, padx=20)

# Bản quyền/Thông tin thêm
tk.Label(root, text="Hệ thống bảo vệ người già khỏi lừa đảo qua điện thoại", font=("Helvetica", 9), bg="#ecf0f1", fg="#95a5a6").pack(side="bottom", pady=10)

root.mainloop()