<?php

$arg1 = $_GET['arg1'];

$command = 'python -u "d:\xampp\htdocs\idir\src\google_search.py" "' . $arg1 . '"';

exec($command, $output, $return_var);

if ($return_var === 0) {
  echo "Python script executed successfully.";
  
  $output = shell_exec($command);

  if (!empty($output)) {
    echo "Python script is running. Output: <br>";
    echo nl2br($output); 
  } else {
    echo "Error executing Python script.";
  }
} else {
  echo "Error executing Python script.";
}
echo $arg1

?>