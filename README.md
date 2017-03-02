# MailBlinker
Blink the capslock LED if new mails are on the IMAP-server.

Change `imap_connection.py` to use your credentials for your IMAP-Server. 
Google users mith 2-factor-auth may have to generate a App-Password for 
this.

Execute the script with root privileges:
```shell
sudo python mailblinker.py
```
The privileges are needed because the script needs to write to 
`/dev/tty0`. Feel free to fork this repository for a better solution. 