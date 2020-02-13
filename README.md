# NPC-info
Get info on NPC entity.

Diplays the following:
* EHP and repair amount and also tells how good different ammo are.
* DPS, range, falloff, missile explosion velocity and missile explosion radius.
* EWAR details
* Speed info

You give the script the type ID of the rat. 
The script gets the stats of the rat fom ESI.

Some of the attributes are different on old and new rats. This script is based on new rats so it may not show all info on old rats. Some rats also have nonsensical/missing stats (bugs?).

Requires:
* Python 3
* Requests: http://docs.python-requests.org/en/master/
* Numpy: http://www.numpy.org/
