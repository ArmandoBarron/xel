
<?php
#e.g. AIzaSyD_qWZ5Z3tHY5JqXksf19meBOmfAR1Wmw4
$google_maps_key = $_ENV["GOOGLE_MAPS_KEY"]

?>
<!-- JAVASCRIPT FILES -->
<!-- JS 



<script defer src="resources/js/extern/jquery-3.2.1.min.js"></script>
<script defer src="resources/js/extern/popper.min.js"></script>-->

<!-- BOOSTRAP BUNDLE-->
<script src="https://code.jquery.com/jquery-3.5.1.js" integrity="sha256-QWo7LDvxbWT2tbbQ97B53yJnYU3WhH/C8ycbRAkjPDc=" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/js/bootstrap.bundle.min.js" integrity="sha384-fQybjgWLrvvRgtW6bFlB7jaZrFsaBXjsOMm/tB9LTS58ONXgqbR9W8oWht/amnpF" crossorigin="anonymous"></script>
<script defer src="resources/js/extern/jquery-ui.min.js"></script>

<!-- BOOSTRAP BUNDLE-->

<script src="https://superal.github.io/canvas2image/canvas2image.js"></script>
<script type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/1.5.3/jspdf.min.js"></script>
<script type="text/javascript" src="https://html2canvas.hertzen.com/dist/html2canvas.js"></script>


<!-- MAP  IN REPORT-->
<meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no" />
<script src="https://api.mapbox.com/mapbox-gl-js/v2.0.1/mapbox-gl.js"></script>
<link href="https://api.mapbox.com/mapbox-gl-js/v2.0.1/mapbox-gl.css" rel="stylesheet" />


<!-- SORTABLEJS-->
<script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
<script defer src="resources/js/extern/jquery-sortable.js"></script>

<script defer
    src="https://maps.googleapis.com/maps/api/js?key=<?php echo $google_maps_key;?>"></script>
<script defer type="text/javascript" src="resources/js/extern/numeric-1.2.6.min.js" ></script>
<script defer type="text/javascript" src="resources/js/extern/GroundOverlayEX.js" ></script>


<!-- LUPA -->
<script defer type="text/javascript" src="resources/js/extern/jquery.mlens-1.6.min.js"></script>

<!-- POPPER -->
<script defer type="text/javascript" src="resources/js/extern/moment.js" ></script>

<!-- RIGHT PANEL -->
  <script defer src="resources/js/extern/BootSideMenu.js" ></script>

<!-- Include Date Range Picker -->
<script defer type="text/javascript" src="resources/js/extern/bootstrap-datetimepicker.min.js" ></script>


<!-- NOTIFICATIONS -->
<script defer src="resources/js/extern/bootstrap-notify.min.js"></script>

<!-- CHARTS -->
<script defer src="resources/js/extern/Chart.min.js"></script>

<!-- SLIDER -->
<script defer src="resources/js/extern/jquery.anythingslider.min.js"></script>

<!-- FLOWY -->
<script defer src="resources/js/extern/flowy.min.js"></script>

<!-- PAPARSE -->
<script defer src="resources/js/extern/papaparse.min.js"></script>

<!-- hoverIntent -->
<script defer src="resources/js/extern/jquery.hoverIntent.min.js"></script>


<!--CUSTOM JS-->
<script defer type="text/javascript" src="resources/js/myjs/functions.js"></script>
<script defer type="text/javascript" src="resources/js/myjs/element.js"></script>
<script defer type="text/javascript" src="resources/js/myjs/copy_text.js"></script>
<script defer type="text/javascript" src="resources/js/extern/intro.js"></script>
<script defer type="text/javascript" src="resources/js/myjs/kmeans.js"></script> <!--kmeans -->
<script defer type="text/javascript" src="resources/js/myjs/Mensajes.js"></script>

<script defer type="text/javascript" src="resources/js/myjs/Services.js"></script> <!--Primer va este y despues las secciones -->
<!--INICIO DE LAS SECCIONES-->
<script defer type="text/javascript" src="resources/js/myjs/ServicesForms/0_config_sections.js"></script> 

<script defer type="text/javascript" src="resources/js/myjs/ServicesForms/mining.js"></script> 
<script defer type="text/javascript" src="resources/js/myjs/ServicesForms/preprocesing.js"></script> 
<script defer type="text/javascript" src="resources/js/myjs/ServicesForms/procesing.js"></script> 
<script defer type="text/javascript" src="resources/js/myjs/ServicesForms/tools.js"></script> 
<script defer type="text/javascript" src="resources/js/myjs/ServicesForms/validation.js"></script> 
<script defer type="text/javascript" src="resources/js/myjs/ServicesForms/visualization.js"></script> 
<script defer type="text/javascript" src="resources/js/myjs/ServicesForms/catalogs.js"></script> 
<script defer type="text/javascript" src="resources/js/myjs/ServicesForms/datasource.js"></script> 
<script defer type="text/javascript" src="resources/js/myjs/ServicesForms/custom.js"></script> 

<!--FIN DE LAS SECCIONES-->
<script defer type="text/javascript" src="resources/js/myjs/designer.js"></script>
<!-- <script defer type="text/javascript" src="resources/js/myjs/ReportePDF.js"></script>-->

<script src="resources/js/extern/xepOnline.jqPlugin.js"></script>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script> <!-- PLOTS-->
<script src="https://algorithmia.com/v1/clients/js/algorithmia-0.2.1.js" type="text/javascript"></script><!--Converter-->
<script src="https://cdnjs.cloudflare.com/ajax/libs/chroma-js/1.3.4/chroma.min.js"></script>

<!--Data tables--
<script src="https://cdn.datatables.net/1.11.4/js/jquery.dataTables.min.js" ></script>-->
<script src="resources/js/extern/DataTables/datatables.min.js" ></script>
<script src="resources/js/extern/DataTables/date-euro.js" ></script>


<!--TreeJss--
<script src="https://cdn.datatables.net/1.11.4/js/jquery.dataTables.min.js" ></script>-->
<script src="resources/js/extern/Treejs/jstree.min.js" ></script>

<!-- SELECT
<script defer src="resources/js/extern/bootstrap-select.min.js"></script>-->
  <!-- Latest compiled and minified CSS -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-select@1.13.14/dist/css/bootstrap-select.min.css">
  <!-- Latest compiled and minified JavaScript -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap-select@1.13.14/dist/js/bootstrap-select.min.js"></script>

<!-- Toggle on/off -->
<link href="https://cdn.jsdelivr.net/gh/gitbrent/bootstrap4-toggle@3.6.1/css/bootstrap4-toggle.min.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/gh/gitbrent/bootstrap4-toggle@3.6.1/js/bootstrap4-toggle.min.js"></script>

<!-- CodeMirror -->
<script src="resources/src/codemirror/lib/codemirror.js"></script>
<script src="resources/src/codemirror/addon/show-hint.js"></script>

<link rel="stylesheet" href="resources/src/codemirror/lib/codemirror.css">
<script src="resources/src/codemirror/mode/python/python.js"></script>
<link rel="stylesheet" href="resources/src/codemirror/theme/mdn-like.css">
<link rel="stylesheet" href="resources/src/codemirror/codemirror_styles.css">
<link rel="stylesheet" href="resources/src/codemirror/addon/show-hint.css">

