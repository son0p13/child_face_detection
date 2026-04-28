import numpy as np
import math

def manual_hog_simplified(img_matrix):
    """
    Tự code HOG rút gọn (Cell-based HOG).
    Chia ảnh thành các ô 10x10, mỗi ô tính histogram 9 góc.
    """
    h, w = img_matrix.shape
    
    # 1. Tự code bộ lọc Sobel để tìm Gradient X và Y
    gx = np.zeros((h, w), dtype=np.float32)
    gy = np.zeros((h, w), dtype=np.float32)
    
    for i in range(1, h-1):
        for j in range(1, w-1):
            # Tính độ chênh lệch pixel lân cận
            gx[i, j] = int(img_matrix[i, j+1]) - int(img_matrix[i, j-1])
            gy[i, j] = int(img_matrix[i+1, j]) - int(img_matrix[i-1, j])
            
    # 2. Tính Độ lớn và Góc
    magnitude = np.sqrt(gx**2 + gy**2)
    # Tính góc theo độ (từ -180 đến 180), ép về 0-180
    angle = np.degrees(np.arctan2(gy, gx)) % 180
    
    # 3. Chia ô (Cells) và bỏ vào Bins
    cell_size = 10
    bin_count = 9
    hog_vector = []
    
    # Duyệt qua từng khối 10x10 pixel
    for i in range(0, h, cell_size):
        for j in range(0, w, cell_size):
            cell_mag = magnitude[i:i+cell_size, j:j+cell_size]
            cell_ang = angle[i:i+cell_size, j:j+cell_size]
            
            # Khởi tạo 9 "rổ" chứa giá trị góc (0, 20, 40,..., 160 độ)
            bins = np.zeros(bin_count)
            
            for cell_i in range(cell_mag.shape[0]):
                for cell_j in range(cell_mag.shape[1]):
                    mag_val = cell_mag[cell_i, cell_j]
                    ang_val = cell_ang[cell_i, cell_j]
                    
                    # Tìm xem góc này thuộc "rổ" nào
                    bin_idx = int(ang_val // (180 / bin_count))
                    if bin_idx == bin_count: bin_idx -= 1
                    
                    # Bỏ độ lớn của pixel vào rổ đó
                    bins[bin_idx] += mag_val
                    
            hog_vector.extend(bins)
            
    # L2 Normalization
    hog_vector = np.array(hog_vector)
    norm = np.linalg.norm(hog_vector)
    if norm > 0:
        hog_vector = hog_vector / norm
        
    return hog_vector.tolist()