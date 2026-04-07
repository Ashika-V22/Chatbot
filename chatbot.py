# chatbot.py
# ─────────────────────────────────────────────────────────────────
# This file is the "brain" of the chatbot.
# It contains all the logic for the 5 features:
#   1. Threat explanations
#   2. Phishing detection
#   3. Quiz mode
#   4. Incident reporting
#   5. Smart advice
# ─────────────────────────────────────────────────────────────────

import random

# ── Threat knowledge base ─────────────────────────────────────────
# A dictionary mapping threat keywords to explanations.
THREATS = {
    "phishing": (
        "🎣 <b>Phishing</b> is when attackers send fake emails or messages that look "
        "like they're from trusted sources (banks, Google, etc.) to steal your "
        "passwords or personal info.<br><br>"
        "<b>How to stay safe:</b><br>"
        "• Never click suspicious links in emails<br>"
        "• Check the sender's actual email address carefully<br>"
        "• When in doubt, go directly to the website by typing the URL yourself"
    ),
    "malware": (
        "🦠 <b>Malware</b> (malicious software) is any program designed to damage or "
        "gain unauthorised access to your device. It includes viruses, spyware, "
        "ransomware, and trojans.<br><br>"
        "<b>How to stay safe:</b><br>"
        "• Only download software from official/trusted sources<br>"
        "• Keep your OS and antivirus updated<br>"
        "• Don't open email attachments from unknown senders"
    ),
    "ransomware": (
        "🔒 <b>Ransomware</b> is malware that encrypts your files and demands a ransom "
        "payment to restore access. It often spreads through phishing emails or "
        "infected downloads.<br><br>"
        "<b>How to stay safe:</b><br>"
        "• Keep regular backups of important files (offline or cloud)<br>"
        "• Never pay the ransom — it doesn't guarantee file recovery<br>"
        "• Keep all software patched and updated"
    ),
    "social engineering": (
        "🎭 <b>Social Engineering</b> is manipulating people psychologically to reveal "
        "confidential information. Attackers impersonate IT support, bosses, or "
        "friends to trick you.<br><br>"
        "<b>How to stay safe:</b><br>"
        "• Always verify identity before sharing any information<br>"
        "• Be sceptical of urgent requests for passwords or money<br>"
        "• Use a callback verification process for sensitive requests"
    ),
    "ddos": (
        "💥 <b>DDoS (Distributed Denial of Service)</b> is an attack that floods a "
        "server or website with massive traffic to make it unavailable to real users.<br><br>"
        "<b>How to stay safe:</b><br>"
        "• Use DDoS protection services (Cloudflare, AWS Shield)<br>"
        "• Rate-limit your APIs<br>"
        "• Have an incident response plan ready"
    ),
    "sql injection": (
        "💉 <b>SQL Injection</b> is a web attack where malicious SQL code is inserted "
        "into input fields to manipulate a database — stealing, deleting, or altering data.<br><br>"
        "<b>How to stay safe:</b><br>"
        "• Use parameterised queries / prepared statements<br>"
        "• Validate and sanitise all user input<br>"
        "• Apply the principle of least privilege for DB accounts"
    ),
    "man in the middle": (
        "🕵️ <b>Man-in-the-Middle (MITM)</b> attacks occur when an attacker secretly "
        "intercepts communication between two parties to eavesdrop or alter data.<br><br>"
        "<b>How to stay safe:</b><br>"
        "• Always use HTTPS websites (look for the padlock 🔒)<br>"
        "• Avoid using public Wi-Fi for sensitive transactions<br>"
        "• Use a VPN on untrusted networks"
    ),
    "brute force": (
        "🔨 <b>Brute Force</b> attacks try every possible password combination until "
        "the correct one is found. Automated tools can test millions of combinations "
        "per second.<br><br>"
        "<b>How to stay safe:</b><br>"
        "• Use long, complex, unique passwords (12+ characters)<br>"
        "• Enable account lockout after failed attempts<br>"
        "• Always enable Multi-Factor Authentication (MFA)"
    ),
    "zero day": (
        "☠️ <b>Zero-Day Exploit</b> targets unknown vulnerabilities in software that "
        "the vendor hasn't patched yet. Attackers exploit these before a fix exists.<br><br>"
        "<b>How to stay safe:</b><br>"
        "• Apply security patches as soon as they're released<br>"
        "• Use behaviour-based antivirus that detects anomalies<br>"
        "• Segment your network to limit blast radius"
    ),
    "keylogger": (
        "⌨️ <b>Keylogger</b> is software (or hardware) that secretly records every "
        "keystroke you make — capturing passwords, credit cards, and messages.<br><br>"
        "<b>How to stay safe:</b><br>"
        "• Use a reputable antivirus and scan regularly<br>"
        "• Use virtual keyboards for sensitive input<br>"
        "• Keep your OS and browser updated"
    ),
}

