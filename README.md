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

## Language Tone Update

Hinglish ab zyada professional/respectful hai — "aap" use hota hai casual "tu/tera" ki jagah, teeno languages (Hindi/English/Hinglish) me consistent tone hai.

## Phase 6 — Multiple Per-Task Reminders (naya feature)

Ab sirf ek subah + ek sham ka reminder hi nahi, balki **din bhar me jitne chaho utne reminders** set kar sakte ho — har ek pe ek naya topic milega, jise turant complete karke mark kar sakte ho.

**Naye commands:**
- `/addreminder HH:MM` — ek naya time slot add karo (jaise `/addreminder 14:30`)
- `/removereminder HH:MM` — koi slot hata do
- `/myreminders` — apni saari active reminder timings dekho

**Kaam kaise karta hai:**
1. Jaise hi koi set kiya hua time aata hai, bot syllabus se agla pending topic uthata hai aur bhej deta hai (subah/sham wale batch plan se alag — ek time me ek hi topic)
2. Message ke saath ek "✅ Mark as Done" button hota hai
3. Tap karte hi topic turant complete mark ho jata hai, streak update hoti hai, aur agla topic agle reminder pe milega

Ye feature purane subah/sham wale flow ke saath-saath kaam karta hai — dono ek dusre ko disturb nahi karte.

### Setup ke liye
Supabase SQL Editor me `migration_phase6_reminders.sql` run karo (naya `reminder_slots` table banayega).

## Phase 7 — Custom Topic Scheduling + Study Log

Ab apna khud ka "timetable" bana sakte ho — time, topic, aur duration set karo, bot start/end dono reminder dega, aur sab kuch ek study log me record hota hai.

**Naye commands:**
- `/addtask` — conversational flow: time puchega → topic puchega → duration puchega (jaise `1h`, `90m`, `1.5h`)
- `/mytopics` — apne saare scheduled topics dekho
- `/removetask HH:MM` — koi scheduled topic hatao
- `/studylog` — pichhle 7 din ka record dekho: kitna padha, kaunse topic, total ghante

**Kaam kaise karta hai:**
1. Set kiye gaye time pe bot topic bhejta hai: "abhi shuru kijiye, X minute ke liye"
2. Duration poora hote hi bot khud follow-up bhejta hai: "kya poora kiya?" ek button ke saath
3. Tap karte hi study log me entry ho jati hai (topic, date, duration, completed status)
4. `/studylog` se dekh sakte ho total kitne ghante padha, kaunse topic complete hue

### Setup ke liye
Supabase SQL Editor me `migration_phase7_custom_tasks.sql` run karo.

## PDF Extraction — Live Progress Bar

`/pdf` ya `/extractquestions` use karte waqt ab ek real-time progress bar dikhta hai — page-by-page reading progress se lekar PDF banane tak, sab live update hota hai chat me.

## Hindi (Devanagari) Support Added

Ab PDF extraction Hindi aur English **dono ek saath** (mixed content) sahi se handle karta hai. Isके liye do naye font families add ki hai (`fonts/` folder me):
- `NotoSans-Regular.ttf` / `NotoSans-Bold.ttf` — English/Latin text ke liye
- `NotoSansDevanagari-Regular.ttf` / `NotoSansDevanagari-Bold.ttf` — Hindi text ke liye

Ye dono Google ke free, open-source Noto fonts hai (SIL Open Font License — bina kisi restriction ke free use kar sakte ho). Code apne aap detect kar leta hai kaunsa hissa Hindi hai aur kaunsa English, aur sahi font switch karta hai — ek hi line me dono mix ho to bhi chalega.

**Zaroori:** `fonts/` folder poora repo me copy karna mat bhoolna, warna PDF generation fail ho jayega.

### Known limitation
- Reasoning section ke questions jisme **graphs/diagrams/images** hote hai, unke aas-paas ka text extract ho sakta hai lekin image khud copy nahi hoti (ye feature abhi text-only hai). Aise questions ko manually dekhna better hoga.

### Aage kya improve kar sakte ho (optional, khud try karna chahe to)
- `/addsyllabus` command — naye topics manually add karne ke liye
- Mock test mode — extracted questions se hi ek timer-based quiz bana sakte ho
- Weak topic detector — jo topics baar-baar skip hote hai unko priority dena

## Phase 8 — Streak Shield + Achievement Badges (gamification)

Padhai me consistency banaye rakhne ke liye ek fun, Duolingo-jaisa gamification layer add kiya hai.

### 🛡️ Streak Shield
- Har 7-din ki streak pe ek **shield** milta hai (max 3 store ho sakti hai)
- Agar koi din miss ho jaye, aur shield available ho, to wo automatically use ho jati hai aur **streak toot ti nahi**
- `/progress` me dikhta hai kitni shields available hai

