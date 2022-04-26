<?php ?>

<div id ="content">
    <div class="collapse navbar-collapse navbar-ex1-collapse">
        <ul id="dashoptions" class="nav navbar-nav  side-nav">
            <?php 
            foreach ($lngarr["dashboard"]["general"] as $key => $value):?>
               <li class="dashitem" id="libusquedas">
                    <a onclick="show('<?php echo  $key ?>')"><span class="glyphicon glyphicon-<?php echo $value['icon'] ?>" aria-hidden="true"></span> <?php echo $value['title'] ?></a>
                </li>
            <?php endforeach;
            if($_SESSION['superuser']):
                foreach ($lngarr["dashboard"]["superuser"] as $key => $value):?>
               <li class="dashitem" id="libusquedas">
                    <a onclick="show('<?php echo  $key ?>')"><span class="glyphicon glyphicon-<?php echo $value['icon'] ?>" aria-hidden="true"></span> <?php echo $value['title'] ?></a>
                </li>
            <?php endforeach;
            endif;
            ?>
        </ul>
    </div>
    <div id="divcontenidodash" class="contenido">
        <h3>Mis búsquedas</h3>
        <div id="divBusquedas">
            <?php include_once( dirname(__FILE__) . "/../../includes/searches.php"); ?>
        </div>
    </div>
</div>
<!-- /#page-wrapper -->