# ── Phishing examples ─────────────────────────────────────────────
# Each item has a message and whether it IS a phishing attempt.
PHISHING_EXAMPLES = [
    {
        "message": "📧 'Dear Customer, your SBI account has been suspended! "
                   "Click here immediately to verify: http://sbi-secure-login.xyz/verify'",
        "is_phishing": True,
        "explanation": (
            "✅ Correct! This IS phishing because:<br>"
            "• The URL is NOT the official SBI website (sbi.co.in)<br>"
            "• It creates <b>urgency/fear</b> to make you click without thinking<br>"
            "• Legitimate banks never ask you to verify via random links"
        ),
    },
    {
        "message": "📧 'Hi, your Amazon order #405-2847 has been shipped. "
                   "Track it at: https://www.amazon.in/orders/track'",
        "is_phishing": False,
        "explanation": (
            "✅ Correct! This looks <b>legitimate</b> because:<br>"
            "• The link goes to the real amazon.in domain<br>"
            "• It references a specific order number<br>"
            "• No urgent threats or suspicious requests<br>"
            "• <i>Tip: Still hover over links before clicking to confirm the domain!</i>"
        ),
    },
    {
        "message": "📧 'URGENT: Your Google account will be deleted in 24 hours! "
                   "Sign in now at http://google-accounts-restore.com to save it!'",
        "is_phishing": True,
        "explanation": (
            "✅ Correct! This IS phishing because:<br>"
            "• 'google-accounts-restore.com' is NOT a Google domain<br>"
            "• Extreme urgency (24 hours, account deleted) is a classic scare tactic<br>"
            "• Google communicates through accounts.google.com, never third-party sites"
        ),
    },
    {
        "message": "📱 SMS: 'Your HDFC Credit Card ending 4821 has a transaction of "
                   "Rs.12,500 at BigBasket on 06-Jul. Not you? Call 1800-266-4332.'",
        "is_phishing": False,
        "explanation": (
            "✅ Correct! This looks <b>legitimate</b> because:<br>"
            "• It references your specific card (last 4 digits)<br>"
            "• It asks you to <b>call a number</b>, not click a link<br>"
            "• 1800-266-4332 is HDFC's official helpline<br>"
            "• <i>Always verify toll-free numbers on the official bank website!</i>"
        ),
    },
    {
        "message": "📧 'Congratulations! You've won an iPhone 15 Pro in our lucky draw! "
                   "Claim your prize at prize-winner-2024.net — offer expires today!'",
        "is_phishing": True,
        "explanation": (
            "✅ Correct! This IS phishing because:<br>"
            "• You didn't enter any contest — random wins are always scams<br>"
            "• Suspicious domain with no relation to any real company<br>"
            "• 'Expires today' creates false urgency<br>"
            "• This is a classic 'too good to be true' lure"
        ),
    },
]

