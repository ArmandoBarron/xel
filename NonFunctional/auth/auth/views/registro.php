<?php
//Incluimos la cabecera y la barra superior de menú
include_once('header.php');
include_once('navbar.php');

?>

<title>Registro</title>
  
    <!-- Formulario Login -->
    <div class="container">
      <div class="row">
        <div class="col-xs-12 col-md-4 col-md-offset-4">
          <!-- Margen superior (css personalizado )-->
          <div class="spacing-1"></div>

          <form class="formulario-registro" id="formulario_registro">
            <!-- Estructura del formulario -->
            <fieldset>

              <legend class="center">Registro</legend>

              <!-- Caja de texto para usuario -->
              <label class="sr-only" for="user">Nombre</label>
              <div class="input-group">
                <div class="input-group-addon"><i class="fa fa-user"></i></div>
                <input type="text" class="form-control" name="username" id="username" placeholder="Ingresa tu nombre">
              </div>

              <!-- Div espaciador -->
              <div class="spacing-2"></div>

              <!-- Caja de texto para usuario -->
              <label class="sr-only" for="user">Email</label>
              <div class="input-group">
                <div class="input-group-addon"><i class="fa fa-envelope"></i></div>
                <input type="text" class="form-control" name="email" id="email"placeholder="Ingresa tu email">
              </div>

              <!-- Div espaciador -->
              <div class="spacing-2"></div>

              <!-- Caja de texto para la clave-->
              <label class="sr-only" for="clave">Contraseña</label>
              <div class="input-group">
                <div class="input-group-addon"><i class="fa fa-lock"></i></div>
                <input type="password" autocomplete="off" class="form-control" name="password" id="password" placeholder="Ingresa tu contraseña">
              </div>

              <!-- Div espaciador -->
              <div class="spacing-2"></div>

              <!-- Caja de texto para la clave-->
              <label class="sr-only" for="clave">Verificar contraseña</label>
              <div class="input-group">
                <div class="input-group-addon"><i class="fa fa-lock"></i></div>
                <input type="password" autocomplete="off" class="form-control" name="password2" id="password2" placeholder="Verifica tu contraseña">
              </div>

              <!-- Animacion de load (solo sera visible cuando el cliente espere una respuesta del servidor )-->
              <div class="row" id="load" hidden="hidden">
                
              </div>
              <!-- Fin load -->

              <!-- boton para activar la funcion click y enviar el los datos mediante ajax -->
              <div class="row">
                <div class="col-xs-8 col-xs-offset-2">
                  <div class="spacing-2"></div>
                <center>  <button type="button" class="btn btn-default" name="button" id="registro">Regístrate</button></center>
                </div>
              </div>

            </fieldset>
          </form>
        </div>
      </div>
    </div>

    <!-- / Final Formulario login -->
    <!-- Js personalizado -->
    <script src="../js/operaciones.js"></script>
    
  </body>
</html>
