# Sample cronjob

A sample cronjob that can be used on the server connected to the information column, is the following: `*/5 * * * * cd /path/to/information-column/ && /path/to/information-column/gettext.pl >/dev/null && /path/to/information-column/sendtozuil.pl 
/path/to/information-column/zuiltext >/dev/null`
