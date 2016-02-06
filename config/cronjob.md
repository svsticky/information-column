# Sample cronjob

A sample cronjob that can be used on the server connected to the zuil, is the following: `0,5,10,15,20,25,30,35,40,45,50,55 * * * * cd /path/to/zuil/ && /path/to/zuil/gettext.pl >/dev/null && /path/to/zuil/sendtozuil.pl 
/path/to/zuil/zuiltext >/dev/null`
