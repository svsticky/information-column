<?php

require_once "src/Google_Client.php";
require_once "src/contrib/Google_CalendarService.php";

$client = new Google_Client();
$client->setUseObjects(true);

$service = new Google_CalendarService($client);

$opts = array(
    'calendarId' => 'stickyutrecht.nl_thvhicj5ijouaacp1elsv1hceo@group.calendar.google.com',
    'maxResults' => 3,
    'timeMin' => date("c"),
    'singleEvents' => 'true',
    'orderBy' => 'startTime'
);
$results = $service->events->list($opts);

$date = new DateTime();
$date->setTimeZone(new DateTimeZone("Europe/Amsterdam"));

$timeString = str_pad($date->format("d-m-Y H:i"), 1, " ", STR_PAD_LEFT);


$activiteiten = str_pad(" Komende Activiteiten ", 32, "-", STR_PAD_BOTH);


?>
        Welkom bij Sticky,
    de studievereniging voor
 Informatica en Informatiekunde!

 Dagelijks van 9-17 uur geopend
        Kom binnen voor
     koffie en een koekje :)
Laatste update: <?= $timeString ?>

PAGE
<?=$activiteiten?>

<?php

function replaceAccents($str) {
        $search = explode(",",
"ç,æ,œ,á,é,í,ó,ú,à,è,ì,ò,ù,ä,ë,ï,ö,ü,ÿ,â,ê,î,ô,û,å,ø,Ø,Å,Á,À,Â,Ä,È,É,Ê,Ë,Í,Î,Ï,Ì,Ò,Ó,Ô,Ö,Ú,Ù,Û,Ü,Ÿ,Ç,Æ,Œ");
        $replace = explode(",",
"c,ae,oe,a,e,i,o,u,a,e,i,o,u,a,e,i,o,u,y,a,e,i,o,u,a,o,O,A,A,A,A,A,E,E,E,E,I,I,I,I,O,O,O,O,U,U,U,U,Y,C,AE,OE");
        return str_replace($search, $replace, $str);
}


foreach($results['items'] as $event)
{
    $name = replaceAccents($event['summary']);
    $date = $event['start'];
    $good_date = "";

    if (array_key_exists('date', $date))
    {
        $good_date = $date['date'] . " - All Day";
    }
    if (array_key_exists('dateTime', $date))
    {
        $datetime = DateTime::createFromFormat(DateTime::RFC3339, $date['dateTime']);
        $good_date = $datetime->format("d-m-Y H:i");
    }

    $better_format = str_pad($good_date, 32, " ", STR_PAD_LEFT);

    echo substr($name,0,32) . "\n" . substr($better_format,0,32) . "\n";
}

?>

END
