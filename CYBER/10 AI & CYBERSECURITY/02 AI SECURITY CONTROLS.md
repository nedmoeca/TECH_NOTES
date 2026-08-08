---
## Review AI open-source libraries
---
AI security controls refer to the measures and protocols implemented to protect artificial intelligence systems from threats, vulnerabilities, and unauthorized access. Security controls can be technical, administrative, physical, regulatory, or operational. AI security controls are technical, administrative, and operational.

---

## Review AI open-source libraries

Open-source software (OSS) is an integral part of modern software development, and AI OSS software is no different. Just like other OSS software, AI OSS tools and libraries need to undergo a comprehensive security review. When you are performing a security review, you need to perform the following steps:

- Assess the suitability of OSS libraries
- Code review and dependency analysis
- Documentation and community support
- Vulnerability Scanning and Remediation:

### Assess the suitability of OSS libraries

You should assess the suitability of the OSS libraries you intend to use. You can do this from the perspective of context and purpose and general risk assessment.

- Context and purpose: Begin by understanding why you're reviewing an OSS library. Are you considering it for integration into your project, assessing its security, or ensuring compliance? Define the context and purpose of your review clearly and the criteria under which the review will be successful.
- Risk Assessment: Consider the potential risks associated with using the library. Threat modeling helps identify attack vectors and security goals. Understand how the library fits into your application's attack surface.

### Code review and dependency analysis

You'll also need to perform a review an OSS library's code and an evaluation of the dependency chains.

- Code inspection: Examine into the library's source code. Look for security flaws, such as buffer overflows, injection vulnerabilities, and insecure cryptographic practices. Pay attention to authentication mechanisms, input validation, and error handling.
- Dependency evaluation: Assess the library's dependencies. Outdated or vulnerable components can introduce risks. Use tools to identify known vulnerabilities in these dependencies.

### Documentation and community support

Perform a review of the ecosystem supporting the OSS library.

- Documentation quality: Evaluate the clarity and completeness of the library's documentation. Good documentation provides insights into security features, usage guidelines, and potential pitfalls.
- Community engagement: Consider the library's community. Active maintainers and responsive communities are indicators of a healthy project. They can help address security issues promptly.

### Vulnerability scanning and remediation

When using OSS libraries, you shouldn't assume that others have performed vulnerability checks. Instead should apply your own vulnerability assessment toolchain to the code you wish to adopt.

- Comprehensive scans: Use vulnerability scanners to identify potential security weaknesses. These tools analyze the library and its dependencies for known vulnerabilities.
- Mitigation strategies: If vulnerabilities are detected, assess their impact and prioritize remediation. Patch or update the library as needed.


---

## Content filters

AI content filters are systems designed to detect and prevent harmful or inappropriate content. They work by evaluating input prompts and output completions, using neural classification models to identify specific categories such as hate speech, sexual content, violence, and self-harm. These filters help ensure that AI-generated content aligns with safety guidelines and provides high-quality information.

Microsoft's Content Safety Studio assists you in ensuring all user-generated content, such as product reviews, forum posts, and images, aligns with your organization's content guidelines.

Content Safety Studio offers a suite of features designed to monitor and moderate content in real-time. It includes:

- **Text Moderation**: Detects and filters out harmful content in text, such as hate speech, violence, or inappropriate language.
- **Image Moderation**: Analyzes images to identify and block content that may be considered unsafe or offensive.
- **Multimodal Content Analysis**: Works across different types of content, ensuring a comprehensive content safety strategy.
- **Groundedness** **Detection**: Detects and blocks incorrect information in model outputs, ensuring that the text responses of large language models are factual and accurate, based on the source materials provided.
- **Prompt Shields**: Analyzes LLM inputs and detects user Prompt attacks and Document attacks.
- **Protected Material Detection**: Identifies and blocks outputs that could potentially violate copyright by scanning for matches against an index of third-party text content, including songs, news articles, recipes, and selected web content.
- **Monitor Online Activity**: Track your moderation API usage and trends across different modalities.

Here you can see an example of content filtering working correctly and also failing:

