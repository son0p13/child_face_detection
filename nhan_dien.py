import math
import ast
import sqlite3
import os

# --- 1. HÀM TOÁN HỌC (COSINE SIMILARITY) ---
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


# --- 2. HÀM ĐỌC DỮ LIỆU TỪ SQLITE ---
def load_database(db_path="csdldpt.db"):
    """
    Truy vấn toàn bộ siêu dữ liệu (Feature Vectors) từ CSDL SQLite.
    """
    database = []
    
    if not os.path.exists(db_path):
        return database
        
    try:
        # Kết nối tới file CSDL
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lấy toàn bộ dữ liệu từ bảng SieuDuLieu
        cursor.execute("SELECT filename, master_vector FROM SieuDuLieu")
        rows = cursor.fetchall()
        
        for row in rows:
            filename = row[0]
            vector_str = row[1]
            
            # Chuyển chuỗi Text lưu trong DB thành mảng list[] của Python
            master_vector = ast.literal_eval(vector_str)
            
            database.append({
                "filename": filename,
                "vector": master_vector
            })
            
        conn.close()
    except sqlite3.Error as e:
        print(f"[-] Lỗi truy vấn CSDL: {e}")
        
    return database


# --- 3. HÀM XẾP HẠNG KẾT QUẢ ---
def get_ranked_results(query_vector, database):
    """
    So sánh vector truy vấn với toàn bộ database.
    Trả về danh sách các kết quả được sắp xếp theo độ tương đồng giảm dần.
    """
    results = []
    for entry in database:
        score = cosine_similarity(query_vector, entry['vector'])
        results.append({
            "filename": entry['filename'],
            "score": score
        })
    
    # Sắp xếp danh sách theo 'score' từ cao xuống thấp (reverse=True)
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


# --- 4. CHẠY THỬ NGHIỆM ĐỘC LẬP TRÊN TERMINAL ---
if __name__ == "__main__":
    db_path = "csdldpt.db"
    print(f"[*] Đang nạp cơ sở dữ liệu từ '{db_path}'...")
    
    db = load_database(db_path)
    
    if len(db) >= 2:
        print(f"[+] Đã nạp thành công {len(db)} khuôn mặt vào bộ nhớ.")
        
        # GIẢ LẬP: Lấy vector của ảnh đầu tiên trong DB làm ảnh truy vấn mới
        query_img_vector = db[0]['vector']
        query_filename = db[0]['filename']
        
        print(f"\n--- Thử nghiệm xếp hạng nhận diện cho ảnh: {query_filename} ---")
        
        # So sánh nó với phần còn lại của database (bỏ qua chính nó)
        database_to_search = db[1:] 
        
        # Gọi hàm xếp hạng
        ranked_results = get_ranked_results(query_img_vector, database_to_search)
        
        print("\n[ TOP 5 ẢNH GIỐNG NHẤT ]")
        for i, res in enumerate(ranked_results[:5]):
            print(f"{i+1}. {res['filename']} - Độ tương đồng: {res['score']*100:.2f}%")
            
    elif len(db) == 1:
        print("[-] CSDL hiện chỉ có 1 ảnh, không đủ để chạy thuật toán so sánh.")
    else:
        print(f"[-] Lỗi: Không tìm thấy dữ liệu. Hãy đảm bảo bạn đã chạy file 'tong_hop_dac_trung.py' để tạo CSDL trước.")
