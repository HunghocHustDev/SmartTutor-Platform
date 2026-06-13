# Frontend Analysis

## 1. Tong quan frontend

- Framework/thu vien dang dung:
  - React 19
  - React Router DOM 7 (`createBrowserRouter`, `RouterProvider`)
  - Vite 8
  - Tailwind CSS 4 qua `@tailwindcss/vite`
  - Heroicons (`@heroicons/react`) duoc dung trong `ClassesPage`
- Cach chay frontend:
  - Cai dependencies: `npm install`
  - Chay dev server: `npm run dev`
  - Build production: `npm run build`
- Trang thai build:
  - Da chay `npm run build`, build thanh cong.
- Cau truc thu muc chinh:

| Thu muc/File | Vai tro |
| --- | --- |
| `frontend/package.json` | Khai bao scripts va dependencies |
| `frontend/src/main.jsx` | Entry point cua React app |
| `frontend/src/App.jsx` | Khai bao router, providers va modal renderer |
| `frontend/src/layouts/MainLayout.jsx` | Layout chung, render `Header`, `Sidebar`, `Outlet` |
| `frontend/src/contexts/` | `AuthContext`, `ModalContext` |
| `frontend/src/pages/` | Cac page duoc gan route |
| `frontend/src/components/` | Cac UI component dung lai va auth modal |
| `frontend/src/components/student/` | Cac component nghiep vu student, hien chua duoc gan vao route |
| `frontend/src/assets/` | Anh tich hop vao frontend |
| `frontend/public/` | Static assets |
| `docs/` | Tai lieu phan tich nay |

- Cac dependency quan trong:

| Dependency | Muc dich |
| --- | --- |
| `react`, `react-dom` | Nen tang UI |
| `react-router-dom` | Routing |
| `tailwindcss`, `@tailwindcss/vite` | Styling |
| `@heroicons/react` | Icon |
| `vite` | Dev server/build |

- Nhan xet tong quan:
  - Frontend hien tai la SPA React dung route client-side.
  - Chua co backend integration that.
  - Chua thay `services/`, `api/`, `hooks/`, `types/`, `interfaces/`, `stores/`, `mocks/` tach rieng.
  - Da co co che role demo bang `fakeLogin` va `localStorage`.
  - Du lieu chu yeu dang nam ngay trong tung page/component duoi dang hard-code/mock array.

## 2. Cau truc route/page

| Route/Page | File tuong ung | Muc dich | Actor su dung | Ghi chu |
| --- | --- | --- | --- | --- |
| `/` | `frontend/src/pages/DashboardPage.jsx` | Trang tong quan/landing page; banner thay doi theo role | Guest, student, tutor, admin | Admin co them 3 so lieu tong hop hard-code |
| `/lop-moi` | `frontend/src/pages/ClassListPage.jsx` | Danh sach lop moi tuyen de tutor dang ky nhan lop | Guest, tutor | Dung `ClassList` voi mock data |
| `/students` | `frontend/src/pages/StudentsPage.jsx` | Placeholder quan ly hoc vien | Khong ro | Chi hien 1 dong "dang phat trien" |
| `/tutors` | `frontend/src/pages/TutorsPage.jsx` | Quan ly gia su | Admin | Co search, filter, add form, table; mock data |
| `/requests` | `frontend/src/pages/LearningRequestsPage.jsx` | Placeholder nhu cau hoc | Chua ro | Noi dung hien tai chi la heading tam |
| `/classes` | `frontend/src/pages/ClassesPage.jsx` | Quan ly lop hoc | Admin | Co search, filter, table; mock data |
| `/tutor-classes` | `frontend/src/pages/ClassesPage.jsx` | Lop phu trach cua tutor | Tutor | Tam thoi tro ve page admin classes, nhung logic page lai chan non-admin |
| `/tutor-schedule` | `frontend/src/pages/DashboardPage.jsx` | Lich day cua tutor | Tutor | Route tam, chua co page rieng |
| `/tutor-profile` | `frontend/src/pages/DashboardPage.jsx` | Ho so tutor | Tutor | Route tam, chua co page rieng |
| `/my-classes` | `frontend/src/pages/ClassesPage.jsx` | Lop dang hoc cua student | Student | Tam thoi tro ve page admin classes, nhung logic page lai chan non-admin |
| `/tuition` | `frontend/src/pages/DashboardPage.jsx` | Hoc phi cua student | Student | Route tam, chua co page rieng |
| `/request` | `frontend/src/pages/LearningRequestsPage.jsx` | Gui nhu cau tim gia su | Student | Dang tro den placeholder |
| `/admin/tutors` | `frontend/src/pages/TutorsPage.jsx` | Quan ly gia su | Admin | Trung voi `/tutors` |
| `/admin/requests` | `frontend/src/pages/LearningRequestsPage.jsx` | Xu ly nhu cau hoc | Admin | Placeholder, chua co nghiep vu that |
| `/admin/classes` | `frontend/src/pages/ClassesPage.jsx` | Quan ly lop hoc | Admin | Dang dung duoc o muc demo |
| `/admin/finance` | `frontend/src/pages/DashboardPage.jsx` | Tai chinh/hoc phi | Admin | Route tam, chua co page rieng |
| `/admin/students` | `frontend/src/pages/StudentList.jsx` | Quan ly hoc vien | Admin | Co search, filter, add form, table; mock data |

