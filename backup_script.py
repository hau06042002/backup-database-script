import os
import shutil
import schedule
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
import time

# Load thông tin từ file .env
load_dotenv()
SENDER_EMAIL = os.getenv("sender_email").strip()
SENDER_PASSWORD = os.getenv("app_password").strip()
RECEIVER_EMAIL = os.getenv("receiver_email").strip()

# Thư mục chứa file database và thư mục backup
DATABASE_DIR = "./"
BACKUP_DIR = "./backup/"

# Hàm gửi email
def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("✅ Email đã được gửi thành công!")
    except Exception as e:
        print(f"❌ Lỗi khi gửi email: {e}")

# Hàm backup file database
def backup_database():
    try:
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)

        files = [f for f in os.listdir(DATABASE_DIR) if f.endswith((".sql", ".sqlite3"))]
        if not files:
            raise Exception("Không tìm thấy file database nào để backup.")

        for file in files:
            src = os.path.join(DATABASE_DIR, file)
            dst = os.path.join(BACKUP_DIR, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file}")
            shutil.copy2(src, dst)

        send_email("Backup Thành Công", f"Backup các file sau thành công: {', '.join(files)}")
        print(f"✅ Backup thành công: {', '.join(files)}")
    except Exception as e:
        send_email("Backup Thất Bại", f"Lỗi khi backup: {e}")
        print(f"❌ Lỗi khi backup: {e}")

# Lên lịch backup
schedule.every().day.at("0:00").do(backup_database)  
schedule.every().day.at("12:00").do(backup_database) 

# Vòng lặp kiểm tra lịch
print("🔄 Đang chạy lịch trình backup...")
while True:
    schedule.run_pending()
    time.sleep(1)