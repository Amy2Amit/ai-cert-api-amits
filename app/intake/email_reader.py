import imaplib
import email
import os
from email.header import decode_header
from dotenv import load_dotenv

# -----------------------------
# LOAD ENV VARIABLES
# -----------------------------
load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", 993))
DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", "downloadcertificates/download/")

TARGET_KEYWORD = "acord25"   # 🔥 flexible match
MAX_EMAILS = 30


def decode_mime_words(s):
    """Decode MIME-encoded email headers"""
    decoded_fragments = decode_header(s)
    return ''.join(
        fragment.decode(encoding or "utf-8") if isinstance(fragment, bytes) else fragment
        for fragment, encoding in decoded_fragments
    )


def fetch_email_attachments():
    print("\n📡 Connecting to email server...")

    if not EMAIL or not PASSWORD:
        print("❌ EMAIL or PASSWORD not set in .env")
        return []

    try:
        # -----------------------------
        # CONNECT TO EMAIL
        # -----------------------------
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL.strip(), PASSWORD.strip())
        mail.select("inbox")
        print("✅ Connected to inbox")

        # -----------------------------
        # FETCH EMAILS
        # -----------------------------
        status, messages = mail.search(None, "ALL")
        if status != "OK" or not messages[0]:
            print("📧 No emails found")
            mail.logout()
            return []

        email_ids = messages[0].split()[-MAX_EMAILS:]
        print(f"📧 Checking {len(email_ids)} recent emails...")

        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

        # -----------------------------
        # PROCESS EMAILS (LATEST FIRST)
        # -----------------------------
        for num in reversed(email_ids):
            status, data = mail.fetch(num, "(RFC822)")
            if status != "OK":
                continue

            msg = email.message_from_bytes(data[0][1])

            # -----------------------------
            # CHECK ATTACHMENTS
            # -----------------------------
            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue

                filename_raw = part.get_filename()
                if not filename_raw:
                    continue

                filename = decode_mime_words(filename_raw).strip()

                # 🔍 DEBUG - see all attachments
                print(f"📎 Found attachment: {filename}")

                # -----------------------------
                # FLEXIBLE MATCHING
                # -----------------------------
                if TARGET_KEYWORD in filename.lower() and filename.lower().endswith(".pdf"):

                    filepath = os.path.join(DOWNLOAD_FOLDER, filename)

                    # avoid overwrite
                    counter = 1
                    base, ext = os.path.splitext(filename)
                    while os.path.exists(filepath):
                        filepath = os.path.join(DOWNLOAD_FOLDER, f"{base}_{counter}{ext}")
                        counter += 1

                    # -----------------------------
                    # SAVE FILE
                    # -----------------------------
                    with open(filepath, "wb") as f:
                        f.write(part.get_payload(decode=True))

                    print(f"✅ ACORD25 PDF downloaded: {filepath}")

                    # -----------------------------
                    # CLEAN EXIT (IMPORTANT)
                    # -----------------------------
                    mail.logout()
                    return [filepath]

        # -----------------------------
        # IF NOT FOUND
        # -----------------------------
        print("⏭️ No ACORD25 PDF found in recent emails")
        mail.logout()
        return []

    except Exception as e:
        print(f"❌ Error fetching emails: {e}")
        return []


# -----------------------------
# STANDALONE TEST
# -----------------------------
if __name__ == "__main__":
    fetch_email_attachments()