### Route co trong menu nhung chua duoc khai bao trong router

| Route | Xuat hien o dau | Ghi chu |
| --- | --- | --- |
| `/tim-gia-su` | `frontend/src/components/Header.jsx` | Chua co route, se 404 neu bam |
| `/dang-ky-gia-su` | `frontend/src/components/Header.jsx` | Chua co route, se 404 neu bam |
| `/gioi-thieu` | `frontend/src/components/Header.jsx` | Chua co route, se 404 neu bam |

## 3. Danh sach component chinh

| Component | File | Duoc dung o dau | Props/Du lieu nhan vao | Chuc nang |
| --- | --- | --- | --- | --- |
| `MainLayout` | `frontend/src/layouts/MainLayout.jsx` | Root layout | Khong co props; dung `useAuth()` | Hien `Header`, `Sidebar` neu da login, va `Outlet` |
| `Header` | `frontend/src/components/Header.jsx` | `MainLayout` | Khong co props; dung `useAuth`, `useModal`, `useNavigate` | Navigation theo role, login/register, fake role switch, logout |
| `Sidebar` | `frontend/src/components/common/Sidebar.jsx` | `MainLayout` khi co user | Khong co props; dung `useAuth` | Menu doc theo role |
| `Banner` | `frontend/src/components/Banner.jsx` | `DashboardPage` | Khong su dung props du da truyen tu page; dung `useAuth`, `useModal` | Hero/mini dashboard theo role, mo modal, alert dieu huong gia |
| `ClassList` | `frontend/src/components/ClassList.jsx` | `ClassListPage` | `onClassClick(cls)` | Hien card danh sach lop moi va nut dang ky nhan lop |
| `LoginForm` | `frontend/src/components/auth/LoginForm.jsx` | `ModalRenderer` trong `App.jsx` | `onClose`, `switchToRegister` | Modal login UI, chua xu ly login that |
| `RegisterForm` | `frontend/src/components/auth/RegisterForm.jsx` | `ModalRenderer` trong `App.jsx` | `onClose`, `switchToLogin` | Modal register UI, submit bang `console.log` + `alert` |
| `StudentClasses` | `frontend/src/components/student/StudentClasses.jsx` | Chua duoc gan route | Khong co props | Mock card cac lop student dang hoc |
| `StudentRequests` | `frontend/src/components/student/StudentRequests.jsx` | Chua duoc gan route | Khong co props | Mock bang nhu cau hoc cua student |
| `StudentSchedule` | `frontend/src/components/student/StudentSchedule.jsx` | Chua duoc gan route | Khong co props | Mock danh sach buoi hoc/session cua student |
| `StudentTuition` | `frontend/src/components/student/StudentTuition.jsx` | Chua duoc gan route | Khong co props | Mock danh sach hoc phi cua student |
| `Workflow` | `frontend/src/components/Workflow.jsx` | Chua duoc import vao app | Khong co props | Component gioi thieu quy trinh tutor/student |
| `Navbar` | `frontend/src/components/Navbar.jsx` | Chua duoc import vao app | `onLogout` | Header cu/demo, hien tai khong dung |
| `Footer` | `frontend/src/components/Footer.jsx` | Chua duoc import vao app | Khong co props | Footer marketing/demo, hien tai khong dung |
| `StatusBadge` | `frontend/src/components/common/StatusBadge.jsx` | Khong duoc dung | Khong co noi dung | File rong/chua hoan thien |