# ── Quiz questions ────────────────────────────────────────────────
QUIZ_QUESTIONS = [
    {
        "question": "What does 'phishing' mean in cybersecurity?",
        "options": [
            "A) A type of encryption algorithm",
            "B) Tricking users into revealing sensitive info via fake messages",
            "C) A method to speed up network connections",
            "D) A firewall configuration technique",
        ],
        "answer": "B",
        "explanation": "Phishing is a social engineering attack where criminals impersonate trusted entities via email/SMS to steal credentials.",
    },
    {
        "question": "Which of these is the STRONGEST password?",
        "options": [
            "A) password123",
            "B) MyDog2020",
            "C) T#9mK$2xQp!vL",
            "D) qwerty",
        ],
        "answer": "C",
        "explanation": "A strong password uses uppercase, lowercase, numbers, and symbols — and is at least 12 characters long with no dictionary words.",
    },
    {
        "question": "What is Two-Factor Authentication (2FA)?",
        "options": [
            "A) Using two different browsers",
            "B) An extra security layer requiring a second verification step beyond your password",
            "C) Having two separate email accounts",
            "D) Logging in from two devices simultaneously",
        ],
        "answer": "B",
        "explanation": "2FA adds an extra layer — even if someone steals your password, they can't log in without the second factor (OTP, fingerprint, etc.).",
    },
    {
        "question": "What should you do if you receive an unexpected OTP?",
        "options": [
            "A) Share it with the caller who says they're from your bank",
            "B) Ignore it and share it later if needed",
            "C) Never share it — an unsolicited OTP means someone is trying to access your account",
            "D) Save it in your notes for future use",
        ],
        "answer": "C",
        "explanation": "OTPs are single-use. If you receive one you didn't request, someone is attempting to log into your account. Contact your bank/service immediately.",
    },
    {
        "question": "Which of the following is a sign of a HTTPS secure website?",
        "options": [
            "A) The URL starts with 'http://'",
            "B) The page loads very fast",
            "C) A padlock icon appears in the browser address bar",
            "D) The website has lots of images",
        ],
        "answer": "C",
        "explanation": "The padlock 🔒 in the address bar means the connection is encrypted via SSL/TLS. Always look for 'https://' — the 's' stands for secure.",
    },
    {
        "question": "What is ransomware?",
        "options": [
            "A) Software that repairs corrupted files",
            "B) A type of antivirus program",
            "C) Malware that encrypts your files and demands payment to restore them",
            "D) A tool for secure file sharing",
        ],
        "answer": "C",
        "explanation": "Ransomware locks your files and demands a ransom. You should never pay — instead, restore from backups and report to cybercrime authorities.",
    },
    {
        "question": "What is the safest way to use public Wi-Fi?",
        "options": [
            "A) Use it freely — public Wi-Fi is always safe",
            "B) Avoid sensitive transactions, or use a VPN",
            "C) Share your device password with others nearby",
            "D) Disable your firewall for better speed",
        ],
        "answer": "B",
        "explanation": "Public Wi-Fi is unencrypted and vulnerable to MITM attacks. Use a VPN to encrypt your traffic, and avoid banking or shopping on public networks.",
    },
]

