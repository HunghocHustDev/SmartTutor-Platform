# Demo Accounts

Tai lieu nay di kem voi [sample_data.sql](/d:/uni/2025.2/Database/SmartTutor-Platform/sql/sample_data.sql).

Muc tieu:

- liet ke tai khoan demo theo tung actor
- chi nhanh nen dang nhap tai khoan nao de test flow nao
- giam mat thoi gian moi lan reset DB

## Cach nap du lieu

```powershell
powershell -ExecutionPolicy Bypass -File .\sql\reset_demo_utf8.ps1 -Seed sample
```

## Mat khau mac dinh

- `staff123` cho moi tai khoan `STAFF`
- `student123` cho moi tai khoan `STUDENT`
- `tutor123` cho moi tai khoan `TUTOR`

## Staff

| Vai tro | Email | Mat khau | Ghi chu |
| --- | --- | --- | --- |
| Staff | `staff1@smarttutor.local` | `staff123` | Dieu phoi vien, phu trach phan cong va lop Toan/Vat ly |
| Staff | `staff2@smarttutor.local` | `staff123` | Tu van tuyen sinh, dang giu cac assignment Van/Anh |
| Staff | `staff3@smarttutor.local` | `staff123` | Ke toan hoc phi, thuan tien test invoices/payments |

## Student

| Student ID | Ho ten | Email | Mat khau | Trang thai | Khu vuc | Lop |
| --- | --- | --- | --- | --- | --- | --- |
| `1` | Pham Gia Lam | `lam.pham@student.local` | `student123` | `ACTIVE` | Cau Giay | Lop 12 |
| `2` | Nguyen Ngoc Linh | `linh.nguyen@student.local` | `student123` | `ACTIVE` | Dong Da | Lop 11 |
| `3` | Tran Duc Minh | `minh.tran@student.local` | `student123` | `ACTIVE` | Ha Dong | Lop 10 |
| `4` | Do Hoang An | `an.do@student.local` | `student123` | `ACTIVE` | Thanh Xuan | Lop 9 |
| `5` | Le Thu Hoa | `hoa.le@student.local` | `student123` | `ACTIVE` | Nam Tu Liem | Lop 8 |
| `6` | Vo Gia Khanh | `khanh.vo@student.local` | `student123` | `ACTIVE` | Long Bien | Lop 7 |
| `7` | Bui Hong Phuc | `phuc.bui@student.local` | `student123` | `INACTIVE` | Ba Dinh | Lop 6 |

## Tutor

| Tutor ID | Ho ten | Email | Mat khau | Trang thai | Chuyen mon chinh |
| --- | --- | --- | --- | --- | --- |
| `1` | Ngo Quoc Bao | `bao.ngo@tutor.local` | `tutor123` | `ACTIVE` | Toan 12, Toan 10, Toan 7 |
| `2` | Pham Khanh Trang | `trang.pham@tutor.local` | `tutor123` | `ACTIVE` | Tieng Anh 8, Tieng Anh 11 |
| `3` | Hoang Duc Vu | `vu.hoang@tutor.local` | `tutor123` | `ACTIVE` | Vat ly 10, Vat ly 12 |
| `4` | Nguyen Thu Mai | `mai.nguyen@tutor.local` | `tutor123` | `ACTIVE` | Ngu van 9, Ngu van 12 |
| `5` | Do My Linh | `linh.do@tutor.local` | `tutor123` | `PAUSED` | Hoa hoc 11 |
| `6` | Trinh Hai Quan | `quan.trinh@tutor.local` | `tutor123` | `ACTIVE` | Tieng Anh 8, Tieng Anh 11 |
| `7` | Vu Phuong Anh | `anh.vu@tutor.local` | `tutor123` | `INACTIVE` | Sinh hoc 12 |

## Request / Assignment / Class Map

