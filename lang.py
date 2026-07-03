"""
Sab user-facing text yaha hai, teeno languages me.
Naya text add karna ho to teeno dict me same key ke saath add karo.
"""

TEXT = {
    "welcome": {
        "hindi": "नमस्ते {name}! 📚 मैं आपका स्टडी बडी बॉट हूँ। रोज सुबह आपको पढ़ाई का प्लान भेजूंगा और शाम को प्रोग्रेस पूछूंगा।",
        "english": "Hey {name}! 📚 I'm your Study Buddy bot. I'll send you a daily study plan every morning and check your progress in the evening.",
        "hinglish": "Hey {name}! 📚 Main tera Study Buddy bot hu. Roz subah study plan bhejunga aur sham ko progress puchunga.",
    },
    "ask_language": {
        "hindi": "पहले बताओ, आप किस भाषा में बात करना पसंद करेंगे?",
        "english": "First, which language would you like to chat in?",
        "hinglish": "Sabse pehle batao, kaunsi language me baat karni hai?",
    },
    "ask_name": {
        "hindi": "आपका नाम क्या है?",
        "english": "What's your name?",
        "hinglish": "Tera naam kya hai?",
    },
    "ask_exam": {
        "hindi": "आप किस एग्जाम की तैयारी कर रहे हो?",
        "english": "Which exam are you preparing for?",
        "hinglish": "Kaunse exam ki tayyari kar raha hai?",
    },
    "ask_syllabus_pdf": {
        "hindi": "अगर आपके पास सिलेबस की PDF है तो भेज दो, वरना 'skip' टाइप करो — मैं डिफॉल्ट सिलेबस लोड कर दूंगा।",
        "english": "If you have a syllabus PDF, send it here, otherwise type 'skip' — I'll load the default syllabus.",
        "hinglish": "Agar syllabus ki PDF hai to bhej de, warna 'skip' type kar de — main default syllabus load kar dunga.",
    },
    "ask_hours": {
        "hindi": "रोज कितने घंटे पढ़ाई कर सकते हो? (सिर्फ नंबर भेजो, जैसे 4)",
        "english": "How many hours can you study daily? (just send the number, e.g. 4)",
        "hinglish": "Roz kitne ghante padh sakta hai? (bas number bhej, jaise 4)",
    },
    "ask_reminder_time": {
        "hindi": "सुबह किस टाइम रिमाइंडर चाहिए? (24hr फॉर्मेट में, जैसे 07:00)",
        "english": "What time should I send your morning reminder? (24hr format, e.g. 07:00)",
        "hinglish": "Subah kis time reminder chahiye? (24hr format me, jaise 07:00)",
    },
    "ask_evening_time": {
        "hindi": "शाम को किस टाइम प्रोग्रेस चेकलिस्ट चाहिए? (24hr फॉर्मेट, जैसे 19:00)",
        "english": "What time should I send your evening progress checklist? (24hr format, e.g. 19:00)",
        "hinglish": "Sham ko kis time progress checklist chahiye? (24hr format, jaise 19:00)",
    },
    "morning_plan_header": {
        "hindi": "☀️ सुप्रभात {name}! आज का प्लान:",
        "english": "☀️ Good morning {name}! Today's plan:",
        "hinglish": "☀️ Good morning {name}! Aaj ka plan:",
    },
    "evening_checklist_header": {
        "hindi": "🌙 शाम हो गई! आज जो पूरा किया उसे टिक करो:",
        "english": "🌙 Evening check-in! Tick off what you completed today:",
        "hinglish": "🌙 Sham ho gayi! Aaj jo complete kiya wo tick kar de:",
    },
    "no_topics_left": {
        "hindi": "वाह! आपके सिलेबस के सारे टॉपिक कवर हो गए 🎉 नया सिलेबस जोड़ने के लिए /addsyllabus टाइप करो।",
        "english": "Wow! You've covered your entire syllabus 🎉 Type /addsyllabus to add more topics.",
        "hinglish": "Wah! Tera pura syllabus cover ho gaya 🎉 Naya syllabus add karne ke liye /addsyllabus type kar.",
    },
    "progress_saved": {
        "hindi": "प्रोग्रेस सेव हो गया! कल फिर मिलते हैं 💪",
        "english": "Progress saved! See you tomorrow 💪",
        "hinglish": "Progress save ho gaya! Kal milte hai 💪",
    },
    "progress_header": {
        "hindi": "📊 {name} की प्रोग्रेस रिपोर्ट\n\n🔥 स्ट्रीक: {streak} दिन (सबसे लंबी: {longest})\n",
        "english": "📊 {name}'s Progress Report\n\n🔥 Streak: {streak} days (longest: {longest})\n",
        "hinglish": "📊 {name} ki Progress Report\n\n🔥 Streak: {streak} din (longest: {longest})\n",
    },
    "ask_question_pdf": {
        "hindi": "जिस PDF से questions निकालने हैं वो भेज दो (MCQ format वाली — options a,b,c,d के साथ)।",
        "english": "Send the PDF you want questions extracted from (MCQ format — with a,b,c,d options).",
        "hinglish": "Jis PDF se questions nikalne hai wo bhej de (MCQ format wali — options a,b,c,d ke saath).",
    },
    "extracting_in_progress": {
        "hindi": "PDF प्रोसेस हो रही है, थोड़ा रुको... ⏳",
        "english": "Processing your PDF, hang on... ⏳",
        "hinglish": "PDF process ho rahi hai, thoda ruk... ⏳",
    },
    "no_questions_found": {
        "hindi": "माफ़ करना, इस PDF में मुझे कोई पहचाने जाने लायक MCQ फॉर्मेट नहीं मिला। सुनिश्चित करो कि questions 'Q1.' या '1)' जैसे शुरू हो और options (a)(b)(c)(d) फॉर्मेट में हो।",
        "english": "Sorry, I couldn't detect any recognizable MCQ format in this PDF. Make sure questions start like 'Q1.' or '1)' and options are in (a)(b)(c)(d) format.",
        "hinglish": "Sorry, is PDF me mujhe koi pehchana jaane layak MCQ format nahi mila. Check kar ki questions 'Q1.' ya '1)' se start ho aur options (a)(b)(c)(d) format me ho.",
    },
    "extraction_done": {
        "hindi": "हो गया! {count} questions मिले, PDF में साफ़-सुथरे तरीके से लगा दिए हैं (आखिरी पेज पर answer key भी है) ✅",
        "english": "Done! Found {count} questions, cleanly formatted into a PDF (answer key on the last page too) ✅",
        "hinglish": "Ho gaya! {count} questions mile, PDF me clean format kar diya hai (last page pe answer key bhi hai) ✅",
    },
    "no_streak_yet": {
        "hindi": "अभी तक कोई स्ट्रीक शुरू नहीं हुई। आज पहला टॉपिक पूरा करके शुरू करो!",
        "english": "No streak started yet. Complete your first topic today to begin!",
        "hinglish": "Abhi tak koi streak start nahi hui. Aaj pehla topic complete karke shuru kar!",
    },
    "setup_done": {
        "hindi": "सेटअप पूरा हो गया! ✅ अब रोज सुबह {time} बजे आपको प्लान मिलेगा।",
        "english": "Setup complete! ✅ You'll get your daily plan at {time} every morning.",
        "hinglish": "Setup ho gaya! ✅ Roz subah {time} baje tujhe plan milega.",
    },
    "invalid_number": {
        "hindi": "कृपया सिर्फ नंबर भेजो।",
        "english": "Please send only a number.",
        "hinglish": "Please sirf number bhej.",
    },
    "invalid_time": {
        "hindi": "सही फॉर्मेट में भेजो, जैसे 07:00",
        "english": "Send it in correct format, e.g. 07:00",
        "hinglish": "Sahi format me bhej, jaise 07:00",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    """Get translated text for a key + language, with optional formatting."""
    lang = lang if lang in ("hindi", "english", "hinglish") else "hinglish"
    text = TEXT.get(key, {}).get(lang, TEXT.get(key, {}).get("hinglish", key))
    return text.format(**kwargs) if kwargs else text