# ── Risky keywords for smart advice ──────────────────────────────
RISKY_PATTERNS = [
    {
        "keywords": ["otp", "one time password", "share otp", "send otp", "give otp"],
        "advice": (
            "🚨 <b>RED ALERT: Never share your OTP with anyone!</b><br><br>"
            "OTPs (One-Time Passwords) are your private authentication codes. "
            "Banks, government agencies, and legitimate companies will <b>NEVER</b> ask for your OTP.<br><br>"
            "<b>What's happening:</b> Someone is trying to access your account and needs your OTP to complete the breach.<br><br>"
            "<b>What to do right now:</b><br>"
            "• Hang up / end the chat immediately<br>"
            "• Do NOT share the OTP under any circumstances<br>"
            "• Log into your account and change your password<br>"
            "• Report the incident to your bank's fraud helpline"
        ),
    },
    {
        "keywords": ["gave password", "shared password", "told my password", "i gave my password"],
        "advice": (
            "🚨 <b>Security Breach: You may have been compromised!</b><br><br>"
            "<b>Act immediately:</b><br>"
            "1. <b>Change your password</b> on the affected account RIGHT NOW<br>"
            "2. <b>Enable 2FA</b> if not already active<br>"
            "3. <b>Check recent activity</b> on your account for unauthorised actions<br>"
            "4. <b>Change passwords</b> on other accounts that use the same password<br>"
            "5. <b>Inform your bank</b> if the account is financial<br><br>"
            "Passwords are like toothbrushes — never share them with anyone."
        ),
    },
    {
        "keywords": ["clicked suspicious", "clicked a link", "opened attachment", "downloaded something strange"],
        "advice": (
            "⚠️ <b>Possible Malware Exposure!</b><br><br>"
            "<b>Do this immediately:</b><br>"
            "1. <b>Disconnect from the internet</b> (turn off Wi-Fi/LAN) to prevent data exfiltration<br>"
            "2. <b>Run a full antivirus scan</b> immediately<br>"
            "3. <b>Do NOT enter any passwords</b> until the device is scanned<br>"
            "4. <b>Change passwords</b> from a different, safe device<br>"
            "5. <b>Check for unusual processes</b> in Task Manager<br><br>"
            "If you suspect serious compromise, consult an IT professional."
        ),
    },
    {
        "keywords": ["free gift", "won a prize", "lottery", "you have won", "claim reward"],
        "advice": (
            "🎁 <b>WARNING: This is almost certainly a SCAM!</b><br><br>"
            "Unsolicited 'prizes' and 'free gifts' are the oldest tricks in the scammer's playbook.<br><br>"
            "<b>Red flags in this scenario:</b><br>"
            "• You didn't enter any contest<br>"
            "• They'll ask for personal info or a 'processing fee' to claim it<br>"
            "• There's artificial urgency to act fast<br><br>"
            "<b>What to do:</b><br>"
            "• Ignore and delete the message<br>"
            "• Never pay any 'release fee' or 'tax' for a prize<br>"
            "• Report to cybercrime.gov.in if in India"
        ),
    },
    {
        "keywords": ["my account was hacked", "i was hacked", "someone logged in", "unauthorised access"],
        "advice": (
            "🆘 <b>Account Compromise Detected — Act Fast!</b><br><br>"
            "<b>Immediate steps:</b><br>"
            "1. <b>Change your password</b> immediately from a trusted device<br>"
            "2. <b>Revoke all active sessions</b> (most platforms have 'Log out everywhere')<br>"
            "3. <b>Enable 2FA</b> right now<br>"
            "4. <b>Check recovery email/phone</b> — hackers change these first<br>"
            "5. <b>Inform contacts</b> — hackers may message them pretending to be you<br>"
            "6. <b>Report to the platform</b> and <b>cybercrime.gov.in</b><br><br>"
            "Need step-by-step help? Type <b>'incident'</b> to use the Incident Reporter."
        ),
    },
    {
        "keywords": ["public wifi", "public wi-fi", "airport wifi", "cafe wifi", "open network"],
        "advice": (
            "📡 <b>Public Wi-Fi Risk Advisory</b><br><br>"
            "Public Wi-Fi networks are <b>unencrypted</b> and hunting grounds for attackers.<br><br>"
            "<b>Risks include:</b><br>"
            "• Man-in-the-Middle (MITM) attacks — someone reading your traffic<br>"
            "• Evil Twin attacks — fake hotspots mimicking the real one<br>"
            "• Session hijacking<br><br>"
            "<b>Stay safe:</b><br>"
            "• Use a <b>VPN</b> (ProtonVPN, Mullvad) whenever on public networks<br>"
            "• Avoid banking, shopping, or logging into sensitive accounts<br>"
            "• Use your mobile hotspot instead when possible<br>"
            "• Always verify the exact network name with staff"
        ),
    },
]

# ── Incident report flow ──────────────────────────────────────────
# A list of questions asked sequentially.
INCIDENT_QUESTIONS = [
    "🔍 <b>Incident Reporter Activated</b><br><br>Let's document this properly. "
    "First — <b>what type of incident occurred?</b><br>"
    "Examples: phishing email, account hacked, malware infection, data breach, financial fraud, suspicious call",

    "📅 <b>When did this happen?</b> (Approximate date and time is fine)",

    "📝 <b>Briefly describe what happened.</b> What did you do, what did you receive, or what did you notice?",

    "💻 <b>Which devices or accounts are affected?</b><br>"
    "Examples: Gmail account, laptop, phone, bank account, social media",

    "🛡️ <b>Have you taken any steps already?</b><br>"
    "Examples: changed password, called bank, ran antivirus, or nothing yet?",
]


