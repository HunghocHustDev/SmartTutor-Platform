# Demo Accounts & Seed Data Reference

Tai lieu nay mo ta du lieu hien tai trong `TutorCenterDB`, duoc tao boi:
- `sql/schema.sql` + `sql/sample_data.sql` (seed chinh)
- `sql/seed_test_request_25.sql` (seed goi y gia su cho request #25)

## Cach nap lai tu dau

```powershell
# 1. Reset schema + sample data
powershell -ExecutionPolicy Bypass -File .\sql\reset_demo_utf8.ps1 -Seed sample

# 2. (Tuy chon) seed goi y gia su cho request #25
sqlcmd ... -i .\sql\seed_test_request_25.sql
```

## Mat khau mac dinh

| Role   | Mat khau |
|--------|----------|
| STAFF  | `staff123` |
| STUDENT| `student123` |
| TUTOR  | `tutor123` |

> Vi du: `staff1@smarttutor.local` / `staff123` login duoc vao role `STAFF`.

## Staff

| ID  | Ho ten         | Email                          | Mat khau | Ghi chu |
|-----|----------------|--------------------------------|----------|---------|
| 1   | Trần Thu Hà    | `staff1@smarttutor.local`      | `staff123` | Dieu phoi vien chinh, test flow phan cong chinh |
| 2   | Lê Minh Quân   | `staff2@smarttutor.local`      | `staff123` | Tu van tuyen sinh |
| 3   | Nguyễn Hoài Nam| `staff3@smarttutor.local`      | `staff123` | Ke toan hoc phi, test invoices/payments |
| 12  | Nhân viên Seed 1 | `staff_seed_1@test.local`   | `staff123` | Seed data (bo sung) |
| 13  | Nhân viên Seed 2 | `staff_seed_2@test.local`   | `staff123` | Seed data |
| 14  | Nhân viên Seed 3 | `staff_seed_3@test.local`   | `staff123` | Seed data |
| 15-21 | Nhân viên Seed 4-10 | `staff_seed_4..10@test.local` | `staff123` | Seed data |

> Tong: 13 staff. Dung `staff1` cho flow chinh, `staff3` cho flow tai chinh.

## Student

| ID  | Ho ten               | Email                          | Mat khau | Trang thai | Khu vuc   | Lop    |
|-----|----------------------|--------------------------------|----------|------------|-----------|--------|
| 1   | Phạm Gia Lâm         | `lam.pham@student.local`       | `student123` | ACTIVE | Cầu Giấy | Lớp 12 |
| 2   | Nguyễn Ngọc Linh     | `linh.nguyen@student.local`    | `student123` | ACTIVE | Đống Đa | Lớp 11 |
| 3   | Trần Đức Minh        | `minh.tran@student.local`      | `student123` | ACTIVE | Hà Đông | Lớp 10 |
| 4   | Đỗ Hoàng An          | `an.do@student.local`          | `student123` | ACTIVE | Thanh Xuân | Lớp 9 |
| 5   | Lê Thu Hòa           | `hoa.le@student.local`         | `student123` | ACTIVE | Nam Từ Liêm | Lớp 8 |
| 6   | Võ Gia Khánh         | `khanh.vo@student.local`       | `student123` | ACTIVE | Long Biên | Lớp 7 |
| 7   | Bùi Hồng Phúc        | `phuc.bui@student.local`       | `student123` | INACTIVE | Ba Đình | Lớp 6 |
| 8-15 | HTTP Smoke / Seed   | `http-*-20260615-*@example.com` | `student123` | mix | Go Vap | - |
| 37-56 | Học viên Seed 1-20 | `student_seed_1..20@test.local` | `student123` | ACTIVE | Diverse | Diverse |

> Tong: 56 students. Student `#7` la INACTIVE de test soft-delete.
> Cac student `#8-15` la test artifact tu `http_crud_smoke.py`.
> Seed `#37-56` la du lieu random de test pagination / list.

## Tutor

| ID  | Ho ten               | Email                          | Mat khau | Trang thai | Khu vuc       | KN (nam) |
|-----|----------------------|--------------------------------|----------|------------|---------------|----------|
| 1   | Ngô Quốc Bảo         | `bao.ngo@tutor.local`          | `tutor123` | ACTIVE | Cầu Giấy | 5 |
| 2   | Phạm Khánh Trang     | `trang.pham@tutor.local`       | `tutor123` | ACTIVE | Đống Đa | 4 |
| 3   | Hoàng Đức Vũ         | `vu.hoang@tutor.local`         | `tutor123` | ACTIVE | Hà Đông | 3 |
| 4   | Nguyễn Thu Mai       | `mai.nguyen@tutor.local`       | `tutor123` | ACTIVE | Thanh Xuân | 6 |
| 5   | Đỗ Mỹ Linh           | `linh.do@tutor.local`          | `tutor123` | PAUSED | Nam Từ Liêm | 2 |
| 6   | Trịnh Hải Quân       | `quan.trinh@tutor.local`       | `tutor123` | ACTIVE | Long Biên | 7 |
| 7   | Vũ Phương Anh        | `anh.vu@tutor.local`           | `tutor123` | INACTIVE | Ba Đình | 1 |
| 8-11 | HTTP Tutor smoke    | `http-tutor-20260615-*@example.com` | `tutor123` | INACTIVE | Phu Nhuan | 4 |
| 901 | Lê Minh Anh          | `tutor901@smarttutor.local`    | `tutor123` | ACTIVE | Cầu Giấy | 5 |
| 902 | Phạm Quốc Đạt        | `tutor902@smarttutor.local`    | `tutor123` | ACTIVE | Cầu Giấy | 8 |
| 924-942 | Gia sư Seed 1-19 | `tutor_seed_1..19@test.local` | `tutor123` | mix | Diverse | 1-15 |

> Tong: 42 tutors.
> - Tutor `#5` (PAUSED) va `#7` (INACTIVE) de test gioi han phan cong.
> - Tutor `#901`, `#902` chi ton tai neu da chay `sql/seed_test_request_25.sql`.
> - Seed tutors `#924-942` co status mix (ACTIVE/PAUSED/INACTIVE).

## Subject

73 mon hoc duoc seed (ID 1-73), bao gom:

| ID  | Mon               | Trinh do     | Trang thai |
|-----|-------------------|--------------|------------|
| 1   | Toán              | Lớp 12       | ACTIVE |
| 2   | Toán              | Lớp 10       | ACTIVE |
| 3   | Vật lý            | Lớp 10       | ACTIVE |
| 4   | Vật lý            | Lớp 12       | ACTIVE |
| 5   | Hóa học           | Lớp 11       | ACTIVE |
| 6   | Ngữ văn           | Lớp 9        | ACTIVE |
| 7   | Ngữ văn           | Lớp 12       | ACTIVE |
| 8   | Tiếng Anh         | Lớp 8        | ACTIVE |
| 9   | Tiếng Anh         | Lớp 11       | ACTIVE |
| 10  | Sinh học          | Lớp 12       | ACTIVE |
| 11  | Tin học           | Lớp 10       | ACTIVE |
| 12  | Lịch sử           | Lớp 11       | ACTIVE |
| 13  | Địa lý            | Lớp 12       | ACTIVE |
| 14  | Toán              | Lớp 7        | ACTIVE |
| 15  | Tiếng Anh         | Lớp 6        | INACTIVE |
| 16-73 | Seed subjects (random) | Diverse | mix |

> Tong: 73 subjects. ID 15 la INACTIVE de test filter.

## Learning Request / Assignment / Class Map

### Requests 1-12 (seed chinh tu sample_data.sql)

| Request | Student | Subject             | Request status | Assignment | Tutor         | Class              | Class status |
|---------|---------|---------------------|----------------|------------|---------------|--------------------|--------------|
| 1       | 1       | Toán Lớp 12 (ID 1)  | ASSIGNED       | 1          | 1 Ngô Quốc Bảo | 1 `CLS-TOAN12-001` | ACTIVE |
| 2       | 3       | Vật lý Lớp 10 (ID 3) | ASSIGNED       | 2          | 3 Hoàng Đức Vũ | 2 `CLS-LY10-001` | ACTIVE |
| 3       | 4       | Ngữ văn Lớp 9 (ID 6) | ASSIGNED       | 3          | 4 Nguyễn Thu Mai | 3 `CLS-VAN9-001` | COMPLETED |
| 4       | 2       | Tiếng Anh Lớp 11 (ID 9) | ASSIGNED     | 4          | 2 Phạm Khánh Trang | 4 `CLS-ENG11-001` | ACTIVE |
| 5       | 5       | Tiếng Anh Lớp 8 (ID 8) | ASSIGNED       | 5          | 6 Trịnh Hải Quân | 5 `CLS-ENG8-001` | ACTIVE |
| 6       | 6       | Toán Lớp 7 (ID 14)  | ASSIGNED       | 6          | 1 Ngô Quốc Bảo | 6 `CLS-TOAN7-001` | ACTIVE |
| 7       | 2       | Hóa học Lớp 11 (ID 5) | PENDING        | -          | -             | -                  | - |
| 8       | 3       | Vật lý Lớp 12 (ID 4) | PENDING        | -          | -             | -                  | - |
| 9       | 4       | Lịch sử Lớp 11 (ID 12) | PENDING       | -          | -             | -                  | - |
| 10      | 5       | Tin học Lớp 10 (ID 11) | PENDING       | -          | -             | -                  | - |
| 11      | 6       | Địa lý Lớp 12 (ID 13) | CANCELED       | -          | -             | -                  | - |
| 12      | 1       | Toán Lớp 10 (ID 2)  | ASSIGNED       | 7          | 1 Ngô Quốc Bảo | 7 `CLS-LIVE-VERIFY-001` | ACTIVE |

### Requests 13-24 (HTTP smoke artifacts, CANCELED hoặc PENDING)

| Request | Student (HTTP)      | Subject                              | Status    | Assignment | Tutor (HTTP)            | Class       | Class status |
|---------|---------------------|--------------------------------------|-----------|------------|-------------------------|-------------|--------------|
| 13-14   | #8 HTTP Smoke       | HTTP Subject 20260615-954961 Lớp 12  | CANCELED  | 8          | #8 HTTP Tutor           | 8 `CLS-0008` | CANCELED |
| 15      | #8 HTTP Smoke       | HTTP Subject 20260615-954961 Lớp 12  | PENDING   | -          | -                       | -           | - |
| 16-17   | #10 HTTP Smoke      | HTTP Subject 20260615-423975 Lớp 12  | CANCELED  | 10         | #9 HTTP Tutor           | 9 `CLS-0010` | CANCELED |
| 18      | #10 HTTP Smoke      | HTTP Subject 20260615-423975 Lớp 12  | PENDING   | -          | -                       | -           | - |
| 19-20   | #12 HTTP Smoke      | HTTP Subject 20260615-291921 Lớp 12  | CANCELED  | 12         | #10 HTTP Tutor          | 10 `CLS-0012` | CANCELED |
| 21      | #12 HTTP Smoke      | HTTP Subject 20260615-291921 Lớp 12  | PENDING   | -          | -                       | -           | - |
| 22-23   | #14 HTTP Smoke      | HTTP Subject 20260615-609172 Lớp 12  | CANCELED  | 14         | #11 HTTP Tutor          | 11 `CLS-0014` | CANCELED |
| 24      | #14 HTTP Smoke      | HTTP Subject 20260615-609172 Lớp 12  | PENDING   | -          | -                       | -           | - |

### Request 25 (test suggested-tutors, da duoc assign)

| Request | Student | Subject        | Status    | Assignment | Tutor     | Class               |
|---------|---------|----------------|-----------|------------|-----------|---------------------|
| 25      | 1       | Tiếng Anh Lớp 11 (ID 9) | ASSIGNED | 16 | 901 Lê Minh Anh | `CLS-SEED-0016` ACTIVE |

> Request 25 luc dau la PENDING de test modal goi y, sau khi chay seed_final.py da thanh ASSIGNED.

### Requests 76-125 (seed bo sung)

50 learning requests random (ID 76-125) voi:
- Student: chon ngau nhien tu pool student seed (ID 37-56)
- Subject: chon ngau nhien tu 73 mon hoc
- Status: PENDING / ASSIGNED / CANCELED (ngau nhien)
- Tutor assignments: 50 assignments (ID 75-124), nhieu cai da ASSIGNED

### Requests #122 va #124 (kịch bản test goi y)

Day la 2 request duoc setup san de test flow goi y + phan cong.

| Request | Mon | Khu vuc | Hinh thuc | Lich | Trang thai |
|---------|-----|---------|-----------|------|------------|
| 122 | Vat ly Lop 10 (ID 3) | Ha Dong | OFFLINE | T2 19:00-20:30 | PENDING |
| 124 | Vat ly Lop 10 (ID 3) | Go Vap | OFFLINE | CN 13:00-16:00 | PENDING |

Tutors goi y:

| Request | Tutor | Khu vuc | KN | Score | Ghi chu |
|---------|-------|---------|----|----|---------|
| 122 | #949 Gia su Vat ly Ha Dong (BOTH) | Ha Dong | 8 nam | 120 | Top match — cung khu vuc, T2 trung lich |
| 122 | #944-948 Gia su Vat ly Go Vap 1-5 | Go Vap | 6-7 nam | 60-90 | Ca 5 tutors deu match |
| 124 | #944 Gia su Vat ly Go Vap 1 | Go Vap | 7 nam | 110 | Top — cung khu vuc, CN trung lich |
| 124 | #948 Gia su Vat ly Go Vap 5 | Go Vap | 7 nam | 110 | Top — cung khu vuc |
| 124 | #945-947 Gia su Go Vap 2-4 | Go Vap | 6 nam | 100 | Ca 3 deu match |

Cach test:
1. Dang nhap `staff1@smarttutor.local`
2. Mo trang danh sach nhu cau
3. Loc PENDING, chon request #122 hoac #124
4. Bam nut **"Goi y gia su"**
5. Modal hien thi tutors, bam **"Phan cong"** chon tutor muon assign

### Study Classes (seed)

| Class ID | Assignment | Class code        | Teaching mode | Status  |
|----------|------------|-------------------|---------------|---------|
| 21-70    | 67-116     | `CLS-SEED-XXXX`   | OFFLINE/ONLINE | mix (ACTIVE/PAUSED/COMPLETED/CANCELED) |

> 50 seed classes. Day la nhung class tu assignments seed_final.py tao ra.

### Class Schedules, Sessions, Invoices, Payments

- **CLASS_SCHEDULE**: 64 rows (schedule_id 15-64), 50 cai la seed
- **LESSON_SESSION**: 50+ rows, session_id 50-99 la seed
- **TUITION_INVOICE**: 66 rows, invoice_id 17-66 la seed
- **TUITION_PAYMENT**: 66 rows, payment_id 17-66 la seed

## Flow test goi y

### 1. Test staff xu ly nhu cau chinh

Dang nhap: `staff1@smarttutor.local`

Nen thay:
- Request `7`, `8`, `9`, `10` dang `PENDING` (request goc)
- Requests `76-125` co nhieu cai `PENDING` de test
- Assignment `16` da assign tutor `#901` cho request `25`
- 50+ classes dang hoat dong (`CLS-SEED-XXXX`)
- Vao `/staff/assignments` de xem danh sach phan cong + goi y gia su

### 2. Test staff goi y gia su (suggested-tutors)

Dang nhap: `staff1@smarttutor.local`

Chay `sql/seed_test_request_25.sql` de co tutor 901/902 (neu chua co):

```powershell
sqlcmd -b -S localhost -d TutorCenterDB -U sa -P 123456 -C -f 65001 -i sql/seed_test_request_25.sql
```

API test:
```bash
curl -H "Authorization: Bearer <staff_token>" \
     http://127.0.0.1:8000/learning-requests/25/suggested-tutors
```

Nen thay 2 goi y:
- `902` Phạm Quốc Đạt - score 100, 8 nam KN
- `901` Lê Minh Anh - score 90, 5 nam KN, khu vuc Cầu Giấy

### 3. Test student xem lop va hoc phi

Dang nhap: `lam.pham@student.local`

Nen thay:
- Request `1` da `ASSIGNED` → class `CLS-TOAN12-001`
- Request `12` da `ASSIGNED` → class `CLS-LIVE-VERIFY-001`
- Invoice da `PAID` hoac `PARTIALLY_PAID`
- 50+ classes trong danh sach lop cua student

### 4. Test tutor co nhieu lop

Dang nhap: `bao.ngo@tutor.local`

Nen thay:
- Class `CLS-TOAN12-001`, `CLS-TOAN7-001`, `CLS-LIVE-VERIFY-001`
- 50+ session tu seed
- Capability va availability day du

### 5. Test ke toan hoc phi

Dang nhap: `staff3@smarttutor.local`

Nen thay:
- 66 invoices (invoice_id 1-66), nhieu cai `UNPAID`, `PARTIALLY_PAID`, `PAID`
- 66 payments voi cac status: SUCCESS, CANCELED, REFUNDED
- Trigger tu dong cap nhat `amount_paid` va `status` khi them payment

## API sanity checks

```text
POST /auth/login
GET /subjects                  → 73 subjects
GET /learning-requests         → 125 requests
GET /classes                   → 63 classes
GET /sessions                  → 50+ sessions
GET /invoices                  → 66 invoices
GET /payments                  → 66 payments
GET /dashboard/summary
GET /learning-requests/25/suggested-tutors
```

## Ghi chu

- Du lieu seed (`#37+` students, `#924+` tutors, `#76+` requests) la du lieu ngau nhien, khong co meaning nhat dinh — chi de test pagination, filter, va volume.
- Cac request `13-24` va tutor/student co tien to `HTTP` la test artifact tu `backend/tests/http_crud_smoke.py`.
- Tutor `#901`, `#902` chi ton tai neu da chay `sql/seed_test_request_25.sql`.
- `ADMIN` khong nam trong bo seed — nghiep vu da chuan hoa ve `STAFF`.
