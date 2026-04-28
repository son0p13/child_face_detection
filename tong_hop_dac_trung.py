import os
import numpy as np
from PIL import Image
from trich_xuat_ket_cau_da import manual_lbp
from trich_xuat_hinh_dang import manual_hog_simplified

def main():
    folder_path = "child"
    if not os.path.exists(folder_path):
        print("Không tìm thấy thư mục")
        return

    # Tự code ghi file CSV thủ công (Không dùng Pandas)
    with open("bo_dac_trung.csv", "w", encoding="utf-8") as f:
        # Ghi Header
        f.write("filename,lbp_features,hog_features\n")
        
        for filename in os.listdir(folder_path):
            if filename.endswith((".jpg", ".png")):
                file_path = os.path.join(folder_path, filename)
                print(f"Đang xử lý: {filename}")
                
                # 1. Đọc ảnh bằng PIL và chuyển thành ma trận numpy 2D (Grayscale)
                img = Image.open(file_path).convert('L')
                img_matrix = np.array(img)
                
                # 2. Gọi các hàm tự code
                lbp_feat = manual_lbp(img_matrix)
                hog_feat = manual_hog_simplified(img_matrix)
                
                # Do bạn phải nhập tọa độ tay nên tôi tạm bỏ qua phần Geometry trong vòng lặp này
                
                # 3. Chuyển mảng thành chuỗi để ghi file
                lbp_str = '"' + str(lbp_feat) + '"'
                hog_str = '"' + str(hog_feat) + '"'
                
                # Ghi dòng dữ liệu
                f.write(f"{filename},{lbp_str},{hog_str}\n")
                
    print("Hoàn tất! Đã tự code xong quá trình trích xuất.")

if __name__ == "__main__":
    main()