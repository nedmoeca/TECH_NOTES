
---

### 🔹 Slide 1: Title Slide

**“Good afternoon everyone. My name is Terrence, and this is my CTF Challenge Report from the 2025 H4K-IT Cybersecurity Bootcamp. Over the next few minutes, I’ll walk you through my experience, key challenges I tackled, lessons learned, and how this has shaped my journey as a cybersecurity analyst slash enthusiast in general.”**

---

### 🔹 Slide 2: Introduction

**“The CTF simulated attacks in web exploitation, pentesting, code audits, OSINT, and forensics. My personal goal was to not only capture as many flags as possible, but also learn from every challenge, fail fast, and improve even faster.”**

---

### 🔹 Slide 3: My Profile

**“A little about me—as mentioned earlier I’m Terrence, a junior cybersecurity analyst deeply interested in offensive security, cloud security and hacking.

---

### 🔹 Slide 4: Categories & Tools Used – Domains

**“Next up I will discuss the Categories & Tools I used in the mentioned domains of the CTF challenges. 
there were 5 key domains. 
Web Exploitation, Pentesting, Code Review (PPC), OSINT and Forensics.

---

### 🔹 Slide 5: Categories & Tools Used – Tools

**“To tackle these challenges in their respective domains, I relied on some essential tools: 
1st is the Chrome browser and Chrome DevTools for web analysis, 
2nd Gobuster and FFUF for fuzzing, 
3rd SSH and the Kali CLI for remote access, and 
finally Python3 for running code from the code review tasks
then curl, and Nmap for enumeration.”**

---

### 🔹 Slide 6–8: Challenge Summary

**“Now Let’s talk results.
I will give a quick rundown of 4 of the challenges I managed to solve and highlights of the exploits and techniques I used to solved them:**

- in **AI Solutions Portal challenge**: I noticed the profile URL of the website contained an ID parameter. I changed the value manually in the browser and gained unauthorized access to the admin profile—classic IDOR. Flag captured.

- **CorpDocs**:  This was a Broken Access Control exploit challenge. To be more specific Insecure Direct Access to Admin Interface. I discovered an `/admin` endpoint via a gobsuter brute force. Accessed it directly via my browser and there was the flag. 

- **“In the ResetRealm challenge, I discovered that the password reset tokens were based on predictable values—likely using timestamps.**  so I tried to prove my theory.
	**I registered a test user, triggered a password reset, then inspected the server’s response headers. The `Date` header looked suspicious, so I converted it to a UNIX timestamp and tried combining it with the username using MD5—but the hash didn’t match. sadly**
	**So instead, I requested a reset for the `admin` user and the system actually returned a full reset link! I used it to reset the admin password, logged in successfully as the admin, and found the flag hidden in the admin dashboard source code.”**

- next ...**ScriptServe**: The website gave me a file upload form. I started with basic uploads, but when they failed, I switched gears to discovery. I used Gobuster to discover an endpoint called `/preview` then fuzzed filenames with FUFF and eventually retrieved a file named `flag.txt` directly from the server. insecure file handling”.

- **PDFVault was particularly interesting: **It was a web app designed for submitting signed PDFs through a form. When I landed on the homepage, it presented an interface with a simple 'Submit a PDF' button.”**
	**“Clicking that took me to a form asking for a document URL. Initially, I tested the system with a public PDF. It worked—it fetched the file and displayed metadata like title and page count.”**
	**“That gave me a hint. Since the system was fetching and processing URLs server-side, I suspected it might be vulnerable to SSRF.”**
	**“So I submitted a series of internal IP-based URLs—like `127.0.0.1`, ports 3000 and 5000, . Eventually, when I tested `http://127.0.0.1:5000/internal`, I hit the jackpot. The system connected internally and returned the flag directly in the response.”**
	**“This confirmed that the backend was blindly following user-provided URLs without any filtering or validation—an SSRF vulnerability**

**“To stay within the time I’ve been given, I’ve only highlighted a few key challenges. However, detailed walkthroughs for all these tasks on your screen are fully documented in my report, which I’m happy to share.”**

---

### 🔹 Slide 9: Lessons Learned and Interests Ignited

**“This CTF sharpened my eyes for hidden flaws and The hands-on experience helped me connect the dots between theory and practice.”**

---

### 🔹 Slide 10: Conclusion

**“The challenge was fun but more than just a game. It gave me an environment to test ideas, break things, and improve. It deepened my passion for hacking, looking for things where most people don't and taught me to approach every system like a puzzle.**

**I’m incredibly grateful to the H4K-IT team for organizing the bootcamp, to all the mentors and to the friends I've made in the process. I’m grateful and proud to be part of Cohort 3.”**

---

### 🔚 Final Slide: THE END!

this is the end of my presentation
**“ I hope this inspired someone to dive deeper into the world of hacking—where curiosity is a skill and persistence is your superpower.”**

Thank you for listening.

---


# FEEDBACK FROM THE PANEL:
6 WORDS
6 SENTENCES
INCORPORATE GRAPHICS
TAILOR THE PRESENTENTATION FOR THE AUDIENCE (MOSTLY MANAGEMENT SO AVOID TECHNICAL JARGON)
STORY TELLING
BUSINESS CASE: IMPACT ON BUSINESS 
HOW MUCH HAVE YOU SAVED THE COMPANY
SOLUTIONS TO PUT IN PLACE
PRESENTATION SKILLS
DON'T READ FROM THE SLIDES