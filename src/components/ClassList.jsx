import React, { useRef } from "react";

// 1. Tạo dữ liệu ảo (Mock Data) cho các lớp học
const MOCK_CLASSES = [
  {
    id: "L001",
    subject: "Toán học (Ôn thi THPT Quốc Gia)",
    grade: "Lớp 12",
    fee: "250.000đ/buổi",
    address: "Quận Hai Bà Trưng, Hà Nội",
    status: "Đang tìm Gia sư",
    frequency: "2 buổi/tuần",
  },
  {
    id: "L002",
    subject: "Tiếng Anh Giao Tiếp Cơ Bản",
    grade: "Người đi làm",
    fee: "300.000đ/buổi",
    address: "Quận Cầu Giấy, Hà Nội",
    status: "Đang tìm Gia sư",
    frequency: "3 buổi/tuần",
  },
  {
    id: "L003",
    subject: "Vật Lý (Luyện thi vào 10)",
    grade: "Lớp 9",
    fee: "200.000đ/buổi",
    address: "Quận Đống Đa, Hà Nội",
    status: "Đang tìm Gia sư",
    frequency: "2 buổi/tuần",
  },
  {
    id: "L004",
    subject: "Hóa Học Cơ Bản & Nâng Cao",
    grade: "Lớp 11",
    fee: "220.000đ/buổi",
    address: "Quận Ba Đình, Hà Nội",
    status: "Đang tìm Gia sư",
    frequency: "2 buổi/tuần",
  },
  {
    id: "L005",
    subject: "Lập trình Python Kid",
    grade: "Lớp 7",
    fee: "350.000đ/buổi",
    address: "Quận Nam Từ Liêm, Hà Nội",
    status: "Đang tìm Gia sư",
    frequency: "1 buổi/tuần",
  },
  {
    id: "L006",
    subject: "Ngữ Văn (Bồi dưỡng học sinh giỏi)",
    grade: "Lớp 9",
    fee: "200.000đ/buổi",
    address: "Quận Hoàn Kiếm, Hà Nội",
    status: "Đang tìm Gia sư",
    frequency: "2 buổi/tuần",
  },
];

