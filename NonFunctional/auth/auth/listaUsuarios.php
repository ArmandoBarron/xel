<?php
    //include_once "view/head.php";
    session_start();
    if(!isset($_SESSION["tokenuser"]) || $_SESSION["tokenuser"]==null){
        print "<script>alert(\"Acceso invalido!\");window.location='index.php';</script>";
    }
?>
<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="UTF-8">
    <title>Usuarios</title>
    <!--CSS-->    
    <link rel="stylesheet" href="css/bootstrap.css">
    <link rel="stylesheet" href="css/dataTables.bootstrap.min.css">
    <link rel="stylesheet" href="css/font-awesome.css">
</head>

<?php 
//include_once('view/head.php');
include_once('views/navbar.php');
?>

<body>
    <div class="col-md-8 col-md-offset-2 col-sm-10 col-sm-offset-1"><br><br><br><br>
        <h1>Usuarios</h1>
    </div>
    <div class="col-md-8 col-md-offset-2 col-sm-10 col-sm-offset-1">    
        <table id="listatable" class="table table-striped table-bordered" cellspacing="0" width="100%">
            <thead>
            <tr>
                <!--th>Id</th-->
                <th>Usuario</th>
                <!--th>Contraseña</th-->
                <th>Correo</th>
                 <th>Estado</th>
                <th>Acciones</th>
            </tr>
            </thead>
            <tbody>
            </tbody>
        </table>        
    </div>
</body>
 
    <!--Javascript-->    
    <script src="js/jquery-3.2.1.min.js"></script>
    <script src="js/bootstrap.js"></script>
    <script src="js/jquery.dataTables.min.js"></script>
    <script src="js/dataTables.bootstrap.min.js"></script>          
    <script src="js/lenguajelistausuarios.js"></script>
    <!-- Js personalizado -->
    <script src="js/operaciones.js"></script>  

    <script>
        $(document).ready(function(){
            $('[data-toggle="tooltip"]').tooltip();
        });
    </script>   

</html>
