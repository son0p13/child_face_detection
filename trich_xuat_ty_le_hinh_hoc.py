import math

def dist_euclidean(p1, p2):
    """Tự code công thức tính khoảng cách 2 điểm"""
    return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

def extract_geometry_manual(landmarks_dict):
    """
    Đầu vào: Dictionary tọa độ { 'top_head': (10, 50), ... }
    """
    # 1. Tự code Min-Max Normalization
    x_coords = [p[0] for p in landmarks_dict.values()]
    y_coords = [p[1] for p in landmarks_dict.values()]
    
    x_min, x_max = min(x_coords), max(x_coords)
    y_min, y_max = min(y_coords), max(y_coords)
    
    w, h = x_max - x_min, y_max - y_min
    if w == 0: w = 1
    if h == 0: h = 1
    
    norm_lm = {}
    for k, (x, y) in landmarks_dict.items():
        norm_lm[k] = ((x - x_min) / w, (y - y_min) / h)
        
    # 2. Tính toán đặc trưng
    forehead = dist_euclidean(norm_lm['top_head'], norm_lm['mid_eyebrows'])
    face_h = dist_euclidean(norm_lm['top_head'], norm_lm['chin'])
    
    eye_dist = dist_euclidean(norm_lm['left_eye'], norm_lm['right_eye'])
    face_w = dist_euclidean(norm_lm['left_cheek'], norm_lm['right_cheek'])
    
    forehead_ratio = forehead / face_h if face_h > 0 else 0
    eye_ratio = eye_dist / face_w if face_w > 0 else 0
    roundness = face_w / face_h if face_h > 0 else 0
    
    return [forehead_ratio, eye_ratio, roundness]