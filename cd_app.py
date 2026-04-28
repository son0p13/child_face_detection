import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np
import os
import sqlite3
import ast

# Import các hàm trích xuất tự code
from trich_xuat_ket_cau_da import manual_lbp
from trich_xuat_hinh_dang import manual_hog_simplified
from nhan_dien import cosine_similarity

class FaceRankingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống CSDLDPT Nhận Diện Trẻ Em")
        self.root.geometry("950x650")
        
        # --- CẤU HÌNH THƯ MỤC & DATABASE ---
        self.db_path = "csdldpt.db" # Đã chuyển sang dùng SQLite Database
        self.image_folder = "child" # Thư mục chứa ảnh gốc để hiển thị avatar
        
        self.database = self.load_database_from_sqlite()
        
        if self.database:
            db_status = f"Trạng thái: Đã kết nối thành công. Nạp {len(self.database)} khuôn mặt."
            status_color = "green"
        else:
            db_status = "Cảnh báo: Chưa có CSDL. Hãy chạy file 'tong_hop_dac_trung.py' trước!"
            status_color = "red"
            
        # Danh sách giữ tham chiếu ảnh để tránh bị Python thu hồi bộ nhớ
        self.result_images = []

        # --- BỐ CỤC GIAO DIỆN (UI) ---
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 1. KHUNG TRÁI: Khu vực tải ảnh và thao tác
        left_frame = tk.Frame(main_frame, width=320, relief=tk.RIDGE, borderwidth=2)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left_frame.pack_propagate(False) 
        
        tk.Label(left_frame, text="ẢNH TRUY VẤN", font=("Arial", 14, "bold"), fg="#333333").pack(pady=15)
        tk.Label(left_frame, text=db_status, fg=status_color, font=("Arial", 9, "italic")).pack(pady=5)

        # Khung chứa ảnh tải lên (Kích thước cố định 250x250)
        img_container = tk.Frame(left_frame, width=250, height=250, bg="#e0e0e0", relief=tk.SUNKEN, borderwidth=1)
        img_container.pack(pady=20)
        img_container.pack_propagate(False)
        
        self.img_label = tk.Label(img_container, text="Chưa có ảnh nào", bg="#e0e0e0")
        self.img_label.pack(expand=True, fill=tk.BOTH)
        
        # Nút bấm chính
        tk.Button(left_frame, text="Chọn Ảnh & Xếp Hạng", command=self.search, 
                  bg="#0056b3", fg="white", font=("Arial", 12, "bold"), 
                  padx=20, pady=10, cursor="hand2").pack(pady=15)

        # 2. KHUNG PHẢI: Khu vực danh sách kết quả trực quan
        right_frame = tk.Frame(main_frame, relief=tk.RIDGE, borderwidth=2)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(right_frame, text="TOP 10 KHUÔN MẶT GIỐNG NHẤT", font=("Arial", 14, "bold"), fg="#333333").pack(pady=15)
        
        # Bố cục Scrollable Canvas cho danh sách ảnh
        self.canvas = tk.Canvas(right_frame, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.pack(side="right", fill="y", pady=10)
        
        # Hỗ trợ lăn chuột
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    # --- HÀM KẾT NỐI DATABASE SQLITE ---
    def load_database_from_sqlite(self):
        database = []
        if not os.path.exists(self.db_path):
            return database
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT filename, master_vector FROM SieuDuLieu")
            rows = cursor.fetchall()
            
            for row in rows:
                filename = row[0]
                vector_str = row[1]
                master_vector = ast.literal_eval(vector_str)
                database.append({
                    "filename": filename,
                    "vector": master_vector
                })
            conn.close()
        except Exception as e:
            print(f"Lỗi đọc DB: {e}")
            
        return database

    # --- LOGIC XỬ LÝ CHÍNH ---
    def search(self):
        if not self.database:
            messagebox.showerror("Lỗi CSDL", "Không có kết nối tới cơ sở dữ liệu. Hãy tạo file csdldpt.db trước!")
            return

        file_path = filedialog.askopenfilename(title="Chọn Ảnh Truy Vấn", filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if not file_path: return 
        
        # 1. Cập nhật ảnh lên giao diện (Tránh méo ảnh)
        try:
            img_display = Image.open(file_path)
            img_display.thumbnail((250, 250))
            img_tk = ImageTk.PhotoImage(img_display)
            self.img_label.config(image=img_tk, text="")
            self.img_label.image = img_tk 
        except Exception as e:
            messagebox.showerror("Lỗi Ảnh", f"Không thể hiển thị ảnh: {e}")
            return
        
        # 2. Rút trích Vector "Siêu Dữ Liệu" (Feature Extraction)
        try:
            img_gray = Image.open(file_path).convert('L').resize((150, 150))
            img_matrix = np.array(img_gray)
            query_vector = manual_lbp(img_matrix) + manual_hog_simplified(img_matrix)
        except Exception as e:
            messagebox.showerror("Lỗi Tính Toán", f"Lỗi trích xuất: {e}")
            return
        
        # 3. Quét DB và Tính Cosine Similarity
        ranked_list = []
        for entry in self.database:
            score = cosine_similarity(query_vector, entry['vector'])
            ranked_list.append((entry['filename'], score))
            
        # Sắp xếp từ cao xuống thấp
        ranked_list.sort(key=lambda x: x[1], reverse=True)
        
        # 4. Hiển thị kết quả trực quan
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.result_images.clear() 

        for idx, (name, score) in enumerate(ranked_list[:10]):
            row_frame = tk.Frame(self.scrollable_frame, pady=8, padx=10, relief=tk.RIDGE, borderwidth=1)
            row_frame.pack(fill=tk.X, expand=True, padx=5, pady=4)
            
            # Khối 1: Số thứ tự
            tk.Label(row_frame, text=f"#{idx+1}", font=("Arial", 16, "bold"), fg="#555", width=3).pack(side=tk.LEFT, padx=5)
            
            # Khối 2: Avatar (Truy xuất ngược về folder gốc)
            img_path = os.path.join(self.image_folder, name)
            try:
                res_img = Image.open(img_path)
                res_img.thumbnail((80, 80)) 
                res_img_tk = ImageTk.PhotoImage(res_img)
                self.result_images.append(res_img_tk) 
                
                lbl_res_img = tk.Label(row_frame, image=res_img_tk, bg="black", borderwidth=1, relief=tk.SOLID)
                lbl_res_img.pack(side=tk.LEFT, padx=15)
            except Exception:
                tk.Label(row_frame, text="[Ảnh gốc\nđã xóa]", width=10, height=4, bg="#ffcccc", fg="red").pack(side=tk.LEFT, padx=15)

            # Khối 3: Thông tin chi tiết
            # Nhấn mạnh màu sắc nếu độ tương đồng cực kỳ cao (>85%)
            if score >= 0.85:
                text_color = "#28a745" # Xanh lá chuẩn
                score_font = ("Arial", 14, "bold")
            else:
                text_color = "#333333" # Đen xám
                score_font = ("Arial", 12)
                
            info_frame = tk.Frame(row_frame)
            info_frame.pack(side=tk.LEFT, padx=10)
            
            tk.Label(info_frame, text=f"Tên File: {name}", font=("Arial", 11, "italic")).pack(anchor="w")
            tk.Label(info_frame, text=f"Tương đồng: {score*100:.2f} %", font=score_font, fg=text_color).pack(anchor="w", pady=3)

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam') 
    app = FaceRankingApp(root)
    root.mainloop()
