# NPC-info
Get info on NPC entity.

Diplays the following:
* HP, EHP and repair amount. Shield repair is given in "active repair"+"peak passive regen"
* Relative effectiveness of different damage and ammo types.
* DPS, range, falloff, missile explosion velocity and missile explosion radius.
* EWAR details. EWAR effects with "(o)" use old mechanics while the ones without "(o)" use new mechanics. Not big practical difference.
* When the rat is shown to have "scram" it means actual scram that shuts down MWD and MJD. "point" is normal warp disruptor.
* Speed details.
* Various other attributes.
* The actual meaning of many of the attributes are not known.

You give the script the type ID of the rat. 
The script gets the stats of the rat fom ESI.

Requires:
* Python 3
* Requests: http://docs.python-requests.org/en/master/
* Numpy: http://www.numpy.org/
