---
tags:
  - HTB_PENETRATION_TESTER
  - HTB
  - MODULE
image: https://cdn.services-k8s.prod.aws.htb.systems/content/modules/logo/9e65e8b3-5af5-4c75-a6cd-bcdd7eb6b7dd.png
---
# Modules Layout

![](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/90/0-PT-Process.png)
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

## Pre-Engagement

The pre-engagement stage is where the main commitments, tasks, scope, limitations, and related agreements are documented in writing. During this stage, contractual documents are drawn up, and essential information is exchanged that is relevant for penetration testers and the client, depending on the type of assessment.

![Penetration testing process: Pre-Engagement, Information Gathering, Vulnerability Assessment, Exploitation, Post-Exploitation, Lateral Movement, Proof-of-Concept, Post-Engagement.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/90/0-PT-Process-PRE.png)

There is only one path we can take from here:

| **Path**                | **Description**                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Information Gathering` | Next, we move towards the `Information Gathering` stage. Before any target systems can be examined and attacked, we must first identify them. It may well be that the customer will not give us any information about their network and components other than a domain name or just a listing of in-scope IP addresses/network ranges. Therefore, we need to get an overview of the target web application(s) or network before proceeding further. |
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

## Information Gathering

Information gathering is an essential part of any assessment. Because information, the knowledge gained from it, the conclusions we draw, and the steps we take are based on the information available. This information must be obtained from somewhere, so it is critical to know how to retrieve it and best leverage it based on our assessment goals.

![Penetration testing process: Pre-Engagement, Information Gathering, Vulnerability Assessment, Exploitation, Post-Exploitation, Lateral Movement, Proof-of-Concept, Post-Engagement.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/90/0-PT-Process-IG.png)

From this stage, the next part of our path is clear:

|**Path**|**Description**|
|---|---|
|`Vulnerability Assessment`|The next stop on our journey is `Vulnerability Assessment`, where we use the information found to identify potential weaknesses. We can use vulnerability scanners that will scan the target systems for known vulnerabilities and manual analysis where we try to look behind the scenes to discover where the potential vulnerabilities might lie.|

The information we gather in advance will influence the results of the `Exploitation` stage. From this, we can see if we have collected enough or dived deep enough. Time, patience, and personal commitment all play a significant role in information gathering. This is when many penetration testers tend to jump straight into exploiting a potential vulnerability. This often fails and can lead, among other things, to a significant loss of time. Before attempting to exploit anything, we should have completed thorough information gathering, keeping detailed notes along the way, focusing on things to hone in on once we get to the exploitation stage. Most assessments are time-based, so we don't want to waste time bouncing around, which could lead to us missing something critical. Organization and patience are vital while being as thorough as possible.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

## Vulnerability Assessment

The vulnerability assessment stage is divided into two areas. On the one hand, it is an approach to scan for known vulnerabilities using automated tools. On the other hand, it is analyzing for potential vulnerabilities through the information found. Many companies conduct regular vulnerability assessment audits to check their infrastructure for new known vulnerabilities and compare them with the latest entries in these tools' databases.

An analysis is more about `thinking outside the box`. We try to discover gaps and opportunities to trick the systems and applications to our advantage and gain unintended access or privileges. This requires creativity and a deep technical understanding. We must connect the various information points we obtain and understand its processes.

![Penetration testing process: Pre-Engagement, Information Gathering, Vulnerability Assessment, Exploitation, Post-Exploitation, Lateral Movement, Proof-of-Concept, Post-Engagement.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/90/0-PT-Process-VA.png)

From this stage, there are four paths we can take, depending on how far we have come:

|**Path**|**Description**|
|---|---|
|`Exploitation`|The first we can jump into is the `Exploitation` stage. This happens when we do not yet have access to a system or application. Of course, this assumes that we have already identified at least one gap and prepared everything necessary to attempt to exploit it.|
|`Post-Exploitation`|The second way leads to the `Post-Exploitation` stage, where we escalate privileges on the target system. This assumes that we are already on the target system and can interact with it.|
|`Lateral Movement`|Our third option is the `Lateral Movement` stage, where we move from the already exploited system through the network and attack other systems. Again, this assumes that we are already on a target system and can interact with it. However, privilege escalation is not strictly necessary because interacting with the system already allows us to move further in the network under certain circumstances. Other times we will need to escalate privileges before moving laterally. Every assessment is different.|
|`Information Gathering`|The last option is returning to the `Information Gathering` stage when we do not have enough information on hand. Here we can dig deeper to find more information that will give us a more accurate view.|

The ability to analyze comes with time and experience. However, it also needs to be trained because proper analysis makes connections between different points and information. Connecting this information about the target network or target system and our experience will often allow us to recognize specific patterns. We can compare this to reading. Once we have read certain words often enough, we will know that word at some point and understand what it means just by looking at the letters.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

## Exploitation

Exploitation is the attack performed against a system or application based on the potential vulnerability discovered during our information gathering and enumeration. We use the information from the `Information Gathering` stage, analyze it in the `Vulnerability Assessment` stage, and prepare the potential attacks. Often many companies and systems use the same applications but make different decisions about their configuration. This is because the same application can often be used for various purposes, and each organization will have different objectives.

![Penetration testing process: Pre-Engagement, Information Gathering, Vulnerability Assessment, Exploitation, Post-Exploitation, Lateral Movement, Proof-of-Concept, Post-Engagement.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/90/0-PT-Process-EX.png)

From this stage, there are four paths we can take, depending on how far we have come:

|**Path**|**Description**|
|---|---|
|`Information Gathering`|Once we have initial access to the target system, regardless of how high our privileges are at that moment, we need to gather information about the local system. Whether we use this new information for privilege escalation, lateral movement, or data exfiltration does not matter. Therefore, before we can take any further steps, we need to find out what we are dealing with. This inevitably takes us to the vulnerability assessment stage, where we analyze and evaluate the information we find.|
|`Post-Exploitation`|`Post-exploitation` is mainly about escalating privileges if we have not yet attained the highest possible rights on the target host. As we know, more opportunities are open to us with higher privileges. This path actually includes the stages `Information Gathering`, `Vulnerability Assessment`, `Exploitation`, and `Lateral Movement` but from an internal perspective on the target system. The direct jump to post-exploitation is less frequent, but it does happen. Because through the exploitation stage, we may already have obtained the highest privileges, and from here on, we start again at `Information Gathering`.|
|`Lateral Movement`|From here, we can also skip directly over to `Lateral Movement`. This can come under different conditions. If we have achieved the highest privileges on a dual-homed system used to connect two networks, we can likely use this host to start enumerating hosts that were not previously available to us.|
|`Proof-of-Concept`|We can take the last path after gaining the highest privileges by exploiting an internal system. Of course, we do not necessarily have to have taken over all systems. However, if we have gained the Domain Admin privileges in an Active Directory environment, we can likely move freely across the entire network and perform any actions we can imagine. So we can create the `Proof-of-Concept` from our notes to detail and potentially automate the paths and activities and make them available to the technical department.|

This stage is so comprehensive that it has been divided into two distinct areas. The first category is general network protocols often used and present in almost every network. The actual exploitation of the potential and existing vulnerabilities is based on the adaptability and knowledge of the different network protocols we will be dealing with. In addition, we need to be able to create an overview of the existing network to understand its individual components' purposes. In most cases, web servers and applications contain a great deal of information that can be used against them. As stated previously, since web is a vast technical area in its own right, it will be treated separately. We are also interested in the remotely exposed services running on the target hosts, as these may have misconfigurations or known public vulnerabilities that we can leverage for initial access. Finally, existing users also play a significant role in the overall network.
<div align="center">
<br>
<br>
</div>

#### Web Exploitation

Web exploitation is the second part of the exploitation stage. Many different technologies, improvements, features, and enhancements have been developed in this area over the last few years, and things are constantly evolving. As a result, many different components come into play when dealing with web applications. This includes many kinds of databases that require differing command syntax to interact with. Due to the diversity of web applications available to companies and their prevalence worldwide, we must deal with this area separately and focus intently on it. Web applications present a vast attack surface and are often the main accessible targets during external penetration testing engagements, so strong web enumeration and exploitation skills are paramount.
<div align="center">
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
</div>

## Post-Exploitation

In most cases, when we exploit certain services for our purposes to gain access to the system, we usually do not obtain the highest possible privileges. Because services are typically configured in a certain way "isolated" to stop potential attackers, bypassing these restrictions is the next step we take in this stage. However, it is not always easy to escalate the privileges. After gaining in-depth knowledge about how these operating systems function, we must adapt our techniques to the particular operating system and carefully study how `Linux Privilege Escalation` and `Windows Privilege Escalation` work.

![Penetration testing process: Pre-Engagement, Information Gathering, Vulnerability Assessment, Exploitation, Post-Exploitation, Lateral Movement, Proof-of-Concept, Post-Engagement.](https://cdn.services-k8s.prod.aws.htb.systems/content/modules/90/0-PT-Process-POEX.png)

From this stage, there are four paths we can take, depending on how far we have come:

|**Path**|**Description**|
|---|---|
|`Information Gathering / Pillaging`|Before we can begin escalating privileges, we must first get an overview of the inner workings of the exploited system. After all, we do not know which users are on the system and what options are available to us up to this point. This step is also known as `Pillaging`. This path is not optional, as with the others, but essential. Again, entering the `Information Gathering` stage puts us in this perspective. This inevitably takes us to the vulnerability assessment stage, where we analyze and evaluate the information we find.|
|`Exploitation`|Suppose we have found sensitive information about the system and its' contents. In that case, we can use it to exploit local applications or services with higher privileges to execute commands with those privileges.|
|`Lateral Movement`|From here, we can also skip directly over to `Lateral Movement`. This can come under different conditions. If we have achieved the highest privileges on a dual-homed system used to connect two networks, we can likely use this host to start enumerating hosts that were not previously available to us.|
|`Proof-of-Concept`|We can take the last path after gaining the highest privileges by exploiting an internal system. Of course, we do not necessarily have to have taken over all systems. However, if we have gained the Domain Admin privileges in an Active Directory environment, we can likely move freely across the entire network and perform any actions we can imagine. So we can create the `Proof-of-Concept` from our notes to detail and potentially automate the paths and activities and make them available to the technical department.|

After we have gained access to a system, we must be able to take further steps from within the system. During a penetration test, customers often want to find out how far an attacker could go in their network. There are many different versions of operating systems. For example, we may run into Windows XP, Windows 7, 8, 10, 11, and Windows Server 2008, 2012, 2016, and 2019. There are also different distributions for Linux-based operating systems, such as Ubuntu, Debian, Parrot OS, Arch, Deepin, Redhat, Pop!_OS, and many others. No matter which of these systems we get into, we have to find our way around it and understand the individual weak points that a system can have from within.