import math
import ast

# --- 1. CÁC HÀM TOÁN HỌC TỰ CODE ---

def cosine_similarity(v1, v2):
    """Tính độ tương đồng Cosine giữa 2 vector"""
    if len(v1) != len(v2):
        print(f"Lỗi kích thước: v1({len(v1)}), v2({len(v2)})")
        return 0
        
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    
    if norm_v1 == 0 or norm_v2 == 0:
        return 0
    return dot_product / (norm_v1 * norm_v2)

# --- 2. HÀM ĐỌC DỮ LIỆU TỪ CSV (Tự code, không dùng Pandas) ---

def load_database(csv_path):
    database = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        # Bỏ qua dòng header đầu tiên
        for line in lines[1:]:
            # Phân tách dữ liệu: filename, "lbp_list", "hog_list"
            # Cần xử lý chuỗi cẩn thận vì danh sách có chứa dấu phẩy
            parts = line.strip().split(',"[')
            
            if len(parts) >= 2:
                filename = parts[0]
                
                # Khôi phục chuỗi thành list các số thực
                # Khôi phục LBP
                lbp_str = "[" + parts[1].split(']')[0] + "]"
                lbp_vector = ast.literal_eval(lbp_str)
                
                # Khôi phục HOG (Nằm ở phần tiếp theo)
                hog_str = "[" + parts[2].split(']')[0] + "]" if len(parts) > 2 else "[]"
                hog_vector = ast.literal_eval(hog_str) if hog_str != "[]" else []
                
                # Nối LBP và HOG thành 1 Master Vector
                master_vector = lbp_vector + hog_vector
                
                database.append({
                    "filename": filename,
                    "vector": master_vector
                })
    return database

# --- 3. HÀM NHẬN DIỆN TÌM KIẾM ---

def find_best_match(query_vector, database, threshold=0.85):
    """
    So sánh vector truy vấn với toàn bộ database để tìm người giống nhất.
    threshold: Ngưỡng quyết định (Ví dụ: phải giống trên 85% mới kết luận là cùng 1 người)
    """
    best_match = None
    highest_score = -1
    
    for entry in database:
        db_name = entry['filename']
        db_vector = entry['vector']
        
        # Tính điểm tương đồng
        score = cosine_similarity(query_vector, db_vector)
        
        if score > highest_score:
            highest_score = score
            best_match = db_name
            
    # Đánh giá kết quả dựa trên ngưỡng
    if highest_score >= threshold:
        print(f"[+] TÌM THẤY: Ảnh mới giống với '{best_match}' nhất (Độ tương đồng: {highest_score*100:.2f}%)")
    else:
        print(f"[-] KHÔNG XÁC ĐỊNH: Không có khuôn mặt nào đủ giống trong cơ sở dữ liệu. Giống nhất là '{best_match}' nhưng chỉ đạt {highest_score*100:.2f}%.")
        
    return best_match, highest_score

# --- 4. CHẠY THỬ NGHIỆM ---
if __name__ == "__main__":
    db_path = "bo_dac_trung.csv"
    print("Đang nạp cơ sở dữ liệu...")
    db = load_database(db_path)
    print(f"Đã nạp {len(db)} khuôn mặt vào bộ nhớ.")
    
    if len(db) >= 2:
        # GIẢ LẬP: Lấy vector của ảnh đầu tiên làm ảnh truy vấn mới
        query_img_vector = db[0]['vector']
        print(f"\n--- Thử nghiệm nhận diện ảnh: {db[0]['filename']} ---")
        
        # So sánh nó với phần còn lại của database (bỏ qua chính nó)
        database_to_search = db[1:] 
        
        find_best_match(query_img_vector, database_to_search, threshold=0.80)