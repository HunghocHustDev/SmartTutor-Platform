import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import Banner from "./components/Banner";
import ClassList from "./components/ClassList";
import Workflow from "./components/Workflow"; // Đã import chính xác
import Footer from "./components/Footer"; // Đã import chính xác
import LoginForm from "./components/auth/LoginForm";
import RegisterForm from "./components/auth/RegisterForm";
import "./App.css";

function App() {
  const [activeModal, setActiveModal] = useState(null);

  // --- BỔ SUNG STATE MỚI ĐỂ QUẢN LÝ TAB CHO HỌC VIÊN ---
  // Mặc định ban đầu ở trang chủ ("home")
  const [activeTab, setActiveTab] = useState("home");

  // State quản lý user hiện tại để ép toàn bộ component con re-render khi đổi vai trò
  const [currentUser, setCurrentUser] = useState(() => {
    return JSON.parse(localStorage.getItem("user")) || null;
  });

  // Hàm đồng bộ trạng thái khi có hành động Đăng nhập/Đăng xuất/Đổi role từ Header
  const handleUserChange = () => {
    const updatedUser = JSON.parse(localStorage.getItem("user")) || null;
    setCurrentUser(updatedUser);
    // Khi người dùng đăng xuất hoặc đổi tài khoản ảo, tự động đưa tab về trang chủ công khai
    setActiveTab("home");
  };

  // Hàm xử lý tương tác khi bấm "Đăng ký nhận lớp" từ danh sách lớp học
  const handleClassApply = (cls) => {
    // 💡 GIẢI THÍCH BACKEND: Sau này bạn sẽ check token thật gửi kèm header của API
    const user = JSON.parse(localStorage.getItem("user"));

    if (!user) {
      // Trường hợp 1: Khách vãng lai chưa đăng nhập -> Yêu cầu đăng nhập tài khoản Gia sư
      alert(
        `Bạn đang đăng ký nhận lớp ${cls.id} - ${cls.subject}.\nVui lòng đăng nhập bằng tài khoản Gia sư để tiếp tục!`,
      );
      setActiveModal("login");
    } else if (user.role !== "tutor") {
      // Trường hợp 2: Đã đăng nhập nhưng sai Role (ví dụ Học viên bấm nhầm)
      alert(
        `Tài khoản hiện tại của bạn là "${user.name}" (Vai trò: ${user.role === "student" ? "Học viên" : "Nhân viên"}).\nChức năng nhận lớp này chỉ dành riêng cho Gia sư!`,
      );
    } else {
      // Trường hợp 3: Đã đăng nhập đúng là Gia sư -> Chạy mượt mà
      // Logic chính đã được xử lý gọn gàng bên trong ClassList.jsx
      console.log("Gia sư hợp lệ đang thực hiện nhận lớp:", cls.id);
    }
  };

  return (
    <div className="app-container min-h-screen bg-gray-50 antialiased font-sans">
      {/* TRUYỀN THÊM CÁC PROP MỚI VÀO HEADER:
        - currentUser: Để Header biết ai đăng nhập mà đổi menu tương ứng
        - activeTab: Tab đang kích hoạt hiện tại
        - onTabChange: Callback nhận sự kiện khi học viên click vào 4 mục mới trên Header
      */}
      <Header
        currentUser={currentUser}
        onLoginClick={() => setActiveModal("login")}
        onRegisterClick={() => setActiveModal("register")}
        onUserChange={handleUserChange}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* ỨNG DỤNG CƠ CHẾ RENDER CÓ ĐIỀU KIỆN (CONDITIONAL RENDERING):
        - Nếu activeTab là "home": Hiển thị giao diện Trang chủ công khai như bình thường.
        - Nếu activeTab đổi thành 1 trong 4 mục học viên: Ẩn trang chủ, hiện không gian giao diện chức năng đó.
      */}
      {activeTab === "home" ? (
        <>
          {/* Key={currentUser?.role || 'guest'} là một mẹo nhỏ trong React (Force Re-render)
            Giúp Banner lập tức chuyển giao diện đổi màu khi đổi tài khoản mà không cần F5 trình duyệt.
          */}
          <Banner
            key={currentUser?.role || "guest"}
            onFindTutorClick={() => {
              // Tối ưu trải nghiệm: Nếu là học viên bấm "Tìm gia sư" ở Banner, chuyển thẳng qua Tab Gửi yêu cầu học
              if (currentUser?.role === "student") {
                setActiveTab("request");
              } else {
                setActiveModal("login");
              }
            }}
            onBeTutorClick={() => setActiveModal("register")}
          />

          {/* Danh sách lớp học mới cập nhật */}
          <ClassList onClassClick={handleClassApply} />

          {/* Quy trình trung tâm làm việc */}
          <Workflow />
        </>
      ) : (
        /* --- KHU VỰC HIỂN THỊ CHI TIẾT NỘI DUNG 4 MỤC MỚI DÀNH CHO HỌC VIÊN --- */
        <div className="max-w-7xl mx-auto px-4 py-8 min-h-[550px]">
          {/* Nút quay lại để thuận tiện hơn trong quá trình test giao diện */}
          <button
            onClick={() => setActiveTab("home")}
            className="mb-6 text-sm font-medium text-blue-600 hover:text-blue-800 flex items-center gap-1 transition-colors"
          >
            ← Quay về Trang chủ hệ thống
          </button>

          {/* Mục 1: Gửi yêu cầu học (request) */}
          {activeTab === "request" && (
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 max-w-2xl">
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Gửi Yêu Cầu Học / Tìm Gia Sư
              </h2>
              <p className="text-sm text-gray-500 mb-6">
                Vui lòng điền thông tin chi tiết. Đội ngũ nhân viên trung tâm sẽ
                liên hệ tư vấn và kết nối lớp học trong vòng 24h.
              </p>

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  alert("Gửi yêu cầu thành công! (Dữ liệu Mockup)");
                }}
                className="space-y-4"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">
                      Môn học cần gia sư
                    </label>
                    <input
                      type="text"
                      placeholder="VD: Toán lớp 12, Tiếng Anh IELTS..."
                      required
                      className="w-full p-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">
                      Số buổi dự kiến / tuần
                    </label>
                    <input
                      type="number"
                      placeholder="VD: 2 buổi, 3 buổi..."
                      required
                      className="w-full p-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">
                    Mức học phí dự kiến (VNĐ/Tháng hoặc VNĐ/Buổi)
                  </label>
                  <input
                    type="text"
                    placeholder="VD: 2.000.000đ/tháng"
                    className="w-full p-2.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold uppercase text-gray-500 mb-1">
                    Yêu cầu cụ thể đối với gia sư
                  </label>
                  <textarea
                    placeholder="VD: Cần gia sư Nam, là Sinh viên trường ĐH Ngoại Thương, giọng miền Nam, kiên nhẫn..."
                    className="w-full p-2.5 border border-gray-200 rounded-lg text-sm h-28 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <button
                  type="submit"
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-4 rounded-lg text-sm transition-colors shadow-sm"
                >
                  Gửi Yêu Cầu Kết Nối Lớp
                </button>
              </form>
            </div>
          )}

          {/* Mục 2: Yêu cầu của tôi (my-requests) */}
          {activeTab === "my-requests" && (
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 max-w-4xl">
              <h2 className="text-2xl font-bold text-gray-800 mb-1">
                Yêu Cầu Của Tôi
              </h2>
              <p className="text-sm text-gray-500 mb-6">
                Theo dõi tiến độ duyệt hồ sơ và kết nối gia sư của trung tâm
                dành cho các nhu cầu học bạn đã gửi.
              </p>

              <div className="border border-gray-100 rounded-xl overflow-hidden shadow-xs divide-y divide-gray-100">
                {/* Dòng dữ liệu mẫu 1 */}
                <div className="p-4 bg-gray-50/50 sm:flex sm:justify-between sm:items-center">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-gray-800 text-base">
                        Toán Học Lớp 12
                      </span>
                      <span className="text-xs font-mono text-gray-400 bg-gray-200/60 px-1.5 py-0.5 rounded">
                        #YC-4091
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">
                      Ngày gửi: 09/06/2026 • 3 buổi/tuần • Yêu cầu: Sinh viên sư
                      phạm
                    </p>
                  </div>
                  <div className="mt-2 sm:mt-0">
                    <span className="inline-flex items-center bg-amber-100 text-amber-800 text-xs px-2.5 py-1 rounded-full font-semibold">
                      Đang tìm gia sư phù hợp
                    </span>
                  </div>
                </div>

                {/* Dòng dữ liệu mẫu 2 */}
                <div className="p-4 bg-white sm:flex sm:justify-between sm:items-center">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-gray-800 text-base">
                        Tiếng Anh Giao Tiếp IELTS
                      </span>
                      <span className="text-xs font-mono text-gray-400 bg-gray-200/60 px-1.5 py-0.5 rounded">
                        #YC-3820
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">
                      Ngày gửi: 01/06/2026 • 2 buổi/tuần • Yêu cầu: Gia sư đã có
                      bằng IELTS 7.5+
                    </p>
                  </div>
                  <div className="mt-2 sm:mt-0">
                    <span className="inline-flex items-center bg-green-100 text-green-800 text-xs px-2.5 py-1 rounded-full font-semibold">
                      Đã phân công - Đã tạo lớp
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Mục 3: Lớp học của tôi (my-classes) */}
          {activeTab === "my-classes" && (
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 max-w-4xl">
              <h2 className="text-2xl font-bold text-gray-800 mb-1">
                Lớp Học Của Tôi
              </h2>
              <p className="text-sm text-gray-500 mb-6">
                Danh sách các lớp học chính thức đang diễn ra và thông tin gia
                sư phụ trách tương ứng.
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="border border-blue-100 bg-blue-50/20 p-5 rounded-xl flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-start mb-3">
                      <h3 className="font-bold text-blue-900 text-lg">
                        Lớp Tiếng Anh IELTS (#LH-004)
                      </h3>
                      <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-md font-semibold">
                        Đang diễn ra
                      </span>
                    </div>
                    <div className="space-y-1.5 text-sm text-gray-600">
                      <p>
                        👨‍🏫 Gia sư:{" "}
                        <span className="font-medium text-gray-800">
                          Lê Văn B (ĐH Ngoại Thương)
                        </span>
                      </p>
                      <p>
                        📅 Lịch học:{" "}
                        <span className="font-medium text-gray-800">
                          Thứ 3 - Thứ 5 (19:30 - 21:30)
                        </span>
                      </p>
                      <p>
                        📍 Hình thức:{" "}
                        <span className="font-medium text-gray-800">
                          Trực tiếp tại nhà
                        </span>
                      </p>
                    </div>
                  </div>
                  <div className="mt-4 pt-3 border-t border-blue-100/50 flex justify-between text-xs text-gray-400">
                    <span>Bắt đầu từ: 05/06/2026</span>
                    <button className="text-blue-600 hover:underline font-medium">
                      Xem nhật ký buổi học
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Mục 4: Học phí (tuition) */}
          {activeTab === "tuition" && (
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 max-w-5xl">
              <h2 className="text-2xl font-bold text-gray-800 mb-1">
                Quản Lý Học Phí
              </h2>
              <p className="text-sm text-gray-500 mb-6">
                Báo cáo học phí chi tiết và tình trạng đóng tiền của từng lớp
                học phát sinh theo tháng.
              </p>

              <div className="overflow-x-auto border border-gray-100 rounded-xl">
                <table className="w-full text-left border-collapse text-sm">
                  <thead>
                    <tr className="bg-gray-100 border-b border-gray-200 text-gray-700 font-semibold">
                      <th className="p-3.5">Mã Lớp / Tên Lớp Học</th>
                      <th className="p-3.5">Học Phí / Tháng</th>
                      <th className="p-3.5">Kỳ Hạn Đóng Kế Tiếp</th>
                      <th className="p-3.5">Trạng Thái Thanh Toán</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100 text-gray-600">
                    <tr className="hover:bg-gray-50/50 transition-colors">
                      <td className="p-3.5 font-medium text-gray-900">
                        #LH-004 - Lớp Tiếng Anh IELTS
                      </td>
                      <td className="p-3.5">2.400.000đ</td>
                      <td className="p-3.5">05/07/2026</td>
                      <td className="p-3.5">
                        <span className="inline-flex items-center text-green-600 font-semibold bg-green-50 px-2 py-0.5 rounded text-xs border border-green-200/50">
                          ● Đã hoàn thành tháng này
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Chân trang hiển thị tại đây */}
      <Footer />

      {/* Modal Đăng nhập */}
      {activeModal === "login" && (
        <LoginForm
          onClose={() => setActiveModal(null)}
          switchToRegister={() => setActiveModal("register")}
          onLoginSuccess={handleUserChange} // Báo cho App biết để cập nhật Header/Banner khi đăng nhập thành công
        />
      )}

      {/* Modal Đăng ký */}
      {activeModal === "register" && (
        <RegisterForm
          onClose={() => setActiveModal(null)}
          switchToLogin={() => setActiveModal("login")}
        />
      )}
    </div>
  );
}

export default App;