def generate_incident_response(answers: list) -> str:
    """
    Takes the user's answers to incident questions and generates
    a personalised incident response plan.
    """
    incident_type = answers[0].lower() if answers else ""

    response = (
        "<b>📋 Incident Report Summary</b><br>"
        "━━━━━━━━━━━━━━━━━━━━━━━━<br>"
        f"<b>Type:</b> {answers[0]}<br>"
        f"<b>Time:</b> {answers[1]}<br>"
        f"<b>Description:</b> {answers[2]}<br>"
        f"<b>Affected:</b> {answers[3]}<br>"
        f"<b>Steps taken:</b> {answers[4]}<br>"
        "━━━━━━━━━━━━━━━━━━━━━━━━<br><br>"
        "<b>🚨 Recommended Actions:</b><br>"
    )

    # Generic steps for all incidents
    steps = [
        "Change passwords on ALL affected accounts immediately",
        "Enable Two-Factor Authentication (2FA) everywhere",
        "Check recent account activity for unauthorised actions",
        "Inform your bank if any financial accounts are involved",
        "Run a full antivirus/malware scan on affected devices",
    ]

    # Add specific steps based on incident type keywords
    if any(w in incident_type for w in ["phishing", "email", "link", "attachment"]):
        steps.append("Report the phishing email to reportphishing@apwg.org")
        steps.append("Mark the sender as spam and block them")

    if any(w in incident_type for w in ["hack", "breach", "unauthorised", "hacked"]):
        steps.append("Revoke all active sessions (check 'Security' settings on the platform)")
        steps.append("Verify your recovery email/phone hasn't been changed by the attacker")

    if any(w in incident_type for w in ["financial", "fraud", "bank", "money", "upi"]):
        steps.append("Call your bank's 24/7 fraud helpline IMMEDIATELY to freeze the account")
        steps.append("File a complaint at cybercrime.gov.in (India) or your country's cybercrime portal")
        steps.append("Keep a record of all transaction IDs and screenshots")

    if any(w in incident_type for w in ["malware", "virus", "ransomware", "infected"]):
        steps.append("Disconnect the device from the internet to prevent spread")
        steps.append("Do NOT pay any ransom — restore from clean backups instead")
        steps.append("Consult a professional IT forensics team if data is critical")

    for i, step in enumerate(steps, 1):
        response += f"{i}. {step}<br>"

    response += (
        "<br><b>🏛️ Authorities to report to (India):</b><br>"
        "• Cyber Crime Portal: <b>cybercrime.gov.in</b><br>"
        "• National Helpline: <b>1930</b><br>"
        "• Local police cyber cell<br><br>"
        "<i>Stay calm — most incidents are recoverable if acted on quickly. Type 'menu' to return to the main menu.</i>"
    )

    return response


# ── Main ChatBot class ────────────────────────────────────────────

