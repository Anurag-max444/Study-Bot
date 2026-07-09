"""
Sab user-facing text yaha hai, teeno languages me.
Naya text add karna ho to teeno dict me same key ke saath add karo.

Tone guide: Hinglish version bhi utni hi respectful/professional honi chahiye
jitni Hindi/English — 'aap' use karo, casual 'tu/tera' avoid karo.
"""

TEXT = {
    "welcome": {
        "hindi": "नमस्ते {name}! 📚 मैं Study Sync हूँ, आपका स्टडी पार्टनर। सभी कमांड्स के लिए /help टाइप कीजिए।",
        "english": "Hello {name}! 📚 I'm Study Sync, your study partner. Type /help to see everything I can do.",
        "hinglish": "Namaste {name}! 📚 Main Study Sync hoon, aapka study partner. Sabhi commands dekhne ke liye /help type kijiye.",
    },
    "ask_language": {
        "hindi": "सबसे पहले बताइए, आप किस भाषा में बात करना पसंद करेंगे?",
        "english": "First, which language would you prefer to chat in?",
        "hinglish": "Sabse pehle bataiye, aap kis language mein baat karna pasand karenge?",
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
        "hindi": "📊 <b>{name} की प्रोग्रेस</b>\n\n🔥 स्ट्रीक: <b>{streak} दिन</b> (सबसे लंबी: {longest})\n",
        "english": "📊 <b>{name}'s progress</b>\n\n🔥 Streak: <b>{streak} days</b> (longest: {longest})\n",
        "hinglish": "📊 <b>{name} ka progress</b>\n\n🔥 Streak: <b>{streak} din</b> (sabse lambi: {longest})\n",
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
            "✅ <b>सेटअप पूरा हो गया, {name}!</b>\n\n"
            "🎯 Exam: {exam}\n"
            "⏱ रोज़ाना लक्ष्य: {hours} घंटे\n\n"
            "अब /addtask से अपना पहला स्टडी सेशन शेड्यूल कीजिए, या नीचे दिए बटन इस्तेमाल कीजिए।"
        ),
        "english": (
            "✅ <b>Setup complete, {name}!</b>\n\n"
            "🎯 Exam: {exam}\n"
            "⏱ Daily target: {hours} hours\n\n"
            "Use /addtask to schedule your first study session, or use the buttons below."
        ),
        "hinglish": (
            "✅ <b>Setup poora ho gaya, {name}!</b>\n\n"
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
    "mytopics_header": {
        "hindi": "📋 <b>आपके शेड्यूल्ड टॉपिक</b>\n",
        "english": "📋 <b>Your scheduled topics</b>\n",
        "hinglish": "📋 <b>Aapke scheduled topics</b>\n",
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
        "hindi": "📊 <b>पिछले {days} दिन का स्टडी लॉग</b>\n\n",
        "english": "📊 <b>Study log — last {days} days</b>\n\n",
        "hinglish": "📊 <b>Pichhle {days} din ka study log</b>\n\n",
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
            "🤖 *Study Sync — कमांड गाइड*\n\n"
            "*/start* — बॉट सेटअप करें (भाषा, नाम, एग्ज़ाम, सिलेबस)\n"
            "*/addtask* — खुद का टॉपिक + समय + अवधि सेट करें\n"
            "*/mytopics* — अपने शेड्यूल्ड टॉपिक देखें\n"
            "*/removetask HH:MM* — कोई शेड्यूल्ड टॉपिक हटाएं\n"
            "*/studylog* — पिछले 7 दिन का पढ़ाई का रिकॉर्ड देखें\n"
            "*/revisions* — अपने पेंडिंग रिवीजन देखें (spaced repetition)\n"
            "*/progress* — स्ट्रीक, शील्ड और बैज देखें\n"
            "*/badges* — अपने सारे अचीवमेंट बैज देखें\n"
            "*/mytree* — अपना Study Tree देखें\n"
            "*/pdf* (या /extractquestions) — किसी PDF से MCQ questions निकालें\n"
            "*/clear* — पुराने मैसेज साफ़ करें\n"
            "*/help* — यह गाइड फिर से देखें\n\n"
            "📌 *बॉट कैसे काम करता है:*\n"
            "• /addtask से अपना टॉपिक, समय और अवधि सेट कीजिए — बॉट सही समय पर याद दिलाएगा\n"
            "• समय पूरा होने पर बॉट पूछेगा कि पूरा हुआ या नहीं\n"
            "• हर पूरे किए गए सेशन के लिए 1/3/7/15 दिन बाद रिवीजन रिमाइंडर अपने आप शेड्यूल होंगे\n"
            "• पुराने पेपर/नोट्स की PDF भेजकर questions अलग निकलवा सकते हैं\n"
            "• नीचे दिए क्विक-मेनू बटन से भी सबसे इस्तेमाल होने वाले कमांड्स एक टैप में खुलते हैं"
        ),
        "english": (
            "🤖 *Study Sync — Command Guide*\n\n"
            "*/start* — Set up the bot (language, name, exam, syllabus)\n"
            "*/addtask* — Set your own topic + time + duration\n"
            "*/mytopics* — View your scheduled topics\n"
            "*/removetask HH:MM* — Remove a scheduled topic\n"
            "*/studylog* — View your last 7 days of study history\n"
            "*/revisions* — View pending revisions (spaced repetition)\n"
            "*/progress* — View your streak, shields, and badges\n"
            "*/badges* — View all your earned achievement badges\n"
            "*/mytree* — View your Study Tree\n"
            "*/pdf* (or /extractquestions) — Extract MCQ questions from a PDF\n"
            "*/clear* — Clear old messages from this chat\n"
            "*/help* — Show this guide again\n\n"
            "📌 *How the bot works:*\n"
            "• Use /addtask to set your topic, start time, and duration — the bot reminds you right on time\n"
            "• Once the duration is up, the bot checks in to confirm you're done\n"
            "• Every completed session automatically schedules revision reminders at 1/3/7/15 days\n"
            "• Send a PDF of practice papers/notes to extract clean, standalone questions\n"
            "• The quick-menu buttons below give you the most-used commands in one tap"
        ),
        "hinglish": (
            "🤖 *Study Sync — Command Guide*\n\n"
            "*/start* — Bot setup kijiye (language, naam, exam, syllabus)\n"
            "*/addtask* — Apna khud ka topic + time + duration set kijiye\n"
            "*/mytopics* — Apne scheduled topics dekhiye\n"
            "*/removetask HH:MM* — Koi scheduled topic hataiye\n"
            "*/studylog* — Pichhle 7 din ka padhai ka record dekhiye\n"
            "*/revisions* — Apne pending revisions dekhiye (spaced repetition)\n"
            "*/progress* — Apni streak, shields aur badges dekhiye\n"
            "*/badges* — Apne saare earned achievement badges dekhiye\n"
            "*/mytree* — Apna Study Tree dekhiye\n"
            "*/pdf* (ya /extractquestions) — Kisi PDF se MCQ questions nikaliye\n"
            "*/clear* — Is chat ke purane messages saaf kijiye\n"
            "*/help* — Yeh guide dobara dekhiye\n\n"
            "📌 *Bot kaise kaam karta hai:*\n"
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
        "hindi": "🎖️ <b>आपके बैज</b> ({count}/{total})\n",
        "english": "🎖️ <b>Your badges</b> ({count}/{total})\n",
        "hinglish": "🎖️ <b>Aapke badges</b> ({count}/{total})\n",
    },

    # ---- Study Tree ----
    "tree_caption": {
        "hindi": "🌳 <b>आपका Study Tree</b>\n\nStage: {stage}\n[{bar}] Growth Score: {score}\n\nहर टॉपिक पूरा करने पर यह और बढ़ेगा!",
        "english": "🌳 <b>Your Study Tree</b>\n\nStage: {stage}\n[{bar}] Growth score: {score}\n\nIt grows a little more every time you complete a topic!",
        "hinglish": "🌳 <b>Aapka Study Tree</b>\n\nStage: {stage}\n[{bar}] Growth score: {score}\n\nHar topic complete karne par yeh aur badhega!",
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
        "hindi": "🧠 <b>आपके पेंडिंग रिवीजन</b>\n",
        "english": "🧠 <b>Your pending revisions</b>\n",
        "hinglish": "🧠 <b>Aapke pending revisions</b>\n",
    },
    "revisions_empty": {
        "hindi": "अभी कोई रिवीजन पेंडिंग नहीं है। जैसे ही कोई टॉपिक पूरा करोगे, यहां रिवीजन शेड्यूल हो जाएंगे।",
        "english": "No revisions pending right now. As you complete topics, revisions will get scheduled here automatically.",
        "hinglish": "Abhi koi revision pending nahi hai. Jaise hi koi topic complete karoge, yahan revisions automatically schedule ho jayenge.",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    """Get translated text for a key + language, with optional formatting."""
    lang = lang if lang in ("hindi", "english", "hinglish") else "hinglish"
    text = TEXT.get(key, {}).get(lang, TEXT.get(key, {}).get("hinglish", key))
    return text.format(**kwargs) if kwargs else text
