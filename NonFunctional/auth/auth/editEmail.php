<?php
session_start();
  include_once('view/header.php');
  include_once('view/navbar.php');

if (!isset($_SESSION["tokenuser"]) || $_SESSION["tokenuser"] == null) {
    print "<script>alert(\"Acceso invalido!\");window.location='index.php';</script>";
}

?>

<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Cambiar correo</title>

  <!-- Importamos los estilos de Bootstrap -->
  <link rel="stylesheet" href="css/bootstrap.min.css">
  <!-- Font Awesome: para los iconos -->
  <link rel="stylesheet" href="css/font-awesome.min.css">
  <!-- Sweet Alert: alertas JavaScript presentables para el usuario (más bonitas que el alert) -->
  <link rel="stylesheet" href="css/sweetalert.css">

  <link rel="stylesheet" href="css/style.css">
</head>

<body>
  <!-- Formulario Login -->
  <div class="container">
    <div class="row">
      <div class="col-xs-12 col-md-4 col-md-offset-4">
        <!-- Margen superior (css personalizado )-->
        <div class="spacing-1"></div>
        <div>
          <legend class="center">Cambiar Correo de Usuario</legend>
          <input type="hidden" id="keyuser" value="<?php echo $_GET['keyuser']; ?>">
          <!-- Caja de texto para usuario -->
          <label class="sr-only" for="email">Correo Nuevo</label>
          <div class="input-group">
            <div class="input-group-addon"><i class="fa fa-user"></i>
            </div>
            <input type="text" class="form-control" id="email" placeholder="Ingresa nuevo correo">
          </div>
          <div id="resp"></div>
          <!-- Div espaciador -->
          <div class="spacing-2"></div>
          <button type="button" class="btn btn-primary btn-block" id="c_email">Cambiar</button>

        </div>
      </div>
    </div>
  </div>

  <!-- / Final Formulario login -->

  <!-- Jquery -->
  <script src="js/jquery.js"></script>
  <!-- Bootstrap js -->
  <script src="js/bootstrap.min.js"></script>
  <!-- SweetAlert js -->
  <script src="js/sweetalert.min.js"></script>
  <!-- Js personalizado -->
  <script src="js/operaciones.js"></script>

</body>
</html>