## 4. Du lieu hien tai trong frontend

Frontend hien tai dang dung nhieu nguon du lieu sau:

- Hard-code ngay trong JSX:
  - So lieu thong ke admin o `DashboardPage`
  - Noi dung banner, menu, text mo ta
- Mock data trong file component/page:
  - `sampleStudents`, `sampleTutors`, `sampleClasses`
  - Mang `classes`, `requests`, `sessions`, `tuitions` trong cac component student
- Local state:
  - Search/filter/form data/loading/show modal
- Context/store:
  - `AuthContext` luu `user`
  - `ModalContext` luu modal dang mo
- `localStorage`:
  - Key `user` de nho role demo
- API service / fetch / axios:
  - Chua thay bat ky API call that nao
  - Khong co `axios`, `fetch`, `services`, `api` config
- Fake async:
  - Dung `setTimeout(..., 500)` de gia lap call API trong nhieu page

| Du lieu | Nguon du lieu | File | Entity lien quan | Ghi chu |
| --- | --- | --- | --- | --- |
| User login state | `localStorage` + `AuthContext` | `frontend/src/contexts/AuthContext.jsx` | User | Gom `role`, `name`, `token` gia |
| Modal login/register | Local state trong context | `frontend/src/contexts/ModalContext.jsx` | UI state | `activeModal` = `login`/`register`/`null` |
| Admin dashboard stats | Hard-code | `frontend/src/pages/DashboardPage.jsx` | Student, Tutor, LearningRequest | 128 hoc vien, 45 gia su, 12 nhu cau cho |
| Lop moi tuyen | Mock array `sampleClasses` | `frontend/src/components/ClassList.jsx` | OpenClass/LearningRequest/Class | Dung de tutor guest xem va dang ky |
| Danh sach hoc vien | Mock array `sampleStudents` | `frontend/src/pages/StudentList.jsx` | Student | Gia lap API bang `setTimeout` |
| Danh sach gia su | Mock array `sampleTutors` | `frontend/src/pages/TutorsPage.jsx` | Tutor | Gia lap API bang `setTimeout` |
| Danh sach lop hoc | Mock array `sampleClasses` | `frontend/src/pages/ClassesPage.jsx` | Class | Gia lap API bang `setTimeout` |
| Nhu cau hoc cua student | Local state khoi tao bang hard-code | `frontend/src/components/student/StudentRequests.jsx` | LearningRequest | Chua duoc route su dung |
| Lich hoc/session cua student | Hard-code | `frontend/src/components/student/StudentSchedule.jsx` | Session | Chua duoc route su dung |
| Hoc phi cua student | Hard-code | `frontend/src/components/student/StudentTuition.jsx` | Payment/Tuition | Chua duoc route su dung |
| Lop dang hoc cua student | Hard-code | `frontend/src/components/student/StudentClasses.jsx` | Class | Chua duoc route su dung |

## 5. Cac entity/field frontend dang su dung

### User/Auth

| Field | Kieu du lieu frontend dang dung | Duoc hien thi o dau | Ghi chu |
| --- | --- | --- | --- |
| `role` | string | `Header`, `Sidebar`, `Banner`, guard trong pages | Gia tri thay ro: `student`, `tutor`, `admin` |
| `name` | string | `Header`, `Banner` | Den tu fake login |
| `token` | string | Khong hien thi | Token gia: `'fake-jwt-token'` |

### Student

| Field | Kieu du lieu frontend dang dung | Duoc hien thi o dau | Ghi chu |
| --- | --- | --- | --- |
| `id` | number | Bang `StudentList` | ID noi bo demo |
| `full_name` | string | Bang `StudentList` | Field duoc dung trong form them |
| `phone` | string | Bang `StudentList` | Co search |
| `email` | string | Bang `StudentList` | Co search |
| `area` | string | Bang `StudentList` | Khu vuc |
| `level` | string | Bang `StudentList` | Trinh do/lop hoc |
| `status` | string | Bang `StudentList` | `ACTIVE` / `INACTIVE` |

### Tutor

