# Tự động Commit & Push Git (Git Auto Commit + Push)

Ứng dụng Python nhỏ gọn hỗ trợ tự động thực hiện chuỗi lệnh `git add .`, `git commit` và `git push` theo chu kỳ thời gian được thiết lập. 

Mục tiêu chính là chạy ổn định, mượt mà trên Windows 10/11 bằng Windows Task Scheduler, NSSM, PowerShell, `cmd.exe`, hoặc chạy trực tiếp thông qua cửa sổ dòng lệnh (console).

## 🚀 Tính năng nổi bật

- **Tự động hóa hoàn toàn**: Tự động stage (`git add .`) tất cả thay đổi trong repository được chỉ định.
- **Tối ưu hóa commit**: Chỉ tạo commit khi thực sự có thay đổi được stage (tránh spam commit trống).
- **Đẩy mã nguồn tự động**: Tự động push lên remote và branch chỉ định.
- **Hai chế độ chạy linh hoạt**:
  - Chạy lặp vô hạn theo chu kỳ cấu hình trước (qua tham số `--interval`).
  - Chạy một lần duy nhất rồi thoát (qua tham số `--once`).
- **Ghi nhận thời gian chi tiết**: Cú pháp tin nhắn commit (commit message) hỗ trợ chèn timestamp động giúp dễ dàng truy vết lịch sử.
- **Đa nền tảng**: Tương thích tốt với Windows, macOS và Linux.

---

## 🛠️ Yêu cầu hệ thống

Trước khi cài đặt, hãy đảm bảo máy tính của bạn đã có:
1. **Git**: Đã được cài đặt và cấu hình thông tin định danh (`git config --global user.name` và `git config --global user.email`). Remote Git cũng cần được cấu hình quyền push (SSH Key hoặc Credential Manager) để không bị hỏi mật khẩu khi đẩy code.
2. **Python**: Phiên bản **3.11** trở lên.
3. **Poetry**: Công cụ quản lý dependency và môi trường ảo cho Python.

---

## 📦 Hướng dẫn cài đặt chi tiết

### Bước 1: Cài đặt Poetry (nếu chưa có)

Nếu máy của bạn chưa cài đặt Poetry, bạn có thể cài đặt nhanh qua `pip` bằng cách chạy lệnh sau trong PowerShell hoặc Terminal:

```powershell
# Trên Windows (Sử dụng PowerShell hoặc cmd)
py -m pip install poetry

# Trên macOS/Linux
python3 -m pip install poetry
```