class CyberBot:
    """
    The main chatbot class. Tracks state per user session.
    State can be: 'menu', 'quiz', 'phishing', 'incident'
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset all state — called on a new session or when user types 'menu'."""
        self.state = "menu"
        self.quiz_index = 0
        self.quiz_score = 0
        self.phishing_index = 0
        self.incident_step = 0
        self.incident_answers = []
        # Shuffle quiz and phishing so every session feels fresh
        random.shuffle(QUIZ_QUESTIONS)
        random.shuffle(PHISHING_EXAMPLES)

    def get_welcome(self) -> str:
        return (
            "👋 <b>Welcome to CyberShield — Your Cybersecurity Awareness Bot!</b><br><br>"
            "I'm here to help you stay safe online. Here's what I can do:<br><br>"
            "🛡️ <b>1. Threat Info</b> — Type a threat name (e.g. <i>phishing</i>, <i>malware</i>, <i>ransomware</i>)<br>"
            "🎣 <b>2. Phishing Test</b> — Type <b>phishing test</b> to spot fake messages<br>"
            "📝 <b>3. Quiz Mode</b> — Type <b>quiz</b> to test your knowledge (MCQ)<br>"
            "🚨 <b>4. Incident Report</b> — Type <b>incident</b> if something bad happened<br>"
            "💡 <b>5. Smart Advice</b> — Just describe your situation — I'll detect risks automatically<br><br>"
            "Type <b>menu</b> anytime to return here. Let's get started! 🔐"
        )

    def get_menu(self) -> str:
        return (
            "🏠 <b>Main Menu</b><br><br>"
            "What would you like to do?<br><br>"
            "🛡️ Type a threat name → <i>phishing, malware, ransomware, ddos, keylogger...</i><br>"
            "🎣 Type <b>phishing test</b> → Spot real vs fake messages<br>"
            "📝 Type <b>quiz</b> → Cybersecurity MCQ quiz<br>"
            "🚨 Type <b>incident</b> → Report a security incident<br>"
            "💡 Just describe your situation → I'll give smart advice"
        )

    def process(self, user_input: str) -> str:
        """
        Main entry point. Routes the input based on current state.
        """
        text = user_input.strip().lower()

        # ── Global commands ────────────────────────────────────────
        if text in ("menu", "home", "restart", "start over", "exit"):
            self.reset()
            return self.get_menu()

        if text in ("help", "?"):
            return self.get_menu()

        # ── Route based on current state ───────────────────────────
        if self.state == "quiz":
            return self._handle_quiz(text)

        if self.state == "phishing":
            return self._handle_phishing(text)

        if self.state == "incident":
            return self._handle_incident(user_input)  # preserve original case

        # ── Menu state — detect intent ─────────────────────────────
        return self._handle_menu(text, user_input)

    def _handle_menu(self, text: str, original: str) -> str:
        """Handle input when user is at the main menu."""

        # Start quiz
        if "quiz" in text:
            self.state = "quiz"
            self.quiz_index = 0
            self.quiz_score = 0
            return self._ask_quiz_question()

        # Start phishing test
        if "phishing test" in text or "phishing game" in text or text == "phishing":
            if "test" in text or "game" in text or text == "phishing":
                self.state = "phishing"
                self.phishing_index = 0
                return self._ask_phishing_question()

        # Start incident reporting
        if any(w in text for w in ["incident", "i was hacked", "report", "help me", "emergency"]):
            self.state = "incident"
            self.incident_step = 0
            self.incident_answers = []
            return INCIDENT_QUESTIONS[0]

        # Check for known threats
        for threat_key, explanation in THREATS.items():
            if threat_key in text:
                return explanation

        # Smart advice — check risky patterns
        for pattern in RISKY_PATTERNS:
            if any(kw in text for kw in pattern["keywords"]):
                return pattern["advice"]

        # Fallback
        return (
            "🤔 I didn't quite catch that. Here are some things you can try:<br><br>"
            "• Type a threat name: <b>phishing</b>, <b>malware</b>, <b>ransomware</b>, <b>ddos</b><br>"
            "• Type <b>quiz</b> to test your knowledge<br>"
            "• Type <b>phishing test</b> to spot scam messages<br>"
            "• Type <b>incident</b> to report a security issue<br>"
            "• Or just describe your situation and I'll help!<br><br>"
            "Type <b>menu</b> to see all options."
        )

    # ── Quiz logic ────────────────────────────────────────────────

    def _ask_quiz_question(self) -> str:
        """Present the current quiz question."""
        q = QUIZ_QUESTIONS[self.quiz_index]
        options_html = "<br>".join(q["options"])
        return (
            f"<b>Question {self.quiz_index + 1} of {len(QUIZ_QUESTIONS)}</b><br><br>"
            f"❓ {q['question']}<br><br>"
            f"{options_html}<br><br>"
            "Type <b>A</b>, <b>B</b>, <b>C</b>, or <b>D</b> to answer."
        )

    def _handle_quiz(self, text: str) -> str:
        """Process a quiz answer."""
        answer = text.strip().upper()

        if answer not in ("A", "B", "C", "D"):
            return "Please answer with <b>A</b>, <b>B</b>, <b>C</b>, or <b>D</b>."

        q = QUIZ_QUESTIONS[self.quiz_index]
        correct = answer == q["answer"]

        if correct:
            self.quiz_score += 1
            feedback = f"✅ <b>Correct!</b> {q['explanation']}"
        else:
            feedback = (
                f"❌ <b>Incorrect.</b> The correct answer is <b>{q['answer']}</b>.<br>"
                f"{q['explanation']}"
            )

        self.quiz_index += 1

        # Check if quiz is over
        if self.quiz_index >= len(QUIZ_QUESTIONS):
            result = self._quiz_result()
            self.state = "menu"
            return f"{feedback}<br><br>{result}"

        # Next question
        next_q = self._ask_quiz_question()
        return f"{feedback}<br><br>━━━━━━━━━━━━━━━━<br><br>{next_q}"

    def _quiz_result(self) -> str:
        """Generate quiz completion summary."""
        score = self.quiz_score
        total = len(QUIZ_QUESTIONS)
        pct = int((score / total) * 100)

        if pct == 100:
            grade = "🏆 Perfect score! You're a cybersecurity expert!"
        elif pct >= 75:
            grade = "🥈 Great job! You have solid cybersecurity awareness."
        elif pct >= 50:
            grade = "🥉 Not bad! Review the topics you missed."
        else:
            grade = "📚 Keep learning! Cybersecurity awareness takes practice."

        return (
            f"<b>🎉 Quiz Complete!</b><br><br>"
            f"Your score: <b>{score}/{total}</b> ({pct}%)<br>"
            f"{grade}<br><br>"
            "Type <b>quiz</b> to try again or <b>menu</b> to go back."
        )

    # ── Phishing detection logic ───────────────────────────────────

    def _ask_phishing_question(self) -> str:
        """Present the current phishing example."""
        ex = PHISHING_EXAMPLES[self.phishing_index]
        return (
            f"<b>🎣 Phishing Test — Example {self.phishing_index + 1} of {len(PHISHING_EXAMPLES)}</b><br><br>"
            f"{ex['message']}<br><br>"
            "Is this a <b>phishing/scam</b> message?<br>"
            "Type <b>yes</b> (it's a scam) or <b>no</b> (it's legitimate)."
        )

    def _handle_phishing(self, text: str) -> str:
        """Process phishing yes/no answer."""
        if text not in ("yes", "no", "y", "n"):
            self.state = "menu"
            return (
                  "↩️ Exiting phishing test...<br><br>"
                  + self._handle_menu(text, text)
    )

        user_says_phishing = text in ("yes", "y")
        ex = PHISHING_EXAMPLES[self.phishing_index]
        correct = user_says_phishing == ex["is_phishing"]

        if correct:
            feedback = f"✅ <b>Correct!</b><br><br>{ex['explanation']}"
        else:
            actual = "phishing/scam" if ex["is_phishing"] else "legitimate"
            feedback = f"❌ <b>Incorrect.</b> This is actually <b>{actual}</b>.<br><br>{ex['explanation']}"

        self.phishing_index += 1

        if self.phishing_index >= len(PHISHING_EXAMPLES):
            self.state = "menu"
            return (
                f"{feedback}<br><br>"
                "━━━━━━━━━━━━━━━━<br>"
                "🎉 <b>Phishing Test Complete!</b> You've reviewed all examples.<br>"
                "Type <b>phishing test</b> to try again or <b>menu</b> to go back."
            )

        next_q = self._ask_phishing_question()
        return f"{feedback}<br><br>━━━━━━━━━━━━━━━━<br><br>{next_q}"

    # ── Incident reporting logic ───────────────────────────────────

    def _handle_incident(self, user_input: str) -> str:
        """Collect incident answers one step at a time."""
        self.incident_answers.append(user_input)
        self.incident_step += 1

        if self.incident_step < len(INCIDENT_QUESTIONS):
            return INCIDENT_QUESTIONS[self.incident_step]

        # All questions answered — generate response
        response = generate_incident_response(self.incident_answers)
        self.state = "menu"
        return response
