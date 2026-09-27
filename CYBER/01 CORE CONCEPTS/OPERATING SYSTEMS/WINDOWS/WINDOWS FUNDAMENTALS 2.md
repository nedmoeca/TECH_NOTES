---
tags:
  - THM
  - THM-PRE_SECURITY
  - 5-WINDOWS_FUNDAMENTALS
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

We will continue our journey exploring the Windows operating system. 

In [Windows Fundamentals 1](https://tryhackme.com/room/windowsfundamentals1xbx), we covered the desktop, the file system, user account control, the control panel, settings, and the task manager. 

This module will attempt to provide an overview of some other utilities available within the Windows operating system and different methods to access these utilities.

Press the **Start Machine** button below to launch the attached virtual machine.

If you wish to access the virtual machine via Remote Desktop, use the credentials below. 

Machine IP: `MACHINE_IP`
User: `administrator`
Password: `letmein123!`
<div align="center"><br><img width="" src="https://assets.tryhackme.com/additional/win-event-logs/remmina.png" alt=""></div>

Accept the Certificate when prompted, and you should be logged into the remote system now.

Note: The virtual machine may take up to 3 minutes to load.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 2. System Configuration

The **System Configuration** utility (`MSConfig`) is for advanced troubleshooting, and its main purpose is to help diagnose startup issues. 

Reference the following document [here](https://docs.microsoft.com/en-us/troubleshoot/windows-client/performance/system-configuration-utility-troubleshoot-configuration-errors) for more information on the System Configuration utility. 

There are several methods to launch System Configuration. One method is from the Start Menu.

![](https://assets.tryhackme.com/additional/win-fun2/msconfig-start.png)  

**Note**: You need local administrator rights to open this utility. 

The utility has five tabs across the top. Below are the names for each tab. We will briefly cover each tab in this task. 

1. General
2. Boot
3. Services
4. Startup
5. Tools

![](https://assets.tryhackme.com/additional/win-fun2/msconfig1.png)  

In the **General** tab, we can select what devices and services for Windows to load upon boot. The options are: **Normal**, **Diagnostic**, or **Selective**. 

In the **Boot** tab, we can define various boot options for the Operating System. 

![](https://assets.tryhackme.com/additional/win-fun2/msconfig2.png)  

The **Services** tab lists all services configured for the system regardless of their state (running or stopped). A service is a special type of application that runs in the background.  

![](https://assets.tryhackme.com/additional/win-fun2/msconfig3.png)  

In the **Startup** tab, you won't see anything interesting in the attached VM.  Below is a screenshot of the Startup tab for **MSConfig** from my local machine. 

![](https://assets.tryhackme.com/additional/win-fun2/msconfig4.png)  

As you can see, Microsoft advises using **Task Manager (**`taskmgr`**)** to manage (enable/disable) startup items. The System Configuration utility is **NOT** a startup management program. 

**Note**: If you open Task Manager for the attached VM, you will notice that Task Manager doesn't show a Startup tab. 

There is a list of various utilities (tools) in the Tools tab that we can run to configure the operating system further. There is a brief description of each tool to provide some insight into what the tool is for. 

![](https://assets.tryhackme.com/additional/win-fun2/msconfig5.png)  

Notice the **Selected command** section. The information in this textbox will change per tool.

To run a tool, we can use the command to launch the tool via the run prompt, command prompt, or by clicking the `Launch` button.
<div>
<br>
<br>
</div>

### Questions

##### What is the name of the service that lists Systems Internals as the manufacturer?
PsShutdown
<div align="center"><br><img width="" src="Pasted image 20250922145522.png" alt=""></div>

##### Whom is the Windows license registered to?
Windows User
<div align="center"><br><img width="" src="Pasted image 20250922145752.png" alt=""></div>
<div align="center"><br><img width="" src="Pasted image 20250922151239.png" alt=""></div>

##### What is the command for Windows Troubleshooting?
C:\Windows\System32\control.exe /name Microsoft.Troubleshooting

##### What command will open the Control Panel? (The answer is  the name of .exe, not the full path)
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 3. Change UAC Settings

We're continuing with Tools that are available through the **System Configuration** panel.  

**User Account Control** (UAC) was covered in great detail in [Windows Fundamentals 1](https://tryhackme.com/room/windowsfundamentals1xbx). 

The UAC settings can be changed or even turned off entirely (not recommended).

You can move the slider to see how the setting will change the UAC settings and Microsoft's stance on the setting.

![](https://assets.tryhackme.com/additional/win-fun2/uac.png)
<div>
<br>
<br>
</div>

### Questions

##### What is the command to open User Account Control Settings? (The answer is the name of the .exe file, not the full path)
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 4. Computer Management
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 5. System Information
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 6. Resource Monitor
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 7. Command Prompt
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 8. Registry Editor
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## 9. Conclusion
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References

https://tryhackme.com/room/windowsfundamentals2x0x