| Field | Kieu du lieu frontend dang dung | Duoc hien thi o dau | Ghi chu |
| --- | --- | --- | --- |
| `id` | number | Bang `TutorsPage` | ID noi bo demo |
| `full_name` | string | Bang `TutorsPage` | Dung trong search va form |
| `phone` | string | Bang `TutorsPage` | Dung trong search va form |
| `email` | string | Bang `TutorsPage` | Dung trong search va form |
| `area` | string | Bang `TutorsPage` | Khu vuc |
| `subjects` | string | Bang `TutorsPage` | Dang la chuoi, chua la array |
| `experience` | number | Bang `TutorsPage` | So nam kinh nghiem |
| `status` | string | Bang `TutorsPage` | `ACTIVE` / `INACTIVE` |

### Subject

Khong thay entity `Subject` tach rieng trong frontend hien tai.

Subject hien dang duoc bieu dien bang text nam trong:

| Field | Kieu du lieu frontend dang dung | Duoc hien thi o dau | Ghi chu |
| --- | --- | --- | --- |
| `subject` | string | `ClassList`, `ClassesPage`, `StudentRequests` | Vi du: `Toan 12`, `Tieng Anh 10` |
| `subjects` | string | `TutorsPage` | Chuoi gom nhieu mon, vi du `Toan, Ly` |
| `level` | string | `ClassList`, `ClassesPage`, `StudentList` | Dang tron voi thong tin cap lop |

### LearningRequest

Entity nay chua co page hoan chinh, nhung co mot so bieu dien dang ro:

| Field | Kieu du lieu frontend dang dung | Duoc hien thi o dau | Ghi chu |
| --- | --- | --- | --- |
| `id` | string | `StudentRequests` | Ma yeu cau, vi du `REQ001` |
| `subject` | string | `StudentRequests` | Mon hoc can tim |
| `target` | string | `StudentRequests` | Muc tieu hoc |
| `status` | string | `StudentRequests` | Vi du `Dang cho`, `Da phan cong` |
| `date` | string | `StudentRequests` | Ngay tao |

Ngoai ra, `ClassList` co du lieu co ve la nhu cau hoc da duoc mo cho tutor nhan lop:

| Field | Kieu du lieu frontend dang dung | Duoc hien thi o dau | Ghi chu |
| --- | --- | --- | --- |
| `id` | number | `ClassList` | Co the la ma lop mo/tin tuyen lop, chua ro |
| `subject` | string | `ClassList` | Mon hoc |
| `level` | string | `ClassList` | Cap lop |
| `area` | string | `ClassList` | Khu vuc hoc |
| `schedule` | string | `ClassList` | Lich hoc text |
| `salary` | string | `ClassList` | Thu lao/buoi dang text |
| `status` | string | `ClassList` | `Dang tuyen` / `Da co gia su` |

### Class

| Field | Kieu du lieu frontend dang dung | Duoc hien thi o dau | Ghi chu |
| --- | --- | --- | --- |
| `id` | number | `ClassesPage` | ID noi bo |
| `code` | string | `ClassesPage` | Ma lop, vi du `LTO-2401` |
| `student` | string | `ClassesPage` | Ten hoc vien, khong phai object |
| `studentId` | number | `ClassesPage` | Co trong mock, khong hien thi tren UI |
| `tutor` | string | `ClassesPage` | Ten gia su, khong phai object |
| `tutorId` | number | `ClassesPage` | Co trong mock, khong hien thi tren UI |
| `subject` | string | `ClassesPage` | Mon hoc |
| `level` | string | `ClassesPage` | Cap lop |
| `schedule` | string | `ClassesPage` | Lich hoc dang text |
| `fee` | number | `ClassesPage` | Hoc phi/buoi |
| `status` | string | `ClassesPage` | `ACTIVE`, `PAUSED`, `FINISHED`, `CANCELED` |
| `startDate` | string | `ClassesPage` | Co trong mock, chua hien thi |
| `endDate` | string | `ClassesPage` | Co trong mot so record, chua hien thi |
| `nextLesson` | string/null | `ClassesPage` | Co trong mock, chua hien thi |

### Schedule / Session

| Field | Kieu du lieu frontend dang dung | Duoc hien thi o dau | Ghi chu |
| --- | --- | --- | --- |
| `id` | number | `StudentSchedule` | Session id |
| `date` | string | `StudentSchedule` | Ngay hoc |
| `class` | string | `StudentSchedule` | Ten lop |
| `content` | string | `StudentSchedule` | Noi dung buoi hoc |
| `attendance` | string | `StudentSchedule` | `Co mat`, `Chua dien ra` |

