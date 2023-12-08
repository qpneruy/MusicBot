def solve(points):
    """Giải quyết bài toán nối điểm bằng thuật toán bọc gói."""

    # Khởi tạo tập bao
    bao = []

    # Thêm điểm đầu tiên vào tập bao
    bao.append(points[0])

    # Chạy vòng lặp cho tất cả các điểm còn lại
    for i in range(1, len(points)):
        # Kiểm tra xem điểm hiện tại có cắt với bất kỳ điểm nào trong tập bao hay không
        for j in range(len(bao)):
            if points[i].intersects(bao[j]):
                break
        else:
            # Điểm hiện tại không cắt với bất kỳ điểm nào trong tập bao
            bao.append(points[i])

    # Vẽ các đường nối
    for i in range(len(bao) - 1):
        points[bao[i]].draw_line(points[bao[i + 1]])


if __name__ == "__main__":
    # Tạo hoán vị
    points = [1, 2, 3, 4, 5]

    # Giải quyết bài toán
    solve(points)
