import React from "react";
import bgImage from "../assets/Bg.png"; // <-- ĐÂY LÀ DÒNG IMPORT ẢNH MỚI THÊM VÀO

export default function Banner({ onFindTutorClick, onBeTutorClick }) {
  return (
    <section style={bannerSectionStyle}>
      {/* Khối nội dung bên trái */}
      <div style={contentLeftStyle}>
        <span style={badgeStyle}>Nền Tảng Uy Tín Toàn Quốc</span>

        <h1 style={titleStyle}>
          Tìm Gia Sư Giỏi,
          <br />
          Nâng Tầm <span style={{ color: "#F97316" }}>Tri Thức</span>
        </h1>

        {/* Đánh giá 5 sao */}
        <div style={ratingStyle}>
          <span style={{ color: "#FBBF24", fontSize: "20px" }}>★★★★★</span>
          <span style={{ color: "#4B5563", fontWeight: "500" }}>
            4.9/5 (15,000+ phụ huynh tin dùng)
          </span>
        </div>

        <p style={descriptionStyle}>
          Kết nối học viên với hơn 5,000+ Gia sư chất lượng cao, sinh viên xuất
          sắc từ các trường đại học top đầu (Bách Khoa, Ngoại Thương, Sư Phạm).
          Học thử miễn phí 2 buổi, cam kết tiến bộ rõ rệt sau 1 tháng.
        </p>

        {/* Các nút bấm tương tác */}
        <div style={buttonGroupStyle}>
          <button onClick={onFindTutorClick} style={btnPrimaryStyle}>
            Tìm Gia Sư Ngay
          </button>
          <button onClick={onBeTutorClick} style={btnSecondaryStyle}>
            Trở Thành Gia Sư
          </button>
        </div>
      </div>

      {/* Khối hình ảnh nổi bật bên phải */}
      <div style={contentRightStyle}>
        <div style={imageCardStyle}>
          {/* ĐÃ THAY src="assets/Bg.png" THÀNH src={bgImage} TRONG DẤU NGOẶC NHỌN */}
          <img src={bgImage} alt="Gia sư và học viên" style={imgStyle} />

          <div style={floatingTagStyle}>Lớp Học 1 kèm 1</div>
        </div>
      </div>
    </section>
  );
}

// ================= STYLING BẰNG INLINE CSS (GIỮ NGUYÊN) =================
const bannerSectionStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "60px 8%",
  backgroundColor: "#F3F4F6",
  minHeight: "550px",
  gap: "40px",
  flexWrap: "wrap",
};

const contentLeftStyle = {
  flex: "1",
  minWidth: "320px",
  display: "flex",
  flexDirection: "column",
  alignItems: "flex-start",
};

const badgeStyle = {
  backgroundColor: "#E1EFFE",
  color: "#1A56DB",
  padding: "6px 14px",
  borderRadius: "20px",
  fontSize: "14px",
  fontWeight: "600",
  marginBottom: "15px",
};

const titleStyle = {
  fontSize: "48px",
  fontWeight: "800",
  color: "#111827",
  lineHeight: "1.2",
  margin: "0 0 15px 0",
};

const ratingStyle = {
  display: "flex",
  alignItems: "center",
  gap: "8px",
  marginBottom: "20px",
};

const descriptionStyle = {
  fontSize: "16px",
  color: "#4B5563",
  lineHeight: "1.6",
  marginBottom: "30px",
  maxWidth: "540px",
  textAlign: "justify",
};

const buttonGroupStyle = {
  display: "flex",
  gap: "15px",
  flexWrap: "wrap",
};

const btnPrimaryStyle = {
  padding: "14px 28px",
  backgroundColor: "#1A56DB",
  color: "white",
  border: "none",
  borderRadius: "8px",
  fontSize: "16px",
  fontWeight: "bold",
  cursor: "pointer",
  transition: "transform 0.2s",
  boxShadow: "0 4px 6px -1px rgba(26, 86, 219, 0.3)",
};

const btnSecondaryStyle = {
  padding: "14px 28px",
  backgroundColor: "#ffffff",
  color: "#1A56DB",
  border: "2px solid #1A56DB",
  borderRadius: "8px",
  fontSize: "16px",
  fontWeight: "bold",
  cursor: "pointer",
  transition: "background-color 0.2s",
};

const contentRightStyle = {
  flex: "1",
  minWidth: "320px",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
};

const imageCardStyle = {
  position: "relative",
  width: "100%",
  maxWidth: "480px",
  height: "360px",
  borderRadius: "16px",
  overflow: "hidden",
  boxShadow:
    "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)",
};

const imgStyle = {
  width: "100%",
  height: "100%",
  objectFit: "cover",
};

const floatingTagStyle = {
  position: "absolute",
  top: "20px",
  left: "20px",
  backgroundColor: "#EF4444",
  color: "white",
  padding: "6px 14px",
  borderRadius: "4px",
  fontSize: "13px",
  fontWeight: "bold",
  textTransform: "uppercase",
};
