# Paperwork - Speaker Script (Spoken Walkthrough)

**Box:** Paperwork (Hack The Box, Linux, Easy)
**Audience:** ~60% beginners, ~40% intermediate/pro
**Time budget:** 120 minutes (live terminal demo)
**How to use this:** Everything in normal text is meant to be said out loud. Anything in [square brackets] is a stage direction for you, the presenter, and must NOT be read aloud. Commands in grey boxes are what you type. Take the pauses. You do not need to understand the box to deliver this well, the words carry the content.

**Time map (adjust live):**
- Opening: 5 min
- Phase 1, Recon: 12 min
- Phase 2, Enumeration: 22 min
- Phase 3, Foothold: 22 min
- [BREAK]: 5 min
- Phase 4, Lateral movement: 22 min
- Phase 5, Privilege escalation: 24 min
- Closing: 6 min
- Q&A: ~10 min

---

## 0. OPENING  [~5 min]

Good [morning/afternoon] everyone, and thanks for being here. Today we are going to break into a machine called Paperwork, start to finish, from knowing nothing about it if you haven't done the box to having complete control of it as the root administrator. 

Here is why this box is worth your time. Paperwork does not fall to some famous exploit you can download. It falls because somebody wrote a custom printing service, and they made small, very human mistakes in the code. Our entire attack is about reading their code, spotting those mistakes, and turning each one into a foothold. So even if you have never touched hacking before, you will leave today understanding how a tiny slip in a program becomes a total system takeover.

In plain terms, this is a Network Service Exploitation box. That just means: there are custom programs listening on the network, and we win by reading how they are built rather than by scanning for known holes.

Here is the journey we are going to take together:

- First, reconnaissance. We knock on the machine's doors to see what is open.
- Second, enumeration. We study a strange custom service and actually get a copy of its source code.
- Third, the foothold. We exploit two bugs in that code to get our first shell on the machine.
- Fourth, lateral movement. We use a hidden internal printer service to become a more powerful user.
- Fifth, privilege escalation. We trick a program running as root into handing us its secret, and we become root ourselves.

If this is your first time doing a lab/box/ctf like engagement no worries and feel free to stop me whenever you miss something and need to break it down further.

Let us get started.

---

## 1. RECON AND DISCOVERY  [~12 min]

### 1.1 Getting onto the network and confirming the target is alive

**SAY BEFORE:**
Before we can attack anything, two housekeeping things. We connect to Hack The Box's private network over a VPN, which is just a secure tunnel that puts our machine on the same network as the target. Then we save the target's address into a shortcut name so we do not have to retype or copy paste it all through, and we send the target a quick ping to confirm it is awake and reachable.

**RUN:**
```bash
sudo openvpn your_file.ovpn

IP=TARGET_IP
ping -c 4 TARGET_IP
```

**WHILE IT RUNS (what the command is doing):**
We are running three quick things here. The first, s-u-d-o openvpn followed by our config file, opens the secure tunnel to Hack The Box, and it will sit there printing connection lines, that is normal, we just leave it running in its own window. The second line saves the target's address into a shortcut we are calling IP, so we can reuse it instead of retyping. The third, ping with dash c four, sends exactly four knock-and-answer packets and then stops, so we get a clean, quick yes or no on whether the box is reachable.

**SAY AFTER:**
[Point at the screen.] The line that matters is right here: zero percent packet loss. All four of our test packets went out and came back. That tells us the machine is up, it is listening, and the path between us and it is clean. We are clear to start mapping it.

**CONCEPT BOX - what a ping is:**
For anyone new, a ping is the digital version of knocking on a door and hearing someone answer. We send a tiny message that just means "are you there," and if the machine is alive it sends one back. 

[Depth line for the pros:] 
One detail worth noting, that round trip is about 220 milliseconds, and the time-to-live on the replies comes back at 63, one below a default of 64, which quietly tells us the target is one network hop away behind the VPN gateway, exactly what we expect on this platform.

**TRANSITION:**
We know the machine is alive. The very next question any attacker asks is: what is it running? For that we use the single most important tool in this whole recon phase.

### 1.2 Scanning for open ports with Nmap

**SAY BEFORE:**
We are going to scan the target with a tool called Nmap. Think of the machine as a building with thousands of numbered doors, and each door is called a port. Behind an open door there is a service running, something we can talk to. Nmap walks down the hallway and tells us which doors are open. We will do this in two passes. First a fast, wide sweep of every single door, all sixty-five thousand of them, just to see which are open.

**RUN:**
```bash
nmap -p- --min-rate 5000 -Pn TARGET_IP
```

**WHILE IT RUNS (what the command is doing):**
While this scans, here is what each part is doing. nmap is the scanner. dash p dash tells it to check every one of the sixty-five thousand five hundred thirty-five ports, not just the common ones. min-rate five thousand pushes it to send at least five thousand packets a second so a full sweep finishes in seconds. And dash capital P n tells it to skip pinging first and just scan, because these machines often ignore pings. It is knocking on every door as fast as it can, and in a moment it will list only the ones that answered.

