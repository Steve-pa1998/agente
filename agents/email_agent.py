import imaplib, email, smtplib, json, os, requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

def load_env():
    env = {}
    for line in (Path(__file__).parent.parent / ".env").read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env

env = load_env()
EMAIL = env["EMAIL"]
APP_PASS = env["EMAIL_APP_PASS"]
GROQ_KEY = env.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

INBOX_DIR = Path(__file__).parent.parent / "leads" / "emails"
INBOX_DIR.mkdir(parents=True, exist_ok=True)

def connect():
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, APP_PASS)
    mail.select("INBOX")
    return mail

def get_unread(mail):
    status, data = mail.search(None, "UNSEEN")
    ids = data[0].split()
    out = []
    for id_ in ids:
        status, msg_data = mail.fetch(id_, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    break
        else:
            p = msg.get_payload(decode=True)
            if p: body = p.decode("utf-8", errors="ignore")
        out.append({"id": id_.decode(), "from": str(msg["From"]), "subject": str(msg["Subject"]), "date": str(msg["Date"]), "body": body})
    return out

def classify(e):
    if not GROQ_KEY:
        return {"action": "flag", "priority": "media", "reply": None}
    prompt = f"""Clasifica este email para Steve (freelancer, scraping, CDMX).
Responde SOLO en JSON:
{{"action": "reply"|"flag"|"ignore", "priority": "alta"|"media"|"baja", "reply": "texto o null"}}
De: {e['from']}
Asunto: {e['subject']}
Cuerpo: {e['body'][:500]}"""
    try:
        r = requests.post(GROQ_URL, headers={"Authorization": f"Bearer {GROQ_KEY}"},
            json={"model": "openai/gpt-oss-120b", "messages": [{"role":"user","content":prompt}]}, timeout=30)
        return json.loads(r.json()["choices"][0]["message"]["content"])
    except Exception as ex:
        print(f"  ⚠️ Groq: {ex}")
        return {"action": "flag", "priority": "media", "reply": None}

def send_reply(to, subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = to
    msg["Subject"] = f"Re: {subject}"
    msg.attach(MIMEText(body, "plain"))
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(EMAIL, APP_PASS)
        s.send_message(msg)

def run():
    print(f"[{datetime.now():%H:%M}] Conectando a {EMAIL}...")
    mail = connect()
    unread = get_unread(mail)
    print(f"  {len(unread)} no leídos\n")
    for e in unread:
        print(f"  • {e['from']} — {e['subject']}")
        result = classify(e)
        print(f"    → {result['action']} | {result['priority']}")
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        safe = e['from'].replace("@","_at_").replace(" ","_").replace("<","").replace(">","")[:30]
        (INBOX_DIR / f"{ts}_{safe}.json").write_text(
            json.dumps({"email": e, "classification": result}, ensure_ascii=False, indent=2), encoding="utf-8")
        if result["action"] == "reply" and result.get("reply"):
            print(f"    ✉️ Respondería: {result['reply'][:80]}...")
            # send_reply(e['from'], e['subject'], result["reply"])
        mail.store(e["id"], "+FLAGS", "\\Seen")
    mail.logout()
    print(f"\n✅ Guardados en: {INBOX_DIR}")

if __name__ == "__main__":
    run()


