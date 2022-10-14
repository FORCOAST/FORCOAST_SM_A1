# FORCOAST-SM-A1

### Description

This service forecasts the water level of a selected point of interest for up to 48 hours, starting from the selected date in the present or past. The resulting buleltin will display the water level in relation to working environments like wind, percipitation and daylight. A working limit can be set, for which the bulletin will provide some additional visual support, enabling faster information extraction (see example bulletin).

### How to run

* Containerize contents in docker
* Run the command Docker run forcoast/forcoast-sm-a1 &lt;pilot> &lt;date> &lt;lat> &lt;lon> &lt;limit> &lt;Telegram token> &lt;Telegram chat_id>
  * Where <pilot> is either "sado_estuary" or "Limfjord"
  * Where limit is preferably between 0 and 2
  * We use a Telegram bot for sendingh the bulletins through messaging services
* Example of use: Docker run forcoast/forcoast-sm-a1 sado_estuary 2022-06-24 38.7229344 -9.0917642 2 5267228188:AAGx60FtWgHkScBb3ISFL1dp6Oq_9z9z0rw -100129988055

### Licence

<a rel="license" href="http://creativecommons.org/licenses/by/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International License</a>.
