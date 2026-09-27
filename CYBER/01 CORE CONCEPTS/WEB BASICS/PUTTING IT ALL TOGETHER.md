---
tags:
  - THM
  - HOW_THE_WEB_WORKS
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

To summarize, when you request a website, your computer needs to know the server's IP address it needs to talk to; for this, it uses DNS. Your computer then talks to the web server using a special set of commands called the HTTP protocol; the webserver then returns HTML, JavaScript, CSS, Images, etc., which your browser then uses to correctly format and display the website to you.

![[Pasted image 20250702235202.png]]

There are also a few other components that help the web run more efficiently and provide extra features.

---

## Other Components
### Load Balancer

==A **load balancer** is a system or device that distributes incoming network traffic across multiple servers or resources to ensure no single server becomes overwhelmed.==

When a website's traffic starts getting quite large or is running an application that needs to have high availability, one web server might no longer do the job. Load balancers provide two main features, ensuring high traffic websites can handle the load and providing a failover if a server becomes unresponsive.

When you request a website with a load balancer, the load balancer will receive your request first and then forward it to one of the multiple servers behind it. The load balancer uses different algorithms to help it decide which server is best to deal with the request. A couple of examples of these algorithms are **round-robin**, which sends it to each server in turn, or **weighted**, which checks how many requests a server is currently dealing with and sends it to the least busy server.

Load balancers also perform periodic checks with each server to ensure they are running correctly; this is called a **health check**. If a server doesn't respond appropriately or doesn't respond, the load balancer will stop sending traffic until it responds appropriately again.

![](https://tryhackme-images.s3.amazonaws.com/user-uploads/5c549500924ec576f953d9fc/room-content/829e340231cd8aa9f5ed2fa5c464ea80.svg)  

### CDN (Content Delivery Networks)

A **CDN** (Content Delivery Network) is a network of geographically distributed servers that work together to deliver web content (like images, videos, scripts, or entire web pages) to users **more quickly and reliably**.

**Here’s how it works:**
- Instead of serving content from a single origin server (like the one where your website is hosted), a CDN stores cached copies of your content on servers all over the world — these are called **edge servers**.
- When a user visits your website, the CDN delivers the content from the **edge server that’s physically closest to them**, which reduces latency and speeds up load times.
- CDNs also help handle **traffic spikes** by distributing requests across many servers, improving reliability and availability.

**Examples of popular CDNs:**
- Cloudflare
- Akamai
- Amazon CloudFront
- Google Cloud CDN
- Fastly

### Databases  

Often websites will need a way of storing information for their users. Webservers can communicate with databases to store and recall data from them. Databases can range from just a simple plain text file up to complex clusters of multiple servers providing speed and resilience. You'll come across some common databases: MySQL, MSSQL, MongoDB, Postgres, and more; each has its specific features.

### WAF (Web Application Firewall)

A **WAF** (Web Application Firewall) is a security system that **monitors, filters, and blocks** malicious HTTP/HTTPS traffic to and from a web application.

A WAF sits between your web request and the web server; its primary purpose is to protect the webserver from hacking or denial of service attacks. It analyses the web requests for common attack techniques, whether the request is from a real browser rather than a bot. It also checks if an excessive amount of web requests are being sent by utilising something called rate limiting, which will only allow a certain amount of requests from an IP per second. If a request is deemed a potential attack, it will be dropped and never sent to the webserver.

![](https://tryhackme-images.s3.amazonaws.com/user-uploads/5c549500924ec576f953d9fc/room-content/24cb6468b4e51e8d8bbe7872e96a22b3.svg)

---

## How Web Servers Work

### What is a Web Server?

A web server is a software that listens for incoming connections and then utilises the HTTP protocol to deliver web content to its clients. The most common web server software you'll come across is Apache, Nginx, IIS and NodeJS. A Web server delivers files from what's called its root directory, which is defined in the software settings. For example, Nginx and Apache share the same default location of /var/www/html in Linux operating systems, and IIS uses C:\inetpub\wwwroot for the Windows operating systems. So, for example, if you requested the file [http://www.example.com/picture.jpg](http://www.example.com/picture.jpg), it would send the file /var/www/html/picture.jpg from its local hard drive.

### Virtual Hosts

Web servers can host multiple websites with different domain names; to achieve this, they use virtual hosts. The web server software checks the hostname being requested from the HTTP headers and matches that against its virtual hosts (virtual hosts are just text-based configuration files). If it finds a match, the correct website will be provided. If no match is found, the default website will be provided instead.

Virtual Hosts can have their root directory mapped to different locations on the hard drive. For example, [one.com](http://one.com/) being mapped to /var/www/website_one, and [two.com](http://two.com/) being mapped to /var/www/website_two

There's no limit to the number of different websites you can host on a web server.

### Static Vs Dynamic Content

Static content, as the name suggests, is content that never changes. Common examples of this are pictures, javascript, CSS, etc., but can also include HTML that never changes. Furthermore, these are files that are directly served from the webserver with no changes made to them.

Dynamic content, on the other hand, is content that could change with different requests. Take, for example, a blog. On the homepage of the blog, it will show you the latest entries. If a new entry is created, the home page is then updated with the latest entry, or a second example might be a search page on a blog. Depending on what word you search, different results will be displayed.

These changes to what you end up seeing are done in what is called the **Backend** with the use of programming and scripting languages. It's called the Backend because what is being done is all done behind the scenes. You can't view the websites' HTML source and see what's happening in the Backend, while the HTML is the result of the processing from the Backend. Everything you see in your browser is called the **Frontend.**

### Scripting and Backend Languages

There's not much of a limit to what a backend language can achieve, and these are what make a website interactive to the user. Some examples of these languages (in no particular order :p) are PHP, Python, Ruby, NodeJS, Perl and many more. These languages can interact with databases, call external services, process data from the user, and so much more. A very basic PHP example of this would be if you requested the website [http://example.com/index.php?name=adam](http://example.com/index.php?name=adam)  

If index.php was built like this:  

`<html><body>Hello <?php echo $_GET["name"]; ?></body></html>`

It would output the following to the client:

`<html><body>Hello adam</body></html>`

You'll notice that the client doesn't see any PHP code because it's on the Backend. This interactivity opens up a lot more security issues for web applications that haven't been created securely, as you learn in further modules.

![[Pasted image 20250703005255.png]]
![[Pasted image 20250703005346.png]]
![[Pasted image 20250703005359.png]]
![[Pasted image 20250703005407.png]]
![[Pasted image 20250703005420.png]]
![[Pasted image 20250703005426.png]]
![[Pasted image 20250703005437.png]]
![[Pasted image 20250703005447.png]]
![[Pasted image 20250703005454.png]]
![[Pasted image 20250703005514.png]]
![[Pasted image 20250703005521.png]]


---

## References

https://tryhackme.com/room/puttingitalltogether