*Hoặc làm theo hướng dẫn cài đặt chính thức tại [trang chủ Poetry](https://python-poetry.org/docs/#installation).*

### Bước 2: Tải mã nguồn và cài đặt thư viện

1. Mở Terminal / PowerShell và di chuyển vào thư mục dự án `auto-commit`:
   ```bash
   cd /duong-dan/den/thu-muc/auto-commit
   ```
2. Thực hiện cài đặt các dependencies và đăng ký package cục bộ:
   ```bash
   poetry install
   ```

Lệnh trên sẽ tự động tạo môi trường ảo Python biệt lập và cài đặt gói lệnh `git-auto-commit` vào môi trường đó.

---

## 💻 Hướng dẫn sử dụng

### 1. Chạy trực tiếp từ dòng lệnh (CLI)

Sau khi cài đặt xong, bạn có thể chạy công cụ này trực tiếp bằng Poetry.

*   **Chạy lặp lại liên tục (Mặc định mỗi 60 giây):**
    ```bash
    poetry run git-auto-commit --repo /path/to/your/repo --interval 60 --branch main
    ```
*   **Chạy một lần duy nhất và thoát (Thích hợp cho cronjob tự dựng):**
    ```bash
    poetry run git-auto-commit --repo /path/to/your/repo --once
    ```
*   **Tùy chỉnh nội dung tin nhắn commit (Commit Message):**
    Bạn có thể dùng chuỗi `{timestamp}` để hệ thống tự động điền thời gian commit.
    ```bash
    poetry run git-auto-commit --repo /path/to/your/repo --message-template "Auto sync - {timestamp}"
    ```

### 2. Các tham số cấu hình khả dụng

| Tham số | Giá trị mặc định | Mô tả |
| :--- | :--- | :--- |
| `--repo` | `.` | Đường dẫn tuyệt đối hoặc tương đối tới thư mục Git repository cần theo dõi. |
| `--interval` | `60` | Thời gian chờ (tính bằng giây) giữa các chu kỳ commit khi chạy ở chế độ lặp. |
| `--remote` | `origin` | Tên của Git remote muốn đẩy code lên. |
| `--branch` | *Nhánh hiện tại* | Tên nhánh Git muốn thực hiện push. Nếu không truyền, công cụ sẽ dùng nhánh hiện tại của repository đích. |
| `--message-template`| `Auto commit {timestamp}` | Định dạng của commit message. Hỗ trợ biến `{timestamp}`. |
| `--once` | *Không có* | Chạy một lần duy nhất để đồng bộ các thay đổi hiện tại rồi kết thúc chương trình. |
| `--push-when-clean` | *Không có* | Luôn thực hiện lệnh push lên remote ngay cả khi không có commit mới được tạo ở chu kỳ này. |
| `--log-level` | `INFO` | Mức độ chi tiết của log hiển thị (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

---

## ⚙️ Cấu hình chạy nền trên Windows 10 / 11

Để công cụ này tự động chạy ẩn dưới nền mà không cần mở cửa sổ dòng lệnh, bạn có thể thiết lập thông qua Windows Task Scheduler hoặc chạy như một Service của Windows.

### Cách 1: Sử dụng PowerShell (Khuyên dùng - Nhanh nhất)

Thư mục `scripts/` chứa sẵn các script tự động hóa để giúp bạn đăng ký công việc vào Windows Task Scheduler chỉ với một câu lệnh duy nhất.

Mở PowerShell với quyền Administrator và chạy:

```powershell
# Chạy script cài đặt kèm cấu hình đường dẫn thư mục Git cần commit
.\scripts\setup_windows_auto_commit.ps1 -RepoPath "C:\duong-dan-den-repo" -Branch "master" -IntervalSeconds 60
```

Script này sẽ tự động:
1. Kiểm tra và cài đặt `poetry` (nếu máy chưa có).
2. Chạy `poetry install` để thiết lập môi trường.
3. Đăng ký một Windows Scheduled Task có tên là `GitAutoCommitPush` với trigger `At startup`, chạy `--once`, và để Task Scheduler tự lặp lại theo chu kỳ bạn cấu hình.

> [!NOTE]
> - Nếu bạn sử dụng Command Prompt (`cmd.exe`), có thể gọi file wrapper:
>   ```cmd
>   scripts\setup_windows_auto_commit.cmd -RepoPath "C:\duong-dan-den-repo" -Branch "master" -IntervalSeconds 60
>   ```
> - Nếu bạn chạy từ môi trường Git Bash trên Windows:
>   ```bash
>   ./scripts/setup_windows_auto_commit.sh --repo /path/to/target/repo --branch master --interval 60
>   ```
> - Nếu PowerShell báo lỗi phân quyền thực thi script, hãy chạy lệnh sau trước:
>   `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

### Cách 2: Đăng ký thủ công qua giao diện Windows Task Scheduler

Nếu muốn cấu hình thủ công bằng giao diện đồ họa Windows:

1. Mở **Task Scheduler** trên Windows.
2. Chọn **Create Task...** ở cột Action bên phải.
3. Ở tab **General**: Đặt tên tác vụ (ví dụ: `GitAutoCommit`).
4. Ở tab **Triggers**: Thêm trigger mới, chọn chạy **At startup** và tích chọn **Repeat task every:** `1 hour` hoặc `1 minute` tùy nhu cầu, mục **for a duration of:** chọn `Indefinitely` (vô hạn).
5. Ở tab **Actions**: Thêm Action mới loại **Start a program**:
   * **Program/script**: `poetry`
   * **Add arguments**: `run git-auto-commit --repo C:\path\to\your\repo --once --branch main`
   * **Start in**: `C:\path\to\auto-commit` (đường dẫn tới thư mục chứa mã nguồn công cụ auto-commit này, nơi có `pyproject.toml`).
6. Nhấn **OK** để lưu lại.

> [!IMPORTANT]
> Với Windows Task Scheduler, không dùng `--interval` bên trong lệnh nếu bạn đã bật `Repeat task every`. Nếu không, mỗi lần trigger sẽ tạo thêm một tiến trình `git-auto-commit` chạy lặp vô hạn và các tiến trình sẽ chồng lên nhau.

---

### Cách 3: Sử dụng NSSM để chạy như một Windows Service

Nếu bạn muốn chương trình chạy ổn định như một dịch vụ hệ thống thực sự:

1. Tải công cụ [NSSM](https://nssm.cc/) về máy.
2. Mở Command Prompt bằng quyền Admin và gõ lệnh tạo service: `nssm install GitAutoCommitService`
3. Trong bảng giao diện NSSM hiện ra, cấu hình như sau:
   * **Application path**: Đường dẫn tới file thực thi `poetry.exe` hoặc `py.exe` trên máy bạn.
   * **Startup directory**: Đường dẫn tới thư mục mã nguồn công cụ này.
   * **Arguments**:
     - Nếu dùng Poetry: `run git-auto-commit --repo C:\path\to\your\repo --interval 60 --branch main`
     - Nếu dùng Python trực tiếp: `-m poetry run git-auto-commit --repo C:\path\to\your\repo --interval 60 --branch main`
4. Chọn **Install service** để hoàn tất.

Với NSSM hoặc khi chạy trực tiếp trong console, dùng `--interval` là hợp lý vì lúc đó chính tiến trình `git-auto-commit` sẽ tự giữ vòng lặp.

---

## ⚠️ Lưu ý quan trọng

* **Xác thực Git**: Hãy chắc chắn tài khoản Git của bạn đã được cấu hình ghi nhớ thông tin đăng nhập (SSH agent hoặc Git Credential Helper). Nếu lệnh `git push` yêu cầu nhập username/password bằng tay, công cụ chạy nền sẽ bị treo hoặc báo lỗi liên tục.
* **Tần suất commit**: Nếu bạn cấu hình chu kỳ commit quá ngắn (dưới 60 giây) và dự án có nhiều file kích thước lớn hoặc thay đổi liên tục, lịch sử Git (commit history) sẽ bị phình to rất nhanh. Hãy lựa chọn chu kỳ phù hợp với nhu cầu công việc.
