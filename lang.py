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
        "hindi": "आपका नाम क्या है?",
        "english": "What's your name?",
        "hinglish": "Aapka naam kya hai?",
    },
    "ask_exam": {
        "hindi": "आप किस परीक्षा की तैयारी कर रहे हैं?",
        "english": "Which exam are you preparing for?",
        "hinglish": "Aap kis exam ki taiyaari kar rahe hain?",
    },
    "ask_syllabus_pdf": {
        "hindi": "अगर आपके पास सिलेबस की PDF है तो कृपया भेज दीजिए, वरना 'skip' टाइप कीजिए — मैं डिफ़ॉल्ट सिलेबस लोड कर दूंगा।",
        "english": "If you have a syllabus PDF, please send it here, otherwise type 'skip' — I'll load the default syllabus for you.",
        "hinglish": "Agar aapke paas syllabus ki PDF hai to kripya bhej dijiye, warna 'skip' type kijiye — main default syllabus load kar dunga.",
    },
    "ask_hours": {
        "hindi": "आप रोज़ कितने घंटे पढ़ाई कर सकते हैं? (सिर्फ नंबर भेजिए, जैसे 4)",
        "english": "How many hours can you study daily? (please send just the number, e.g. 4)",
        "hinglish": "Aap roz kitne ghante study kar sakte hain? (bas number bhejiye, jaise 4)",
    },
    "ask_reminder_time": {
        "hindi": "सुबह किस समय रिमाइंडर चाहिए? (24hr फॉर्मेट में, जैसे 07:00)",
        "english": "What time would you like your morning reminder? (24hr format, e.g. 07:00)",
        "hinglish": "Subah kis time reminder chahiye? (24hr format mein, jaise 07:00)",
    },
    "ask_evening_time": {
        "hindi": "शाम को किस समय प्रोग्रेस चेकलिस्ट चाहिए? (24hr फॉर्मेट, जैसे 19:00)",
        "english": "What time should I send your evening progress checklist? (24hr format, e.g. 19:00)",
        "hinglish": "Shaam ko kis time progress checklist chahiye? (24hr format, jaise 19:00)",
    },
    "morning_plan_header": {
        "hindi": "☀️ सुप्रभात {name}! आज का प्लान तैयार है:",
        "english": "☀️ Good morning {name}! Here's today's plan:",
        "hinglish": "☀️ Good morning {name}! Aaj ka plan taiyaar hai:",
    },
    "evening_checklist_header": {
        "hindi": "🌙 शाम हो गई! आज जो पूरा किया है उसे टिक कर दीजिए:",
        "english": "🌙 Evening check-in! Please tick off what you completed today:",
        "hinglish": "🌙 Shaam ho gayi! Aaj jo complete kiya hai use tick kar dijiye:",
    },
    "no_topics_left": {
        "hindi": "बधाई हो! आपके सिलेबस के सारे टॉपिक कवर हो गए 🎉 नया सिलेबस जोड़ने के लिए /addsyllabus टाइप कीजिए।",
        "english": "Congratulations! You've covered your entire syllabus 🎉 Type /addsyllabus to add more topics.",
        "hinglish": "Badhai ho! Aapka poora syllabus cover ho gaya 🎉 Naya syllabus add karne ke liye /addsyllabus type kijiye.",
    },
    "progress_saved": {
        "hindi": "प्रोग्रेस सेव हो गया! कल फिर मिलते हैं 💪",
        "english": "Progress saved! See you tomorrow 💪",
        "hinglish": "Progress save ho gaya! Kal phir milte hain 💪",
    },
    "progress_header": {
        "hindi": "📊 {name} की प्रोग्रेस रिपोर्ट\n\n🔥 स्ट्रीक: {streak} दिन (सबसे लंबी: {longest})\n",
        "english": "📊 {name}'s Progress Report\n\n🔥 Streak: {streak} days (longest: {longest})\n",
        "hinglish": "📊 {name} ki Progress Report\n\n🔥 Streak: {streak} din (sabse lambi: {longest})\n",
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
        "hindi": "सेटअप पूरा हो गया! ✅ अब रोज़ सुबह {time} बजे आपको प्लान मिलेगा।",
        "english": "Setup complete! ✅ You'll receive your daily plan at {time} every morning.",
        "hinglish": "Setup poora ho gaya! ✅ Ab roz subah {time} baje aapko plan milega.",
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

    # ---- Per-task reminder feature ----
    "addreminder_usage": {
        "hindi": "इस तरह इस्तेमाल कीजिए: /addreminder HH:MM\nउदाहरण: /addreminder 14:30\n\nहर टाइम स्लॉट पर मैं आपको एक नया टॉपिक भेजूंगा, पूरा होने पर तुरंत टिक कर सकते हैं।",
        "english": "Use it like this: /addreminder HH:MM\nExample: /addreminder 14:30\n\nAt each time slot, I'll send you one new topic — you can mark it done right away once completed.",
        "hinglish": "Is tarah use kijiye: /addreminder HH:MM\nExample: /addreminder 14:30\n\nHar time slot par main aapko ek naya topic bhejunga, complete hone par turant tick kar sakte hain.",
    },
    "reminder_added": {
        "hindi": "बढ़िया! {time} बजे का रिमाइंडर जुड़ गया है। इस समय आपको अगला टॉपिक मिलेगा।",
        "english": "Great! A reminder at {time} has been added. You'll receive your next topic at that time.",
        "hinglish": "Badhiya! {time} baje ka reminder add ho gaya hai. Is time par aapko agla topic milega.",
    },
    "reminder_removed": {
        "hindi": "{time} बजे का रिमाइंडर हटा दिया गया है।",
        "english": "The reminder at {time} has been removed.",
        "hinglish": "{time} baje ka reminder remove kar diya gaya hai.",
    },
    "reminder_not_found": {
        "hindi": "इस समय पर कोई रिमाइंडर सेट नहीं मिला। /myreminders से लिस्ट देखिए।",
        "english": "No reminder found at that time. Use /myreminders to see your current list.",
        "hinglish": "Is time par koi reminder set nahi mila. /myreminders se current list dekhiye.",
    },
    "reminder_list_header": {
        "hindi": "⏰ आपके एक्टिव टास्क रिमाइंडर:\n",
        "english": "⏰ Your active task reminders:\n",
        "hinglish": "⏰ Aapke active task reminders:\n",
    },
    "reminder_list_empty": {
        "hindi": "अभी तक कोई टास्क रिमाइंडर सेट नहीं है। /addreminder HH:MM से जोड़िए।",
        "english": "No task reminders set yet. Add one using /addreminder HH:MM.",
        "hinglish": "Abhi tak koi task reminder set nahi hai. /addreminder HH:MM se add kijiye.",
    },
    "task_reminder_header": {
        "hindi": "📖 पढ़ाई का समय हो गया, {name}! अभी इस टॉपिक पर फोकस कीजिए:",
        "english": "📖 Time to study, {name}! Please focus on this topic now:",
        "hinglish": "📖 Study karne ka time ho gaya hai, {name}! Abhi is topic par focus kijiye:",
    },
    "task_all_done_today": {
        "hindi": "शानदार! आज के सारे टॉपिक कवर हो चुके हैं 🎉 कल फिर मिलते हैं।",
        "english": "Excellent! All of today's topics are covered 🎉 See you tomorrow.",
        "hinglish": "Shaandaar! Aaj ke saare topics cover ho chuke hain 🎉 Kal phir milte hain.",
    },
    "mark_done_button": {
        "hindi": "✅ पूरा हुआ",
        "english": "✅ Mark as Done",
        "hinglish": "✅ Complete Kiya",
    },
    "task_time_already_passed": {
        "hindi": "⚠️ ध्यान दें: यह समय आज के लिए निकल चुका है, इसलिए यह टास्क कल इसी समय चलेगा।",
        "english": "⚠️ Note: this time has already passed for today, so this task will trigger tomorrow at this time instead.",
        "hinglish": "⚠️ Dhyan dein: yeh time aaj ke liye nikal chuka hai, isliye yeh task kal isi time par chalega.",
    },
    "task_marked_done": {
        "hindi": "शाबाश, {name}! यह टॉपिक पूरा दर्ज हो गया है। अगला टास्क अगले रिमाइंडर पर मिलेगा।",
        "english": "Well done, {name}! This topic has been marked complete. Your next task will arrive at the next reminder.",
        "hinglish": "Shaabaash, {name}! Yeh topic complete mark ho gaya hai. Agla task agle reminder par milega.",
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
        "hindi": "📋 आपके शेड्यूल्ड टॉपिक:\n",
        "english": "📋 Your scheduled topics:\n",
        "hinglish": "📋 Aapke scheduled topics:\n",
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
        "hindi": "📖 समय हो गया, {name}! अभी शुरू कीजिए:\n\n📌 *{topic}*\n⏱ {duration} मिनट के लिए\n\nमैं {duration} मिनट बाद पूछूंगा कि पूरा हुआ या नहीं।",
        "english": "📖 Time to begin, {name}!\n\n📌 *{topic}*\n⏱ For {duration} minutes\n\nI'll check back in {duration} minutes to see if you're done.",
        "hinglish": "📖 Time ho gaya hai, {name}! Abhi shuru kijiye:\n\n📌 *{topic}*\n⏱ {duration} minute ke liye\n\nMain {duration} minute baad puchunga ki poora hua ya nahi.",
    },
    "task_session_followup": {
        "hindi": "⏰ समय पूरा हो गया! क्या आपने '{topic}' पूरा कर लिया?",
        "english": "⏰ Time's up! Did you finish '{topic}'?",
        "hinglish": "⏰ Time poora ho gaya! Kya aapne '{topic}' poora kar liya?",
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
        "hindi": "📊 पिछले {days} दिन का स्टडी लॉग\n\n",
        "english": "📊 Study log — last {days} days\n\n",
        "hinglish": "📊 Pichhle {days} din ka study log\n\n",
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
            "*/progress* — विषय-वार प्रगति, स्ट्रीक, शील्ड और बैज देखें\n"
            "*/badges* — अपने सारे अचीवमेंट बैज देखें\n"
            "*/mytree* — अपना Study Tree देखें (जो पढ़ाई के साथ grow होता है)\n"
            "*/revisions* — अपने पेंडिंग रिवीजन देखें (spaced repetition)\n"
            "*/pdf* (या /extractquestions) — किसी PDF से MCQ questions निकालकर साफ़-सुथरी PDF बनवाएं\n"
            "*/addreminder HH:MM* — दिन में कोई भी नया टास्क रिमाइंडर जोड़ें\n"
            "*/removereminder HH:MM* — कोई रिमाइंडर हटाएं\n"
            "*/myreminders* — अपने सभी एक्टिव रिमाइंडर देखें\n"
            "*/addtask* — खुद का टॉपिक + समय + अवधि सेट करें (जैसे टाइमटेबल)\n"
            "*/mytopics* — अपने शेड्यूल्ड टॉपिक देखें\n"
            "*/removetask HH:MM* — कोई शेड्यूल्ड टॉपिक हटाएं\n"
            "*/studylog* — पिछले 7 दिन का पढ़ाई का रिकॉर्ड देखें (कितने घंटे, कौन से टॉपिक)\n"
            "*/help* — यह गाइड फिर से देखें\n\n"
            "📌 *बॉट कैसे काम करता है:*\n"
            "• रोज़ सुबह आपको सिलेबस से एक स्टडी प्लान मिलेगा, शाम को उसका चेकलिस्ट\n"
            "• चाहें तो /addreminder से दिन में और भी रिमाइंडर सेट करें — हर एक पर एक नया टॉपिक मिलेगा, तुरंत टिक कर सकते हैं\n"
            "• जब चाहें /progress से देखें कितना सिलेबस कवर हो चुका है\n"
            "• पुराने पेपर/नोट्स की PDF भेजकर questions अलग निकलवा सकते हैं"
        ),
        "english": (
            "🤖 *Study Sync — Command Guide*\n\n"
            "*/start* — Set up the bot (language, name, exam, syllabus)\n"
            "*/progress* — View subject-wise progress, streak, shields, and badges\n"
            "*/badges* — View all your earned achievement badges\n"
            "*/mytree* — View your Study Tree (grows as you study)\n"
            "*/revisions* — View your pending revisions (spaced repetition)\n"
            "*/pdf* (or /extractquestions) — Extract MCQ questions from a PDF into a clean, formatted PDF\n"
            "*/addreminder HH:MM* — Add a new task reminder at any time of day\n"
            "*/removereminder HH:MM* — Remove a reminder\n"
            "*/myreminders* — View all your active reminders\n"
            "*/addtask* — Set your own topic + time + duration (like a timetable entry)\n"
            "*/mytopics* — View your scheduled topics\n"
            "*/removetask HH:MM* — Remove a scheduled topic\n"
            "*/studylog* — View your last 7 days of study history (hours studied, topics covered)\n"
            "*/help* — Show this guide again\n\n"
            "📌 *How the bot works:*\n"
            "• Every morning you get a study plan from your syllabus, and an evening checklist for it\n"
            "• Optionally add more reminders during the day with /addreminder — each one delivers a fresh topic you can mark done instantly\n"
            "• Check /progress anytime to see how much of your syllabus is covered\n"
            "• Send a PDF of practice papers/notes to extract clean, standalone questions"
        ),
        "hinglish": (
            "🤖 *Study Sync — Command Guide*\n\n"
            "*/start* — Bot setup kijiye (language, naam, exam, syllabus)\n"
            "*/progress* — Subject-wise progress, streak, shields aur badges dekhiye\n"
            "*/badges* — Apne saare earned achievement badges dekhiye\n"
            "*/mytree* — Apna Study Tree dekhiye (jo padhai ke saath grow hota hai)\n"
            "*/revisions* — Apne pending revisions dekhiye (spaced repetition)\n"
            "*/pdf* (ya /extractquestions) — Kisi PDF se MCQ questions nikaal kar clean, formatted PDF banwaiye\n"
            "*/addreminder HH:MM* — Din mein kabhi bhi ek naya task reminder add kijiye\n"
            "*/removereminder HH:MM* — Koi reminder hataiye\n"
            "*/myreminders* — Apne saare active reminders dekhiye\n"
            "*/addtask* — Apna khud ka topic + time + duration set kijiye (timetable jaisa)\n"
            "*/mytopics* — Apne scheduled topics dekhiye\n"
            "*/removetask HH:MM* — Koi scheduled topic hataiye\n"
            "*/studylog* — Pichhle 7 din ka padhai ka record dekhiye (kitne ghante, kaunse topics)\n"
            "*/help* — Yeh guide dobara dekhiye\n\n"
            "📌 *Bot kaise kaam karta hai:*\n"
            "• Roz subah aapko syllabus se ek study plan milega, aur shaam ko uska checklist\n"
            "• Chahen to /addreminder se din mein aur reminders set kijiye — har ek par ek naya topic milega, turant tick kar sakte hain\n"
            "• Jab chahe /progress se dekhiye kitna syllabus cover ho chuka hai\n"
            "• Purane papers/notes ki PDF bhej kar usse questions alag nikalwa sakte hain"
        ),
    },

    # ---- Gamification: streak shields + achievement badges ----
    "shields_line": {
        "hindi": "🛡️ शील्ड: {shields}/3\n",
        "english": "🛡️ Shields: {shields}/3\n",
        "hinglish": "🛡️ Shields: {shields}/3\n",
    },
    "badges_summary_line": {
        "hindi": "🎖️ बैज: {count}/{total} अनलॉक\n",
        "english": "🎖️ Badges: {count}/{total} unlocked\n",
        "hinglish": "🎖️ Badges: {count}/{total} unlock hue\n",
    },
    "shield_used_notification": {
        "hindi": "🛡️ आपकी स्ट्रीक बच गई! एक दिन मिस होने पर भी शील्ड ने उसे बचा लिया। बची हुई शील्ड: {remaining}",
        "english": "🛡️ Your streak was saved! A shield covered the missed day. Shields remaining: {remaining}",
        "hinglish": "🛡️ Aapki streak bach gayi! Ek din miss hone par bhi shield ne use bacha liya. Bachi hui shields: {remaining}",
    },
    "badge_earned_notification": {
        "hindi": "🎉 नया बैज अनलॉक हुआ!\n{badge_name}\n\n/badges से सारे बैज देखिए।",
        "english": "🎉 New badge unlocked!\n{badge_name}\n\nSee all your badges with /badges.",
        "hinglish": "🎉 Naya badge unlock hua!\n{badge_name}\n\n/badges se saare badges dekhiye.",
    },
    "badges_header": {
        "hindi": "🎖️ आपके बैज ({count}/{total})\n",
        "english": "🎖️ Your Badges ({count}/{total})\n",
        "hinglish": "🎖️ Aapke Badges ({count}/{total})\n",
    },

    # ---- Study Tree ----
    "tree_caption": {
        "hindi": "🌳 आपका Study Tree\n\nStage: {stage}\nGrowth Score: {score}\n\nहर टॉपिक पूरा करने पर यह और बढ़ेगा!",
        "english": "🌳 Your Study Tree\n\nStage: {stage}\nGrowth Score: {score}\n\nIt grows a little more every time you complete a topic!",
        "hinglish": "🌳 Aapka Study Tree\n\nStage: {stage}\nGrowth Score: {score}\n\nHar topic complete karne par yeh aur badhega!",
    },
    "tree_wilted_warning": {
        "hindi": "⚠️ लगता है कुछ दिनों से पढ़ाई नहीं हुई — पेड़ मुरझा रहा है। वापस आ जाओ, इसे फिर से हरा-भरा कर दो! 🌱",
        "english": "⚠️ Looks like it's been a few days — your tree is wilting. Come back and help it bloom again! 🌱",
        "hinglish": "⚠️ Lagta hai kuch dinon se padhai nahi hui — tree murjha raha hai. Wapas aa jao, ise phir se hara-bhara kar do! 🌱",
    },

    # ---- Spaced repetition revisions ----
    "revision_due_message": {
        "hindi": "🧠 रिवीजन टाइम! ({interval})\n\n📌 {subject}: {topic}\n\nक्या यह अभी भी याद है? दोबारा देख लो।",
        "english": "🧠 Revision time! ({interval})\n\n📌 {subject}: {topic}\n\nStill remember this? Give it a quick review.",
        "hinglish": "🧠 Revision time! ({interval})\n\n📌 {subject}: {topic}\n\nAbhi bhi yaad hai kya? Ek baar dobara dekh lo.",
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
        "hindi": "🧠 आपके पेंडिंग रिवीजन:\n",
        "english": "🧠 Your pending revisions:\n",
        "hinglish": "🧠 Aapke pending revisions:\n",
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
