<?php ?>
<body>
  <title>Login</title>
  <!-- Formulario Login -->
  <div class="container">
    <div class="row">
      <div class="col-xs-12 col-md-4 col-md-offset-4">
        <!-- Margen superior (css personalizado )-->
        <div class="spacing-1">
        </div>
       
          <legend class="center">Login</legend>
          <div id="resp"></div>
          <!-- Caja de texto para usuario -->
          <label class="sr-only" for="email">Usuario</label>
          <div class="input-group">
            <div class="input-group-addon"><i class="fa fa-user"></i>
            </div>
            <input type="text" class="form-control" id="email" name="email" placeholder="Ingresa tu email">
          </div>
          <!-- Div espaciador -->
          <div class="spacing-2"></div>
          <!-- Caja de texto para la clave-->
          <label class="sr-only" for="password">Contraseña</label>
          <div class="input-group">
            <div class="input-group-addon"><i class="fa fa-lock"></i></div>
            <input type="password" autocomplete="off" class="form-control" id="password" name="password" placeholder="Ingresa tu contraseña">
          </div>
          <div class="col-xs-12 center text-accent">  </div>
        </div>
        <!-- Animacion de load (solo sera visible cuando el cliente espere una respuesta del servidor )-->
              <div class="row" id="load" hidden="hidden">
                
              </div>
        <!-- Fin load -->
        <div class="row">
          <div class="col-xs-8 col-xs-offset-2">
            <div class="spacing-2"></div>
            <center><button type="button" class="btn btn-default" name="button" id="login">Iniciar sesión</button></center>
          </div>
        </div>

        <section class="text-accent center">
          <div class="spacing-2">
          </div>  
          <p>
           ¿Aun no tienes una cuenta? <a href="view/registro.php"> Regístrate</a>
          </p>
        </section>
    
    </div>
  </div>

  <!-- / Final Formulario login -->
  <!-- Js personalizado -->
  <script src="../js/operaciones.js"></script>
  
</body>