export default function ClassList({ onClassClick }) {
  // Dùng useRef để điều khiển cuộn thanh trượt bằng nút bấm
  const scrollContainerRef = useRef(null);

  // Hàm xử lý khi bấm nút trượt sang trái/phải
  const handleScroll = (direction) => {
    if (scrollContainerRef.current) {
      const cardWidth = 360 + 24; // Chiều rộng của 1 card + gap
      const scrollAmount = direction === "left" ? -cardWidth : cardWidth;
      scrollContainerRef.current.scrollBy({
        left: scrollAmount,
        behavior: "smooth", // Hiệu ứng trượt mượt mà
      });
    }
  };

  return (
    <section style={containerStyle}>
      {/* Tiêu đề vùng hiển thị */}
      <div style={headerStyle}>
        <div>
          <h2 style={titleStyle}>Lớp Học Mới Đang Tìm Gia Sư</h2>
          <p style={subtitleStyle}>
            Các lớp học vừa được đăng ký, nhận lớp ngay hôm nay
          </p>
        </div>

        {/* Nút bấm điều hướng trượt ngang */}
        <div style={arrowGroupStyle}>
          <button onClick={() => handleScroll("left")} style={arrowButtonStyle}>
            ←
          </button>
          <button
            onClick={() => handleScroll("right")}
            style={arrowButtonStyle}
          >
            →
          </button>
        </div>
      </div>

      {/* Vùng chứa danh sách lớp có hỗ trợ scroll ngang ẩn thanh cuộn */}
      <div
        ref={scrollContainerRef}
        style={scrollWrapperStyle}
        className="hide-scrollbar"
      >
        {MOCK_CLASSES.map((cls) => (
          <div key={cls.id} style={cardStyle}>
            <div style={cardHeaderStyle}>
              <span style={codeStyle}>Mã: {cls.id}</span>
              <span style={statusBadgeStyle}>{cls.status}</span>
            </div>

            <h3 style={subjectStyle}>{cls.subject}</h3>

            <div style={infoRowStyle}>
              <span style={infoLabelStyle}>Trình độ:</span>
              <span style={infoValueStyle}>{cls.grade}</span>
            </div>
            <div style={infoRowStyle}>
              <span style={infoLabelStyle}>Học phí:</span>
              <span
                style={{
                  ...infoValueStyle,
                  color: "#EF4444",
                  fontWeight: "bold",
                }}
              >
                {cls.fee}
              </span>
            </div>
            <div style={infoRowStyle}>
              <span style={infoLabelStyle}>Lịch học:</span>
              <span style={infoValueStyle}>{cls.frequency}</span>
            </div>
            <div style={infoRowStyle}>
              <span style={infoLabelStyle}>Địa điểm:</span>
              <span style={infoValueStyle}>{cls.address}</span>
            </div>

            <button onClick={() => onClassClick(cls)} style={btnApplyStyle}>
              Đăng Ký Nhận Lớp
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}

// ================= STYLING BẰNG INLINE CSS =================
const containerStyle = {
  padding: "60px 8%",
  backgroundColor: "#ffffff",
  position: "relative",
};

const headerStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "end",
  marginBottom: "30px",
};

const titleStyle = {
  fontSize: "28px",
  fontWeight: "700",
  color: "#111827",
  margin: "0 0 8px 0",
};

const subtitleStyle = {
  fontSize: "16px",
  color: "#6B7280",
  margin: 0,
};

const arrowGroupStyle = {
  display: "flex",
  gap: "10px",
};

const arrowButtonStyle = {
  width: "40px",
  height: "40px",
  borderRadius: "50%",
  border: "1px solid #D1D5DB",
  backgroundColor: "#fff",
  fontSize: "18px",
  cursor: "pointer",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
  userSelect: "none",
  transition: "all 0.2s",
};

const scrollWrapperStyle = {
  display: "flex",
  gap: "24px",
  overflowX: "auto", // Cho phép kéo/cuộn ngang
  scrollBehavior: "smooth",
  paddingBottom: "15px",
  // Đoạn CSS ẩn thanh cuộn scrollbar chuẩn của trình duyệt (Sẽ bổ sung thêm global CSS ở bước sau)
};

const cardStyle = {
  flex: "0 0 calc(33.333% - 16px)", // Đảm bảo hiện đúng 3 lớp trên 1 màn hình lớn
  minWidth: "340px", // Để không bị quá bóp méo trên màn hình nhỏ
  backgroundColor: "#F9FAFB",
  border: "1px solid #E5E7EB",
  borderRadius: "12px",
  padding: "24px",
  boxSizing: "border-box",
  display: "flex",
  flexDirection: "column",
  justifyContent: "space-between",
  boxShadow: "0 4px 6px -1px rgba(0,0,0,0.02)",
};

const cardHeaderStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "15px",
};

const codeStyle = {
  fontSize: "13px",
  fontWeight: "600",
  color: "#9CA3AF",
};

const statusBadgeStyle = {
  backgroundColor: "#FEF3C7",
  color: "#D97706",
  padding: "4px 10px",
  borderRadius: "12px",
  fontSize: "12px",
  fontWeight: "600",
};

const subjectStyle = {
  fontSize: "18px",
  fontWeight: "700",
  color: "#1F2937",
  margin: "0 0 15px 0",
  lineHeight: "1.4",
  height: "50px", // Khóa chiều cao cố định để các card đều nhau
  overflow: "hidden",
};

const infoRowStyle = {
  display: "flex",
  justifyContent: "space-between",
  fontSize: "14px",
  marginBottom: "10px",
  lineHeight: "1.5",
};

const infoLabelStyle = {
  color: "#6B7280",
};

const infoValueStyle = {
  color: "#374151",
  fontWeight: "500",
  textAlign: "right",
  maxWidth: "70%",
};

const btnApplyStyle = {
  marginTop: "20px",
  padding: "12px",
  backgroundColor: "#1A56DB",
  color: "white",
  border: "none",
  borderRadius: "6px",
  fontSize: "15px",
  fontWeight: "bold",
  cursor: "pointer",
  textAlign: "center",
  width: "100%",
};