### Payment / Tuition

| Field | Kieu du lieu frontend dang dung | Duoc hien thi o dau | Ghi chu |
| --- | --- | --- | --- |
| `id` | string | `StudentTuition` | Ma hoc phi |
| `className` | string | `StudentTuition` | Lop hoc lien quan |
| `amount` | string | `StudentTuition` | Dang luu chuoi da format, khong phai number |
| `period` | string | `StudentTuition` | Ky hoc phi |
| `status` | string | `StudentTuition` | `Da hoan thanh`, `Chua thanh toan` |

## 6. Cac form trong frontend

| Form | File | Dung de lam gi | Cac input | Du lieu submit |
| --- | --- | --- | --- | --- |
| Login form | `frontend/src/components/auth/LoginForm.jsx` | Dang nhap | `email`, `password` | Chua submit that, `preventDefault()` |
| Register form | `frontend/src/components/auth/RegisterForm.jsx` | Dang ky hoc vien/gia su | `fullName`, `email`, `phone`, `password`, `role` | `console.log({ fullName, email, password, phone, role })` + `alert` |
| Them hoc vien | `frontend/src/pages/StudentList.jsx` | Them hoc vien moi | `full_name`, `phone`, `email`, `area`, `level` | Them object moi vao state `students`, auto them `id`, `status: 'ACTIVE'` |
| Them gia su | `frontend/src/pages/TutorsPage.jsx` | Them gia su moi | `full_name`, `phone`, `email`, `area`, `subjects`, `experience` | Them object moi vao state `tutors`, parse `experience`, auto them `id`, `status: 'ACTIVE'` |

### Form chua thay trong frontend hien tai

- Form them/chinh sua Subject
- Form tao LearningRequest day du
- Form tao Class
- Form phan cong tutor vao class
- Form cap nhat buoi hoc/session
- Form thanh toan hoc phi
- Form cap nhat ho so tutor/student

## 7. Cac thao tac nguoi dung hien co

| Actor | Thao tac | Page/component | Du lieu lien quan | Da hoat dong hay chua |
| --- | --- | --- | --- | --- |
| Guest | Mo login modal | `Header`, `Banner`, `ClassListPage` | UI modal state | Co |
| Guest | Mo register modal | `Header`, `Banner` | UI modal state | Co |
| Guest | Xem danh sach lop moi tuyen | `/lop-moi`, `ClassList` | Mock open class data | Co |
| Guest | Bam dang ky nhan lop | `ClassListPage` | `cls.id`, `cls.subject` | Chi `alert` + mo login |
| Student | Dang ky tai khoan | `RegisterForm` | User registration fields | Chi log + alert |
| Student | Xem dashboard | `/` | Banner role student | Co |
| Student | Vao `/my-classes` | Route | Class data | Khong dung duoc do route tro den `ClassesPage` va bi chan boi admin guard |
| Student | Vao `/tuition` | Route | Tuition data | Chi tro den `DashboardPage`, chua co page hoc phi |
| Student | Vao `/request` | Route | Learning request | Chi tro den placeholder `LearningRequestsPage` |
| Tutor | Xem dashboard | `/` | Banner role tutor | Co |
| Tutor | Xem lop moi va dang ky nhan lop | `/lop-moi` | Mock class openings | Co, nhung chi alert |
| Tutor | Vao `/tutor-classes` | Route | Class data | Khong dung duoc do tro den `ClassesPage` va bi admin guard |
| Tutor | Vao `/tutor-schedule` | Route | Schedule | Tam thoi tro ve dashboard |
| Tutor | Vao `/tutor-profile` | Route | Profile | Tam thoi tro ve dashboard |
| Admin | Fake login vao role admin | `Header` | `role`, `name`, fake token | Co |
| Admin | Xem dashboard | `/` | Hard-code stats | Co |
| Admin | Tim hoc vien | `StudentList` | `searchTerm` | Co |
| Admin | Loc hoc vien theo status | `StudentList` | `statusFilter` | Co |
| Admin | Them hoc vien | `StudentList` | Student form data | Co, local state |
| Admin | Bam sua/xoa hoc vien | `StudentList` | Student row | Chua co handler |
| Admin | Tim gia su | `TutorsPage` | `searchTerm` | Co |
| Admin | Loc gia su theo status | `TutorsPage` | `statusFilter` | Co |
| Admin | Them gia su | `TutorsPage` | Tutor form data | Co, local state |
| Admin | Bam sua/xoa gia su | `TutorsPage` | Tutor row | Chua co handler |
| Admin | Tim lop hoc | `ClassesPage` | `searchTerm` | Co |
| Admin | Loc lop hoc theo status | `ClassesPage` | `statusFilter` | Co |
| Admin | Bam them lop | `ClassesPage` | Class | Chua co form/handler |
| Admin | Bam xem/sua lop | `ClassesPage` | Class row | Chua co handler |
| Admin | Vao `/admin/requests` | Route | Learning request | Page placeholder, chua xu ly |
| Admin | Vao `/admin/finance` | Route | Finance | Tro ve dashboard, chua co page rieng |

