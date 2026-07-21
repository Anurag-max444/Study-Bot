"""
Sab user-facing text yaha hai, teeno languages me.
Naya text add karna ho to teeno dict me same key ke saath add karo.

Tone guide: Hinglish version bhi utni hi respectful/professional honi chahiye
jitni Hindi/English — 'aap' use karo, casual 'tu/tera' avoid karo.
"""

TEXT = {
    "welcome": {
        "hindi": "नमस्ते {name}! 📚 <b>मैं Study Sync हूँ</b>, आपका स्टडी पार्टनर।\n\nसभी कमांड्स के लिए /help टाइप कीजिए।",
        "english": "Hello {name}! 📚 <b>I'm Study Sync</b>, your study partner.\n\nType /help to see everything I can do.",
        "hinglish": "Namaste {name}! 📚 <b>Main Study Sync hoon</b>, aapka study partner.\n\nSabhi commands dekhne ke liye /help type kijiye.",
    },
    "ask_language": {
        "hindi": (
            "📚 <b>Study Sync में आपका स्वागत है!</b>\n"
            "आपका पर्सनल स्टडी पार्टनर — शेड्यूलिंग, रिवीजन रिमाइंडर और प्रोग्रेस ट्रैकिंग सब एक जगह।\n"
            "━━━━━━━━━━\n"
            "सबसे पहले बताइए, आप किस भाषा में बात करना पसंद करेंगे?"
        ),
        "english": (
            "📚 <b>Welcome to Study Sync!</b>\n"
            "Your personal study partner — scheduling, revision reminders, and progress tracking, all in one place.\n"
            "━━━━━━━━━━\n"
            "First, which language would you prefer to chat in?"
        ),
        "hinglish": (
            "📚 <b>Study Sync mein aapka swagat hai!</b>\n"
            "Aapka personal study partner — scheduling, revision reminders aur progress tracking sab ek jagah.\n"
            "━━━━━━━━━━\n"
            "Sabse pehle bataiye, aap kis language mein baat karna pasand karenge?"
        ),
    },
    "ask_name": {
        "hindi": "📝 Step 1/3 — आपका नाम क्या है?",
        "english": "📝 Step 1/3 — What's your name?",
        "hinglish": "📝 Step 1/3 — Aapka naam kya hai?",
    },
    "invalid_name": {
        "hindi": "कृपया एक सही नाम भेजिए (1–40 अक्षर, बिना / से शुरू हुए)।",
        "english": "Please send a valid name (1–40 characters, not starting with /).",
        "hinglish": "Kripya ek sahi naam bhejiye (1–40 characters, / se shuru na ho).",
    },
    "ask_exam": {
        "hindi": "🎯 Step 2/3 — आप किस परीक्षा की तैयारी कर रहे हैं?",
        "english": "🎯 Step 2/3 — Which exam are you preparing for?",
        "hinglish": "🎯 Step 2/3 — Aap kis exam ki taiyaari kar rahe hain?",
    },
    "ask_hours": {
        "hindi": "⏱ Step 3/3 — आप रोज़ कितने घंटे पढ़ाई कर सकते हैं? (नंबर भेजिए, जैसे 4 या 3.5)",
        "english": "⏱ Step 3/3 — How many hours can you study daily? (send a number, e.g. 4 or 3.5)",
        "hinglish": "⏱ Step 3/3 — Aap roz kitne ghante study kar sakte hain? (number bhejiye, jaise 4 ya 3.5)",
    },
    "invalid_hours": {
        "hindi": "कृपया 0.5 से 18 के बीच एक नंबर भेजिए (जैसे 4 या 3.5)।",
        "english": "Please send a number between 0.5 and 18 (e.g. 4 or 3.5).",
        "hinglish": "Kripya 0.5 se 18 ke beech ek number bhejiye (jaise 4 ya 3.5).",
    },
    "progress_header": {
        "hindi": "📊 <b>{name} की प्रोग्रेस</b>\n━━━━━━━━━━\n🔥 स्ट्रीक: <b>{streak} दिन</b> (सबसे लंबी: {longest})\n",
        "english": "📊 <b>{name}'s progress</b>\n━━━━━━━━━━\n🔥 Streak: <b>{streak} days</b> (longest: {longest})\n",
        "hinglish": "📊 <b>{name} ka progress</b>\n━━━━━━━━━━\n🔥 Streak: <b>{streak} din</b> (sabse lambi: {longest})\n",
    },
    "ask_question_pdf": {
        "hindi": "जिस PDF से questions निकालने हैं वो भेज दीजिए (MCQ फॉर्मेट में — options a, b, c, d के साथ)।",
        "english": "Please send the PDF you'd like questions extracted from (MCQ format — with a, b, c, d options).",
        "hinglish": "Jis PDF se questions nikalne hain wo bhej dijiye (MCQ format mein — options a, b, c, d ke saath).",
    },
    "extracting_in_progress": {
        "hindi": "PDF प्रोसेस हो रही है, कृपया थोड़ा प्रतीक्षा कीजिए... ⏳",
        "english": "Processing your PDF, please hold on a moment... ⏳",
        "hinglish": "PDF process ho rahi hai, kripya thoda intezaar kijiye... ⏳",
    },
    "no_questions_found": {
        "hindi": "क्षमा कीजिए, इस PDF में कोई पहचाने जाने लायक MCQ फॉर्मेट नहीं मिला। सुनिश्चित कीजिए कि questions 'Q1.' या '1)' जैसे शुरू हों और options (a)(b)(c)(d) फॉर्मेट में हों।",
        "english": "Sorry, I couldn't detect a recognizable MCQ format in this PDF. Please make sure questions start like 'Q1.' or '1)' and options follow the (a)(b)(c)(d) format.",
        "hinglish": "Maaf kijiye, is PDF mein koi pehchana jaane layak MCQ format nahi mila. Kripya check karein ki questions 'Q1.' ya '1)' se start hon aur options (a)(b)(c)(d) format mein hon.",
    },
    "extraction_done": {
        "hindi": "हो गया! {count} questions मिले, PDF में साफ़-सुथरे तरीके से व्यवस्थित कर दिए हैं (आख़िरी पेज पर answer key भी है) ✅",
        "english": "Done! Found {count} questions, neatly formatted into a PDF (with an answer key on the last page) ✅",
        "hinglish": "Ho gaya! {count} questions mile, PDF mein clean tareeke se organize kar diya hai (last page par answer key bhi hai) ✅",
    },
    "no_streak_yet": {
        "hindi": "अभी तक कोई स्ट्रीक शुरू नहीं हुई है। आज पहला टॉपिक पूरा करके शुरुआत कीजिए!",
        "english": "No streak started yet. Complete your first topic today to get going!",
        "hinglish": "Abhi tak koi streak start nahi hui hai. Aaj pehla topic complete karke shuruaat kijiye!",
    },
    "setup_done": {
        "hindi": (
            "✅ <b>सेटअप पूरा हो गया, {name}!</b>\n"
            "━━━━━━━━━━\n"
            "🎯 Exam: {exam}\n"
            "⏱ रोज़ाना लक्ष्य: {hours} घंटे\n\n"
            "अब /addtask से अपना पहला स्टडी सेशन शेड्यूल कीजिए, या नीचे दिए बटन इस्तेमाल कीजिए।"
        ),
        "english": (
            "✅ <b>Setup complete, {name}!</b>\n"
            "━━━━━━━━━━\n"
            "🎯 Exam: {exam}\n"
            "⏱ Daily target: {hours} hours\n\n"
            "Use /addtask to schedule your first study session, or use the buttons below."
        ),
        "hinglish": (
            "✅ <b>Setup poora ho gaya, {name}!</b>\n"
            "━━━━━━━━━━\n"
            "🎯 Exam: {exam}\n"
            "⏱ Daily target: {hours} ghante\n\n"
            "Ab /addtask se apna pehla study session schedule kijiye, ya neeche diye buttons use kijiye."
        ),
    },
    "invalid_number": {
        "hindi": "कृपया केवल नंबर भेजिए।",
        "english": "Please send only a number.",
        "hinglish": "Kripya sirf number bhejiye.",
    },
    "invalid_time": {
        "hindi": "कृपया सही फॉर्मेट में भेजिए, जैसे 07:00",
        "english": "Please send it in the correct format, e.g. 07:00",
        "hinglish": "Kripya sahi format mein bhejiye, jaise 07:00",
    },
    "task_time_already_passed": {
        "hindi": "⚠️ ध्यान दें: यह समय आज के लिए निकल चुका है, इसलिए यह टास्क कल इसी समय चलेगा।",
        "english": "⚠️ Note: this time has already passed for today, so this task will trigger tomorrow at this time instead.",
        "hinglish": "⚠️ Dhyan dein: yeh time aaj ke liye nikal chuka hai, isliye yeh task kal isi time par chalega.",
    },

    # ---- Custom task scheduling (time + topic + duration) ----
    "ask_task_time": {
        "hindi": "किस समय पढ़ाई शुरू करनी है? (24hr फॉर्मेट, जैसे 18:00)",
        "english": "What time should this study session start? (24hr format, e.g. 18:00)",
        "hinglish": "Kis time study session start karna hai? (24hr format, jaise 18:00)",
    },
    "ask_task_topic": {
        "hindi": "किस टॉपिक पर पढ़ाई करनी है? (जो चाहें लिखें, जैसे 'Percentage Revision')",
        "english": "What topic would you like to study? (write anything, e.g. 'Percentage Revision')",
        "hinglish": "Kis topic par study karni hai? (jo chahen likhein, jaise 'Percentage Revision')",
    },
    "ask_task_duration": {
        "hindi": "कितनी देर पढ़ेंगे? (जैसे 1h, 90m, या 1.5h)",
        "english": "How long will you study for? (e.g. 1h, 90m, or 1.5h)",
        "hinglish": "Kitni der padhenge? (jaise 1h, 90m, ya 1.5h)",
    },
    "invalid_duration": {
        "hindi": "कृपया सही फॉर्मेट में भेजिए — जैसे 1h, 90m, या 1.5h",
        "english": "Please send it in a valid format — e.g. 1h, 90m, or 1.5h",
        "hinglish": "Kripya sahi format mein bhejiye — jaise 1h, 90m, ya 1.5h",
    },
    "task_scheduled": {
        "hindi": "बढ़िया! {time} बजे '{topic}' के लिए {duration} मिनट का सेशन सेट हो गया है। ✅\n(यह एक बार चलेगा — अगले दिन फिर से चाहिए तो दोबारा /addtask कीजिए)",
        "english": "Great! A {duration}-minute session for '{topic}' is scheduled at {time}. ✅\n(This is one-time — add it again with /addtask if you want it tomorrow too)",
        "hinglish": "Badhiya! {time} baje '{topic}' ke liye {duration} minute ka session set ho gaya hai. ✅\n(Yeh ek baar chalega — agle din phir chahiye to dobara /addtask kijiye)",
    },
    "generating_progress_line": {
        "hindi": "{label}\n[{bar}] {pct}%",
        "english": "{label}\n[{bar}] {pct}%",
        "hinglish": "{label}\n[{bar}] {pct}%",
    },
    "tree_generating_label": {
        "hindi": "🌳 आपका Study Tree बन रहा है...",
        "english": "🌳 Growing your Study Tree...",
        "hinglish": "🌳 Aapka Study Tree ban raha hai...",
    },
    "report_generating_label": {
        "hindi": "📊 आपकी weekly report बन रही है...",
        "english": "📊 Building your weekly report...",
        "hinglish": "📊 Aapki weekly report ban rahi hai...",
    },
    "report_ready_caption": {
        "hindi": "📊 <b>यह रही आपकी weekly report, {name}!</b>",
        "english": "📊 <b>Here's your weekly report, {name}!</b>",
        "hinglish": "📊 <b>Yeh rahi aapki weekly report, {name}!</b>",
    },
    "report_failed": {
        "hindi": "माफ़ कीजिए, report बनाने में कोई दिक्कत आ गई। थोड़ी देर बाद फिर कोशिश कीजिए।",
        "english": "Sorry, something went wrong while building the report. Please try again in a bit.",
        "hinglish": "Sorry, report banane mein kuch dikkat aa gayi. Thodi der baad phir try kijiye.",
    },
    "mytopics_header": {
        "hindi": "📋 <b>आपके शेड्यूल्ड टॉपिक</b>\n━━━━━━━━━━\n",
        "english": "📋 <b>Your scheduled topics</b>\n━━━━━━━━━━\n",
        "hinglish": "📋 <b>Aapke scheduled topics</b>\n━━━━━━━━━━\n",
    },
    "mytopics_empty": {
        "hindi": "अभी तक कोई टॉपिक शेड्यूल नहीं है। /addtask से जोड़िए।",
        "english": "No topics scheduled yet. Add one with /addtask.",
        "hinglish": "Abhi tak koi topic schedule nahi hai. /addtask se add kijiye.",
    },
    "task_removed": {
        "hindi": "{time} बजे का टास्क हटा दिया गया है।",
        "english": "The task at {time} has been removed.",
        "hinglish": "{time} baje ka task remove kar diya gaya hai.",
    },
    "task_not_found": {
        "hindi": "इस समय पर कोई टास्क नहीं मिला। /mytopics से लिस्ट देखिए।",
        "english": "No task found at that time. Use /mytopics to see your list.",
        "hinglish": "Is time par koi task nahi mila. /mytopics se list dekhiye.",
    },
    "task_session_start": {
        "hindi": "📖 समय हो गया, {name}! अभी शुरू कीजिए:\n\n📌 <b>{topic}</b>\n⏱ {duration} मिनट के लिए\n\nमैं {duration} मिनट बाद पूछूंगा कि पूरा हुआ या नहीं।",
        "english": "📖 Time to begin, {name}!\n\n📌 <b>{topic}</b>\n⏱ For {duration} minutes\n\nI'll check back in {duration} minutes to see if you're done.",
        "hinglish": "📖 Time ho gaya hai, {name}! Abhi shuru kijiye:\n\n📌 <b>{topic}</b>\n⏱ {duration} minute ke liye\n\nMain {duration} minute baad puchunga ki poora hua ya nahi.",
    },
    "task_session_followup": {
        "hindi": "⏰ समय पूरा हो गया! क्या आपने '<b>{topic}</b>' पूरा कर लिया?",
        "english": "⏰ Time's up! Did you finish '<b>{topic}</b>'?",
        "hinglish": "⏰ Time poora ho gaya! Kya aapne '<b>{topic}</b>' poora kar liya?",
    },
    "session_done_button": {
        "hindi": "✅ हां, पूरा हुआ",
        "english": "✅ Yes, done",
        "hinglish": "✅ Haan, poora hua",
    },
    "session_marked_done": {
        "hindi": "शानदार, {name}! '{topic}' आपके स्टडी लॉग में दर्ज हो गया है। 💪",
        "english": "Excellent, {name}! '{topic}' has been logged in your study record. 💪",
        "hinglish": "Shaandaar, {name}! '{topic}' aapke study log mein record ho gaya hai. 💪",
    },
    "studylog_header": {
        "hindi": "📊 <b>पिछले {days} दिन का स्टडी लॉग</b>\n━━━━━━━━━━\n",
        "english": "📊 <b>Study log — last {days} days</b>\n━━━━━━━━━━\n",
        "hinglish": "📊 <b>Pichhle {days} din ka study log</b>\n━━━━━━━━━━\n",
    },
    "studylog_empty": {
        "hindi": "अभी तक कोई सेशन दर्ज नहीं हुआ। /addtask से एक टॉपिक शेड्यूल कीजिए।",
        "english": "No sessions logged yet. Schedule a topic with /addtask.",
        "hinglish": "Abhi tak koi session record nahi hua. /addtask se ek topic schedule kijiye.",
    },
    "studylog_total": {
        "hindi": "\n📌 कुल पूर्ण समय: {hours} घंटे",
        "english": "\n📌 Total completed time: {hours} hours",
        "hinglish": "\n📌 Total complete kiya hua time: {hours} ghante",
    },
    "help_text": {
        "hindi": (
            "🤖 <b>Study Sync — कमांड गाइड</b>\n"
            "━━━━━━━━━━\n\n"
            "⚙️ <b>सेटअप</b>\n"
            "/start — बॉट सेटअप करें (भाषा, नाम, एग्ज़ाम, सिलेबस)\n\n"
            "📖 <b>स्टडी शेड्यूल</b>\n"
            "/addtask — खुद का टॉपिक + समय + अवधि सेट करें\n"
            "/mytopics — अपने शेड्यूल्ड टॉपिक देखें\n"
            "/removetask HH:MM — कोई शेड्यूल्ड टॉपिक हटाएं\n"
            "/studylog — पिछले 7 दिन का पढ़ाई का रिकॉर्ड देखें\n"
            "/revisions — अपने पेंडिंग रिवीजन देखें (spaced repetition)\n\n"
            "📊 <b>प्रोग्रेस</b>\n"
            "/progress — स्ट्रीक, शील्ड और बैज देखें\n"
            "/badges — अपने सारे अचीवमेंट बैज देखें\n"
            "/mytree — अपना Study Tree देखें\n"
            "/report — पिछले 7 दिन की PDF रिपोर्ट कार्ड पाएं (हर रविवार अपने आप भी आती है)\n\n"
            "🛠️ <b>यूटिलिटी</b>\n"
            "/pdf (या /extractquestions) — किसी PDF से MCQ questions निकालें\n"
            "/clear — पुराने मैसेज साफ़ करें\n"
            "/help — यह गाइड फिर से देखें\n"
            "/cancel — कोई भी चालू step-by-step प्रोसेस (addtask, addmocktest वगैरह) रोकें\n\n"
            "🧾 <b>Mock Tests</b>\n"
            "/addmocktest — कोई mock test log करें (platform, score, percentile, rank, weak/strong topics वगैरह)\n"
            "/mocktests — अपने सारे logged mock tests देखें\n\n"
            "━━━━━━━━━━\n"
            "📌 <b>बॉट कैसे काम करता है:</b>\n"
            "• /addtask से अपना टॉपिक, समय और अवधि सेट कीजिए — बॉट सही समय पर याद दिलाएगा\n"
            "• समय पूरा होने पर बॉट पूछेगा कि पूरा हुआ या नहीं\n"
            "• हर पूरे किए गए सेशन के लिए 1/3/7/15 दिन बाद रिवीजन रिमाइंडर अपने आप शेड्यूल होंगे\n"
            "• पुराने पेपर/नोट्स की PDF भेजकर questions अलग निकलवा सकते हैं\n"
            "• नीचे दिए क्विक-मेनू बटन से भी सबसे इस्तेमाल होने वाले कमांड्स एक टैप में खुलते हैं"
        ),
        "english": (
            "🤖 <b>Study Sync — Command Guide</b>\n"
            "━━━━━━━━━━\n\n"
            "⚙️ <b>Setup</b>\n"
            "/start — Set up the bot (language, name, exam, syllabus)\n\n"
            "📖 <b>Study schedule</b>\n"
            "/addtask — Set your own topic + time + duration\n"
            "/mytopics — View your scheduled topics\n"
            "/removetask HH:MM — Remove a scheduled topic\n"
            "/studylog — View your last 7 days of study history\n"
            "/revisions — View pending revisions (spaced repetition)\n\n"
            "📊 <b>Progress</b>\n"
            "/progress — View your streak, shields, and badges\n"
            "/badges — View all your earned achievement badges\n"
            "/mytree — View your Study Tree\n"
            "/report — Get a PDF report card of your last 7 days (also arrives automatically every Sunday)\n\n"
            "🛠️ <b>Utility</b>\n"
            "/pdf (or /extractquestions) — Extract MCQ questions from a PDF\n"
            "/clear — Clear old messages from this chat\n"
            "/help — Show this guide again\n"
            "/cancel — Stop any in-progress step-by-step flow (addtask, addmocktest, etc.)\n\n"
            "🧾 <b>Mock Tests</b>\n"
            "/addmocktest — Log a mock test (platform, score, percentile, rank, weak/strong topics, etc.)\n"
            "/mocktests — View all your logged mock tests\n\n"
            "━━━━━━━━━━\n"
            "📌 <b>How the bot works:</b>\n"
            "• Use /addtask to set your topic, start time, and duration — the bot reminds you right on time\n"
            "• Once the duration is up, the bot checks in to confirm you're done\n"
            "• Every completed session automatically schedules revision reminders at 1/3/7/15 days\n"
            "• Send a PDF of practice papers/notes to extract clean, standalone questions\n"
            "• The quick-menu buttons below give you the most-used commands in one tap"
        ),
        "hinglish": (
            "🤖 <b>Study Sync — Command Guide</b>\n"
            "━━━━━━━━━━\n\n"
            "⚙️ <b>Setup</b>\n"
            "/start — Bot setup kijiye (language, naam, exam, syllabus)\n\n"
            "📖 <b>Study schedule</b>\n"
            "/addtask — Apna khud ka topic + time + duration set kijiye\n"
            "/mytopics — Apne scheduled topics dekhiye\n"
            "/removetask HH:MM — Koi scheduled topic hataiye\n"
            "/studylog — Pichhle 7 din ka padhai ka record dekhiye\n"
            "/revisions — Apne pending revisions dekhiye (spaced repetition)\n\n"
            "📊 <b>Progress</b>\n"
            "/progress — Apni streak, shields aur badges dekhiye\n"
            "/badges — Apne saare earned achievement badges dekhiye\n"
            "/mytree — Apna Study Tree dekhiye\n"
            "/report — Pichhle 7 din ki PDF report card paiye (har Sunday apne aap bhi aati hai)\n\n"
            "🛠️ <b>Utility</b>\n"
            "/pdf (ya /extractquestions) — Kisi PDF se MCQ questions nikaliye\n"
            "/clear — Is chat ke purane messages saaf kijiye\n"
            "/help — Yeh guide dobara dekhiye\n"
            "/cancel — Koi bhi chalu step-by-step process (addtask, addmocktest wagera) roke\n\n"
            "🧾 <b>Mock Tests</b>\n"
            "/addmocktest — Koi mock test log kijiye (platform, score, percentile, rank, weak/strong topics wagera)\n"
            "/mocktests — Apne saare logged mock tests dekhiye\n\n"
            "━━━━━━━━━━\n"
            "📌 <b>Bot kaise kaam karta hai:</b>\n"
            "• /addtask se apna topic, start time aur duration set kijiye — bot sahi time par yaad dilayega\n"
            "• Duration poora hone par bot check karega ki poora hua ya nahi\n"
            "• Har complete kiye session ke liye 1/3/7/15 din baad revision reminders apne aap schedule ho jayenge\n"
            "• Purane papers/notes ki PDF bhej kar usse questions alag nikalwa sakte hain\n"
            "• Neeche diye quick-menu buttons se bhi sabse zyada use hone wale commands ek tap mein khulte hain"
        ),
    },

    # ---- Gamification: streak shields + achievement badges ----
    "shields_line": {
        "hindi": "{shields_visual}  Shields: {shields}/3\n",
        "english": "{shields_visual}  Shields: {shields}/3\n",
        "hinglish": "{shields_visual}  Shields: {shields}/3\n",
    },
    "badges_summary_line": {
        "hindi": "🎖️ Badges: [{bar}] {count}/{total}\n",
        "english": "🎖️ Badges: [{bar}] {count}/{total}\n",
        "hinglish": "🎖️ Badges: [{bar}] {count}/{total}\n",
    },
    "shield_used_notification": {
        "hindi": "🛡️ <b>आपकी स्ट्रीक बच गई!</b> एक दिन मिस होने पर भी शील्ड ने उसे बचा लिया। बची हुई शील्ड: {remaining}",
        "english": "🛡️ <b>Your streak was saved!</b> A shield covered the missed day. Shields remaining: {remaining}",
        "hinglish": "🛡️ <b>Aapki streak bach gayi!</b> Ek din miss hone par bhi shield ne use bacha liya. Bachi hui shields: {remaining}",
    },
    "badge_earned_notification": {
        "hindi": "🎉 <b>नया बैज अनलॉक हुआ!</b>\n{badge_name}\n\n/badges से सारे बैज देखिए।",
        "english": "🎉 <b>New badge unlocked!</b>\n{badge_name}\n\nSee all your badges with /badges.",
        "hinglish": "🎉 <b>Naya badge unlock hua!</b>\n{badge_name}\n\n/badges se saare badges dekhiye.",
    },
    "badges_header": {
        "hindi": "🎖️ <b>आपके बैज</b> ({count}/{total})\n━━━━━━━━━━",
        "english": "🎖️ <b>Your badges</b> ({count}/{total})\n━━━━━━━━━━",
        "hinglish": "🎖️ <b>Aapke badges</b> ({count}/{total})\n━━━━━━━━━━",
    },
    "badges_tap_hint": {
        "hindi": "\nकिसी भी बैज पर टैप करके देखिए वो कैसे मिलता है 👇",
        "english": "\nTap any badge to see how to unlock it 👇",
        "hinglish": "\nKisi bhi badge par tap karke dekhiye wo kaise milta hai 👇",
    },
    "badge_unlocked_popup": {
        "hindi": "✅ {name} — हासिल किया!\n\n{hint}",
        "english": "✅ {name} — Unlocked!\n\n{hint}",
        "hinglish": "✅ {name} — Unlock ho gaya!\n\n{hint}",
    },
    "badge_locked_popup": {
        "hindi": "🔒 {name} — अभी लॉक है\n\n{hint}",
        "english": "🔒 {name} — Still locked\n\n{hint}",
        "hinglish": "🔒 {name} — Abhi locked hai\n\n{hint}",
    },
    "badge_hint_streak_7": {
        "hindi": "लगातार 7 दिन पढ़ाई करके मिलता है।",
        "english": "Earned by studying for 7 days in a row.",
        "hinglish": "Lagatar 7 din padhai karke milta hai.",
    },
    "badge_hint_streak_30": {
        "hindi": "लगातार 30 दिन पढ़ाई करके मिलता है।",
        "english": "Earned by studying for 30 days in a row.",
        "hinglish": "Lagatar 30 din padhai karke milta hai.",
    },
    "badge_hint_topics_10": {
        "hindi": "10 टॉपिक पूरे करने पर मिलता है।",
        "english": "Earned by completing 10 topics.",
        "hinglish": "10 topics complete karne par milta hai.",
    },
    "badge_hint_topics_50": {
        "hindi": "50 टॉपिक पूरे करने पर मिलता है।",
        "english": "Earned by completing 50 topics.",
        "hinglish": "50 topics complete karne par milta hai.",
    },
    "badge_hint_topics_100": {
        "hindi": "100 टॉपिक पूरे करने पर मिलता है।",
        "english": "Earned by completing 100 topics.",
        "hinglish": "100 topics complete karne par milta hai.",
    },
    "badge_hint_night_owl": {
        "hindi": "रात 10 बजे के बाद कोई सेशन पूरा करने पर मिलता है।",
        "english": "Earned by completing a session after 10 PM.",
        "hinglish": "Raat 10 baje ke baad koi session complete karne par milta hai.",
    },
    "badge_hint_early_bird": {
        "hindi": "सुबह 7 बजे से पहले कोई सेशन पूरा करने पर मिलता है।",
        "english": "Earned by completing a session before 7 AM.",
        "hinglish": "Subah 7 baje se pehle koi session complete karne par milta hai.",
    },
    "badge_hint_shield_saver": {
        "hindi": "पहली बार स्ट्रीक शील्ड इस्तेमाल होने पर मिलता है।",
        "english": "Earned the first time a streak shield saves your streak.",
        "hinglish": "Pehli baar streak shield use hone par milta hai.",
    },

    # ---- Study Tree ----
    "tree_caption": {
        "hindi": "🌳 <b>आपका Study Tree</b>\n━━━━━━━━━━\nStage: {stage}\n[{bar}] Growth Score: {score}\n\nहर टॉपिक पूरा करने पर यह और बढ़ेगा!",
        "english": "🌳 <b>Your Study Tree</b>\n━━━━━━━━━━\nStage: {stage}\n[{bar}] Growth score: {score}\n\nIt grows a little more every time you complete a topic!",
        "hinglish": "🌳 <b>Aapka Study Tree</b>\n━━━━━━━━━━\nStage: {stage}\n[{bar}] Growth score: {score}\n\nHar topic complete karne par yeh aur badhega!",
    },
    "tree_wilted_warning": {
        "hindi": "⚠️ लगता है कुछ दिनों से पढ़ाई नहीं हुई — पेड़ मुरझा रहा है। वापस आ जाओ, इसे फिर से हरा-भरा कर दो! 🌱",
        "english": "⚠️ Looks like it's been a few days — your tree is wilting. Come back and help it bloom again! 🌱",
        "hinglish": "⚠️ Lagta hai kuch dinon se padhai nahi hui — tree murjha raha hai. Wapas aa jao, ise phir se hara-bhara kar do! 🌱",
    },

    # ---- Spaced repetition revisions ----
    "revision_due_message": {
        "hindi": "🧠 <b>रिवीजन टाइम!</b> ({interval})\n\n📌 <b>{topic}</b>\n\nक्या यह अभी भी याद है? दोबारा देख लो।",
        "english": "🧠 <b>Revision time!</b> ({interval})\n\n📌 <b>{topic}</b>\n\nStill remember this? Give it a quick review.",
        "hinglish": "🧠 <b>Revision time!</b> ({interval})\n\n📌 <b>{topic}</b>\n\nAbhi bhi yaad hai kya? Ek baar dobara dekh lo.",
    },
    "revision_done_button": {
        "hindi": "✅ रिवाइज़ कर लिया",
        "english": "✅ Revised",
        "hinglish": "✅ Revise Kar Liya",
    },
    "revision_marked_done": {
        "hindi": "बढ़िया! रिवीजन दर्ज हो गया। 🧠",
        "english": "Great! Revision logged. 🧠",
        "hinglish": "Badhiya! Revision record ho gaya. 🧠",
    },
    "revisions_header": {
        "hindi": "🧠 <b>आपके पेंडिंग रिवीजन</b>\n━━━━━━━━━━",
        "english": "🧠 <b>Your pending revisions</b>\n━━━━━━━━━━",
        "hinglish": "🧠 <b>Aapke pending revisions</b>\n━━━━━━━━━━",
    },
    "cancel_done": {
        "hindi": "❌ ठीक है, जो भी चल रहा था वो रोक दिया। जब चाहें दोबारा शुरू कर सकते हैं।",
        "english": "❌ Okay, cancelled whatever was in progress. Start again anytime.",
        "hinglish": "❌ Theek hai, jo bhi chal raha tha wo rok diya. Jab chaho dobara shuru kar sakte ho.",
    },
    "cancel_nothing_active": {
        "hindi": "अभी कुछ भी चल नहीं रहा था जिसे रोका जाए।",
        "english": "Nothing was in progress to cancel.",
        "hinglish": "Abhi kuch bhi chal nahi raha tha jise cancel kiya jaaye.",
    },
    "stale_callback": {
        "hindi": "यह बटन अब काम नहीं करेगा — कृपया /start भेजकर फिर से शुरू करें।",
        "english": "This button isn't valid anymore — please send /start to begin again.",
        "hinglish": "Yeh button ab kaam nahi karega — kripya /start bhejkar phir se shuru karein.",
    },
    "revisions_empty": {
        "hindi": "अभी कोई रिवीजन पेंडिंग नहीं है। जैसे ही कोई टॉपिक पूरा करोगे, यहां रिवीजन शेड्यूल हो जाएंगे।",
        "english": "No revisions pending right now. As you complete topics, revisions will get scheduled here automatically.",
        "hinglish": "Abhi koi revision pending nahi hai. Jaise hi koi topic complete karoge, yahan revisions automatically schedule ho jayenge.",
    },

    # ---- Mock test logging ----
    "mt_ask_platform": {
        "hindi": "📝 Step {n}/{total} — यह टेस्ट किस प्लेटफॉर्म पर दिया था? (जैसे Testbook, PW, Unacademy)\n(ya 'skip' bhejo)",
        "english": "📝 Step {n}/{total} — Which platform was this test on? (e.g. Testbook, PW, Unacademy)\n(or send 'skip')",
        "hinglish": "📝 Step {n}/{total} — Yeh test kis platform pe diya tha? (jaise Testbook, PW, Unacademy)\n(ya 'skip' bhejo)",
    },
    "mt_ask_scope_type": {
        "hindi": "🎯 Step {n}/{total} — यह फुल सिलेबस टेस्ट था या किसी सब्जेक्ट/टॉपिक का?",
        "english": "🎯 Step {n}/{total} — Was this a full syllabus test, or subject/topic-specific?",
        "hinglish": "🎯 Step {n}/{total} — Yeh full syllabus test tha ya kisi subject/topic ka?",
    },
    "mt_ask_scope_breadth": {
        "hindi": "📚 Step {n}/{total} — पूरा सब्जेक्ट था या सिर्फ 1-2 चैप्टर/टॉपिक?",
        "english": "📚 Step {n}/{total} — Was it the whole subject, or just 1-2 chapters/topics?",
        "hinglish": "📚 Step {n}/{total} — Pura subject tha ya sirf 1-2 chapters/topics?",
    },
    "mt_ask_scope_detail_subject": {
        "hindi": "📗 कौनसा सब्जेक्ट था?\n(ya 'skip' bhejo)",
        "english": "📗 Which subject was it?\n(or send 'skip')",
        "hinglish": "📗 Konsa subject tha?\n(ya 'skip' bhejo)",
    },
    "mt_ask_scope_detail_chapters": {
        "hindi": "📄 कौनसा सब्जेक्ट और कौनसे चैप्टर/टॉपिक थे?\n(ya 'skip' bhejo)",
        "english": "📄 Which subject and which chapters/topics?\n(or send 'skip')",
        "hinglish": "📄 Konsa subject aur konse chapters/topics the?\n(ya 'skip' bhejo)",
    },
    "mt_ask_duration": {
        "hindi": "⏱ Step {n}/{total} — टेस्ट कितने मिनट का था? (सिर्फ नंबर भेजिए)\n(ya 'skip' bhejo)",
        "english": "⏱ Step {n}/{total} — How many minutes was the test? (just the number)\n(or send 'skip')",
        "hinglish": "⏱ Step {n}/{total} — Test kitne minute ka tha? (sirf number bhejiye)\n(ya 'skip' bhejo)",
    },
    "mt_ask_total_questions": {
        "hindi": "🔢 Step {n}/{total} — कुल कितने सवाल थे?\n(ya 'skip' bhejo)",
        "english": "🔢 Step {n}/{total} — How many total questions were there?\n(or send 'skip')",
        "hinglish": "🔢 Step {n}/{total} — Kitne total questions the?\n(ya 'skip' bhejo)",
    },
    "mt_ask_total_marks": {
        "hindi": "🏆 Step {n}/{total} — टेस्ट कितने मार्क्स का था?\n(ya 'skip' bhejo)",
        "english": "🏆 Step {n}/{total} — How many total marks was the test out of?\n(or send 'skip')",
        "hinglish": "🏆 Step {n}/{total} — Test kitne marks ka tha?\n(ya 'skip' bhejo)",
    },
    "mt_ask_negative_marking": {
        "hindi": "➖ Step {n}/{total} — नेगेटिव मार्किंग क्या थी? (जैसे -1/4, -0.25, ya 'none')\n(ya 'skip' bhejo)",
        "english": "➖ Step {n}/{total} — What was the negative marking? (e.g. -1/4, -0.25, or 'none')\n(or send 'skip')",
        "hinglish": "➖ Step {n}/{total} — Negative marking kya thi? (jaise -1/4, -0.25, ya 'none')\n(ya 'skip' bhejo)",
    },
    "mt_ask_attempted": {
        "hindi": "✍️ Step {n}/{total} — कितने सवाल अटेम्प्ट किए?\n(ya 'skip' bhejo)",
        "english": "✍️ Step {n}/{total} — How many questions did you attempt?\n(or send 'skip')",
        "hinglish": "✍️ Step {n}/{total} — Kitne questions attempt kiye?\n(ya 'skip' bhejo)",
    },
    "mt_invalid_attempted": {
        "hindi": "यह total questions ({total}) से ज़्यादा नहीं हो सकता। सही नंबर भेजिए, ya 'skip' bhejo.",
        "english": "This can't be more than the total questions ({total}). Send a valid number, or 'skip'.",
        "hinglish": "Yeh total questions ({total}) se zyada nahi ho sakta. Sahi number bhejiye, ya 'skip' bhejo.",
    },
    "mt_ask_wrong": {
        "hindi": "❌ Step {n}/{total} — कितने सवाल गलत हुए?\n(ya 'skip' bhejo)",
        "english": "❌ Step {n}/{total} — How many were wrong?\n(or send 'skip')",
        "hinglish": "❌ Step {n}/{total} — Kitne questions wrong hue?\n(ya 'skip' bhejo)",
    },
    "mt_invalid_wrong": {
        "hindi": "यह attempted questions ({attempted}) से ज़्यादा नहीं हो सकता। सही नंबर भेजिए, ya 'skip' bhejo.",
        "english": "This can't be more than attempted questions ({attempted}). Send a valid number, or 'skip'.",
        "hinglish": "Yeh attempted questions ({attempted}) se zyada nahi ho sakta. Sahi number bhejiye, ya 'skip' bhejo.",
    },
    "mt_ask_skipped": {
        "hindi": "⏭ Step {n}/{total} — कितने सवाल छोड़े (skip किए)?\n(ya 'skip' bhejo)",
        "english": "⏭ Step {n}/{total} — How many questions did you skip?\n(or send 'skip')",
        "hinglish": "⏭ Step {n}/{total} — Kitne questions skip kiye?\n(ya 'skip' bhejo)",
    },
    "mt_ask_percentile": {
        "hindi": "📈 Step {n}/{total} — कितनी percentile आई?\n(ya 'skip' bhejo)",
        "english": "📈 Step {n}/{total} — What percentile did you get?\n(or send 'skip')",
        "hinglish": "📈 Step {n}/{total} — Kitni percentile aayi?\n(ya 'skip' bhejo)",
    },
    "mt_invalid_percentile": {
        "hindi": "Percentile 0 se 100 ke beech honi chahiye. Sahi number bhejiye, ya 'skip' bhejo.",
        "english": "Percentile should be between 0 and 100. Send a valid number, or 'skip'.",
        "hinglish": "Percentile 0 se 100 ke beech honi chahiye. Sahi number bhejiye, ya 'skip' bhejo.",
    },
    "mt_ask_rank": {
        "hindi": "🏅 Step {n}/{total} — कौनसी रैंक आई?\n(ya 'skip' bhejo)",
        "english": "🏅 Step {n}/{total} — What rank did you get?\n(or send 'skip')",
        "hinglish": "🏅 Step {n}/{total} — Kaunsi rank aayi?\n(ya 'skip' bhejo)",
    },
    "mt_ask_weak_topics": {
        "hindi": "⚠️ Step {n}/{total} — कौनसे टॉपिक weak लगे?\n(ya 'skip' bhejo)",
        "english": "⚠️ Step {n}/{total} — Which topics felt weak?\n(or send 'skip')",
        "hinglish": "⚠️ Step {n}/{total} — Konse topics weak lage?\n(ya 'skip' bhejo)",
    },
    "mt_ask_average_topics": {
        "hindi": "⚖️ Step {n}/{total} — कौनसे टॉपिक average लगे?\n(ya 'skip' bhejo)",
        "english": "⚖️ Step {n}/{total} — Which topics felt average?\n(or send 'skip')",
        "hinglish": "⚖️ Step {n}/{total} — Konse topics average lage?\n(ya 'skip' bhejo)",
    },
    "mt_ask_strong_topics": {
        "hindi": "💪 Step {n}/{total} — कौनसे टॉपिक strong लगे?\n(ya 'skip' bhejo)",
        "english": "💪 Step {n}/{total} — Which topics felt strong?\n(or send 'skip')",
        "hinglish": "💪 Step {n}/{total} — Konse topics strong lage?\n(ya 'skip' bhejo)",
    },
    "mt_ask_test_date": {
        "hindi": "📅 Step {n}/{total} — यह टेस्ट किस तारीख को दिया था? (DD-MM-YYYY, ya 'aaj')\n(ya 'skip' bhejo aaj ke liye)",
        "english": "📅 Step {n}/{total} — What date did you take this test? (DD-MM-YYYY, or 'today')\n(or send 'skip' for today)",
        "hinglish": "📅 Step {n}/{total} — Yeh test kis date ko diya tha? (DD-MM-YYYY, ya 'aaj')\n(ya 'skip' bhejo aaj ke liye)",
    },
    "mt_invalid_test_date": {
        "hindi": "तारीख समझ नहीं आई। DD-MM-YYYY फॉर्मेट में भेजिए (जैसे 11-07-2026), ya 'aaj'.",
        "english": "Couldn't understand that date. Send it as DD-MM-YYYY (e.g. 11-07-2026), or 'today'.",
        "hinglish": "Date samajh nahi aayi. DD-MM-YYYY format mein bhejiye (jaise 11-07-2026), ya 'aaj'.",
    },
    "mt_invalid_text": {
        "hindi": "कृपया 1-200 अक्षरों का सही जवाब भेजिए, ya 'skip' bhejo.",
        "english": "Please send a valid answer (1-200 characters), or send 'skip'.",
        "hinglish": "Kripya 1-200 characters ka sahi jawab bhejiye, ya 'skip' bhejo.",
    },
    "mt_invalid_number": {
        "hindi": "कृपया एक सही नंबर भेजिए (0 ya usse zyada), ya 'skip' bhejo.",
        "english": "Please send a valid number (0 or more), or send 'skip'.",
        "hinglish": "Kripya ek sahi number bhejiye (0 ya usse zyada), ya 'skip' bhejo.",
    },
    "mt_saved": {
        "hindi": "✅ <b>Mock test log ho gaya!</b>",
        "english": "✅ <b>Mock test logged!</b>",
        "hinglish": "✅ <b>Mock test log ho gaya!</b>",
    },
    "mt_detail_block": {
        "hindi": (
            "📝 <b>Mock Test Details</b>\n━━━━━━━━━━\n"
            "📅 Date: {date}\n"
            "🏢 Platform: {platform}\n"
            "🎯 Scope: {scope}\n"
            "⏱ Duration: {duration} min\n"
            "🔢 Questions: {total_q} • Marks: {total_marks}\n"
            "➖ Negative marking: {negative}\n"
            "✍️ Attempted: {attempted} • ✅ Correct: {correct} • ❌ Wrong: {wrong} • ⏭ Skipped: {skipped}\n"
            "📈 Percentile: {percentile} • 🏅 Rank: {rank}\n\n"
            "💪 Strong: {strong}\n"
            "⚖️ Average: {average}\n"
            "⚠️ Weak: {weak}"
        ),
        "english": (
            "📝 <b>Mock Test Details</b>\n━━━━━━━━━━\n"
            "📅 Date: {date}\n"
            "🏢 Platform: {platform}\n"
            "🎯 Scope: {scope}\n"
            "⏱ Duration: {duration} min\n"
            "🔢 Questions: {total_q} • Marks: {total_marks}\n"
            "➖ Negative marking: {negative}\n"
            "✍️ Attempted: {attempted} • ✅ Correct: {correct} • ❌ Wrong: {wrong} • ⏭ Skipped: {skipped}\n"
            "📈 Percentile: {percentile} • 🏅 Rank: {rank}\n\n"
            "💪 Strong: {strong}\n"
            "⚖️ Average: {average}\n"
            "⚠️ Weak: {weak}"
        ),
        "hinglish": (
            "📝 <b>Mock Test Details</b>\n━━━━━━━━━━\n"
            "📅 Date: {date}\n"
            "🏢 Platform: {platform}\n"
            "🎯 Scope: {scope}\n"
            "⏱ Duration: {duration} min\n"
            "🔢 Questions: {total_q} • Marks: {total_marks}\n"
            "➖ Negative marking: {negative}\n"
            "✍️ Attempted: {attempted} • ✅ Correct: {correct} • ❌ Wrong: {wrong} • ⏭ Skipped: {skipped}\n"
            "📈 Percentile: {percentile} • 🏅 Rank: {rank}\n\n"
            "💪 Strong: {strong}\n"
            "⚖️ Average: {average}\n"
            "⚠️ Weak: {weak}"
        ),
    },
    "mt_list_header": {
        "hindi": "📝 <b>Aapke Mock Tests</b> ({count})\n",
        "english": "📝 <b>Your Mock Tests</b> ({count})\n",
        "hinglish": "📝 <b>Aapke Mock Tests</b> ({count})\n",
    },
    "mt_list_empty": {
        "hindi": "अभी तक कोई mock test log नहीं हुआ। /addmocktest se shuru kijiye!",
        "english": "No mock tests logged yet. Start with /addmocktest!",
        "hinglish": "Abhi tak koi mock test log nahi hua. /addmocktest se shuru kijiye!",
    },
    "mt_tap_hint": {
        "hindi": "🔍 पूरी डिटेल्स देखने के लिए नीचे नंबर पर टैप कीजिए:",
        "english": "🔍 Tap a number below to see full details:",
        "hinglish": "🔍 Poori details dekhne ke liye neeche number pe tap kijiye:",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    """Get translated text for a key + language, with optional formatting."""
    lang = lang if lang in ("hindi", "english", "hinglish") else "hinglish"
    text = TEXT.get(key, {}).get(lang, TEXT.get(key, {}).get("hinglish", key))
    return text.format(**kwargs) if kwargs else text
