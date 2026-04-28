import numpy as np

def manual_lbp(img_matrix):
    """
    Tự code thuật toán Local Binary Pattern với bán kính R=1, 8 điểm lân cận.
    Đầu vào: Ma trận numpy 2D của ảnh xám (150x150)
    Đầu ra: Vector Histogram 256 chiều
    """
    h, w = img_matrix.shape
    # Tạo ma trận rỗng để chứa giá trị LBP, nhỏ hơn ảnh gốc 1 viền để tránh lỗi index
    lbp_img = np.zeros((h - 2, w - 2), dtype=np.uint8)
    
    # Duyệt qua từng pixel (bỏ qua viền ngoài cùng)
    for i in range(1, h - 1):
        for j in range(1, w - 1):
            center = img_matrix[i, j]
            binary_code = 0
            
            # So sánh 8 hướng xung quanh (Top-Left, Top, Top-Right, Right, Bottom-Right, Bottom, Bottom-Left, Left)
            # Dịch bit (<<) để tạo số nguyên từ chuỗi nhị phân
            binary_code |= (1 if img_matrix[i-1, j-1] >= center else 0) << 7
            binary_code |= (1 if img_matrix[i-1, j]   >= center else 0) << 6
            binary_code |= (1 if img_matrix[i-1, j+1] >= center else 0) << 5
            binary_code |= (1 if img_matrix[i, j+1]   >= center else 0) << 4
            binary_code |= (1 if img_matrix[i+1, j+1] >= center else 0) << 3
            binary_code |= (1 if img_matrix[i+1, j]   >= center else 0) << 2
            binary_code |= (1 if img_matrix[i+1, j-1] >= center else 0) << 1
            binary_code |= (1 if img_matrix[i, j-1]   >= center else 0) << 0
            
            lbp_img[i-1, j-1] = binary_code
            
    # Tự code hàm tính Histogram (tần suất xuất hiện của các số từ 0 đến 255)
    histogram = np.zeros(256, dtype=np.float32)
    for row in lbp_img:
        for val in row:
            histogram[val] += 1
            
    # Chuẩn hóa Histogram
    histogram = histogram / (np.sum(histogram) + 1e-7)
    return histogram.tolist()