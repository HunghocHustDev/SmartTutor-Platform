import Header from "../components/Header";
import Banner from "../components/Banner";
import ClassList from "../components/ClassList";
import Workflow from "../components/Workflow";
import Footer from "../components/Footer";

export default function HomePage({ setActiveModal, handleClassApply }) {
  return (
    <>
      {/* Đưa toàn bộ giao diện trang chủ hiện tại của bạn vào đây */}
      <Header
        onLoginClick={() => setActiveModal("login")}
        onRegisterClick={() => setActiveModal("register")}
      />
      <Banner
        onFindTutorClick={() => setActiveModal("login")}
        onBeTutorClick={() => setActiveModal("register")}
      />
      <ClassList onApply={handleClassApply} />
      <Workflow />
      <Footer />
    </>
  );
}
