---
tags:
  - JR_PENETRATION_TESTER
  - INTRODUCTION_TO_PENTESTING
  - THM
  - ROOM
link:
description:
---
## Summary

| SECTION/TASK | FLAG |
| ------------ | ---- |
|              |      |

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 1. Introduction

The following room is going to outline some of the fundamental principles of information security. The frameworks used to protect data and systems to the elements of what exactly makes data secure.

The measures, frameworks and protocols discussed throughout this room all play a small part in "Defence in Depth."

==DEF-Defence in Depth is a security strategy that uses multiple layers of defensive mechanisms to protect systems, networks, and data. The idea is that if one security control fails or is bypassed, additional layers continue to provide protection.==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. The CIA Triad

DEF-CIA Triad: ==The CIA Triad is a foundational model in information security that represents the three core principles used to guide policies, practices, and controls for protecting information and systems==. ^58f409

This model has an extensive background, ranging from being used in 1998.

This history is because the security of information (information security) does not start and/or end with cybersecurity, but instead, applies to scenarios like filing, record storage, etc.

Consisting of three sections: **C**onfidentiality, **I**ntegrity and **A**vailability (**CIA**), this model has quickly become an industry standard today. This model should help determine the value of data that it applies to, and in turn, the attention it needs from the business.

![](https://tryhackme-images.s3.amazonaws.com/user-uploads/5de96d9ca744773ea7ef8c00/room-content/5de96d9ca744773ea7ef8c00-1725781488612.png)  

[[Nist.gov](https://www.nccoe.nist.gov/)]

The CIA triad is unlike a traditional model where you have individual sections; instead, it is a continuous cycle. Whilst the three elements to the CIA triad can arguably overlap, if even just one element is not met, then the other two are rendered useless (similar to the fire triangle). If a security policy does not answer these three sections, it is seldom an effective security policy.

Whilst the three elements to the CIA triad are arguably self-explanatory, let's explore these and contextualize them into cybersecurity.
<div align="center">
<br>
<br>
</div>

### Confidentiality

DEF-Confidentiality: ==Confidentiality is the principle of ensuring that information is kept private, accessible only to authorized individuals with a legitimate need to know, and protected from unauthorized access or misuse through appropriate access controls.== ^e6c51a

There are many real-world examples for this, for example, employee records and accounting documents will be considered sensitive. Confidentiality will be provided in the sense that only HR administrators will access employee records, where vetting and tight access controls are in place. Accounting records are less valuable (and therefore less sensitive), so not as stringent access controls would be in place for these documents. Or, for example, governments using a sensitivity classification rating system (top-secret, classified, unclassified)
<div align="center">
<br>
<br>
</div>

### Integrity

DEF-Integrity: ==Integrity is the assurance that information remains accurate, consistent, complete, and authentic, safeguarded against unauthorized modification or tampering.== ^dc0537

It is possible for the information to change because of careless access and use, errors in the information system, or unauthorized access and use. In the CIA triad, integrity is maintained when the information remains unchanged during storage, transmission, and usage not involving modification to the information. Steps must be taken to ensure data cannot be altered by unauthorised people (for example, in a breach of confidentiality).

Many defenses to ensure integrity can be put in place. Access control and rigorous authentication can help prevent authorized users from making unauthorized changes. Hash verifications and digital signatures can help ensure that transactions are authentic and that files have not been modified or corrupted.
<div align="center">
<br>
<br>
</div>

### Availability

DEF-Availability: ==Availability is the guarantee that information and resources are accessible and usable when needed by authorized users, without undue delay or disruption.== ^3df46e

Availability is very often a key benchmark for an organisation. For example, having 99.99% uptime on their websites or systems (this is laid out in Service Level Agreements). When a system is unavailable, it often results in damage to an organisations reputation and financial. Availability is achieved through a combination of many elements, including:

- Having reliable and well-tested hardware for their information technology servers (i.e. reputable servers)
- Having redundant technology and services in the case of failure of the primary
- Implementing well-versed security protocols to protect technology and services from attack
<div align="center">
<br>
<br>
</div>

### Questions

##### What element of the CIA triad ensures that data cannot be altered by **unauthorised** people?
integrity
<div align="center">
<br>
</div>

##### What element of the CIA triad ensures that data is available?
availability
<div align="center">
<br>
</div>

##### What element of the CIA triad ensures that data is only accessed by **authorised** people?
confidentiality
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Principles of Privileges

<div align="center"><br><img width=400 src="https://tryhackme-images.s3.amazonaws.com/user-uploads/5de96d9ca744773ea7ef8c00/room-content/b89ffd2bbfbdd7c3837508619ff7027f.png"></div>

It is vital to administrate and correctly define the various levels of access to an information technology system individuals require. 

The levels of access given to individuals are determined on two primary factors:
- The individual's role/function within the organisation
- The sensitivity of the information being stored on the system

Two key concepts are used to assign and manage the access rights of individuals: Privileged Identity Management (PIM) and Privileged Access Management (PAM).

DEF-PIM is used to translate a user's role within an organisation into an access role on a system. Whereas DEF-PAM is the management of the privileges a system's access role has, amongst other things.

What is essential when discussing privilege and access controls is the principle of least privilege. ==The DEF-Principle of Least Privilege (PoLP)** is a security concept that states Users, applications, systems, and processes should be granted the **minimum level of access or permissions** necessary to perform their required tasks—**and no more**.==

This reduces the attack surface and limits potential damage if an account or system is compromised.
- **Example (User):** An employee in HR only gets access to personnel records, not financial systems.
- **Example (System):** A web application service account can read from a database but cannot delete or modify tables.  

As we previously mentioned, PAM incorporates more than assigning access. It also encompasses enforcing security policies such as password management, auditing policies and reducing the attack surface a system faces.
<div align="center">
<br>
<br>
</div>

### Questions

##### What does the acronym "PIM" stand for?
Privileged Identity Management
<div align="center">
<br>
</div>

##### What does the acronym "PAM" stand for?
Privileged Access Management
<div align="center">
<br>
</div>

##### If you wanted to manage the privileges a system access role had, what methodology would you use?
PAM
<div align="center">
<br>
</div>

##### If you wanted to create a system role that is based on a users role/responsibilities with an organisation, what methodology is this?
PIM
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Security Models Continued

Before discussing security models further, let's recall the three elements of the CIA triad: Confidentiality, Integrity and Availability. We've previously outlined what these elements are and their importance. However, there is a formal way of achieving this.

According to a security model, any system or piece of technology storing information is called an information system, which is how we will reference systems and devices in this task.

Let's explore some popular and effective security models used to achieve the three elements of the CIA triad.
<div align="center">
<br>
<br>
</div>

### The Bell-La Padula Model

The Bell-La Padula Model is used to achieve confidentiality. This model has a few assumptions, such as an organisation's hierarchical structure it is used in, where everyone's responsibilities/roles are well-defined.

The model works by granting access to pieces of data (called objects) on a strictly need to know basis. This model uses the rule "no write down, no read up".

| **Advantages**                                                                                   | **Disadvantages**                                                                                                                   |
| ------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| Policies in this model can be replicated to real-life organisations hierarchies (and vice versa) | Even though a user may not have access to an object, they will know about its existence -- so it's not confidential in that aspect. |
| Simple to implement and understand, and has been proven to be successful.                        | The model relies on a large amount of trust within the organisation.                                                                |

<div align="center"><br><img src="https://tryhackme-images.s3.amazonaws.com/user-uploads/5de96d9ca744773ea7ef8c00/room-content/0e6e5d9d80785fc287b4a67e1453b295.png"><br></div>


The Bell LaPadula Model is popular within organisations such as governmental and military. This is because members of the organisations are presumed to have already gone through a process called vetting. Vetting is a screening process where applicant's backgrounds are examined to establish the risk they pose to the organisation. Therefore, applicants who are successfully vetted are assumed to be trustworthy - which is where this model fits in.
<div align="center">
<br>
<br>
</div>

### Biba Model

The Biba model is arguably the equivalent of the Bell-La Padula model but for the integrity of the CIA triad.

This model applies the rule to objects (data) and subjects (users) that can be summarised as "no write up, no read down". This rule means that subjects **can** create or write content to objects at or below their level but **can only** read the contents of objects above the subject's level.

Let's compare some advantages and disadvantages of this model in the table below:

| **Advantages**                                                                                              | **Disadvantages**                                                                                                                                   |
| ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| This model is simple to implement.                                                                          | There will be many levels of access and objects. Things can be easily overlooked when applying security controls.                                   |
| Resolves the limitations of the Bell-La Padula model by addressing both confidentiality and data integrity. | Often results in delays within a business. For example, a doctor would not be able to read the notes made by a nurse in a hospital with this model. |

<div align="center"><br><img src="https://tryhackme-images.s3.amazonaws.com/user-uploads/5de96d9ca744773ea7ef8c00/room-content/895ba351ef24ef6495d290222e49470e.png"></div>


The Biba model is used in organisations or situations where integrity is more important than confidentiality. For example, in software development, developers may only have access to the code that is necessary for their job. They may not need access to critical pieces of information such as databases, etc.
<div align="center">
<br>
<br>
</div>

### Questions

##### What is the name of the model that uses the rule "**can't** read up, **can** read down"?
The Bell-LaPadula Model
<div align="center">
<br>
</div>

##### What is the name of the model that uses the rule "**can** read up, **can't** read down"?
The Biba Model
<div align="center">
<br>
</div>

##### If you were a military, what security model would you use?
The Bell-LaPadula Model
<div align="center">
<br>
</div>

##### If you were a software developer, what security model would the company perhaps use?
The Biba Model
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. Threat Modelling & Incident Response

==DEF-Threat modelling is the process of reviewing, improving, and testing the security protocols in place in an organisation's information technology infrastructure and services.==

A critical stage of the threat modelling process is identifying likely threats that an application or system may face, the vulnerabilities a system or application may be vulnerable to.

<div align="center"><br><img src="https://tryhackme-images.s3.amazonaws.com/user-uploads/5de96d9ca744773ea7ef8c00/room-content/aabdd83977336fd44b3645a86e5ba20e.png"></div>


The threat modelling process is very similar to a risk assessment made in workplaces for employees and customers. The principles all return to:
- Preparation
- Identification
- Mitigations
- Review

It is, however, a complex process that needs constant review and discussion with a dedicated team. An effective threat model includes:
- Threat intelligence
- Asset identification
- Mitigation capabilities
- Risk assessment

To help with this, there are frameworks such as **STRIDE** (**S**poofing identity, **T**ampering with data, **R**epudiation threats, **I**nformation disclosure, **D**enial of Service and **E**levation of privileges) and **PASTA** (**P**rocess for **A**ttack **S**imulation and **T**hreat **A**nalysis) infosec never tasted so good!. Let's detail STRIDE below. STRIDE, authored by two Microsoft security researchers in 1999 is still very relevant today. STRIDE includes six main principles, which I have detailed in the table below:

| **Principle**          | **Description**                                                                                                                                                                                                                                               |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Spoofing               | This principle requires you to authenticate requests and users accessing a system. Spoofing involves a malicious party falsely identifying itself as another.<br><br>Access keys (such as API keys) or signatures via encryption helps remediate this threat. |
| Tampering              | By providing anti-tampering measures to a system or application, you help provide integrity to the data. Data that is accessed must be kept integral and accurate.<br><br>For example, shops use seals on food products.                                      |
| Repudiation            | This principle dictates the use of services such as logging of activity for a system or application to track.                                                                                                                                                 |
| Information Disclosure | Applications or services that handle information of multiple users need to be appropriately configured to only show information relevant to the owner.                                                                                                        |
| Denial of Service      | Applications and services use up system resources, these two things should have measures in place so that abuse of the application/service won't result in bringing the whole system down.                                                                    |
| Elevation of Privilege | This is the worst-case scenario for an application or service. It means that a user was able to escalate their authorization to that of a higher level i.e. an administrator. This scenario often leads to further exploitation or information disclosure.    |

==A breach of security is known as an DEF-incident.== And despite all rigorous threat models and secure system designs, incidents do happen. ==Actions taken to resolve and remediate the threat that caused an incident are known as DEF-Incident Response (IR)== and are a whole career path in cybersecurity.

Incidents are classified using a rating of urgency and impact. Urgency will be determined by the type of attack faced, where the impact will be determined by the affected system and what impact that has on business operations.

<div align="center"><br><img src="https://tryhackme-images.s3.amazonaws.com/user-uploads/5de96d9ca744773ea7ef8c00/room-content/ab0cc8478b0bce9a400187f559d36dd6.png"></div>


An incident is responded to by a **C**omputer **S**ecurity **I**ncident **R**esponse **T**eam (**CSIRT**) which is prearranged group of employees with technical knowledge about the systems and/or current incident. To successfully solve an incident, these steps are often referred to as the six phases of Incident Response that takes place, listed in the table below:

| **Action**      | **Description**                                                                                                                             |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Preparation     | Do we have the resources and plans in place to deal with the security incident?                                                             |
| Identification  | Has the threat and the threat actor been correctly identified in order for us to respond to?                                                |
| Containment     | Can the threat/security incident be contained to prevent other systems or users from being impacted?                                        |
| Eradication     | Remove the active threat.                                                                                                                   |
| Recovery        | Perform a full review of the impacted systems to return to business as usual operations.                                                    |
| Lessons Learned | What can be learnt from the incident? I.e. if it was due to a phishing email, employees should be trained better to detect phishing emails. |
<div>
<br>
<br>
</div>

### Questions

##### What model outlines "Spoofing"?
STRIDE
<div>
<br>
</div>

##### What does the acronym "IR" stand for?
Incident Response
<div>
<br>
</div>

##### You are tasked with adding some measures to an application to improve the integrity of data, what STRIDE principle is this?
Tampering
<div>
<br>
</div>

##### An attacker has penetrated your organisation's security and stolen data. It is your task to return the organisation to business as usual. What incident response stage is this?
Recovery
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

https://tryhackme.com/room/principlesofsecurity