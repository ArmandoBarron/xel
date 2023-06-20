<?php

//INCLUYE LOS ARCHIVOS NECESARIOS
include_once("resources/conf.php");
include_once(SESIONES);
include_once(CLASES . "/class.PageManagment.php");

?>

<!DOCTYPE html>
<html>
<body style="height: 99vh;overflow: auto">

<div class="col-12 tab-pane options" style="height:100%" id="dataViewContainer"> 
  <div id="DataViewPanel"></div>

</div>


</body>


<script src="https://code.jquery.com/jquery-3.5.1.js" integrity="sha256-QWo7LDvxbWT2tbbQ97B53yJnYU3WhH/C8ycbRAkjPDc=" crossorigin="anonymous"></script>
<script src="resources/js/extern/jquery-ui.min.js"></script>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script> <!-- PLOTS-->
<script defer src="resources/js/extern/papaparse.min.js"></script>
<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>

<!-- PivotTable -->
<link rel="stylesheet" href="resources/src/PivotTable/pivot.min.css">

<script src="resources/src/PivotTable/pivot.min.js"></script>
<script src="resources/src/PivotTable/gchart_renderers.min.js"></script>
<script src="resources/src/PivotTable/plotly_renderers.min.js"></script>
<script src="resources/src/PivotTable/export_renderers.min.js"></script>

<style>


</style>
<script type="text/javascript">
      function DataView(url_data){

          $(function(){
              google.load("visualization", "1", {packages:["corechart", "charteditor"]});

              Papa.parse(url_data, {
                  download: true,
                  skipEmptyLines: true,
                  complete: function(parsed){
                      console.log(parsed)
                      console.log(parsed.data['0'][0])


                      $("#DataViewPanel").pivotUI(
                          parsed.data, {
                              rows: [parsed.data['0'][0]],
                              cols: [parsed.data['0'][1]],
                            aggregatorName: "Sum over Sum",
                            rendererName: "Bar Chart",
                            renderers: $.extend(
                              $.pivotUtilities.renderers, 
                              $.pivotUtilities.plotly_renderers

                            )
                          });
                        
                  }
              });
          });

          }

   
  var url = "<?php echo $_GET['url']; ?>";
  console.log(url)
  DataView(url)
    
</script>
</html>
