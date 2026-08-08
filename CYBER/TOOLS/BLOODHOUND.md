**BloodHound** is a powerful **cybersecurity tool** used to analyze **Active Directory (AD)** environments, typically during **penetration testing** and **red team** engagements. It helps security professionals understand and visualize **privilege escalation paths** within a Windows domain.

## What BloodHound Does:

BloodHound maps out **relationships and permissions** in an Active Directory network to reveal **hidden paths attackers can use** to escalate privileges — for example, how a low-privileged user could eventually gain **domain admin** access.


## How BloodHound Works:

1. **Data Collection** – A component called **SharpHound** (a C# data collector) is run on a domain-joined system to gather:
    - Group memberships
    - Session data (who is logged into what)
    - Trust relationships
    - ACLs on AD objects
    - Local admin rights
2. **Data Upload** – The data is uploaded to the BloodHound interface.
3. **Graph Analysis** – BloodHound visualizes the AD environment as a **graph database**, showing nodes (users, computers, groups) and edges (relationships).
4. **Attack Path Discovery** – Analysts use built-in queries to find paths such as:
    - **Shortest path to domain admin**
    - **Unconstrained delegation paths**
    - **Kerberoastable users**
    - **ACL-based privilege escalation**


## Example Use Case:

An attacker compromises a low-level user account. BloodHound reveals that this user has local admin rights on a machine where a domain admin is logged in. From there, the attacker uses credential dumping to get domain admin privileges — all visualized in BloodHound.


---

## Installing BloodHound

```
sudo apt install bloodhound neo4j
```

**Neo4j** is a graph database BloodHound relies on.


---

## References

https://tryhackme.com/room/attacktivedirectory