## 8. API/mock hien co

Khong thay API call that nao.

- Khong co `fetch`
- Khong co `axios`
- Khong co service layer
- Khong co endpoint backend duoc goi

### Fake async/mock dang dung

| Method | Endpoint hoac mock function | File goi | Request data | Response data frontend mong doi |
| --- | --- | --- | --- | --- |
| N/A | `setTimeout(() => setStudents(sampleStudents), 500)` | `frontend/src/pages/StudentList.jsx` | Khong co | Array Student |
| N/A | `setTimeout(() => setTutors(sampleTutors), 500)` | `frontend/src/pages/TutorsPage.jsx` | Khong co | Array Tutor |
| N/A | `setTimeout(() => setClasses(sampleClasses), 500)` | `frontend/src/pages/ClassesPage.jsx` | Khong co | Array Class |
| N/A | `setTimeout(() => setClasses(sampleClasses), 500)` | `frontend/src/components/ClassList.jsx` | Khong co | Array OpenClass/Class |
| N/A | `fakeLogin(role, name)` | `frontend/src/contexts/AuthContext.jsx`, goi tu `Header` | `role`, `name` | Object user `{ role, name, token }` |

### Mock data can phan tich ky

1. `StudentList.sampleStudents`
   - Cau truc phang, chua co thong tin guardian, ngay sinh, dia chi chi tiet, lich su dang ky.
   - `level` dang dai dien cho cap hoc/lop.

2. `TutorsPage.sampleTutors`
   - `subjects` dang la chuoi, khong tach thanh danh sach mon hoc.
   - Chua co cac field nghiep vu thuong gap nhu bang cap, lich ranh, gioi tinh, nguyen quan, verified status.

3. `ClassesPage.sampleClasses`
   - Frontend dang hinh dung `Class` gom ca `student`, `tutor`, `subject`, `schedule`, `fee`, `status`.
   - `studentId` va `tutorId` co mat nhung UI hien tai lai hien ten string, chua co relation object day du.
   - `schedule` dang la text, chua la cau truc lich hoc co the xu ly may.
   - `nextLesson` co trong mock nhung chua hien thi.

4. `ClassList.sampleClasses`
   - Co ve la lop dang mo tuyen/nhu cau hoc da duoc cong khai cho tutor.
   - Chua ro day la `LearningRequest`, `OpenClass`, hay `Class` that.
   - `salary` dang la string da format, khong phai number.

5. `StudentRequests`
   - La bieu dien gan nhat cho `LearningRequest` cua student.
   - Chua thay thong tin khu vuc, lich mong muon, hoc phi de xuat, trang thai xu ly chi tiet.

## 9. Nhung diem frontend dang thieu hoac chua ro

### Page/component chua co hoac chua hoan thien

- `LearningRequestsPage.jsx` moi la placeholder, chua co bang/list/form xu ly nhu cau hoc.
- `StudentsPage.jsx` moi la placeholder.
- Cac route tutor/student nhieu cho dang tro tam ve `DashboardPage` hoac `ClassesPage`.
- `StatusBadge.jsx` la file rong.
- `Workflow`, `Footer`, `Navbar`, nhom `components/student/*` chua duoc gan vao luong app hien tai.

### Route va phan quyen dang bat cap

- `/my-classes` va `/tutor-classes` cung tro den `ClassesPage`, nhung `ClassesPage` chan moi role khac admin, nen student/tutor vao se bi bao khong co quyen.
- Header menu guest co cac route `/tim-gia-su`, `/dang-ky-gia-su`, `/gioi-thieu` nhung router chua khai bao.
- `/tuition`, `/tutor-schedule`, `/tutor-profile`, `/admin/finance` dang tro tam ve `DashboardPage`.

