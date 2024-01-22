<nav  class="navbar navbar-dark" style="background: linear-gradient(90deg, rgba(37,27,35,1) 0%, rgba(48,42,49,1) 43%, rgba(61,53,62,1) 64%, rgba(64,55,64,1) 65%, rgb(50 0 18) 100%);">
  <div class="navbar-brand"> 
    <img width="100px" height="30px" src="./resources/imgs/xelhua_logo-default.png" alt="Geoportal/Xel" />
  </div>
  <span class="navbar-text" id="span_solution_save_status"> </span>

  <div class="navbar-toggler">
      <div>
        <div class="dropdown">
          <a class=" dropdown-toggle" id="menu1" type="button" data-toggle="dropdown">
            <span class="startsesion">USER</span></a>
          <ul class="dropdown-menu front" role="menu" aria-labelledby="menu1">
            <li class="dropdown-item" role="presentation"><a role="menuitem" >Options</a></li>
            <li class="dropdown-item" role="presentation"><a role="menuitem" href="javascript:;" onclick="LogOutUser()"><?php echo $lngarr['signout']; ?></a></li>
          </ul>
        </div>
      </div>
  
  </div>
</nav >