| Request | Student | Subject | Request status | Assignment | Tutor | Class | Class status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `1` | `1` Pham Gia Lam | Toan 12 | `ASSIGNED` | `1` | `1` Ngo Quoc Bao | `1` `CLS-TOAN12-001` | `ACTIVE` |
| `2` | `3` Tran Duc Minh | Vat ly 10 | `ASSIGNED` | `2` | `3` Hoang Duc Vu | `2` `CLS-LY10-001` | `ACTIVE` |
| `3` | `4` Do Hoang An | Ngu van 9 | `ASSIGNED` | `3` | `4` Nguyen Thu Mai | `3` `CLS-VAN9-001` | `COMPLETED` |
| `4` | `2` Nguyen Ngoc Linh | Tieng Anh 11 | `ASSIGNED` | `4` | `2` Pham Khanh Trang | `4` `CLS-ENG11-001` | `ACTIVE` |
| `5` | `5` Le Thu Hoa | Tieng Anh 8 | `ASSIGNED` | `5` | `6` Trinh Hai Quan | `5` `CLS-ENG8-001` | `ACTIVE` |
| `6` | `6` Vo Gia Khanh | Toan 7 | `ASSIGNED` | `6` | `1` Ngo Quoc Bao | `6` `CLS-TOAN7-001` | `ACTIVE` |
| `7` | `2` Nguyen Ngoc Linh | Hoa hoc 11 | `PENDING` | - | - | - | - |
| `8` | `3` Tran Duc Minh | Vat ly 12 | `PENDING` | - | - | - | - |
| `9` | `4` Do Hoang An | Lich su 11 | `PENDING` | - | - | - | - |
| `10` | `5` Le Thu Hoa | Tin hoc 10 | `PENDING` | - | - | - | - |
| `11` | `6` Vo Gia Khanh | Dia ly 12 | `CANCELED` | - | - | - | - |
| `12` | `1` Pham Gia Lam | Toan 10 | `PENDING` | - | - | - | - |

## Flow test goi y

### 1. Test staff xu ly nhu cau

Dang nhap:

- `staff1@smarttutor.local`

Nen thay:

- request `7`, `8`, `9`, `10`, `12` dang `PENDING`
- request `1..6` da duoc phan cong
- co the vao `/staff/assignments`, `/staff/classes`, `/staff/schedules`, `/staff/sessions`, `/staff/finance`

Muc tieu test:

- xem danh sach nhu cau
- tao assignment moi tu request pending
- mo class tu assignment
- tao schedule va session

### 2. Test student co lop dang hoc + hoc phi

Dang nhap:

- `lam.pham@student.local`

Nen thay:

- request `1` da `ASSIGNED`
- request `12` dang `PENDING`
- class `CLS-TOAN12-001`
- invoices:
  - invoice `1` da `PAID`
  - invoice `2` dang `PARTIALLY_PAID`

Muc tieu test:

- student view request list
- student view my classes
- student view tuition / payment history

### 3. Test student co request pending nhung chua co class

Dang nhap:

- `linh.nguyen@student.local`

Nen thay:

- request `4` da thanh class `CLS-ENG11-001`
- request `7` dang `PENDING`
- co ca trang thai "da co lop" va "dang cho xu ly"

### 4. Test student chi co lop online

Dang nhap:

- `hoa.le@student.local`

Nen thay:

- class `CLS-ENG8-001`
- invoice `6` dang `PARTIALLY_PAID`
- co 1 payment thanh cong va van con cong no

### 5. Test tutor co nhieu lop

Dang nhap:

- `bao.ngo@tutor.local`

Nen thay:

- class `CLS-TOAN12-001`
- class `CLS-TOAN7-001`
- session da hoc va session sap toi

Muc tieu test:

- tutor xem dashboard / lop phu trach
- tutor cap nhat status buoi hoc cua lop minh
- tutor cap nhat capability va availability

### 6. Test tutor online tieng Anh

Dang nhap:

- `trang.pham@tutor.local`

Nen thay:

- class `CLS-ENG11-001`
- sessions online

### 7. Test tutor paused / inactive

Dang nhap:

- `linh.do@tutor.local` -> `PAUSED`
- `anh.vu@tutor.local` -> `INACTIVE`

Muc tieu test:

- kiem tra UI ho so van doc duoc
- kiem tra staff khong nen phan cong request moi cho tutor khong active

### 8. Test completed class

Dang nhap:

- `an.do@student.local`
- hoac `mai.nguyen@tutor.local`

Nen thay:

- class `CLS-VAN9-001`
- class status `COMPLETED`
- invoice da thanh toan du

### 9. Test ke toan hoc phi

Dang nhap:

- `staff3@smarttutor.local`

Nen thay:

- invoice `7` dang `UNPAID`
- invoice `2`, `6` dang `PARTIALLY_PAID`
- payment co ca `SUCCESS` va `REFUNDED`

Muc tieu test:

- loc invoices theo status
- tao payment moi
- cap nhat / huy payment
- quan sat trigger cap nhat lai invoice

## API sanity checks goi y

Sau khi reset sample data, co the test nhanh:

```text
POST /auth/login
GET /subjects
GET /learning-requests
GET /classes
GET /sessions
GET /invoices
GET /payments
GET /dashboard/summary
```

Luu y:

- Cac endpoint business tren khong con la public sanity check.
- Can dang nhap truoc va gui header:

```text
Authorization: Bearer <token>
```

## Ghi chu

- Tai khoan `STUDENT` va `TUTOR` la tai khoan demo public de test UI.
- `STAFF` moi la actor van hanh trung tam.
- `ADMIN` khong nam trong bo seed nay vi nghiep vu hien tai da chuan hoa ve `STAFF`.