### Entity/nghiep vu chua ro hoac thieu

- Chua co entity `Subject` tach rieng.
- Chua co entity `LearningRequest` du chi tiet theo nghiep vu trung tam.
- Chua co entity `Session`/`Lesson` cho gia su cap nhat noi dung da day.
- Chua co entity `Payment`/`Tuition` du cau truc cho theo doi hoc phi theo lop.
- Chua co page/du lieu cho quan ly lich hoc, phan cong gia su, tao lop hoc, theo doi buoi hoc.

### Nhung cho de gay kho khi noi backend

- Cung mot khai niem "lop" dang xuat hien o hai dang:
  - `ClassList`: lop moi tuyen/cong khai cho tutor nhan
  - `ClassesPage`: lop dang van hanh cua trung tam
  - Can xac nhan day la 2 entity khac nhau hay 2 trang thai cua cung 1 entity.
- `subjects` cua tutor dang la string, kho map voi bang `Subject` neu backend can relation nhieu-nhieu.
- `schedule` dang la string o ca `ClassList` va `ClassesPage`, chua du cau truc de quan ly lich hoc/buoi hoc.
- `amount`, `salary` co cho dang string da format, co cho dang number; can thong nhat khi noi backend.
- Role `student` dang duoc mo ta mot luc la "hoc vien / phu huynh", nhung chua co field tach guardian/student.

### Nghiep vu theo 3 actor doi chieu voi frontend hien tai

| Actor | Frontend da co | Frontend chua co/rat mo |
| --- | --- | --- |
| Nhan vien trung tam | Quan ly hoc vien, gia su, lop hoc o muc demo | Quan ly mon hoc, xu ly nhu cau hoc that, tao lop, phan cong gia su, quan ly lich hoc, buoi hoc, hoc phi |
| Gia su | Xem banner/dashboard, xem lop moi, dang ky nhan lop bang alert | Xem lop duoc phan cong that, lich day that, cap nhat session, ghi chu noi dung da day |
| Hoc vien | Dashboard role student, modal register, component nhap `StudentRequests/Classes/Tuition/Schedule` co san nhung chua gan route | Tao nhu cau hoc that, xem lop dang hoc that, xem lich hoc that, xem hoc phi that |

## 10. Goi y chuan bi cho backend sau nay

Chi o muc phan tich, chua implement:

- Backend sau nay can kha nang cap du lieu cho cac nhom page sau:
  - Dashboard theo role
  - Danh sach hoc vien
  - Danh sach gia su
  - Danh sach lop hoc dang hoat dong
  - Danh sach lop moi tuyen/nhu cau hoc cong khai cho tutor
  - Nhu cau hoc cua student
  - Lich hoc/session
  - Hoc phi theo lop

- Field frontend dang mong doi rat ro:
  - Student: `id`, `full_name`, `phone`, `email`, `area`, `level`, `status`
  - Tutor: `id`, `full_name`, `phone`, `email`, `area`, `subjects`, `experience`, `status`
  - Class: `code`, `student`, `tutor`, `subject`, `level`, `schedule`, `fee`, `status`, co the them `startDate`, `endDate`, `nextLesson`
  - LearningRequest: it nhat `id`, `subject`, `target`, `status`, `date`

- Cac endpoint co the se can, nhung hien tai frontend chua goi:
  - Auth/login/register
  - CRUD student
  - CRUD tutor
  - List/create/update class
  - List/create/update learning request
  - List schedule/session theo student/tutor/class
  - List payment/tuition theo student/class
  - Dashboard stats theo role

- Nhung diem can hoi lai team/frontend developer truoc khi lam backend:
  - `ClassList` la entity nao: learning request da duyet, open class, hay class that?
  - `student` co bao gom phu huynh hay phai tach `student` va `guardian`?
  - `subject` co can bang rieng hay chi luu text?
  - `schedule` du kien backend tra ve string hay cau truc chi tiet theo thu/gio/buoi?
  - `fee`/`salary`/`amount` can thong nhat dang number hay string format?
  - Trang thai chuan cho `LearningRequest`, `Class`, `Session`, `Payment` la gi?
  - Nhung route tutor/student placeholder se duoc giu hay se tach thanh page rieng?

