import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
import os

# Import các hàm trích xuất và nhận diện bạn đã tự code
from trich_xuat_ket_cau_da import manual_lbp
from trich_xuat_hinh_dang import manual_hog_simplified
from nhan_dien import load_database, cosine_similarity

class FaceRankingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng Dụng Nhận Diện Trẻ Em - cd_app (Phiên bản Trực quan)")
        self.root.geometry("900x650")
        
        # --- NẠP CƠ SỞ DỮ LIỆU ---
        self.db_path = "bo_dac_trung.csv"
        self.image_folder = "child" # Thư mục chứa ảnh gốc để hiển thị kết quả
        
        if os.path.exists(self.db_path):
            self.database = load_database(self.db_path)
            db_status = f"Trạng thái: Đã nạp {len(self.database)} khuôn mặt."
            status_color = "green"
        else:
            self.database = []
            db_status = "Cảnh báo: Không tìm thấy file bo_dac_trung.csv!"
            status_color = "red"
            
        # Danh sách giữ tham chiếu ảnh (tránh bị Python xóa bộ nhớ)
        self.result_images = []

        # --- BỐ CỤC GIAO DIỆN (UI) ---
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. Khung bên trái (Khu vực tải ảnh)
        left_frame = tk.Frame(main_frame, width=320, relief=tk.RIDGE, borderwidth=2)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left_frame.pack_propagate(False) # Giữ cố định chiều rộng khung trái
        
        tk.Label(left_frame, text="ẢNH TRUY VẤN", font=("Arial", 13, "bold")).pack(pady=15)
        tk.Label(left_frame, text=db_status, fg=status_color, font=("Arial", 9, "italic")).pack(pady=5)

        # Khung cố định cho ảnh tải lên (để ảnh không bị méo)
        img_container = tk.Frame(left_frame, width=250, height=250, bg="#e0e0e0", relief=tk.SUNKEN, borderwidth=1)
        img_container.pack(pady=20)
        img_container.pack_propagate(False) # Ép khung phải đúng 250x250
        
        self.img_label = tk.Label(img_container, text="Chưa có ảnh nào", bg="#e0e0e0")
        self.img_label.pack(expand=True, fill=tk.BOTH)
        
        # Nút bấm tìm kiếm
        tk.Button(left_frame, text="Chọn Ảnh & Xếp Hạng", command=self.search, 
                  bg="#007bff", fg="white", font=("Arial", 12, "bold"), 
                  padx=15, pady=8, cursor="hand2").pack(pady=10)

        # 2. Khung bên phải (Khu vực danh sách kết quả chứa ảnh)
        right_frame = tk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(right_frame, text="DANH SÁCH TOP 10 ẢNH GIỐNG NHẤT", font=("Arial", 13, "bold")).pack(pady=15)
        
        # Tạo Canvas và Scrollbar để có thể cuộn danh sách ảnh
        self.canvas = tk.Canvas(right_frame, borderwidth=0)
        self.scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.scrollbar.pack(side="right", fill="y", pady=5)
        
        # Hỗ trợ cuộn chuột
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # --- LOGIC XỬ LÝ ---
    def search(self):
        if not self.database:
            messagebox.showerror("Lỗi CSDL", "Không có dữ liệu. Vui lòng chạy file tổng hợp đặc trưng trước!")
            return

        file_path = filedialog.askopenfilename(title="Chọn một bức ảnh", filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if not file_path: return 
        
        # 1. Hiển thị ảnh truy vấn nguyên vẹn
        try:
            img_display = Image.open(file_path)
            img_display.thumbnail((250, 250)) # Tự động thu nhỏ theo tỷ lệ, không làm méo ảnh
            img_tk = ImageTk.PhotoImage(img_display)
            self.img_label.config(image=img_tk, text="")
            self.img_label.image = img_tk 
        except Exception as e:
            messagebox.showerror("Lỗi đọc ảnh", f"Không thể hiển thị ảnh: {e}")
            return
        
        # 2. Trích xuất đặc trưng
        try:
            img = Image.open(file_path).convert('L').resize((150, 150))
            img_matrix = np.array(img)
            query_vector = manual_lbp(img_matrix) + manual_hog_simplified(img_matrix)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi khi tính toán đặc trưng: {e}")
            return
        
        # 3. So sánh và Xếp hạng
        ranked_list = []
        for entry in self.database:
            score = cosine_similarity(query_vector, entry['vector'])
            ranked_list.append((entry['filename'], score))
        ranked_list.sort(key=lambda x: x[1], reverse=True)
        
        # 4. Hiển thị danh sách kết quả kèm ảnh thực tế
        # Xóa các dòng kết quả cũ trên giao diện
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.result_images.clear() # Xóa tham chiếu ảnh cũ

        # Lấy Top 10 người giống nhất
        for idx, (name, score) in enumerate(ranked_list[:10]):
            # Tạo một khung con (row) cho mỗi kết quả
            row_frame = tk.Frame(self.scrollable_frame, pady=5, padx=5, relief=tk.SOLID, borderwidth=1)
            row_frame.pack(fill=tk.X, expand=True, padx=5, pady=3)
            
            # STT
            tk.Label(row_frame, text=f"#{idx+1}", font=("Arial", 14, "bold"), width=3).pack(side=tk.LEFT, padx=10)
            
            # Tải ảnh kết quả từ thư mục child
            img_path = os.path.join(self.image_folder, name)
            try:
                res_img = Image.open(img_path)
                res_img.thumbnail((80, 80)) # Resize nhỏ lại thành avatar 80x80
                res_img_tk = ImageTk.PhotoImage(res_img)
                self.result_images.append(res_img_tk) # Giữ tham chiếu
                
                lbl_res_img = tk.Label(row_frame, image=res_img_tk, bg="black")
                lbl_res_img.pack(side=tk.LEFT, padx=10)
            except Exception:
                # Nếu ảnh trong CSDL bị xóa mất, hiển thị chữ báo lỗi
                tk.Label(row_frame, text="[Mất ảnh]", width=10, bg="gray").pack(side=tk.LEFT, padx=10)

            # Thông tin Text (Tên + Độ tương đồng)
            info_text = f"Tên File: {name}\nĐộ tương đồng: {score*100:.2f} %"
            
            # Bôi màu xanh nếu độ tương đồng cao (trên 85%)
            text_color = "green" if score >= 0.85 else "black"
            font_style = ("Arial", 11, "bold") if score >= 0.85 else ("Arial", 11)
            
            tk.Label(row_frame, text=info_text, font=font_style, fg=text_color, justify=tk.LEFT).pack(side=tk.LEFT, padx=15)

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam') 
    app = FaceRankingApp(root)
    root.mainloop()