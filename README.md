# Study Buddy Telegram Bot — Phase 1

Phase 1 me ye ban chuka hai:
- `/start` → language select (Hindi/English/Hinglish)
- Naam, exam (SSC CGL / JEE Mains / Custom) puchna
- Syllabus PDF upload (basic text extraction) ya default syllabus load
- Daily study hours aur reminder time save karna
- Sab Supabase me permanently save

## Setup Steps

### 1. Telegram Bot Token lena
- Telegram pe **@BotFather** ko message karo
- `/newbot` type karo, naam aur username do
- Jo token milega wo `.env` me daalna hai

### 2. Supabase Setup
1. https://supabase.com pe free account bana (GitHub se login ho jayega)
2. New project banao
3. Left sidebar me **SQL Editor** kholo
4. `schema.sql` file ka pura content paste karke **Run** karo
5. Left sidebar me **Project Settings > API** me jao
6. `Project URL` aur `anon public key` copy karo

### 3. Local `.env` file banao
`.env.example` ko copy karke `.env` banao, apne values daalo:
```
TELEGRAM_BOT_TOKEN=xxxx
SUPABASE_URL=xxxx
SUPABASE_KEY=xxxx
```

### 4. Local test (optional, VS Code me)
```bash
pip install -r requirements.txt
python bot.py
```
Telegram pe apne bot ko `/start` bhejo aur test karo.

### 5. GitHub pe push
```bash
git add .
git commit -m "Phase 1: onboarding flow"
git push origin main
```

### 6. Railway pe Deploy (Free)
1. https://railway.app pe GitHub se login karo
2. **New Project > Deploy from GitHub repo** > apna repo select karo
3. Railway apne aap `requirements.txt` dekh ke Python detect kar lega
4. **Variables** tab me jaake `.env` wali teeno cheezein add karo (TELEGRAM_BOT_TOKEN, SUPABASE_URL, SUPABASE_KEY)
5. **Settings > Start Command** me daalo: `python bot.py`
6. Deploy hote hi bot 24x7 chalega, free tier me ~500 hours/month milte hai (ek bot ke liye kaafi hai)

---

## Phase 2 — Daily Plan + Evening Checklist (done)

Ye add hua hai:
- Onboarding me ab evening reminder time bhi puchta hai
- Har minute bot check karta hai kiska reminder time ab hua hai
- Subah: pending syllabus topics se plan banta hai, checkbox keyboard ke saath bhejta hai
- Sham: wahi checklist dobara bhejta hai, tap karke check/uncheck ho jata hai
- Jo topic check ho jaye wo syllabus me "done" mark ho jata hai, agle din nahi aayega

### Phase 2 ke liye extra setup:
1. Supabase SQL Editor me `migration_phase2.sql` run karo
2. Railway pe Variables tab me ek aur variable add karo: `TZ=Asia/Kolkata`
   (zaroori hai warna server UTC time use karega, reminders galat time pe aayenge)
3. GitHub pe push karo, Railway apne aap redeploy kar dega

### Test kaise kare
- `/start` se onboarding poora karo, reminder time abhi se 2 min aage set karo
- Us time pe plan aana chahiye checkboxes ke saath
- Tap karke check/uncheck karo, sham ke time pe wahi checklist current state ke saath aayegi

## Phase 3 — Progress Tracking + Streaks (done)

Ye add hua hai:
- `/progress` command — subject-wise progress bar (▓░), streak count, longest streak
- Jab bhi koi topic evening checklist me tick hota hai, streak automatically update hoti hai
  (agar kal bhi active the to streak +1, warna naye se 1 se start)
- Har Sunday sham ko evening checklist ke sath weekly summary bhi aata hai (total topics done)

### Test kaise kare
- Kuch topics evening checklist me tick karo
- `/progress` bhejo — progress bar aur streak dikhna chahiye
- Agle din bhi kuch tick karo — streak 2 ho jani chahiye

## Phase 4 — PDF Question Extractor (done, bina API ke)

`/extractquestions` command bhejo, phir apni MCQ wali PDF bhejo. Bot:
- Regex/pattern-matching se questions detect karta hai (koi AI API nahi, 100% free)
- Supported patterns: `Q1.`, `1)`, `1.`, `Question 1:` se shuru hone wale questions
- Options: `(a)`, `a)`, `A.` format me
- Answers: `Ans: b`, `Answer: (c)`, `Ans - d` jaise format me (agar PDF me diye ho)
- Ek clean naya PDF banata hai — questions ek jagah, answer key alag page pe

### Limitations (imandaari se bata raha hu)
- Ye sirf **text-based PDFs** pe kaam karega, scanned/image PDFs pe nahi (OCR nahi hai isme)
- Agar questions ka format bahut different hai (jaise numbering style alag), to kuch questions miss ho sakte hai — regex-based hai, AI jaisa smart nahi
- Kabhi kabhi options ke beech me stray text (headers/footers) galti se ek option me chipak sakta hai — best results ke liye clean PDF use karo

## Sab Phases Complete! 🎉

Bot ab poora kaam karta hai:
1. Onboarding (naam, exam, syllabus, language, timing)
2. Daily morning plan + evening checklist with checkboxes
3. Progress tracking + streaks (`/progress`)
4. PDF se questions extract karna (`/extractquestions`)

### Aage kya improve kar sakte ho (optional, khud try karna chahe to)
- `/addsyllabus` command — naye topics manually add karne ke liye
- Mock test mode — extracted questions se hi ek timer-based quiz bana sakte ho
- Weak topic detector — jo topics baar-baar skip hote hai unko priority dena
