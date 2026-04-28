import os
import sqlite3
import numpy as np
from PIL import Image

# Import các hàm trích xuất tự code của bạn
from trich_xuat_ket_cau_da import manual_lbp
from trich_xuat_hinh_dang import manual_hog_simplified

def main():
    folder_path = "child"
    db_path = "csdldpt.db"
    
    if not os.path.exists(folder_path):
        print(f"[-] Lỗi: Không tìm thấy thư mục '{folder_path}' chứa ảnh.")
        return

    # --- 1. KẾT NỐI VÀ KHỞI TẠO CƠ SỞ DỮ LIỆU ---
    print(f"[*] Đang kết nối tới Cơ sở dữ liệu: {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Xóa bảng cũ (nếu có) để trích xuất lại từ đầu, đảm bảo không bị trùng lặp
    cursor.execute('DROP TABLE IF EXISTS SieuDuLieu')
    
    # Tạo bảng quản trị Siêu dữ liệu
    cursor.execute('''
        CREATE TABLE SieuDuLieu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT UNIQUE NOT NULL,
            master_vector TEXT NOT NULL
        )
    ''')
    print("[+] Đã khởi tạo xong bảng 'SieuDuLieu'. Bắt đầu trích xuất...\n")

    # --- 2. DUYỆT ẢNH VÀ TRÍCH XUẤT ĐẶC TRƯNG ---
    count = 0
    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".png", ".jpeg")):
            file_path = os.path.join(folder_path, filename)
            print(f"  -> Đang xử lý: {filename}")
            
            try:
                # Đọc ảnh bằng PIL và chuyển thành ma trận numpy 2D (Grayscale)
                img = Image.open(file_path).convert('L').resize((150, 150))
                img_matrix = np.array(img)
                
                # Gọi các hàm trích xuất
                lbp_feat = manual_lbp(img_matrix)
                hog_feat = manual_hog_simplified(img_matrix)
                
                # Nối 2 vector lại thành 1 Master Vector duy nhất
                master_vector = lbp_feat + hog_feat
                
                # Chuyển mảng thành chuỗi Text để lưu vào SQLite
                vector_text = str(master_vector)
                
                # --- 3. LƯU TRỰC TIẾP VÀO CSDL ---
                cursor.execute('''
                    INSERT INTO SieuDuLieu (filename, master_vector)
                    VALUES (?, ?)
                ''', (filename, vector_text))
                
                count += 1
                
            except Exception as e:
                print(f"     [!] Lỗi khi xử lý ảnh {filename}: {e}")

    # --- 4. LƯU THAY ĐỔI VÀ ĐÓNG KẾT NỐI ---
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print(f"[+] HOÀN TẤT! Đã trích xuất và lưu thành công {count} bản ghi vào CSDL SQLite.")

if __name__ == "__main__":
    main()