**SAY AFTER:**
[Point.] Three open doors, that is it. Port 22, which is SSH, the normal way to log into a Linux machine remotely. Port 80, which is a website. And port 1515, and this is the interesting one. Nmap labels it "ifor-protocol," but do not trust that label. That is just Nmap guessing based on the port number. The honest truth is Nmap does not recognize what is on 1515. An unrecognized custom service is a gift to an attacker, so that is immediately our prime suspect.

**TRANSITION:**
Now that we know which three doors are open, we go back and interrogate each one more deeply to learn exactly what software is behind it.

**PACING:** ~5 min

### 1.3 Fingerprinting the services

**SAY BEFORE:**
This second scan is slower and more aggressive, but we only point it at the three open ports, so it stays fast. It tries to read version numbers and coax each service into revealing what it is. We especially want to see if that mystery service on 1515 will say anything about itself.

**RUN:**
```bash
nmap -A -p 22,80,1515 TARGET_IP
```

**WHILE IT RUNS (what the command is doing):**
This one is heavier, so give it a moment. The dash capital A turns on the works: it fingerprints software versions, runs a batch of detection scripts, and even traces the route to the host, all at once. And dash p with our three port numbers keeps it aimed only at the doors we already know are open, so all that heavy machinery stays fast. It is basically interviewing each of the three services to learn exactly what it is.

**SAY AFTER:**
[Walk the three results slowly.] Port 22 is OpenSSH, a current, patched version, so there is no easy way to force the door. It becomes useful only later, once we have a key. Port 80 is an nginx web server, but notice it tries to redirect us to "paperwork dot h-t-b," a name our machine does not know yet. Hold that thought. And port 1515, our mystery service, finally speaks. It greets us with "Archive underscore Printer is ready and printing." So this is some kind of homemade print server. We now have our map, and we have our target.

**CONCEPT BOX - why a banner matters:**
Plain version: a banner is just the greeting a service says when you connect, like a shop that says its name when you walk in. [Depth line:] That greeting came back because the aggressive scan sent probe data that the service interpreted as a status request, and it answered with its ready message. A custom service that talks back is one we can script a conversation with, which is the whole game on this box.

**TRANSITION and PHASE 1 RECAP:**
So where are we now? We have confirmed the target is alive, we found exactly three open doors, and we have singled out a custom print service on port 1515 as our way in, with a website on port 80 that we need to coax into loading. That closes recon. Next we dig into that website, because it is going to hand us something very valuable.

**PACING:** ~3 min

---

## 2. ENUMERATION  [~22 min]

### 2.1 Reading the Intake Portal on the website

**SAY BEFORE:**
Remember the website tried to redirect us to the name "paperwork dot h-t-b." Websites can host many sites on one server and only answer to the right name, so we have to tell our machine that this name points at the target. We add one line to our hosts file, which is just our computer's personal address book, and then we open the site.

