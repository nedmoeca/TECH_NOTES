==DEF-Threat Intelligence is the analysis of data and information using tools and techniques to generate meaningful patterns on how to mitigate against potential risks associated with existing or emerging threats targeting organizations, industries, sectors or governments.== ^a34113

To mitigate against risks, we can start by trying to answer a few simple questions:
- Who's attacking you?
- What's their motivation?
- What are their capabilities?
- What artefacts and indicators of compromise should you look out for?

## Threat Intelligence Classifications:

Threat Intel is geared towards understanding the relationship between your operational environment and your adversary. With this in mind, we can break down threat intel into the following classifications: 

- **Strategic Intel:** High-level intel that looks into the organisation's threat landscape and maps out the risk areas based on trends, patterns and emerging threats that may impact business decisions.
- **Technical Intel:** Looks into evidence and artefacts of attack used by an adversary. Incident Response teams can use this intel to create a baseline attack surface to analyse and develop defence mechanisms.
- **Tactical Intel:** Assesses adversaries' tactics, techniques, and procedures (TTPs). This intel can strengthen security controls and address vulnerabilities through real-time investigations.
- **Operational Intel:** Looks into an adversary's specific motives and intent to perform an attack. Security teams may use this intel to understand the critical assets available in the organisation (people, processes, and technologies) that may be targeted.


---

## Threat Intelligence Tools

- Using [UrlScan.io](https://urlscan.io/) to scan for malicious URLs.
- Using [Abuse.ch](https://abuse.ch/) to track malware and botnet indicators. It was developed to identify and track malware and botnets through several operational platforms developed under the project. These platforms are:
	- [Malware Bazaar](https://bazaar.abuse.ch/):  A resource for sharing malware samples.
	- [Feodo Tracker](https://feodotracker.abuse.ch/):  A resource used to track botnet command and control (C2) infrastructure linked with Emotet, Dridex and TrickBot.
	- [SSL Blacklist](https://sslbl.abuse.ch/):  A resource for collecting and providing a blocklist for malicious SSL certificates and JA3/JA3s fingerprints.
	- [URL Haus](https://urlhaus.abuse.ch/):  A resource for sharing malware distribution sites.
	- [Threat Fox](https://threatfox.abuse.ch/):  A resource for sharing indicators of compromise (IOCs).
- Investigate phishing emails using [PhishTool](https://www.phishtool.com/)
- Using [Cisco's Talos Intelligence](https://talosintelligence.com/) platform for intel gathering


---

## References

https://tryhackme.com/room/threatinteltools
https://urlscan.io/
https://abuse.ch/
https://www.phishtool.com/
https://talosintelligence.com/
