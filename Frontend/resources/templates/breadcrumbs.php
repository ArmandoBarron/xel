<ul id="breadcrumb">
  <?php
  $n = count($ancestors);
  ?>
  <li><a href="index.php?lang=<?php echo $_SESSION['lang'] ?>&busqueda=<?php echo $idbusqueda ?>"><span><?php echo $lngarr['backgeo'].$lngarr['geoportal'] ?></span></a></li>
  <?php
  for ($i=$n-1;$i>=0;$i--):?>
    <li><a href="element.php?elemento=<?php echo $ancestors[$i]['hash_name']?>&busqueda=<?php echo $idbusqueda ?>"><span><?php echo $ancestors[$i]['descriptor'] ?></span></a></li>
  <?php endfor;?>
</ul>