![Screenshot of guardrail protection and failure modes.](https://learn.microsoft.com/en-us/training/advocates/ai-security-controls/media/content-filtering.png)

---

## Implement AI data security

Data security is crucial for AI because AI systems can exacerbate existing issues with data classification, permissions, and governance. As AI makes data discovery easy, any problems with data handling are magnified, leading to potential data leakage, and unauthorized access. AI not only relies on data but also creates new data that gains value, making it a target for attackers who want to steal secrets or cause harm. Therefore, although data security isn't a new issue, AI makes getting data security right even more critical. Access control decisions should never be devolved to the AI system. AI should only have access to the same data as the user it's acting on behalf of.

The image provides a summary of the important challenges of AI data security. Using AI amplifies existing data security challenges, increases the value of data, and provides new avenues for data leakage.

![Screenshot of the challenges of AI governance and security.](https://learn.microsoft.com/en-us/training/advocates/ai-security-controls/media/challenges-governance-security.png)

The image provides a breakdown of the kinds of data that generative AI consumes and the kind of data it creates and the kind of data to which it has access. There's a huge range of data that needs to be taken into consideration when assessing and planning to implement AI data security.

![Screenshot of the types of data used by generative AI.](https://learn.microsoft.com/en-us/training/advocates/ai-security-controls/media/generative-ai-data.png)

---

## Create metaprompts

A metaprompt, or system message, is a set of natural language instructions used to guide an AI system's behavior (_do this, not that_). A good metaprompt would say "if a user requests large quantities of content, only return a summary of those search results." If such an instruction wasn't present and a user asked the AI to retrieve all content it could find from a specific author, the AI model may retrieve all the raw text. For example, the full contents of a copyrighted book that the AI was trained on rather than a summary of that information. Metaprompt design is crucial for every generative AI application.

Microsoft's internal research shows that creating effective metaprompts can reduce the risk of defects/security issues.

![Screenshot showing metaprompts and the issues they mitigate.](https://learn.microsoft.com/en-us/training/advocates/ai-security-controls/media/metaprompts.png)

Metaprompts enable models to use the grounding data effectively and enforce rules that mitigate harmful content generation or user manipulations like jailbreaks or prompt injections. Microsoft continually updates prompt engineering guidance and metaprompt templates with the latest best practices from the industry and Microsoft research.

---

## Ground AI systems

Grounding an AI is the process of connecting the abstract concepts and knowledge within an AI system to real-world data and experiences. For example: an AI model predicts the weather by using real-time and historical weather data. Grounding ensures the model's predictions are based on historical weather patterns, which improves accuracy. Grounding ensures that the AI's understanding and responses are accurate and relevant to the actual environment it operates in and helps in the following ways:

- **Bridging abstract concepts with reality**: Grounding helps AI systems bridge the gap between their internal, abstract concepts and the practical, tangible world. It's like teaching a robot to understand and use real-world objects and ideas.

- **Enhancing decision making accuracy**: By anchoring AI's learning and decision-making processes in real-world data, grounding improves the accuracy and reliability of AI outputs, making them more trustworthy and effective.

- **Adapting to real-world changes**: Grounding allows AI systems to adapt to changing real-world scenarios, maintaining their effectiveness over time by understanding and applying context.


Grounding is crucial for developing AI systems that can interact with and understand the complexities of the real world, providing contextually appropriate, accurate, and meaningful results.

Microsoft employs several techniques to achieve grounding in AI products, ensuring that the AI's responses are relevant, accurate, and tailored to specific use-cases. Here are some of the key methods used:

- **Retrieval Augmented Generation (RAG)**: This technique involves retrieving information relevant to a task and providing it to the language model along with a prompt. The model then uses this specific information when responding, which helps in grounding the AI's output in the context of the particular use-case.

- **Prompt engineering**: Microsoft uses advanced prompt engineering techniques to increase the accuracy and grounding of responses generated by Large Language Models (LLMs). This includes crafting prompts that provide context, instructions, or other relevant information to prime the model for generating appropriate responses.

- **Groundedness detection**: Azure AI has a groundedness detection feature that evaluates claims made by the AI using a custom language model fine-tuned to a Natural Language Inference (NLI) task. This helps in detecting and mitigating ungrounded model outputs.

---

## Implement application security best practices for AI enabled applications

AI enabled applications are still applications, and therefore it is still important to follow secure coding and other application security best practices. When building AI applications, make sure that you consider the following security principles and practices:

- **Secure Software Development Life Cycle (SDLC)**
    - Integrate security measures at every stage of development.
    - Conduct regular security reviews and automated testing.
    - Adopt a DevSecOps approach to balance security and development velocity.
- **AI plugin security**
    - Use application security best practices to develop plugins
    - Plugins must securely request and retrieve data
    - Sanitize and validate inputs
- **Adopt the Principle of Least Privilege**
    - Limit permissions to the minimum necessary for users, applications, and services.
    - Reduce the impact of compromised accounts and unauthorized data access.
- **Secure Data Storage and Transmission:**
    - Encrypt sensitive data both at rest and in transit.
    - Implement secure protocols for data exchange.
- **Leverage Monitoring and Observability:**
    - Monitor application behavior for anomalies and security incidents.
    - Use logging and auditing to track events and detect threats.
- **Perform Regular Security Testing and Auditing:**
    - Conduct vulnerability assessments, penetration testing, and code reviews.
    - Address vulnerabilities early to minimize post-deployment remediation.

---

## References

https://learn.microsoft.com/en-us/training/modules/ai-security-controls/