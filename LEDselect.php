<html>
 <head>
 <meta name="viewport" content="width=device-width" />
 <title>Watering System Control</title>
 </head>
      <body>
         <h4> Timer Over-ride:
         <form method="get" action="<?php echo htmlspecialchars($_SERVER['PHP_SELF']);?>">
                 <input type="submit" style="color:green" value="Turn Fern Drippers ON" name="Fern"> <br>
                 <input type="submit" style="color:green" value="Turn Front Drippers ON" name="Front"> <br>
                 <input type="submit" style="color:green" value="Turn Rear Drippers ON" name="Rear"> <br>
                 <input type="submit" style="color:green" value="Turn Side Drippers ON" name="Side"> <br>
                 <input type="submit" style="color:red" value="Turn All Drippers OFF" name="off"> <br>
                 <input type="submit" style="color:blue" value="Return Drippers to Timer Control" name="off"> <br>
         </form>
         <?php
         $pin_alloc = array("Fern"=>"16", "Front"=>"18", "Rear"=>"22", "Side"=>"24", "NewCct"=>"11");
         if(isset($_GET['Fern'])){
                 $CMD = shell_exec("sudo ./led_select.py 16 on");
                 echo "Relay on circuit " . $pin_alloc['Fern'] . " activated";
                 }                        
           else if(isset($_GET['Front'])){
                 $CMD = shell_exec("sudo ./led_select.py 18 on");
                 echo "Relay on circuit " . $pin_alloc['Front'] . " activated";
                 }         
             else if(isset($_GET['Rear'])){
                 $CMD = shell_exec("sudo ./led_select.py 22 on");
                 echo "Relay on circuit " . $pin_alloc['Rear'] . " activated";
                 }           
                  else if(isset($_GET['Side'])){
                      $CMD = shell_exec("sudo ./led_select.py 24 on");
                      echo "Relay on circuit " . $pin_alloc['Side'] . " activated";
                      }                 
                       else if(isset($_GET['off'])){
                            $CMD = shell_exec("sudo ./led_select.py 16 off");
                            echo "All circuits are off";
                           echo "<pre>$CMD</pre>";
                           }
            echo $_SERVER['PHP_SELF'];
            echo "<br>";
            echo $_SERVER['SERVER_NAME'];
            echo "<br>";
            echo $_SERVER['HTTP_HOST'];
            echo "<br>";
            echo $_SERVER['HTTP_REFERER'];
            echo "<br>"; echo "<br>";
            echo $_SERVER['HTTP_USER_AGENT'];
            echo "<br>"; echo "<br>";
            echo $_SERVER['SCRIPT_NAME']; 
            echo "<br>"; echo "<br>";
            echo $CMD;
            echo "<br>";            
         ?>
      </body>
 </html>