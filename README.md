BayIMCO Appointment Checker
===========================

This is a quick and dirty bot, that checks every time it is called if there are any new available vaccination 
appointments available within the BayIMCO system for a given user.


**Prerequisites**

* If you haven't been invited yet by the system to select an appointment, this will not work.
* If you haven't confirmed your phone number after having been invited to select an appointment, this will not work.
* python3.something


**Installation**

* `mkdir c19ac`
* `cd c19ac`
* `git clone https://github.com/pc-coholic/c19ac.git`
* `python3 -m venv venv`
* `source venv/bin/activate`
* `pip install -r c19ac/requirements.txt`

**Configuration**

* Rename the `config.json.dist`-file to `config.json` and adjust to your desired settings
    * The `userid` is your BayIMCO UUID and can be taken from the URL (e.g. for 
      `https://impfzentren.bayern/citizen/overview/34622806-40C1-4FDF-8F36-D6C4DCD6564E` use 
      `34622806-40C1-4FDF-8F36-D6C4DCD6564E`).
    * The `mail...`-settings should be self-explanatory.
    * The `starttoken` needs to be taken from BayIMCO after the login. Open your browser's Devtools and look for a call 
      to `https://ciam.impfzentren.bayern/auth/realms/C19V-Citizen/protocol/openid-connect/token`. Copy and paste the 
      value of the `refresh_token`.
    * `recipient` is the mail-address that will receive the notifications.
    * Using `stop_on_success`, you can decide if the bot should keep working, even after an appointment has been found.
    * `stop_on_fail` will not let the bot run, if the query for appointments fails.
    * `stop_on_tokenfail` controls if the bot will keep trying to get data, if refreshing the Authorization token fails.
    * `sys_stop` is the setting that will be set by the script, if any of the above three settings have triggered a 
      stop. To reset, set this back to false.
* `cd` into the script's directory, run it, and check the output.
* Setup a cronjob to run the script at your desired intervals. Every 5 Minutes should be plenty:
    * `*/5 * * * * cd /home/user/c19ac/c19ac; /home/user/c19ac/venv/bin/python3 check.py >> /home/user/c19ac/c19ac.log 2>&1`
    

**Things to keep in mind**

The following information is accurate as of 02.04.2021/BayIMCO v6.19.1:
* The appointment-selection page (`https://impfzentren.bayern/citizen/appointment-selection/<UUID>`) will display 
  **by default** that there are no appointments available. This is not always true:
    * When accessing the page, a XHR-call is made to `https://impfzentren.bayern/api/v1/citizens/<UUID>/appointments/next`
    * This call is supposed to return almost instantly - but it does not always do so.
    * If no appointments could be found, the call returns `404` and the message is correct.
    * During high load times (e.g.: New appointments have been added), the call might timeout with an error `500`.
    * In this case, the message will still be displayed - even though there might be appointments available.
    * Actually, an error `500` is a good indication that there are indeed appointments available - the `404` is the one, 
      that returns instantly.
* When calling upon `https://impfzentren.bayern/api/v1/citizens/<UUID>/appointments/next`, the system will not only 
  display the appointment to your (or expose it to the system) - it will also reserve it for your user for 10 minutes.
    * The reservation expiration can be seen on the email you will be sent: `expiresAt`.
    * The message also contains the date and time for your first and second vaccination, the location of the vaccination 
      site (you might be eligible to access more than one site) and the type of vaccine that you will receive.
* While the call to `https://impfzentren.bayern/api/v1/citizens/<UUID>/appointments/next` produces a 10 minute 
  reservation for that specific appointment for you in the backend, it is not known at this point, if that exact 
  reservation will be proposed to you when accessing BayIMCO through the webinterface.
* If you access your appointment selection page (bookmark `https://impfzentren.bayern/citizen/appointment-selection/<UUID>` 
  for faster access), open your browser's devtools network tab and keep an eye on the calls to 
  `https://impfzentren.bayern/api/v1/citizens/<UUID>/appointments/next`. There is absolutely no need to franatically 
  refresh the page, as long as they have not timed out. This will generally take about 2 minutes.
* If you access the appointment selection page after having received the email from this script and having refreshed the 
  page ever so often after the XHR-requests have timed out: Don't despair! If you don't log in and out of the system, 
  there is a good chance that you actually got an appointment reserved for you and that once the system load has reduced 
  you will be able to see it on the selection page.
* If the script sees an available appointment (which probably results in a reservation of that appointment for your user 
  for 10 minutes), this script **will not confirm it for you! You will have to manually click the appointment 
  confirmation button in the BayIMCO-webinterface yourself!**
* If you just want to play around with this script, please consider using the UAT-system instead of the production one: 
  https://uat.impfzentren.bayern/
 
 
**Further research**

This script has been hacked together in about 30 minutes with no regard to style and functionality. There are probably 
a lot of areas for improvement. Feel free to submit a PR!


**List of vaccines**

| ID  | Type                          |
|-----|:-----------------------------:|
| 001 | COVID-19 Vaccine AstraZeneca® |
| 002 | Comirnaty (BioN-Tech/Pfizer)  |
| 003 | Moderna COVID19 Vaccine       |
| 004 | SP/GSK                        |
| 005 | J&J/Jansen                    |
| 006 | Novavax                       |
| 007 | Curevac                       |
