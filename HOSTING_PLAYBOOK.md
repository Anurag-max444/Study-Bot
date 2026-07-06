# Study Sync — Bot Ko Hamesha Zinda Rakhne Ka Playbook

Ye guide tab kaam aayegi jab Render ya Supabase ka free tier khatam ho jaye,
ya limit cross ho jaye. Abhi kuch karne ki zarurat nahi — bas future reference hai.

---

## 1. Sabse pehle samjho: kyun code portable hai

Humne shuru se hi bot ko is tarah banaya hai ki **hosting aur database dono
easily badle ja sakte hain**, bina bot ka core code chhue:

- Saare secrets (`TELEGRAM_BOT_TOKEN`, `SUPABASE_URL`, `SUPABASE_KEY`) environment
  variables se aate hain — kahi bhi deploy karo, bas naye variables daalo
- Database access sirf `db.py` file se hota hai — agar database provider badalna
  ho, to sirf isi ek file ko update karna padega, baaki bot untouched rahega

Isliye "migration" ka matlab hai: **naya account banao, env variables copy karo,
data ka backup restore karo, deploy karo** — code dobara likhna nahi padega.

---

## 2. Render free tier khatam hone par — hosting alternatives

**Sabse pehle check karna:** Render dashboard → Billing me dekho free tier ki
kya limit lagi hai (hours/month ya koi aur cap). Agar sirf temporary spike hai
to wait bhi kar sakte ho.

**Agar permanently switch karna pade, priority order:**

1. **Oracle Cloud "Always Free" tier** — sabse best long-term free option.
   Ek chhota VM (2 AMD cores ya 4 ARM cores) **hamesha ke liye free** milta hai,
   koi expiry nahi. Thoda setup complex hai (apna Linux VM manage karna padta
   hai) lekin ek baar ho gaya to bohot stable hai.
2. **Fly.io** — free allowance milta hai chhote apps ke liye, Render jaisa hi
   easy deploy experience.
3. **Paid VPS (₹300-500/month)** — agar free options thak jaye, ek chhota VPS
   (Hetzner, DigitalOcean, Contabo) sabse reliable hota hai — bas `python bot.py`
   ko `systemd` service bana ke chala do, hamesha chalega, koi sleep/limit nahi.
4. **Apna ghar ka computer/Raspberry Pi** — agar bot ko chhoti scale pe chalana
   hai (tu aur tera dost), ek purana laptop ya Raspberry Pi bhi 24x7 chala sakte
   ho ghar ke internet pe (thoda technical setup chahiye — `systemd` ya `screen`/`tmux`).

**Migration steps (kisi bhi naye host pe):**
1. Naye platform pe account banao
2. Apna GitHub repo connect karo (ya code upload karo)
3. Environment variables wahi copy-paste karo jo Render me the
4. Start command same rahega: `python bot.py`
5. Purane Render service ko band kar do (warna dono ek saath poll karke Telegram
   409 Conflict dega — jaisa pehle hua tha)

---

## 3. Supabase free tier khatam hone par — database alternatives

**Pehle samjho:** Humne is bot me RLS disable kiya hai aur sirf simple REST
calls use kiye hain — isliye koi bhi Postgres-compatible service easily kaam
karega.

**Priority order:**

1. **Neon.tech** — free tier, serverless Postgres, Supabase jaisa hi easy setup.
   `supabase-py` library specifically Supabase API use karti hai, isliye Neon pe
   jaana ho to `db.py` ko thoda rewrite karna padega (raw `psycopg2` ya
   `asyncpg` se connect karna hoga instead of supabase client) — lekin tables
   ka structure (`schema.sql`) same rahega.
2. **Railway Postgres** — agar Railway pe hosting bhi kar rahe ho to unka apna
   Postgres add-on bhi use kar sakte ho, sab ek hi jagah.
3. **Self-hosted Postgres** — agar VPS pe already ho, wahi VPS pe Docker se
   Postgres bhi chala sakte ho, bilkul free (bas VPS ka cost).

**Zaroori: regular backup lete raho** — Supabase dashboard → Database →
Backups me se ya `pg_dump` command se, mahine me ek baar apna data export
karke rakh lo apne paas. Isse agar kabhi account issue ho, data safe rahega.

```bash
# Supabase connection string se backup lene ka tarika (jab zarurat pade)
pg_dump "postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres" > backup.sql
```

---

## 4. Ek cheez jo abhi se dhyan rakhni chahiye

Supabase free projects agar **1 hafte tak koi activity na ho to automatically
pause** ho jate hain. Chunki humara bot har minute database ko query karta hai
(reminders check karne ke liye), ye apne aap active rehta hai — koi extra kaam
nahi karna padega jab tak bot chal raha hai.

---

## 5. Quick reference — kab kya karna hai

| Situation | Kya karo |
|---|---|
| Render "sleep" ho raha hai | UptimeRobot check karo, sahi se ping ho raha hai kya |
| Render ki monthly hours khatam | Oracle Cloud Always Free ya paid VPS pe migrate karo |
| Supabase pause ho gaya (inactivity) | Dashboard se "resume" kar do, ya bot check karo chal raha hai kya |
| Supabase free tier limit (rows/storage) | Neon.tech pe migrate karo, `db.py` thoda modify karna hoga |
| Sab kuch band ho gaya achanak | Apna latest backup restore karo naye provider pe |

Sab se simple long-term solution: agar budget hai to **₹300-500/month ka ek
chhota VPS** (jisme Python bot + Postgres dono khud host kar lo) — na koi free
tier limit, na koi sleep/pause ka jhanjhat.
