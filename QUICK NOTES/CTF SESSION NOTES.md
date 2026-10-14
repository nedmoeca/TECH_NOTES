| Port  | Service  | Version                | Analysis                                                                          | Simple Explanation                                                                        |
| ----- | -------- | ---------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 22    | SSH      | OpenSSH 9.6p1          | Modern, no public RCE. Credential-only entry point.                               | The front door. Useless until we find a username and password.                            |
| 80    | HTTP     | nginx 1.24.0           | 301 to `https://management.htb/`. Confirms name-based vhosting.                   | Plain web port that just bounces you to the secure one and reveals the real hostname.     |
| 443   | HTTPS    | nginx 1.24.0           | Main site. Cert SAN is wildcard `*.management.htb`.                               | The real website. Its ID card admits other subdomains exist but won’t name them.          |
| 1689  | Java RMI | OpenDJ JMX             | Registry dump names OpenDJ, points to the dynamic RMI port. Refuses unauth use.   | A management channel for the directory server. Locked, but it confirms what’s running.    |
| 4444  | LDAPS    | OpenDJ Admin Connector | Secure admin endpoint, refuses anonymous ops. Cert CN leaks `sso.management.htb`. | A locked admin line, but its certificate accidentally prints the hidden subdomain’s name. |
| 38591 | Java RMI | (dynamic)              | Secondary JMX endpoint tied to the JVM. Changes each reboot. Noise.               | A second locked management channel. Ignore it.                                            |
| 50389 | LDAP     | OpenDJ config store    | Anonymous bind accepted. Non-standard port. The reconnaissance jackpot.           | The directory database lets strangers connect without a password. Worth a closer look.    |



#### CVE Breakdown

The vulnerability we picked, CVE-2026-33439, is a **Java deserialization** bug. That phrase sounds intimidating, so here it is in plain terms.

Programs often need to save a live object (a chunk of data sitting in memory) to disk or send it across the network. To do that, Java flattens the object into a stream of bytes. That flattening is called **serialization**. **Deserialization** is the reverse: taking those bytes and rebuilding the original object back in memory.

Here is where the danger lives. While Java rebuilds an object from bytes, it automatically runs certain setup methods on the classes it reconstructs. If an attacker gets to supply the bytes, they get to choose which classes are rebuilt and, by extension, which of those automatic methods fire. String enough of these together in the right order and you can steer the program into running a command of your choice. That smuggled sequence of classes is called a **gadget chain**.

OpenAM takes the value of an HTTP parameter named `jato.clientSession`, decodes it, and feeds it straight into Java's deserializer with no checks on which classes are allowed. So an unauthenticated attacker can hand OpenAM a malicious byte blob in that one parameter and have it rebuilt into something that runs code on the server. No login is needed, because the vulnerable pages (login and password reset) are reachable before you sign in.

A bit of history makes it worse: a nearly identical bug was fixed years ago (CVE-2021-35464) on a related parameter, `jato.pageSession`, by adding an allow-list of safe classes. Nobody applied that same fix to `jato.clientSession`, so the hole was left wide open on a parameter sitting right next to the patched one.