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

### 6. Render pe Deploy (Free — Web Service)
1. https://render.com pe GitHub se login karo
2. **New > Web Service** > apna repo select karo
3. Settings:
   - **Language:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
4. **Environment** tab me jaake ye variables add karo:
   - `TELEGRAM_BOT_TOKEN`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `TZ` = `Asia/Kolkata` (warna reminders galat time pe aayenge)
5. Deploy karo. Render free Web Service ko ek open HTTP port chahiye hota hai — bot me isliye ek chhota health-check server already add kiya hua hai jo apne aap chal jayega, kuch extra karne ki zarurat nahi.

### 7. Render Free Tier ko sote rehne se rokna (UptimeRobot)
Render free Web Service 15 min inactivity ke baad sleep ho jata hai. Isse bachne ke liye:
1. https://uptimerobot.com pe free account banao
2. **Add New Monitor** > Monitor Type: `HTTP(s)`
3. URL me apne Render service ka URL daalo (jaise `https://your-bot-name.onrender.com`)
4. Monitoring interval: **5 minutes**
5. Save kar do — ab UptimeRobot har 5 min me bot ko ping karega, wo kabhi sleep nahi hoga

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
2. `TZ=Asia/Kolkata` already Render Environment tab me add kiya hua hoga (Step 6 me batay anusar)
3. GitHub pe push karo, Render apne aap redeploy kar dega

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
