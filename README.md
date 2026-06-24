# Git Auto Commit + Push

Ung dung Python nho gon de tu dong `git add .`, `git commit`, va `git push` theo chu ky. Muc tieu la chay tot tren Windows 10/11 bang Task Scheduler, NSSM, PowerShell, `cmd.exe`, hoac chay truc tiep trong console.

## Tinh nang

- Tu dong stage moi thay doi trong repo
- Chi commit khi thuc su co thay doi da duoc stage
- Tu dong push len remote/branch chi dinh
- Ho tro che do chay 1 lan hoac lap vo han theo `--interval`
- Commit message co timestamp de de truy vet

## Yeu cau

- Git da cai va repo da co remote push hop le
- Python 3.11+
- Poetry
- Windows Task Scheduler neu muon chay nen theo chu ky

## Cai dat

```bash
poetry install
```

Neu may chua co Poetry:

```powershell
py -m pip install poetry
```

## Su dung

Chay lien tuc moi 60 giay:

```bash
poetry run git-auto-commit --repo . --interval 60 --branch main
```

Chay 1 lan:

```bash
poetry run git-auto-commit --repo . --once
```

Tuy chinh message:

```bash
poetry run git-auto-commit --repo . --message-template "Auto sync {timestamp}"
```

## Windows 10

### Cach 1: Task Scheduler

#### Cach nhanh nhat: PowerShell

Chay script setup native:

```powershell
.\scripts\setup_windows_auto_commit.ps1 -RepoPath C:\path\to\repo -Branch main -IntervalSeconds 60
```

Script nay se:

- cai `poetry` neu may chua co
- chay `poetry install`
- dang ky Windows Scheduled Task

Neu ban dung `cmd.exe`, co the chay wrapper:

```bat
scripts\setup_windows_auto_commit.cmd -RepoPath C:\path\to\repo -Branch main -IntervalSeconds 60
```

#### Dang ky thu cong

1. Cai Python va Poetry tren may Windows.
2. Chay `poetry install` trong repo.
3. Tao Scheduled Task voi action.

Program/script:

```text
poetry
```

Add arguments:

```text
run git-auto-commit --repo C:\path\to\repo --interval 60 --branch main
```

Start in:

```text
C:\path\to\repo
```

Luu y:

- `-IntervalSeconds` toi thieu la `60`
- PowerShell co the can `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` neu bi chan script local
- Task Scheduler nen chay bang user co quyen push repo do

Neu ban dung Git Bash tren Windows, co the chay mot lenh de cai dependency va dang ky task:

```bash
./scripts/setup_windows_auto_commit.sh
```

Co the tuy chinh qua env var:

```bash
TASK_NAME=GitAutoCommitPush BRANCH=main REMOTE=origin INTERVAL_SECONDS=60 ./scripts/setup_windows_auto_commit.sh
```

### Cach 2: NSSM

Neu muon chay nhu Windows Service, tao service tro den:

- Application: duong dan toi `poetry.exe` hoac `py.exe`
- Arguments:
  - voi Poetry executable: `run git-auto-commit --repo C:\path\to\repo --interval 60 --branch main`
  - voi Python launcher: `-m poetry run git-auto-commit --repo C:\path\to\repo --interval 60 --branch main`
- Startup directory: `C:\path\to\repo`

## Luu y

- May can duoc cau hinh Git credentials truoc khi tu dong push.
- Nhanh gon nhung khong phu hop neu ban can review thu cong truoc moi commit.
- Neu repo co file lon hoac binary thay doi lien tuc, commit tu dong se tao lich su rat day.
