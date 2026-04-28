# child_face_detection
-Chayj file tong_hop_dac_trung trước
-chạy file cd_app.py
Nhóm 1: Đặc trưng hình học Tỉ lệ trán/mặt: Trẻ em có vầng trán cao và chiếm tỉ trọng lớn (khoảng 1/3 đến 1/2 khuôn mặt) do hộp sọ phát triển nhanh hơn xương hàm.

Vị trí "Đường mắt": Ở trẻ em, đôi mắt thường nằm ở vị trí trung tâm hoặc thấp hơn một chút so với chiều dọc khuôn mặt. Ở người lớn, vị trí này thường cao hơn.

Độ bo tròn của cằm: Cằm trẻ em thường ngắn, lẹm và có đường viền rất mềm mại, không có góc cạnh xương hàm rõ rệt như người trưởng thành. Nhóm 2: Đặc trưng kết cấu (Texture Features) Độ mịn của da: Da trẻ em có mật độ lỗ chân lông nhỏ và hầu như không có nếp nhăn vùng mắt/khóe miệng.

Độ tương phản vùng má: Trẻ em thường có đôi má phúng phính, tạo ra sự chuyển biến ánh sáng rất mịn (gradient) trên ảnh đen trắng, thay vì các mảng sáng tối gắt do xương -------------------------------------------------Thuật toán sử dụng------------------------------------------------- Trích xuất hình dáng: Histogram of Oriented Gradients (HOG: Tính Gradient: Tính độ biến thiên ánh sáng theo trục X và Y để tìm các cạnh (edges). Tính Hướng: Xác định hướng của các cạnh đó (ví dụ: đường cong của má trẻ em sẽ có hướng gradient thay đổi rất mượt). Chia Cell: Chia ảnh 150x150 thành các ô nhỏ (ví dụ 8x8 pixel) và thống kê hướng gradient trong mỗi ô. Trích xuất đặc trưng hình học (Geometric Ratios): Tính khoảng cách Euclidean d = sqrt((x2 - x1)^2 + (y2 - y1)^2) chuẩn hóa min max
