## IOC

An **IOC** stands for **Indicator of Compromise**. An **IOC** is a piece of forensic data that identifies potentially malicious activity on a system or network. These indicators help security teams **detect, respond to, and investigate** potential threats or intrusions.

## Examples of Common IOCs:

- **IP addresses** or domains known to be associated with malicious activity
- **File hashes** (e.g., MD5, SHA256) of known malware
- **Unusual outbound traffic** to foreign or untrusted IPs
- **Anomalous login activity**, like logins at strange hours or from unusual locations
- **Unexpected changes** in system files or configurations
- **Phishing email artifacts**, such as suspicious sender addresses or attachments
- **Registry changes** in Windows that are commonly used by malware
- **Command and control (C2) server connections**

### How Are IOCs Used?

1. **Detection** – SIEM systems and antivirus software use IOCs to scan for signs of compromise.
2. **Threat Hunting** – Analysts search for IOCs within logs and systems to identify threats.
3. **Incident Response** – During or after an attack, IOCs help in understanding the scope and nature of the breach.
4. **Threat Intelligence Sharing** – Organizations share IOCs with peers or industry groups to help others defend against known threats.

### Example:

If a threat actor uses the domain `malicious-update[.]com` to deliver malware, that domain becomes an IOC. Security teams can then block or monitor this domain across their infrastructure.

---

## IOA


---

## References



