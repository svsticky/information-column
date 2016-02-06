#!/usr/bin/perl -w

use strict;

use IO::Socket;
use vars qw($remote $soh $cr $syn $esc $fs $gs $spc $linecount);

$soh="\001";
$cr ="\015";
$syn="\026";
$esc="\033";
$fs ="\034";
$gs ="\035";

$remote = IO::Socket::INET -> new
 ( Proto => "tcp"
 , PeerAddr => "131.211.83.245"
 , PeerPort => "23"
 ) ;

unless($remote) { die "Cannot connect to infozuil $@"}

print "Connection successfully established";

$linecount=0;

sleep(3);

# set up transmission, select controller 0

print $remote "${soh} ${fs}";

while (<>)
  { my $tmp ;
    chomp ;
    chop while /[\r\n\s]$/ ;

	if (/^PAGE/){
		# blank rest of lines
		my $cnt;
		for ($cnt=$linecount;$cnt<8;$cnt++){
			print $remote $cnt." ".${fs};
		}
		print $remote "${esc}A  \067\047${fs}";
		# wait at end of page for 0*4096+0*256+11*16+11
		# = 187 * 26.7 millisec = 4.99 sec
		sleep(5);
		$linecount=0;
	} elsif (/^END/){
		# blank rest of lines
		my $cnt;
		for ($cnt=$linecount;$cnt<8;$cnt++){
			print $remote $cnt." ".${fs};
		}
		print $remote "${esc}A  \067\047${fs}";
		# wait at end of page for 0*4096+0*256+11*16+11
		# = 187 * 26.7 millisec = 4.99 sec
		#print $remote "${esc}A  \045\055${fs}";
		# wait at end of page for 0*4096+0*256+5*16+13
		# = 93 * 26.7 millisec = 2.48 sec
		sleep(3);
		last;
	} else {
		if ($linecount<8){
			# send lines as 0blabla{fs}
			#               1boeboe{fs}
			print $remote $linecount.$_.${fs};
			$linecount++;
		}
	}
}

print $remote "${syn}${cr}";
sleep(10);
print "done sending to zuil\n";

# print $remote "${syn}${soh} ${fs}";
# print $remote "0All your base${fs}";
# print $remote "1${fs}";
# print $remote "${esc}A  \053\053${fs}";
# print $remote "0${fs}";
# print $remote "1are belong to us${fs}";
# print $remote "${esc}A  \053\053${fs}";
# print $remote "${syn}${cr}";

