<div class="navbar navbar-dark" style="background-color:#bb415c;">
  <div class="logo">
    <a href="index.php?lang?=<?php echo $_SESSION['lang'] ?>"><img width="100px" height="30px" src="./resources/imgs/xelhua_logo-default.png" alt="Geoportal/Xel" /></a>
  </div>
<!--
  <div class="downloads">
    <div onclick="checkSession('downloadImages')">
      <a href="javascript:;">
      <h3>
        <div>
          <span class="simpleCart_total"></span>
        </div>
        <span class="glyphicon glyphicon-download-alt"  aria-hidden="true"><label id="lblNumberProducts" class="badge badge-warning"><?php if(isset($_SESSION['descargas'])) echo count($_SESSION['descargas']); ?></label></span>
      </a>
    </div>
  </div>
  <div class="downloads">
    <div>
      <a href="javascript:;">
      <h3> <div>
        <span class="simpleCart_total"></span> </div>
        <span class="glyphicon glyphicon-bell" id="notificaciones" aria-hidden="true"><label id="lblNumberNews" class="badge badge-warning">0</label></span>
      </a>
    </div>
  </div>
  <div class="downloads space">
        |
  </div>
-->
  <div class="downloads">
    <?php if(empty($_SESSION['user'])): ?>
      <div onclick="LogOutUser()">
        <a href="javascript:;">
          <h3></h3>
          <span class="glyphicon glyphicon-user" aria-hidden="true"></span><span class="startsesion"> log out</span>
        </a>
      </div>
    <?php else: ?>
      <div>
        <div class="dropdown">
          <h3></h3>
          <a class=" dropdown-toggle" id="menu1" href="javascript:void(0);" type="button" data-toggle="dropdown"><span class="glyphicon glyphicon-user" aria-hidden="true"></span><span class="startsesion"><?php echo $_SESSION['user']; ?></span></a>
          <ul class="dropdown-menu front" role="menu" aria-labelledby="menu1">
            <li class="front" role="presentation"><a role="menuitem" tabindex="-1" href="user.php"><?php echo $lngarr['mysearches']; ?></a></li>
            <li class="front" role="presentation"><a role="menuitem" tabindex="-1" href="javascript:;" onclick="logout()"><?php echo $lngarr['signout']; ?></a></li>
          </ul>
        </div>
      </div>
    <?php endif ?>
  </div>
</div>