### 🎖️ Achievement Badges
8 badges hai jo alag-alag milestones pe unlock hote hai:
- 🔥 Week Warrior (7-day streak)
- 🌟 Monthly Master (30-day streak)
- 📘 Getting Started (10 topics complete)
- 📚 Half Century (50 topics complete)
- 🏅 Century Club (100 topics complete)
- 🦉 Night Owl (raat 10 baje ke baad padhai complete ki)
- 🐦 Early Bird (subah 7 baje se pehle padhai complete ki)
- 🛡️ Shield Saver (pehli baar shield use hui)

Jab bhi koi naya badge unlock hota hai, bot turant ek celebration message bhejta hai. **`/badges`** command se sab dekh sakte ho — kaunse unlock ho chuke hai, kaunse abhi lock hai.

### Setup ke liye
Supabase SQL Editor me `migration_phase8_gamification.sql` run karo.

## Phase 9 — Reliable Follow-up Reminders (bug fix)

**Bug fix:** Pehle "kya poora kiya?" wala follow-up reminder sirf bot ki memory me schedule hota tha. Agar Render free tier beech me kabhi restart/sleep ho jaye (jo free tier pe hota rehta hai), to wo scheduled reminder gum ho jata tha — matlab session kabhi "complete" mark nahi hota tha, aur study log me nahi dikhta tha.

**Fix:** Ab follow-up ka time **database me save hota hai**, aur ek regular job (jo har minute chalta hai, baaki reminders ki tarah) check karta hai ki kiska time ho gaya hai. Isse bot kabhi bhi restart ho, koi follow-up miss nahi hoga.

### Setup ke liye
Supabase SQL Editor me `migration_phase9_reliable_followups.sql` run karo.

## Bug Hunt — Sab Fixes (is round me)

Pura codebase systematically audit kiya — static analysis (pyflakes) + poora `/addtask` flow ek fake database ke against end-to-end simulate karke test kiya. Ye mila aur fix kiya:

1. **Sabse badi wajah "message nahi aa raha" ki:** Agar Supabase me `migration_phase8` ya `migration_phase9` nahi chalayi gayi ho, to naye columns missing hote hai, aur database insert silently fail ho jata hai — matlab bot ka message bhejne wala code tak kabhi pahuchta hi nahi. **Isीलिye ek नया `ALL_MIGRATIONS.sql` file banayi hai** jisme saari migrations ek saath, safe order me, idempotent tarike se hai — bas ye ek file chala do, koi step miss nahi hoga.

2. **Per-user error isolation:** Pehle agar scheduler ke ek loop me kisi ek user ka data problematic hota (jaise koi missing field), to us minute ke baaki saare users ka message bhi nahi jata tha (poora loop crash ho jata tha beech me). Ab har user ka processing apne try/except me hai — ek fail ho to baaki sab normally chalte rahenge.

3. **Global error handler add kiya** — ab koi bhi unhandled exception properly Render logs me dikhega, kuch bhi silently fail nahi hoga.

4. **"Beet chuka time" wali confusion fix ki** — agar `/addtask` me aisa time do jo aaj ke liye already nikal chuka hai, ab bot clearly bata dega ki "yeh kal chalega", pehle silently kal tak wait karta tha bina bataye.

### Zaroori: Agar pehli baar ye sab chala rahe ho ya kisi step ko lekar confusion hai
Bas Supabase SQL Editor me **`ALL_MIGRATIONS.sql`** chala do — chahe naya project ho ya purana, ye safe hai (sab `IF NOT EXISTS` guarded hai, dobara chalane se bhi kuch nahi tootega). Isse alag-alag migration files yaad rakhne ka jhanjhat khatam ho jata hai.

## Phase 11 — Study Tree (naya feature, bina API ke)

`/mytree` command bhejo — bot ek real tree image banata hai (Pillow se, 100% free, koi API nahi) jo tumhari consistency ke saath grow hota hai.

**6 Growth Stages:**
- 🌰 Seed (0 activities)
- 🌱 Sprout (1-4)
- 🪴 Sapling (5-14)
- 🌳 Young Tree (15-29)
- 🌲 Mature Tree (30-59)
- 🌸 Blooming Tree (60+) — flowers ke saath!

Growth score = total completed syllabus topics + completed custom task sessions — ye kabhi kam nahi hota, sirf badhta hai.

**Wilted warning:** Agar 2+ din se koi activity nahi hui, tree murjha ke (brown, drooping branches) dikhta hai — ek gentle visual reminder ki wapas aana hai.

### Setup ke liye
Koi naya SQL migration nahi chahiye — ye maujooda data (syllabus + task_sessions) se hi calculate hota hai. Bas `bot.py`, `db.py`, `lang.py` aur nayi file `tree_generator.py` copy kar lena.