**RUN:**
```bash
echo "TARGET_IP paperwork.htb" | sudo tee -a /etc/hosts
```
[Then switch to the browser and load http://paperwork.htb/ . If you prefer the terminal, the alternative is: curl -s http://paperwork.htb/ ]

**WHILE IT RUNS (what the command is doing):**
This single line is editing our computer's address book. echo prints the pairing of the target's address and the name paperwork dot h-t-b, and the tee command with dash a appends that line to the hosts file. The sudo is there because that file is protected. After this, our browser will know where that name lives, and we just open the site.

**SAY AFTER:**
[Point at the portal page.] This page is basically an instruction manual for the service on 1515. It tells us three things. The protocol is something called R-F-C eleven seventy-nine, which is the official standard for line printer services. The target queue is named "archive underscore intake." And every job needs a valid identifier or it gets rejected. That word "identifier" is a breadcrumb, it is pointing us at a specific field we will abuse later. And see this, the "Internal Processor" is a clickable link, not just text. On a box about reading code, a link like that often leads straight to the source.

**CONCEPT BOX - what a hosts file is:**
Plain version: your hosts file is a private notebook where your computer writes down "this name equals this address," and it checks that notebook before asking the wider internet. We just wrote one entry so our browser knows where paperwork dot h-t-b lives. [Depth line:] This is name-based virtual hosting, the same nginx server can serve completely different sites depending on the Host header, which is why the raw IP redirected and only the hostname renders the real app.

**PRONOUNCE:** nginx, say "engine-x." RFC, three letters, R-F-C.

**TRANSITION:**
That link is too tempting to ignore. Let us see exactly where it points before we click it.

**PACING:** ~5 min

### 2.2 Following the link to the source download

**SAY BEFORE:**
We want to know the destination of that "Internal Processor" link without blindly clicking. In the browser you can simply hover over it and read the address at the bottom of the window. From the terminal, we can pull the page's raw code and filter for links.

**RUN:**
```bash
curl -s http://paperwork.htb/ | grep -iE 'href|src='
```

**WHILE IT RUNS (what the command is doing):**
Two tools working together here. curl with dash s quietly downloads the page's raw code without any progress clutter. The pipe hands that code to grep, which with dash i and dash capital E filters, ignoring case, for any line that contains a link reference. So instead of eyeballing the whole page, we pull out just the links in one shot.

**SAY AFTER:**
[Point.] There it is. The link goes to "slash download slash archive." That is a download endpoint. On a box that is all about reading the service's code, this is almost certainly how we get our hands on that code. Let us grab it.

**TRANSITION:**
We download the file, but we do not trust its name, we check what it actually is.

**PACING:** ~3 min

### 2.3 and 2.4 Downloading and unpacking the source

**SAY BEFORE:**
We download whatever that endpoint gives us, then identify its true file type, then unpack it. We are hoping for the actual source code of the thing listening on 1515.

**RUN:**
```bash
curl -s http://paperwork.htb/download/archive -o paperwork-archive-v1.02.zip
unzip paperwork-archive-v1.02.zip -d paperwork-archive
ls -laR paperwork-archive
```

**WHILE IT RUNS (what the command is doing):**
Three steps running back to back. curl downloads the file from that endpoint and dash o saves it under a name we choose. unzip then unpacks the archive into its own folder, dash d naming that folder. And ls with dash l-a-R lists everything inside, recursively, with sizes and permissions, so we can see exactly what we were given.

**SAY AFTER:**
[Point.] It was a zip archive, and inside is a single file: server dot py, a Python program, about two and a half thousand bytes. This is the complete source code of the custom print service on port 1515. This is the moment the box opens up. We are no longer guessing at a black box, we can read exactly how it works, and more importantly, exactly how it breaks.

**CONCEPT BOX - white-box versus black-box:**
Plain version: attacking without the source is like picking a lock in the dark, feeling for the pins. Having the source is like being handed the lock's blueprint. You can see precisely where it is weak. [Depth line:] Getting source handed to you turns this from black-box testing into white-box review, which is faster and far more reliable, and it is why the rest of this box moves so cleanly, every exploit we write is informed by the actual code path.

**PRONOUNCE:** server.py, say "server dot pie."

**TRANSITION and audience checkpoint:**
[Pause.] We are about fifteen minutes in. Any quick questions before we read the code, because the next part is the heart of the foothold? [Take one or two, then continue.] Alright, let us read their program and find the bugs.

**PACING:** ~5 min

### 2.5 Reading the source and finding two bugs  [the big one]

**SAY BEFORE:**
We are going to open server dot py and read it like the developer's own reviewer. I am going to point you at two specific spots. You do not need to be a programmer to follow this, I will translate every line.

**RUN:**
```bash
cat paperwork-archive/server.py
```

**WHILE IT RUNS (what the command is doing):**
cat simply prints the whole file to the screen so we can read it. There are no clever flags here, the skill is in the reading, not the command. As it scrolls, I am going to stop at two specific places.

**SAY AFTER:**
[Scroll slowly. Stop at the queue check.] Here is the first bug. The program wants to check that you asked for the correct print queue, "archive underscore intake." But look at how it wrote the check. In this programming language, the way they wrote it does not ask "is this exactly the right queue." It asks "is your text contained somewhere inside the right queue." And here is the kicker, an empty piece of text is contained inside every piece of text. So if we send nothing at all as the queue name, the check says "yep, that is fine," and lets us straight through. That is bug number one, an authentication bypass by sending emptiness.

[Scroll to the job-name line.] Here is the second bug, and it is the dangerous one. Further down, the program takes the job's name, the name you give your print job, and it builds a system command out of it and runs it. It never cleans or checks that name first. So if instead of a normal name we send a cleverly shaped piece of text, we can break out of the intended command and run our own commands on their machine. That is bug number two, command injection.

**CONCEPT BOX 1 - the substring mistake [DUAL-TRACK, expand this]:**
Plain version: imagine a bouncer told to only let in people named "archive intake." But instead of checking your whole name, he only checks whether your name appears anywhere inside "archive intake." If you walk up and say absolutely nothing, well, nothing technically appears inside any name, so he waves you in. That is the exact mistake here. [Depth line for pros:] The code uses the containment operator on two strings, which performs a substring test rather than an equality test, and the empty string is a substring of every string, so an empty queue satisfies the guard. [Real-world tie-in:] This class of bug, using "contains" where you meant "equals," shows up constantly in real authentication and allow-list code, and empty-input edge cases are a first thing a reviewer should probe.

**CONCEPT BOX 2 - command injection [DUAL-TRACK, expand this]:**
Plain version: picture a form that fills in the blank in the sentence "print the file called ______." Normally you write a filename. But if the program just trusts whatever you type and runs the whole sentence as an instruction, you can write something that finishes their sentence and then sneaks in your own order after it. The computer obediently does both. [Depth line:] The job name is interpolated into a shell command run with shell equals true, and because the value lands inside single quotes, we close the quote, chain our own command, and comment out the rest of their line, giving arbitrary command execution as the service account. [Real-world tie-in:] Command injection is perennially in the industry's top-ten web risks, and the fix is always the same, never build a shell command out of untrusted text.

[OPTIONAL DEEP DIVE - skip if behind] For the developers in the room, the clean fix for the first bug is an equality check or a membership test against a set, and for the second, pass arguments as a list with the shell disabled so user data can never be parsed as commands. We will list exact fixes at the end.

**PRONOUNCE:** "shell equals true," just say it in plain words.

**TRANSITION and PHASE 2 RECAP:**
Where are we now? We pulled the service's own source code off the website and found two flaws: we can walk past the queue check by sending nothing, and we can smuggle our own commands through the job name. Enumeration is done. Next we chain those two bugs together and get our first shell on the machine.

**PACING:** ~9 min

---

## 3. EXPLOITATION, GETTING OUR FIRST SHELL  [~22 min]

### 3.1 Firing the exploit for a foothold

**SAY BEFORE:**
Now we combine both bugs into one attack. We wrote a small script that speaks the printer's language just enough to do three things: slip past the queue check with an empty queue, then hand over a print job whose name is actually our malicious command, and that command tells the target to connect back to us and give us a shell. Before we fire, we start a listener on our own machine, which is just us waiting by the phone for the target to call back.

**RUN:**
```bash
nc -lvnp 4444          # terminal 1: our listener, waiting for the call
python3 foothold.py    # terminal 2: fire the exploit
```

**WHILE IT RUNS (what the command is doing):**
Two terminals doing two jobs. In the first, nc, Netcat, is our listener: dash l means listen, dash v verbose so we see the connection, dash n skip name lookups, and dash p four-four-four-four sets the port we are waiting on. In the second terminal, we run our exploit script, which speaks the printer's protocol and plants the command that makes the target call back to that listener. Watch the first terminal for the moment it connects.

**SAY AFTER:**
[Point at the listener terminal.] Look at this. The target connected back to us, and our prompt changed. We are now sitting at a shell that says "l-p at paperwork." We are inside the machine. Those two lines about "no job control," ignore them, that is just a cosmetic complaint from a basic shell, not an error. We went from reading their code to standing inside their server, as the user that runs the print service.

**CONCEPT BOX - a reverse shell [DUAL-TRACK]:**
Plain version: instead of us dialing into the target, which its firewall would block, we make the target dial out to us. We leave our phone ringing with the listener, and our command tells the victim to call us. When it does, we can type commands and it runs them. [Depth line:] The payload is a bash reverse shell over a dev-tcp socket, which is why no extra tools are needed on the target to initiate it, and our Netcat listener catches the connection and gives us an interactive session. [Real-world tie-in:] Reverse shells are the standard move precisely because outbound connections are usually allowed even when inbound ones are firewalled.

**PRONOUNCE:** Netcat, say "net-cat." The "l-p" user, say the letters, L-P, it is the Linux printing account.

**TRANSITION:**
We have a shell, but it is a flimsy one. Before we explore, we make it sturdier and we confirm exactly who we are.

**PACING:** ~8 min

### 3.2 Stabilizing the shell and checking who we are

**SAY BEFORE:**
This raw shell will break if we hit the wrong key. We upgrade it to a proper interactive terminal with a quick trick, and then we ask the machine two basic questions: who am I, and what machine am I on.

**RUN:**
```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
# [then Ctrl-Z, and on your own machine: stty raw -echo; fg , press Enter twice]
id ; hostname
```

**WHILE IT RUNS (what the command is doing):**
The first line is the shell-upgrade trick: it uses Python to spawn a proper interactive terminal so our session behaves normally. Then the bracketed steps, which are for the presenter, hand control back and forth so our own keyboard settings line up. Finally, id asks who we are, and hostname asks which machine we are on. Two simple questions that confirm our foothold.

**SAY AFTER:**
[Point.] We are the user "l-p," user ID seven, and we belong to no special groups. That is deliberately a low-power account. It runs the printer and nothing else. So we are in, but we are weak. The machine's name is "paperwork," confirming we are on the real server, not some decoy. This tells us our next job: this user cannot do much, so we need to find something on this machine that can hand us more power.

**TRANSITION and PHASE 3 RECAP:**
Quick recap. We chained the empty-queue bypass and the command injection into a working exploit and landed a shell as the low-privilege print user. Our own account is nearly powerless, so the next phase is about finding a more powerful user to become. 

[BREAK MARKER - ~5 min] This is a natural stopping point, and we are about halfway. Let us take a five minute break, stretch, grab water. When we come back, we go hunting for a hidden service inside the machine. [After break:] Welcome back. To recap in one line, we are inside Paperwork as a weak user called l-p, and now we go looking for a way up.

**PACING:** ~6 min plus break

---

## 4. LATERAL MOVEMENT, BECOMING A STRONGER USER  [~22 min]

### 4.1 Finding services hidden inside the machine

**SAY BEFORE:**
When we scanned from outside, we only saw three doors. But machines often run extra services that only listen internally, to themselves, and those are invisible from the outside. Now that we are inside, we can see them. We list every service the machine is listening on locally.

**RUN:**
```bash
ss -tlnp
```

**WHILE IT RUNS (what the command is doing):**
ss is the socket statistics tool, it lists network connections. The flags stack up: dash t for T-C-P only, dash l for listening services only, dash n to show raw numbers instead of looking up names, and dash p to show which program owns each one where it can. In short, show me every service this machine is listening on, right now.

**SAY AFTER:**
[Point at the 9100 line.] Here is the prize. There is a service on port 9100 that only listens internally, so our outside scan never saw it. Port 9100 is the classic port for raw printing, the protocol real network printers use. There is also a service on port 1337, and I will tell you now, that one is a deliberate trap on this box, a dead end. Ignore it. The real path forward is 9100.

**CONCEPT BOX - internal-only services [DUAL-TRACK]:**
Plain version: think of a building with a public front desk but also internal phone lines that only work inside the building. From the street you cannot even tell they exist. Once you are inside, you can pick them up. [Depth line:] These are services bound to the loopback address, 127.0.0.1, so they are reachable only from on the host, which is exactly why they never appeared in the external Nmap and why post-foothold internal enumeration is mandatory. [Real-world tie-in:] Some of the most serious findings in real tests are internal admin services that were never meant to be reachable, exposed the moment an attacker gets a foothold.

**PRONOUNCE:** The command is "ess-ess." Port numbers, just say "ninety-one hundred" and "thirteen thirty-seven." JetDirect, say "jet-direct."

**TRANSITION:**
Let us talk to that printer service on 9100, because printer protocols can do far more than print.

**PACING:** ~5 min

### 4.2 Reading the user flag through the printer service

**SAY BEFORE:**
Printers speak a language called P-J-L. And P-J-L can touch the printer's files. In this case, the implementation is sloppy: we can use its file-read command and sneak a path that escapes the printer's own folder and reaches into the rest of the machine. We will use it to read the first trophy of the box, the user flag, out of a folder our weak user is not even allowed to open.

**RUN:**
```bash
python3 -c '
import socket
s=socket.socket()
s.connect(("127.0.0.1",9100))
s.send(b"@PJL FSUPLOAD NAME=\"../../../../home/archivist/user.txt\"\n")
print(s.recv(4096).decode(errors="ignore"))
s.close()
'
```

**WHILE IT RUNS (what the command is doing):**
This little Python block opens a direct connection to the internal printer on port ninety-one hundred, then sends one printer command, F-S upload, asking for a file. The trick is in the file path: those stacked dot-dot-slash sequences climb up out of the printer's own folder and reach across to the archivist user's home. Then it prints whatever the printer sends back. In a second we will see if it coughs up the file.

**SAY AFTER:**
[Point, but do not read the value aloud.] It worked. The printer service happily handed us the contents of a file belonging to another user, named "archivist." That is the user flag, our first proof trophy. We will record the value for the record, but the real significance is bigger: we just proved we can read files anywhere on this machine through the printer, as a more powerful context than our own.

**CONCEPT BOX - directory traversal [DUAL-TRACK]:**
Plain version: imagine a library kiosk that is supposed to only fetch books from one shelf. But if you ask for "the shelf behind this one, and the one behind that," over and over, it walks right out of the library and into the staff offices. Those dot-dot-slash sequences mean "go up one folder," and stacking them walks us out of the printer's area into the whole filesystem. [Depth line:] The P-J-L F-S-UPLOAD command honors relative path traversal, so stacked dot-dot-slash escapes the printer's virtual filesystem root to the host root, giving arbitrary file read in the service's context. [Real-world tie-in:] Path traversal is one of the oldest and still most common web and device bugs, and real network printers have been abused this exact way to steal documents and credentials.

**PRONOUNCE:** PJL, three letters, P-J-L. FSUPLOAD, say "F-S upload." The user "archivist," say it normally.

**TRANSITION:**
Reading files is powerful, but we want a real, stable login as this archivist user. The same printer flaw that reads files can also write them, and that changes everything.

**PACING:** ~5 min

### 4.3 Writing an SSH key to log in as archivist

**SAY BEFORE:**
We are going to turn file-read into full access. The plan: generate a digital key pair on our machine, then use the printer's file-write command to drop our public key into archivist's list of trusted keys. After that, the machine will let us log in as archivist with no password. First, though, we quickly check that the folder we need to write into actually exists, because the write command will not create missing folders.

**RUN:**
```bash
# generate our key pair on our own machine
ssh-keygen -t ed25519 -f archivist_key -N ""
# write our public key into archivist's trusted keys, through the printer
python3 -c '
import socket
key = b"ssh-ed25519 AAAA...OUR_KEY... nedmoeca@kali\n"
s=socket.socket(); s.connect(("127.0.0.1",9100))
hdr=b"@PJL FSDOWNLOAD FORMAT:BINARY NAME=\"../../../../home/archivist/.ssh/authorized_keys\" SIZE=%d\n" % len(key)
s.send(hdr); s.send(key); s.close()
print("[+] key written")
'
```

**WHILE IT RUNS (what the command is doing):**
Two parts. ssh-keygen makes a fresh key pair on our machine: dash t ed25519 picks a modern key type, dash f names the files, and dash capital N with empty quotes means no passphrase, so logins are smooth. The second block connects to the printer again, but this time uses the write command, F-S download, to drop our public key into archivist's trusted-keys file, through the same path-climbing trick. It is read in reverse, we are putting a file in rather than taking one out.

**SAY AFTER:**
[Point.] The key is written, and when we read it back to verify, the exact key we sent is sitting in archivist's trusted-keys file. We have essentially cut our own key to the archivist's front door and slid it into their lock.

**CONCEPT BOX - SSH keys [DUAL-TRACK]:**
Plain version: an SSH key pair is like a very fancy lock and key. You keep the private key secret, and you can place the matching public lock on any door you want to be let through. We just placed our lock on archivist's door. [Depth line:] Dropping a public key into authorized keys is the classic traversal-write-to-shell pivot, far more stable than a reverse shell, and it works because the write primitive lets us plant trust that SSH then honors. [Real-world tie-in:] Any arbitrary-file-write on a Linux host is quietly a full-compromise primitive, because authorized keys, cron jobs, and startup scripts are all just files.

**PRONOUNCE:** SSH, S-S-H. FSDOWNLOAD, say "F-S download." authorized_keys, say "authorized keys."

**TRANSITION:**
Now we simply walk through the door we just unlocked.

**PACING:** ~7 min

### 4.4 Logging in as archivist

**SAY BEFORE:**
We log in over SSH using our private key, as the archivist user. This gives us a proper, stable session instead of the fragile shell we had, and sets us up for the final climb to root.

**RUN:**
```bash
ssh -i archivist_key archivist@TARGET_IP
id ; ls -la /run/paperwork
```

**WHILE IT RUNS (what the command is doing):**
ssh is the login command. dash i points at the private key we just made, and we log in as archivist at the target. Once we are in, id confirms which user we became, and ls with dash l-a lists that interesting run folder in detail, so we can see the root-owned socket sitting there.

**SAY AFTER:**
[Point.] We are in as archivist, a normal user, and we have a clean, stable shell now. And look at what archivist can see here: a special file called a socket, named "m-g-m-t dot sock," owned by root but readable and writable by archivist's group. That is a program running as the all-powerful root user, leaving a little window open that our new user is allowed to talk through. That window is our path to root.

**TRANSITION and PHASE 4 RECAP:**
Recap. We found a hidden printer service, abused it to read the user flag, then abused it again to plant our key and log in as archivist. And we have already spotted our next target, a root-owned program we are allowed to talk to. That is lateral movement done. Final phase: becoming root.

**PACING:** ~5 min

---

## 5. PRIVILEGE ESCALATION, BECOMING ROOT  [~24 min]

### 5.1 Investigating the root program

**SAY BEFORE:**
Let us learn about that root-owned program before we poke it. We check what it is, who runs it, and whether it is guarding anything valuable.

**RUN:**
```bash
ps -ef | grep -i paperwork | grep -v grep
file /usr/bin/paperwork-daemon
ls -la /usr/bin/paperwork-daemon /etc/paperwork
```

**WHILE IT RUNS (what the command is doing):**
Three quick look-around commands. ps with dash e-f lists every running process, and we pipe it through grep to keep only the paperwork one and drop the grep line itself. file tells us what kind of program the daemon is. And ls with dash l-a shows its permissions and the protected config file beside it. Together they answer: what is this thing, who runs it, and what is it guarding.

**SAY AFTER:**
[Point at each.] Three facts, and they line up perfectly. One, the program is running as root, the most powerful account. Two, it is a Python script that we are allowed to read, so once again we get to see the source. Three, there is a config file called "admin pins," readable only by root, thirty-eight bytes, almost certainly holding a secret. So the shape of this puzzle is: a root program we can talk to, guarding a file we cannot read. The question is how talking to the program gets us the contents of that file.

**TRANSITION:**
Since we can read the program's code, we do exactly what we did before. We read it and look for the trick.

**PACING:** ~5 min

### 5.2 Reading the root program and finding the leak  [the big one]

**SAY BEFORE:**
We open the root program and read how it behaves when someone connects to that socket. I will point you at the one dangerous thing it does.

**RUN:**
```bash
cat /usr/bin/paperwork-daemon
```

**WHILE IT RUNS (what the command is doing):**
Again just cat, printing the root program so we can read it. The whole move here is comprehension, not a fancy command. I will point out the one dangerous thing it does as it comes up.

**SAY AFTER:**
[Scroll slowly.] Here is how this program thinks. Every time someone connects, it checks a log file to decide if something suspicious happened. If the log looks clean, it just sends back a harmless signature and nothing useful. But if it decides there was a "security violation," it goes into a panic mode it calls lockdown, and in that panic it tries to bundle up evidence and hand it to the connecting client. And here is the fatal mistake. The evidence bundle it hands over includes an open handle to that secret admin-pins file, the one only root can read. It is trying to share forensic evidence, and it accidentally shares root's own access to the secret.

Now the beautiful part. Which path does it take, clean or panic? It decides by reading a log file. And that log file lives inside archivist's own home folder, which means we control it. So we get to decide whether root panics. We simply write a trigger word into that log, force the panic branch, and catch what it hands us.

**CONCEPT BOX - passing a file handle [DUAL-TRACK, expand this]:**
Plain version: imagine root opens a locked filing cabinet with its own master key, and then, trying to be helpful, hands you the already-open drawer. You were never allowed to open that cabinet, but it does not matter, because the drawer is open and you are holding it. That is what is happening. The permission is checked when the drawer is opened, by root, not when you look inside. [Depth line for pros:] This is file-descriptor passing over a Unix socket using S-C-M underscore rights ancillary data. The receiver gets a descriptor referring to the same open file, carrying the opener's access, because permission is enforced at open time, not at read time. [Real-world tie-in:] This is a subtle, real privilege-escalation pattern in multi-process daemons, and it is exactly why passing descriptors to less-trusted peers is dangerous.

**CONCEPT BOX - the attacker-controlled gate [DUAL-TRACK]:**
Plain version: the program's alarm is wired to a switch that happens to sit in our room. So we get to pull the alarm whenever we like. [Depth line:] The vulnerable branch is gated on the contents of a log file inside the attacker's home directory, so the attacker fully controls whether the leak fires. [Real-world tie-in:] Any security decision that depends on data a lower-privileged user can modify is not a security decision at all, it is a gift to the attacker.

[OPTIONAL DEEP DIVE - skip if behind] For the curious, the clean branch only ever returns a one-way scrambled version of the secret, a hash, which would be useless to us. That is why we must force the panic branch, because only the panic branch leaks the actual open file, not a scrambled copy.

**PRONOUNCE:** SCM_RIGHTS, say "S-C-M rights." daemon, say "demon." socket, say "socket."

**TRANSITION:**
We understand the trick. Now we pull the alarm and catch root's secret.

**PACING:** ~9 min

### 5.3 Leaking root's secret

**SAY BEFORE:**
Three moves in one. We write a trigger word into the log file that we control, so the program will panic. We connect to the root program's socket. And we catch the open file handle it hands us, then read straight through it to get the secret, bypassing the file's permissions entirely.

**RUN:**
```bash
mkdir -p /home/archivist/printer/logs
echo "FSQUERY" > /home/archivist/printer/logs/commands.log
python3 -c '
import socket, array, os
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect("/run/paperwork/mgmt.sock")
msg, anc, flags, addr = s.recvmsg(4096, socket.CMSG_SPACE(8))
print("msg:", msg.decode(errors="ignore"))
for level, typ, data in anc:
    if level == socket.SOL_SOCKET and typ == socket.SCM_RIGHTS:
        fds = array.array("i"); fds.frombytes(data)
        for fd in fds:
            try:
                print(f"[fd {fd}]", os.pread(fd, 1024, 0).decode(errors="ignore").strip())
            except Exception as e:
                print(f"[fd {fd}] read error: {e}")
s.close()
'
```

**WHILE IT RUNS (what the command is doing):**
Three moves. mkdir with dash p makes sure the log folder exists. echo writes our trigger word into the log file the program watches, which is the switch we control. Then the Python block connects to the root program's socket and, crucially, uses a receive-message call that can catch not just text but an actual open file handle the program passes along. If it works, it reads straight through that handle and prints the secret.

**SAY AFTER:**
[Point, but do not read the actual password aloud.] There it is. The program panicked exactly as we planned, handed us root's open handle to the secret file, and we read the admin password straight out of it, even though our user has zero permission on that file. We now hold the administrator's password, pulled directly from root's own hands.

**CONCEPT BOX - reading through the leaked handle:**
Plain version: we did not break the lock on the file. Root handed us the open drawer, and we just read what was inside. [Depth line:] We parse the descriptor out of the ancillary data and read it directly with a positioned read, which never re-checks file permissions, so the low-privileged user reads a root-only file.

**TRANSITION:**
One secret, one last step. This box reuses that admin password for the root account itself.

**PACING:** ~7 min

### 5.4 Becoming root

**SAY BEFORE:**
We try the admin password we just stole against the root account directly. If the machine reused it, and this box does, we become root.

**RUN:**
```bash
su root
# [enter the recovered admin password when prompted]
id ; cat /root/root.txt
```

**WHILE IT RUNS (what the command is doing):**
su means switch user, and su root asks to become the root administrator. It will prompt for a password, and we give it the one we just recovered. Then id confirms we are user zero, root, and we read the final trophy file. Short command, huge result.

**SAY AFTER:**
[Point.] User ID zero. That is root. That is total control of the machine, nothing on this system is off limits to us now. And we read the final trophy, the root flag. We own Paperwork, top to bottom.

**CONCEPT BOX - password reuse:**
Plain version: it is the same as using one password for your email, your bank, and your front door. Steal it once, and you have everything. [Depth line:] The admin pin doubled as the root account password, so a single secret disclosure collapsed the entire privilege boundary. [Real-world tie-in:] Credential reuse across accounts and systems is one of the most common ways a single small leak turns into a full domain compromise in the real world.

**PRONOUNCE:** The command "su," say "ess-you," it means switch user.

**PACING:** ~3 min

---

## 6. CLOSING  [~6 min]

[Slow down, this is the payoff.]

So let us tell the whole story in one breath. We knocked on the machine and found a strange custom printer service. We talked the website into handing us that service's source code, and reading it we found two mistakes: a door check we could walk past by saying nothing, and a job name we could stuff our own commands into. That got us inside as a weak user. From there we found a second, hidden printer service, and we abused it first to read a protected file, then to plant our own key and log in as a stronger user. Finally, we found a root program that, in a panic it designed itself, would hand out root's own access to a secret. We triggered that panic, stole the admin password, and because the machine reused that password for root, we became root.

Here are the lessons worth carrying home:

- A tiny coding slip, using "contains" when you meant "equals," can be a full authentication bypass.
- Never let untrusted text become part of a command. That is how injection happens.
- A hole that lets you read files usually also lets you write them, and file-write on Linux is game over.
- Security decisions must never depend on data an attacker can change.
- Reusing one password everywhere means one leak loses everything.

And honestly, notice how this box rewarded reading over scanning. I opened by calling it a network service and source review challenge, and that held true the whole way. The one twist worth flagging, that final root step was really a lesson in how programs share resources with each other, a different and deeper skill than the earlier work, and it is the most advanced idea we touched today.

That is Paperwork, from zero to root. [Pause.] Let me take your questions.

---

## 7. Q&A PREP  [presenter safety net]

[These are likely questions with short, safe answers you can give without deep expertise. If you get something outside these, use the two graceful deflections at the end.]

1. **"Why didn't the first scan show the printer service on 9100?"**
   Because that service only listens to the machine itself, internally. External scans cannot see internal-only services. We only found it after we got inside and listed local services.

2. **"What was that port 1337 you skipped?"**
   It is a deliberate decoy on this box, a dead end that does not lead anywhere useful. Part of the skill is recognizing a distraction and not wasting time on it.

3. **"How did sending an empty queue name get us past the check?"**
   The code checked whether our text was contained inside the valid name, instead of checking whether it equaled the valid name. Empty text is contained inside everything, so it passed.

4. **"Is this a real vulnerability or just a CTF trick?"**
   Both patterns are very real. Command injection, path traversal, and password reuse are among the most common issues found in actual security assessments. The box just packages them cleanly.

5. **"Why write an SSH key instead of just using the first shell?"**
   The first shell was fragile and tied to one user. Planting an SSH key gave us a stable, normal login as a stronger user, which is much easier to work from.

6. **"How can reading a file give you a root password you have no permission to read?"**
   We never read it with our own permissions. The root program opened the file itself and then handed us the already-open access. Permission is checked when a file is opened, not each time it is read.

7. **"Could the defenders have caught us?"**
   Several steps are noisy and logganle: the reverse shell connection, the SSH login, and the socket interaction. Good monitoring would flag these, which is part of why we also cover remediation.

8. **"What is the single most important fix here?"**
   There is no single one, but if forced to pick, never build shell commands from untrusted input, and never pass sensitive file handles to less-trusted programs. Those two close the worst doors.

9. **"How long does this take a real attacker?"**
   Once you have done boxes like this, maybe thirty to sixty minutes. We are going slowly today so everyone understands the why, not just the how.

10. **"Do I need to know Python to do this?"**
    It helps, because reading the source is central here, but you can follow the logic without being a Python expert. The mistakes are about logic, not syntax.

11. **"Why does it matter that the daemon runs as root?"**
    Because any access it leaks carries root's power. A low-privilege program making the same mistake would not have handed us anything valuable.

12. **"What is the difference between the user flag and the root flag?"**
    They are just proof files. The user flag proves you reached a normal user, the root flag proves you reached full administrative control. They mark the two big milestones.

**Graceful deflections for anything you cannot answer:**
- "That is a great question and it goes a bit deeper than my notes cover. Let me take it offline and follow up with you afterward."
- "I want to give you an accurate answer rather than guess, so let me check with Ned and get back to you on that one."

---

## 8. DELIVERY CUES  [live demo safety]

**If a command fails or the box is slow:**
- "Networks over a VPN can lag, give it a second. While that runs, let me recap what we are expecting to see."
- "If this hangs, it usually just means the machine is busy. I have the expected output ready to show either way."
- [If the reverse shell does not catch:] "Sometimes the callback needs a second attempt, that is normal with reverse shells. Let me re-fire it." [Re-run foothold.py.]

**Natural places to pause and breathe:**
- After the first shell lands in 3.1. Let it sink in, it is the big moment.
- Right before reading each piece of source, 2.5 and 5.2. Give people a beat to look at the screen.
- Before the final su to root in 5.4. Build a little suspense.

**Do not break the demo:**
- Do not close the listener terminal while the l-p shell is live.
- Do not type into the wrong terminal. Keep the listener and the attack terminal clearly separated, ideally labeled.
- Do not read any flag value or the real admin password out loud. Say "the user flag," "the admin password," and move on.
- If you drop the archivist SSH session, just reconnect with the same ssh command in 4.4, the key is already planted.
