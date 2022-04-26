/*
*  FUNCTIONES JS PARA EL MANEJO DEL CLIENTE Y LA COMUNICACIÓN CON EL SERVIDOR
*/

//VARIABLES GLOBALES
var startTimeMS = 0;  // EPOCH Time of event count started
var timerId;          // Current timer handler
var timerStep=5000;   // Time beetwen calls
var polys_agregados = []; //POLIGONOS DE LAS IMAGENES MOSTRADOS EN EL MAPA
var imgsMaps_agregados = []; //IMAGENES MOSTRADAS EN EL MAPA
var markers = []; //MARCADORES AGREGDOS EN EL MAPA
var coors = []; //COORDENADAS AGREGADAS EN EL MAPA
var show_in_degrees = false; //MOSTRAR EN DECIMAL O GRADOS
var place = ""; //LUGAR BUSCADO (LOCALIZACION DE LUGAR)
var place_coors = []; //COORDENADAS DE UN LUGAR SELECCIONADO POR LA LOCALIZACION DE PUNTOS
var lang;
var filtro = "todas"; //GUARGA LO QUE SE VA  A MOSTRAR (todas,poligonos,solapamientos)
const FILTROS = {todas:1,poligonos:2,solapamientos:3};
var MONTHS = ["Enero","Febrero","Marzo","Abril",
                "Mayo","Junio","Julio","Agosto",
                "Septiembre","Octubre","Noviembre","Diciembre"]
//temporizador
var centesimas = 0;
var segundos = 0;
var minutos = 0;
var horas = 0;
var htmlAnt;

$(document).ready(function(){
  document.marcadoresClima = [];
  document.height = $(window).height(); //ALTURA MAXIMA DE LA VENTANA
  document.place = "";
  checkSession();
  var gets = get_variables();
  window.busqueda = 0;

  /**
  * OBTIENE EL LENGUAJE DE LA URL O EL NAVEGADOR
  */
  lang = "es";
  if(gets.hasOwnProperty("lang")){
    lang = gets['lang'];
    if(!(lang == "es" || lang == "en")){
      lang = (navigator.language || navigator.userLanguage).substring(0,2); 
    }
  }else{
    lang = (navigator.language || navigator.userLanguage).substring(0,2); 
  }
  //console.log(lang);
  loadTexts(lang);

  //OBTIENE EL ID DE LA BUSQUEDA SI ES PASADO POR GET
  if (gets.hasOwnProperty('busqueda')) {
    if(Object.keys(gets).length == 1){
      if(gets['busqueda'].length > 1){
        window.busqueda = gets['busqueda'];
      }
    }
  }
  /// DROPDOWN
  $('.dropdown-submenu a.test').on("click", function(e){
    $(this).next('ul').toggle();
    e.stopPropagation();
    e.preventDefault();
  });


  /// EMPIEZA LA INICIALIZACIÓN DEL CONTROL PARA LA FECHA
  $('#datetimepicker1').datetimepicker({
    viewMode: 'years',
    format: 'DD/MM/YYYY',
    locale: lang,
    maxDate: 'now'
  });
  $('#datetimepicker2').datetimepicker({
    viewMode: 'years',
    format: 'DD/MM/YYYY',
    locale: lang,
    maxDate: 'now'
  });
  $("#datetimepicker1").on("dp.change",function(e){ validarFecha(1,e)  });
  $("#datetimepicker2").on("dp.change",function(e){ validarFecha(2,e)  });

  /// FIN DE LA INICIALIZACION DEL CONTROL DE FECHA
  if(window.location.href.indexOf("element.php") == -1 &&  window.location.href.indexOf("user.php") == -1){
    getLocation("initMap"); //geolacalización del usuario
  }
  

  //PANEL DE SUGERENCIAS Y RECOMENDACIONES
  $('#test').BootSideMenu({
      side: "right",
      pushBody: false,
      remember: false,
      width: '380px'
  });

  //// SELECTOR DE FORMA DE BÚSQUEDA, SE INICIALIZA COMO VALOR SIN ACCION
  $("#slShape").val("opcion");
  $("#slShape").change(function(){
    switch (this.value) {
      case "nombre":
        deleteAllCoord();
        $('#modSearchPlace').modal('show');
        $("#btnAddNew").addClass("hidden");
        break;
      case "pathrow":
        deleteAllCoord();
        $("#modPathRow").modal("show");
        $("#btnAddNew").addClass("hidden");
        break;
      case "grados":
        if(document.ant != "poligono" && document.ant != "decimales" && document.ant != "grados"){
          deleteAllCoord();
        }
        $("#modNewGrad").modal("show");
        break;
      case "decimales":
        if(document.ant != "poligono" && document.ant != "decimales" && document.ant != "grados"){
          deleteAllCoord();
        }
        $("#modNewDec").modal("show");
        break;
      case "poligono":
        if(document.ant != "poligono" && document.ant != "decimales" && document.ant != "grados"){
          deleteAllCoord();
        }
        $("#btnAddNew").removeClass("hidden");
        break;
      default:
        deleteAllCoord();
        $("#btnAddNew").addClass("hidden");
    }
    document.ant = this.value;
    $("#slShape").val("opcion");
  });
  //// FIN DE SELECTOR

  $("#slShape2").val("opcion");
  $("#slShape2").change(function(){
    console.log("entro");
    switch (this.value) {
      case "nombre":
        deleteAllCoord();
        $('#modSearchPlace').modal('show');
        $("#btnAddNew").addClass("hidden");
        break;
      case "pathrow":
        deleteAllCoord();
        $("#modPathRow").modal("show");
        $("#btnAddNew").addClass("hidden");
        break;
      case "grados":
        if(document.ant != "poligono" && document.ant != "decimales" && document.ant != "grados"){
          deleteAllCoord();
        }
        $("#modNewGrad").modal("show");
        break;
      case "decimales":
        if(document.ant != "poligono" && document.ant != "decimales" && document.ant != "grados"){
          deleteAllCoord();
        }
        $("#modNewDec").modal("show");
        break;
      case "poligono":
        if(document.ant != "poligono" && document.ant != "decimales" && document.ant != "grados"){
          deleteAllCoord();
        }
        $("#btnAddNew").removeClass("hidden");
        break;
      default:
        deleteAllCoord();
        $("#btnAddNew").addClass("hidden");
    }
    document.ant = this.value;
    $("#slShape2").val("opcion");
  });

  // HACE EL CAMBIO DE DECIMALES A GRADOS Y VICEVERSA
  $("#btnConvert :input").change(function() {
    if(this.value == "decimales"){
      mostrarEnDecimales();
      $('#btnAddNew').attr('data-target','#modNewDec');
    }else{
      mostrarEnGrados();
      $('#btnAddNew').attr('data-target','#modNewGrad');
    }
  });

  //CAMBIA A LA PESTANA DE SATELITES CON UN BOTON
  $('#toSatelitsTab').click(function(e){
     e.preventDefault();
     $('#mytabs a[href="#2b"]').tab('show');
  });

  //CAMBIA A LA PESTAÑA DE RESULTADOS
  $('#toResults').click(function(e){
     e.preventDefault();
     toResults();
  });

  //CAMBIA A LA PESTAÑA DE OPCIONES
  $('#backToOptions').click(function(e){
     e.preventDefault();
     $('#mytabs a[href="#1b"]').tab('show');
  });

  //CLIC EN LA TERCERA PESTAÑA
  $(".disable").click(function (e) {
      e.preventDefault();
      var aux = toResults();
      return aux;
   });

  //LOCALIZAR LUGAR
  $("#btnBuscarLugar").click(function(e){
     e.preventDefault();
     mostrarLugares();
  });

  //LIMPIA EL CAMPO DE BUSQUEDA
  $("#btnLimpiarCampo").click(function(e){
    e.preventDefault();
    $("#txtSearchText").val("");
  });

  //AGREGAR NUEVA COORDENADA EN DECIMALES
  $('#btnAddNewDecimal').click(function(e){
    $("#error").html("");
    var error = true;
    if( !$("#txtNewLat").val() ) {
      $("#error").html("No se ha específicado el valor para el campo latitud.")
      return;
    }else if(isNaN($("#txtNewLat").val())){
      $("#error").html("Dato invalido en el campo latitud.")
      return;
    }else if($("#txtNewLat").val() < - 90 || $("#txtNewLat").val() > 90){
      $("#error").html("Dato invalido en el campo latitud. Debe de ser un valor entre -90 y 90.")
      return;
    }
    if( !$("#txtNewLon").val() ) {
      $("#error").html("No se ha específicado el valor para el campo longitud.")
      return;
    }else if(isNaN($("#txtNewLon").val())){
      $("#error").html("Dato invalido en el campo longitud.")
      return;
    }else if($("#txtNewLon").val() < - 180 || $("#txtNewLon").val() > 180){
      $("#error").html("Dato invalido en el campo longitud. Debe de ser un valor entre -180 y 180.")
      return;
    }

    var latlng = new google.maps.LatLng($("#txtNewLat").val(),$("#txtNewLon").val());
    addCoorToPoli(latlng);
    document.map.setCenter(latlng);

    $("#txtNewLat").val("");
    $("#txtNewLon").val("");
    $('#modNewDec').modal('hide');
  });

  //AGREGA UNA NUEVA COORDENADA EN GRADOS
  $('#btnAddNewGrad').click(function(e){
     $("#error2").html("");

     if( !$("#txtNewGradsLat").val() || !$("#txtNewMinsLat").val() || !$("#txtNewSegsLat").val() ) {
       $("#error2").html("No se ha específicado el valor para el campo latitud.")
       return;
     }else if(isNaN($("#txtNewGradsLat").val()) || isNaN($("#txtNewMinsLat").val()) || isNaN($("#txtNewSegsLat").val())){
       $("#error2").html("Dato invalido en el campo latitud.")
       return;
     }
     if( !$("#txtNewGradsLon").val() || !$("#txtNewMinsLon").val() || !$("#txtNewSegsLon").val() ) {
       $("#error2").html("No se ha específicado el valor para el campo longitud.")
       return;
     }else if(isNaN($("#txtNewGradsLon").val()) || isNaN($("#txtNewMinsLon").val()) || isNaN($("#txtNewSegsLon").val())){
       $("#error2").html("Dato invalido en el campo longitud.")
       return;
     }

     var lat = toDecimal($("#txtNewGradsLat").val(),$("#txtNewMinsLat").val(),$("#txtNewSegsLat").val(),$("#latOrien").val());
     var lon = toDecimal($("#txtNewGradsLon").val(),$("#txtNewMinsLon").val(),$("#txtNewSegsLon").val(),$("#lonOrien").val());

     if(lat > 90 || lat < -90){
         $("#error2").html("Dato invalido en el campo latitud. Debe de ser un valor entre -90 y 90.")
         return;
     }

     if(lon > 180 || lon < -180){
       $("#error2").html("ato invalido en el campo longitud. Debe de ser un valor entre -180 y 180.")
       return;
     }
     var latlng = new google.maps.LatLng(lat,lon);
     addCoorToPoli(latlng);
     document.map.setCenter(latlng);
     $("#txtNewGradsLat").val("");
     $("#txtNewMinsLat").val("");
     $("#txtNewSegsLat").val("");
     $("#txtNewGradsLon").val("");
     $("#txtNewMinsLon").val("");
     $("#txtNewSegsLon").val("");
     $('#modNewGrad').modal('hide');
  });

  //LIMPIA LOS CAMPOS DEL FORMULARIO PARA AGREGAR UN POLIGONO POR PATH/Row
  $("#btnCleanPathRow").click(function(){
     event.preventDefault();
     $("#txtPath").val("");
     $("#txtRow").val("");
  });

  //AGREGA UN POLIGONO DEL PATH/ROW BUSCADO
  $("#btnAddPolygon").click(function(event){
     event.preventDefault();
     if(!$("#txtPath").val() || !$("#txtRow").val() ){
       notificarUsuario("Debe de llenar todos los campos.","danger");
     }else{
       var path = $("#txtPath").val();
       var row = $("#txtRow").val();
       showPathRowsCoors(path,row);
     }
  });

  /* CHANGE LOG IN TO SIGN UP */
  $("#logindiv").on('change','#btnchangelogin :input',function(){
    console.log(this.value);
    if(this.value == "signup"){
      $("#frmlogin").addClass("invisible animation");
      $("#frmsignup").removeClass("invisible");
    }else{
      $("#frmlogin").removeClass("invisible animation");
      $("#frmsignup").addClass("invisible");
    }
  });

  /*change(function() {
    if(this.value == "signup"){
      $("#frmlogin").addClass("invisible animation");
      $("#frmsignup").removeClass("invisible");
    }else{
      $("#frmlogin").removeClass("invisible animation");
      $("#frmsignup").addClass("invisible");
    }

  });*/

  $("#btnModalReloadPage").click(function(event){
    event.preventDefault();
    logout();
  });

  $("#btnLogGhest").click(function(event){
    event.preventDefault();
    var formData = new FormData($("#frmlogin")[0]);
    formData.append("username","invitado");
    formData.append("password","invitado");
    formData.append("action","login");

    if(document.position != null){
      formData.append("lat",document.position.coords.latitude);
      formData.append("lon",document.position.coords.longitude);
      formData.append("locationByIp",0);
    }

    $.ajax({ //OBTIENE LA IP Y DATOS DE LOCALIZACION COMPLEMENTARIOS
      url: "http://ipinfo.io",
      dataType: "jsonp",
      success: function(response){
        formData.append("ip",response.ip);
        if(document.position == null){
          latlng = response.loc.split(",");
          formData.append("lat",latlng[0]);
          formData.append("lon",latlng[1]);
          formData.append("locationByIp",1);
        }
        login(formData);
      },
      error: function(response){
        formData.append("ip","-");
        login(formData);
      }
    });
  });

  //LOG IN
  $("#logindiv").on('submit','#frmlogin',function(event){
    event.preventDefault();
    console.log("entro");
    var formData = new FormData($("#frmlogin")[0]);
    formData.append("action","login");

    if(document.position != null){
      formData.append("lat",document.position.coords.latitude);
      formData.append("lon",document.position.coords.longitude);
      formData.append("locationByIp",0);
    }

    $.ajax({ //OBTIENE LA IP Y DATOS DE LOCALIZACION COMPLEMENTARIOS
      url: "http://ipinfo.io",
      dataType: "jsonp",
      success: function(response){
        formData.append("ip",response.ip);
        if(document.position == null){
          latlng = response.loc.split(",");
          formData.append("lat",latlng[0]);
          formData.append("lon",latlng[1]);
          formData.append("locationByIp",1);
        }
        login(formData);
      },
      error: function(response){
        formData.append("ip","-");
        login(formData);
      }
    });
    
  });

  //SIGN UP
  $("#logindiv").on('submit','#frmsignup',function(event){
    event.preventDefault();
    var formData = new FormData($("#frmsignup")[0]);
    formData.append("action","signup")
    //formData
    $.ajax({
        url: 'includes/controladores/controller.Session.php',  //Server script to process data
        type: 'POST',
        data: formData,
        dataType: 'json',
        contentType: false,
        processData: false,
        beforeSend: function(){
        },
        success  : function(data){ //muestra la respuesta
          if(data['codigo'] == 0){
            $("#mensaje_signup").html('<div class="alert alert-success">'+ data['mensaje']+'</div>');
          }else{
            $("#mensaje_signup").html('<div class="alert alert-danger">'+ data['mensaje']+'</div>');
          }
        },
        error: function(data){ //se lanza cuando ocurre un error
          console.log(data.responseText);
        }
     });
  });

  //MUESTRA EL MODAL DE LOGEO
  $("#divLogin").click(function(){
    $('#loginmodal').modal('show');
  });

  //MANDA A LLAMAR A CERRAR LA SESIONES
  $("#btnLogout").click(function(){
    deleteAllCookies();
    window.location = "includes/controladores/controller.Session.php";
  });

  //AGREGA UNA IMAGEN PARA DESCARGARLA
  $("#btnAddImageToDownload").click(function(e){
    id = $("#spanImagen").html();
    var opciones = []
    $('.choose:checked').each(
      function() {
          opciones.push($(this).val());
      }
    );
    item = {id:id,opciones:opciones,isfolder:false,type:"single"};
    $("#btn"+id).html("<button title='Eliminar de las descargas'   type='button'  onclick='checkSession(\"addToCar\",\""+id+"\",\"remove\")' class='btn btn-danger btn-xs'>Eliminar</button>");
    $("#modChoose").modal('hide');
    updateCarSession(item,"add");
  });

  document.place = "";
  
  //PARA QUE NO SE CIERRE EL MODAL HASTA QUE NO SE INICIE SESION
  $('#loginmodal').on('hidden.bs.modal', function () {
    checkSession();
  });

  $("#logindiv").on('click','#btnResetPass',function(e){
    e.preventDefault();
    htmlAnt = $("#logindiv").html();
    
    $("#logindiv").html("<h4>"+document.lngarr['passrecup']+"</h4><div>"
                        +"<p>"+document.lngarr['typeemail']+"</p>"+
                        "<form id='frmReset'><fieldset><input id='txtEmailRec' type='email' name='email' placeholder='"+
                        document.lngarr['email']+"' required/></fieldset><div id='divErrGetEm'></div><input type='submit' value='"+document.lngarr['search']+"'/><a id='btnCancelRec' onclick='backLogin()'>"+document.lngarr['cancel']+"</a></form><br></div>");
  });

  /*
  * VERIFICA SI EL EMAIL EXISTE PARA LA RECUPERACIÓN DE CONTRASEÑA
  */
  $("#logindiv").on("submit","#frmReset",function(e){
    e.preventDefault();
    var email = $("#txtEmailRec").val();
    //console.log(username);
    $.ajax({
      url: 'includes/controladores/controller.Session.php',  //Server script to process data
      type: 'POST',
      data: {email:email,action:"checkmail"},
      dataType: 'json',
      beforeSend: function(){
      },
      success  : function(data){ //muestra la respuesta
        console.log(data);
        if(data['codigo'] == 1){
          $("#divErrGetEm").html('<div class="alert alert-success">'+document.lngarr['emailexists']+'</div>');
          sendEmailPass(email,data['hash'],data['id']);
        }else{
          $("#divErrGetEm").html('<div class="alert alert-danger">'+document.lngarr['emailnotexists']+'</div>');
        }
      },
      error: function(data){ //se lanza cuando ocurre un error
        console.log(data.responseText);
      }
    });
  });

  $("#frmpasswordchange").submit(function(e){
    e.preventDefault();
    var pass1 = $("#txtpass").val();
    var pass2 = $("#txtconfpass").val();
    var user = $("#txtUser").val();
    if(pass1 != pass2){
      $("#diverror").html('<div class="alert alert-danger">'+document.lngarr["nopassmatch"]+'</div>');
    }else{
      $.ajax({
        url: 'includes/controladores/controller.Session.php',  //Server script to process data
        type: 'POST',
        data: {password:pass1,action:"changepass",user:user},
        dataType: 'json',
        beforeSend: function(){
        },
        success  : function(data){ //muestra la respuesta
          if(data['keyuser'] != null){
            $("#diverror").html('<div class="alert alert-success">'+document.lngarr["passchanged"]+'</div>');
          }
        },
        error: function(data){ //se lanza cuando ocurre un error
          console.log(data.responseText);
        }
      });
    }
  });

  //console.log(document.lngarr["option"]);
  $('#slDiv2').hide();
  $("#options2").hide();
  $("#results2").hide();
  //SELECCION DEL BOTON DE CLIMA
  $('#chclima').change(function() {
    if($(this).is(":checked")) {
      $('#slDiv').hide();
      $('#slDiv2').show();
      $("#divDates").hide();
      $("#options1").hide();
      $("#options2").show();
      $("#results").hide();
      $("#results2").show();
      //$('#modClust').modal('show');
    }else{
      $('#slDiv2').hide();
      $('#slDiv').show();
      $("#divDates").show();
      $("#options1").show();
      $("#options2").hide();
      $("#results").show();
      $("#results2").hide();
      //$('#modClust').modal('hide');
    }
  });
});

/*
* ENVIA EL EMAIL DE RECUPERACIÓN DE CONTRASEÑA
*/
function sendEmailPass(email,hash,id){
  $.ajax({
    url: 'includes/controladores/controller.Session.php',  //Server script to process data
    type: 'POST',
    data: {email:email,action:"sendmailpass",hash:hash,id:id},
    dataType: 'json',
    beforeSend: function(){
    },
    success  : function(data){ //muestra la respuesta
      console.log(data);
    },
    error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

function backLogin(){
  $("#logindiv").html(htmlAnt);
}

/**
* VALIDA LAS FECHAS
*/
function validarFecha(picker,e){
  if(picker == 1){
    $("#datetimepicker2").data('DateTimePicker').minDate(e.date);
  }else if(picker == 2){
    $("#datetimepicker1").data('DateTimePicker').maxDate(e.date);
  }

}

/**
* MUESTRA EL MODAL DEL INICIO DE SESION
*/
function showLoginModal(){
  $('#loginmodal').modal('show');
}

/**
* INICIA LA SESION
*/
function login(data){
  $.ajax({
    url: 'includes/controladores/controller.Session.php',  //Server script to process data
    type: 'POST',
    data: data,
    dataType: 'json',
    contentType: false,
    processData: false,
    beforeSend: function(){
    },
    success  : function(data){ //muestra la respuesta
      if(data['codigo'] == 0){
        $("#mensaje_login").html('<div class="alert alert-success">'+ data['mensaje']+'</div>');
        location.href="index.php?lang="+lang;
      }else{
        $("#mensaje_login").html('<div class="alert alert-danger">'+ data['mensaje']+'</div>');
      }
    },
    error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

/**
* CIERRA LA SESION
*/
function logout(){
  console.log("LOGOUT");
  clearTimeout(timerId); // clear timer
  deleteAllCookies();
  window.location = "includes/controladores/controller.Session.php";
}

/**
* MUESTRA LOS LUGARES EN BASE A LA BUSQUEDA REALIZADA
*/
function mostrarLugares(){
  var geocoder =  new google.maps.Geocoder();
  geocoder.geocode( { 'address': $("#txtSearchText").val()}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        this.lugares_obtenidos = results;
        content = "<table class='table table-striped'>  <thead><tr><th>#</th><th>Lugar</th><th>Latitud</th><th>Longitud</th></tr></thead><tbody>";
        for(var i=0;i<results.length;i++){
          content += "<tr><td>"+(i+1)+"</td><td><a class='lugar' onclick='addPlaceToSearch(\""+results[i].geometry.location.lat()+"\",\""+results[i].geometry.location.lng()+"\",\""+results[i].formatted_address+"\","+i+")'>"+results[i].formatted_address+"</a></td><td>"+results[i].geometry.location.lat().toFixed(5)+"</td><td>"+results[i].geometry.location.lng().toFixed(5)+"</td></tr>";
        }
        content += "</tbody></table>"
        $("#lugaresEncontrados").html(content);
      } else {
        console.log("Something got wrong " + status);
      }
  });
}

/**
* CAMBIA A LA PESTAÑA DE RESULTADOS
*/
function toResults(){
  cleanMap();
  //console.log(Object.keys(this.coors).length);
  //console.log(Object.keys(this.coors).length > 2);
  var clima = $("#chclima").is(":checked") ? 1 : 0;
  if((isSatSelected() &&  Object.keys(this.coors).length > 2) || 
    (isSatSelected() &&  Object.keys(this.coors).length > 0 && document.ant == "circulo") || 
    document.place.length > 0 || (clima && Object.keys(this.coors).length > 2)){
    console.log("entro");
    document.band = false;
    checkSession("getResults");
    if(filtro == "todas"){
      mostrar = $('input:radio[name=radiosResultados]:checked').val();
    }
    $('#mytabs a[href="#3b"]').tab('show');
    return true;
  }
  return false;
}

/*
* establece las fechas en el selector
*/
function setDate(date1,date2){
  if(moment(date1, "YYYY-MM-DD", true).isValid() && moment(date2, "YYYY-MM-DD", true).isValid()){
    $("#datetimepicker1").data('DateTimePicker').date(moment(date1));
    $("#datetimepicker2").data('DateTimePicker').date(moment(date2));
  }
}

/**
* VERIFICA SI UN SATELITE ESTA SELECCIONADO
*/
function isSatSelected(){
  var band = false;
  $('.satelite:checked').each(
    function() {
        band = true;
    }
  );
  return band;
}

/*
* OBTIENE LAS VARIABLES GET DESDE LA URL
*/
function get_variables(){
  var $_GET = {};
  document.location.search.replace(/\??(?:([^=]+)=([^&]*)&?)/g, function () {
    function decode(s) {
      return decodeURIComponent(s.split("+").join(" "));
    }
    $_GET[decode(arguments[1])] = decode(arguments[2]);
  });
  return $_GET;
}

/**
* OBTIENE LA GEOLOCALIZACION DEL USUARIO
* @params Nombre de la funcion a llamar
*/
function getLocation(strfunction){
  if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(window[strfunction],function(error){
        showError(error,strfunction);
      });
  } else {
      console.log("Geolocation is not supported by this browser.");
  }
}

/**
* MANEJO DE ERRORES EN LA GEOLOCALIZACIÓN
*/
function showError(error,strfunction) {
  switch(error.code) {
    case error.PERMISSION_DENIED:
      notificarUsuario("No ha sido posible obtener la ubicación. El denego la solicitud.","danger");
      console.log("User denied the request for Geolocation.");
      break;
    case error.POSITION_UNAVAILABLE:
      notificarUsuario("No ha sido posible obtener la ubicación.","danger");
      console.log("Location information is unavailable.");
      break;
    case error.TIMEOUT:
      notificarUsuario("Tiempo de solicitud de localización excedido.","danger");
      console.log("The request to get user location timed out.");
      break;
    case error.UNKNOWN_ERROR:
      notificarUsuario("Error desconocido. NO es posible obtener la ubicación.","danger");
      console.log("An unknown error occurred.");
      break;
  }
  window[strfunction](null);
}

/**
* CARGA EL MAPA
* PARAMAS: posicion del centro
*/
function initMap(position) {

  var mapDiv = document.getElementById('map');
  if(mapDiv != null){
    //INSTANCIA UN NUEVO OBJETO DE MAPA
    document.map = new google.maps.Map(mapDiv, {
      zoom: 5,
      minZoom: 6,
      center: {lat: 23.948089, lng: -102.514651},
      mapTypeId: google.maps.MapTypeId.ROADMAP
    });

    //INICIALIZA EL POLIGONO QUE EL USUARIO DIBUJARA
    document.shape = new google.maps.Polygon({
      strokeColor: '#FF0000',
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: '#FF0000',
      fillOpacity: 0.35
    });

    document.shape.setMap(document.map); //ASIGNA EL POLIGONO AL MAPA

    //LISTENER PARA ESCUCHAR EVENTOS DE CLICK
    document.map.addListener('click', agregar_forma);
    document.position = position;
    if(position){ //CAMBIA LA POSICION DEL MAPA
      document.map.setCenter({lat: position.coords.latitude, lng: position.coords.longitude});
      document.map.setZoom(7);
    }

    // Create the DIV to hold the control and call the CenterControl()
    // constructor passing in this DIV.
    var cleanControlDiv = document.createElement('div');
    var cleanControl = new CleanControl(cleanControlDiv, document.map);

    cleanControlDiv.index = 1;
    document.map.controls[google.maps.ControlPosition.TOP_CENTER].push(cleanControlDiv);
  }

  //CARGA LA BUSQUEDA O LAS COOKIES
  if(window.location.href.indexOf("element.php") == -1 &&  window.location.href.indexOf("user.php") == -1){
    if(window.busqueda == 0){
      checkSession("cargar_cookies");
    }else if(window.busqueda.length > 0){
      checkSession("loadSearch",busqueda);
    }
  }
}

/**
* FUNCION QUE CARGA EL ARCHIVO DE LENGUAJE
*/
function loadTexts(lang){
  $.getJSON("resources/langs.json", function(json) {
    //console.log(json[lang]);
    document.lngarr = json[lang];
    MONTHS = document.lngarr['months'];
  });
}

/**
* AGREGA UNA FORMA AL MAPA CUANDO SE HACE CLIC EN EL
*/
function agregar_forma(event){
  switch (document.ant){
    case "rectangulo":
      deleteAllCoord();
      var lat = event.latLng.lat();
      var lon = event.latLng.lng();
      var bounds = {
        north: lat+.5,
        south: lat,
        east: lon+.5,
        west: lon
      };
      addRectangleToMap(bounds);
      break;
    case "poligono":
      addCoorToPoli(event.latLng);
      break;
    case "circulo":
      deleteAllCoord();
      console.log("entro");
      if(document.coorsRecomendations != null){
        document.coorsRecomendations = {definedbyuser:true,lat:event.latLng.lat(),
                                        lon:event.latLng.lng()};
      }
      
      addCircle(event.latLng.lat(),event.latLng.lng(),0);
      break;
  }
}

/**
* MUESTRA EL LUGAR SELECCIONADO EN EL MAPA
*/
function addPlaceToSearch(lat,lng,address,i){
  document.country = this.lugares_obtenidos[i]['address_components'].filter(place => place.types.indexOf("country") > -1);
  document.country = (document.country.length > 0) ? document.country[0]["long_name"]:"";
  document.state = this.lugares_obtenidos[i]['address_components'].filter(place => place.types.indexOf("administrative_area_level_1") > -1);
  document.state = (document.state.length > 0) ? document.state[0]["long_name"]:"";
  document.city = this.lugares_obtenidos[i]['address_components'].filter(place => place.types.indexOf("locality") > -1);
  document.city = (document.city.length > 0) ? document.city[0]["long_name"]:"";
  var latlng = new google.maps.LatLng(lat,lng);
  addCoorToPoli(latlng);
  document.place = address;
  this.place_coors['lat'] = lat;
  this.place_coors['lon'] = lng;
  $("#txtSearchText").val("");
  $("#lugaresEncontrados").html("");
  $('#modSearchPlace').modal('hide');
  document.map.setCenter(latlng);
}

/*
* AGREGA UN CIRCULO AL MAPA
* @parameters lat y lon del centro, radio
*/
function addCircle(c_lat,c_lon,radius){
  var center = {lat: c_lat, lng: c_lon};
  //CALCULA EL RADIO EN FUNCION DEL ZOOM DEL MAPA CUANDO ESTE ES CERO
  if(radius <= 0){
    radius = Math.pow(2, (21 - document.map.getZoom()));
    document.radius = radius * 1128.497220 * 0.0027;
  }else{
    document.radius = radius;
  }
  console.log("radius " + radius);
  //CREA EL CIRCULO
  document.shape = new google.maps.Circle({
    editable: true,
    center: center,
    radius: document.radius
  });
  showCoorsInDiv(document.shape.getCenter());
  document.shape.setMap(document.map);
  google.maps.event.addListener(document.shape, 'radius_changed', function(evt) { 
    console.log(document.shape.getRadius());
  });
}


/*
* AGREGA UN NUEVO RECTANGULO AL MAPA
*/
function addRectangleToMap(bounds){
  //CREA EL RECTANGULO
  document.shape = new google.maps.Rectangle({
    bounds: bounds,
    editable: true
  });

  document.shape.addListener('bounds_changed', onRectChange);
  onRectChange(null);
  document.shape.setMap(document.map);
}

/**
* FUNCION QUE ES LLAMADA CUANDO EL RECTANGULO ES EDITADO, ADEMÁS
* MANDA A LLAMAR LA FUNCIÓN QUE MUESTRA LAS COORDENADAS
*/
function onRectChange(event) {
  deleteAllCoord(false);
  showCoorsInDiv(document.shape.getBounds().getNorthEast());
  showCoorsInDiv(document.shape.getBounds().getSouthWest());
  showCoorsInDiv( new google.maps.LatLng(
      document.shape.getBounds().getNorthEast().lat(),
      document.shape.getBounds().getSouthWest().lng())
  );
  showCoorsInDiv( new google.maps.LatLng(
    document.shape.getBounds().getSouthWest().lat(),
    document.shape.getBounds().getNorthEast().lng())
  );
}


/**
* AGREGA UNA NUEVA COORDENADA AL POLIGONO
*/
function addCoorToPoli(){
  var latLng;
  if(arguments.length == 2){
    latLng = new google.maps.LatLng(arguments[0],arguments[1]);
  }else if(arguments.length == 1){
    latLng = arguments[0];
  }
  path = document.shape.getPath(); //obtiene el arreglo de coordenadas actuales

  // Because path is an MVCArray, we can simply append a new coordinate
  // and it will automatically appear.
  path.push(latLng);
  showCoorsInDiv(latLng);
}

/**
* MUESTRA LAS COORDENADAS EN DECIMALES
*/
function mostrarEnDecimales(){
  show_in_degrees = false;
  if(path != null){
    var childs = document.getElementById("coordinates").childNodes;
    for(i=0;i<childs.length;i++){
      document.getElementById("ch"+childs[i].id).innerHTML =  coors[childs[i].id]['decimal']['lat']+","+coors[childs[i].id]['decimal']['lon'];
    }
  }
}

/**
* MUESTRA LAS COORDENADAS EN GRADOS
*/
function mostrarEnGrados(){
  show_in_degrees = true;
  if(path != null){
    var childs = document.getElementById("coordinates").childNodes;
    for(i=0;i<childs.length;i++){
      document.getElementById("ch"+childs[i].id).innerHTML =  coors[childs[i].id]['grados']['lat']+","+coors[childs[i].id]['grados']['lon'];
    }
  }
}

/**
* MUESTRA LAS COORDENADAS AGREGADAS EN UN DIV
*/
function showCoorsInDiv(latLng){
  var n = Object.keys(this.coors).length;
  var key = "div" + n; //CLAVE PARA LOS ARREGLOS
  var aux = n+1; //NUMERO DE OBJETOS EN EL ARRAY
  // Add a new marker at the new plotted point on the polyline.
  //GUARDA EL MARCADOR EN UN ARREGLO
  this.markers[key] = new google.maps.Marker({
    position: latLng,
    map: document.map
  });
  //GUARDA LAS COORDENADAS EN UN OBJETO
  coors[key] = {decimal:{lat:latLng.lat().toFixed(5),lon:latLng.lng().toFixed(5)},grados:{lat:toDegrees(latLng.lat().toFixed(5),true),lon:toDegrees(latLng.lng().toFixed(5),false)}};

  //MUESTRA LAS COORDENADAS
  if(show_in_degrees){
    if(aux == 1){
      $("#coordinates").html("<div class='coords1' id='div"+n+"'><div class='divcoordenadas' id='chdiv"+n+"'>"+ coors[key]['grados']['lat']+" , "+ coors[key]['grados']['lon'] + "</div> <div class='btndelete'><button type='button' class='btn btn-default btn-xs pull-right'  onclick=\"deleteCoord("+n+")\"><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button></div> </div>");
    }else if(aux%2 == 0){
      $("#coordinates").append("<div class='coords2' id='div"+n+"'><div class='divcoordenadas' id='chdiv"+n+"'>"+ coors[key]['grados']['lat']+" , "+ coors[key]['grados']['lon'] + "</div> <div class='btndelete'><button type='button' class='btn btn-default btn-xs pull-right'  onclick=\"deleteCoord("+n+")\"><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button></div> </div>");
    }else{
      $("#coordinates").append("<div class='coords1' id='div"+n+"'><div class='divcoordenadas' id='chdiv"+n+"'>"+coors[key]['grados']['lat']+" , "+ coors[key]['grados']['lon'] + "</div> <div class='btndelete'><button type='button' class='btn btn-default btn-xs pull-right'  onclick=\"deleteCoord("+n+")\"><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button></div> </div>");
    }
  }else{
    if(aux == 1){
      $("#coordinates").html("<div class='coords1' id='div"+n+"'><div class='divcoordenadas' id='chdiv"+n+"'>"+ coors[key]['decimal']['lat']+" , "+coors[key]['decimal']['lon'] + "</div> <div class='btndelete'><button type='button' class='btn btn-default btn-xs pull-right'  onclick=\"deleteCoord("+n+")\"><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button></div> </div>");
    }else if(aux%2 == 0){
      $("#coordinates").append("<div class='coords2' id='div"+n+"'><div class='divcoordenadas' id='chdiv"+n+"'>"+ coors[key]['decimal']['lat']+","+coors[key]['decimal']['lon'] + "</div> <div class='btndelete'><button type='button' class='btn btn-default btn-xs pull-right'  onclick=\"deleteCoord("+n+")\"><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button></div> </div>");
    }else{
      $("#coordinates").append("<div class='coords1' id='div"+n+"'><div class='divcoordenadas' id='chdiv"+n+"'>"+  coors[key]['decimal']['lat']+","+coors[key]['decimal']['lon']  + "</div> <div class='btndelete'><button type='button' class='btn btn-default btn-xs pull-right'  onclick=\"deleteCoord("+n+")\"><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button></div> </div>");
    }
  }
}

/**
* ELIMINA UNA COORDENADA AGREGADA
*/
function deleteCoord(marker){

  if(document.ant == "poligono"){
    markers["div"+marker].setMap(null);
    var i = 0;
    var childs = document.getElementById("coordinates").childNodes;
    for(i=0;i<childs.length;i++){
      if(childs[i].id == "div"+marker){
        break;
      }
    }
    path.removeAt(i);
    delete this.coors["div"+marker];
    $("#div"+marker).remove();
    if(path.length == 0){
      $("#coordinates").html('<div class="coords1">No se han agregado coordenadas.</div>');
    }
  }else{
    deleteAllCoord();
  }
  
}

//convierte las coordenadas a decimales
function toDecimal(grad,mins,segs,orien){
    sign = (orien == "N" || orien == "E") ? 1 : -1;
    return (sign * (parseInt(grad) + parseInt(mins)/60 + parseInt(segs)/3600)).toFixed(5);
}

//convierte las coordenadas a grados
function toDegrees(decimal,lat){
  ent = parseInt(decimal);

  sign = (lat) ? "N" : "E";
  if(ent < 0){
    if(!lat){
      sign = "W";
    }else{
      sign = "S";
    }
    ent *= -1;
    decimal *= -1;
  }
  dec = decimal - ent;
  seg = dec * 60;
  dec = seg - parseInt(seg);
  seg = parseInt(seg);

  return ent+"° " +seg +"\' " + (dec*60).toFixed(3) + "\'\' " +sign;
}

//LIMPIA EL MAPA REMOVIENDO LOS POLIGONOS E IMAGENES QUE AGREGO EL USUARIO
function cleanMap(){
  for (var key in polys_agregados) {
    polygonToMap(key);
  }
  for (var key in this.imgsMaps_agregados) {
    imageToMap(null,key);
  }
  if(document.marcadoresClima.length > 0){
    document.marcadoresClima.forEach(function(item,index){
      item.setMap(null);
    });
  }
}

//ELIMINA TODAS LAS COORDENADAS AGREGADAS
function deleteAllCoord(shape_null=true){
  for (var key in this.markers) {
    this.markers[key].setMap(null);
  }

  if(shape_null){
    document.shape.setMap(null);
    document.shape = new google.maps.Polygon({
      strokeColor: '#FF0000',
      strokeOpacity: 0.8,
      strokeWeight: 2,
      fillColor: '#FFF',
      fillOpacity: 0
    });
    document.shape.setMap(document.map);
  }

  this.coors = [];
  this.markers = [];
  $("#coordinates").html('<div class="coords1">No se han agregado coordenadas.</div>');
  /*if(polyfoto){
    polyfoto.setMap(null);
  }*/
}

/**
* The CenterControl adds a control to the map that recenters the map on
* Chicago.
* This constructor takes the control DIV as an argument.
* @constructor
*/
function CleanControl(controlDiv, map) {
  // Set CSS for the control border.
  var controlUI = document.createElement('div');
  controlUI.style.backgroundColor = '#fff';
  controlUI.style.border = '2px solid #fff';
  controlUI.style.borderRadius = '3px';
  controlUI.style.boxShadow = '0 2px 6px rgba(0,0,0,.3)';
  controlUI.style.cursor = 'pointer';
  controlUI.style.marginBottom = '22px';
  controlUI.style.textAlign = 'center';
  controlUI.title = 'Click to clean the map';
  controlDiv.appendChild(controlUI);

  // Set CSS for the control interior.
  var controlText = document.createElement('div');
  controlText.style.color = 'rgb(25,25,25)';
  controlText.style.fontFamily = 'Roboto,Arial,sans-serif';
  controlText.style.fontSize = '16px';
  controlText.style.lineHeight = '38px';
  controlText.style.paddingLeft = '5px';
  controlText.style.paddingRight = '5px';
  controlText.innerHTML = document.lngarr['cleanmap'];
  controlUI.appendChild(controlText);

  // Setup the click event listeners: simply set the map to Chicago.
  controlUI.addEventListener('click', function() {
    cleanMap();
  });
}

//NOTIFICA UN ERROR
function notificarUsuario(msj,tipo){
  $.notify({
    message: msj
  },{
    type: tipo
  });
}

/**
* MUESTRA EL POLIGONO DE UN PATH ROW
*/
function showPathRowsCoors(path,row){
  data = {path:path,row:row,action:"get_pathrow_poly"};
  $.ajax({
      url: 'includes/controladores/controller.Images.php',  //Server script to process data
      type: 'POST',
      data: data,
      dataType: 'json',
      success  : function(data){ //muestra la respuesta
        lat = data[0]['ul_lat'];
        lon = data[0]['ul_lon'];
        var latlng = new google.maps.LatLng(lat,lon);
        addCoorToPoli(latlng);
        lat = data[0]['ur_lat'];
        lon = data[0]['ur_lon'];
        latlng = new google.maps.LatLng(lat,lon);
        addCoorToPoli(latlng);
        lat = data[0]['lr_lat'];
        lon = data[0]['lr_lon'];
        latlng = new google.maps.LatLng(lat,lon);
        addCoorToPoli(latlng);
        lat = data[0]['ll_lat'];
        lon = data[0]['ll_lon'];
        latlng = new google.maps.LatLng(lat,lon);
        addCoorToPoli(latlng);
        document.map.setCenter(new google.maps.LatLng(data[0]['ctr_lat'],data[0]['ctr_lon']));
        $("#txtPath").val("");
        $("#txtRow").val("");
        $('#modPathRow').modal('hide');
      },
      error: function(data){ //se lanza cuando ocurre un error
        console.log("error " + data.responseText);
      }
   });
}


///////// MANEJO DE COOKIES
//agrega una nueva cookie
function setCookie(cname,cvalue,minutes) {
    var d = new Date();
    d.setTime(d.getTime() + (minutes * 60 * 1000));
    var expires = "expires=" + d.toGMTString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

//elimina todas las cookies
function deleteAllCookies() {
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');

  for(var i = 0; i < ca.length; i++) {
      var c = ca[i].trim().split("=",2);
      setCookie(c[0],"",-1);
  }
}

//regresa el valor de una cookie
function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');

    for(var i = 0; i < ca.length; i++) {
        var c = ca[i].trim().split("=",2);
        if(c[0] == cname.trim()){
          return c[1];
        }
    }
    return "";
}

//CARGA LAS COOKIES GUARDADAS
function cargar_cookies(){
  console.log("CARGANDO COOKIES");
  cook_shape = getCookie("shape");
  cook_onmap = getCookie("onmap");
  cook_onmap = cook_onmap  ==  "true"
  $('#chOnMap').prop('checked', cook_onmap);
  if(cook_shape != null){
    cook_sats = getCookie("satelites").split(',');
    startDate = getCookie("startDate");
    endDate = getCookie("endDate");

    if(cook_shape == "poligono"){
      cook = jQuery.parseJSON(getCookie("poligono"));
      cook.forEach(function(val,ind){
        addCoorToPoli(val['lat'],val['lon']);
      });
    }else if(cook_shape == "rectangulo"){
      cook = jQuery.parseJSON(getCookie("poligono"));
      var bounds = {
        north: Number(cook[0]['lat']),
        south: Number(cook[1]['lat']),
        east: Number(cook[0]['lon']),
        west: Number(cook[1]['lon'])
      };
      addRectangleToMap(bounds);
    }else if(cook_shape == "circulo"){
      cook = jQuery.parseJSON(getCookie("poligono"));
      radio_cook = Number(getCookie("radio"));
      addCircle(Number(cook[0]['lat']),Number(cook[0]['lon']),radio_cook);
    }else if(cook_shape == "nombre"){
      place_coors['lat'] = getCookie("lat");
      place_coors['lon'] = getCookie("lon");
      document.state = getCookie("state");
      document.country = getCookie("country");
      document.city = getCookie("city");
      document.place = getCookie("place");
      addCoorToPoli(place_coors['lat'],place_coors['lon']);
    }

    setDate(startDate,endDate);

    document.ant = cook_shape;
    cook_sats.forEach(function(val,ind){
      $('#ch'+val).prop('checked', true);
    });
    toResults();
  }
}

/*
* CHECA SI LA SESIÓN ESTA ACTIVA
*/
function checkSession(){
  strfunction = arguments[0];
  function_arguments = arguments;
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Session.php',
    dataType: 'json',
    data    : {action:"check"},
    success : function(response) {
      if(response){
        if(timerId != null){
          clearTimeout(timerId); // clear timer
        }
        startTimer();
        if(strfunction != null && strfunction.length > 0){
          if(strfunction != "sesionExpirada"){
            if(function_arguments.length > 1){
              window[strfunction](function_arguments);
            }else{
              window[strfunction]();
            }
          }
        }
      }else{
        if(strfunction == "sesionExpirada"){
          window[strfunction]();
        }else{
          $('#loginmodal').modal('show');
        }
      }
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

/*
* CAMBIA LA PUNTUACIÓN DE UNA IMAGEN EN LA BASE DE DATOS
*/
function rate(){
  element = arguments[0][1];
  id = arguments[0][2];
  rating = arguments[0][3];
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Session.php',
    data    : {img:id,rating:rating,action:"rate"},
    success : function(response) {
      for(i=1;i<=5;i++){
        if(i<=rating){
          $("#btnStar"+id+i).html('<span class="glyphicon glyphicon-star" aria-hidden="true"></span>');
        }else{
          $("#btnStar"+id+i).html('<span class="glyphicon glyphicon-star-empty" aria-hidden="true"></span>');
        }
      }
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}


/*
* MODIFICA LA BASE DE DATOS CON LOS VALORES DE LA RECCIOÓN DEL USUARIO (LIKE OR DISLIKE)
*/
function modifyreactiondb(imagen,rating){
  $.ajax({
    type    : 'POST',
    url     : 'includes/reactions.php',
    dataType: 'json',
    data    : {img:imagen,rating:rating},
    success : function(response) {
      $("#btnLike"+imagen+" span").text(""+response[0].likes);
      $("#btnDislike"+imagen+" span").text(""+response[0].dislikes);
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

/*
* AGREGA UNA VENTANA DE INFORMACIÓN AL ELEMENTO ESPECIFICADO
*/
function addInfoWindow(element,data){
  var contentString = '<h5>'+data['nombre']+'</h5><br>';
  if(data['city'] != null){
    contentString += data['city'];
  }

  if(data['state'] != null){
    contentString += ", "+data['state'];
  }

  if(data['country'] != null){
    contentString += ", "+data['country'];
  }
  contentString += '<br><strong>Path</strong>:'+data['path']+'<br><strong>Row</strong>:'+data['row']+'<br>';
  var infowindow = new google.maps.InfoWindow({
    content: contentString
  });
  /*element.addListener('click', function() {
    infowindow.open(map, marker);
  });*/
  var listener = google.maps.event.addListener(element, "click", function(mouseEvent, theGoex, imageX, imageY, lat, lon) { infowindow.open(map, element); });
}

/*
* MUESTRA UNA IMAGEN EN EL MAPA
*/
function imageToMap(elemento,nombre,action,rightP=false,idrecomendacion=-1){
  if(nombre in imgsMaps_agregados){
    if(imgsMaps_agregados[nombre]){
      imgsMaps_agregados[nombre].setMap(null);
      delete imgsMaps_agregados[nombre];
      $(elemento).html("<span class='glyphicon glyphicon-picture' aria-hidden='true'></span>");
      $(elemento).removeClass( "btn btn-secondary" ).addClass( "btn btn-info" );
      $(elemento).prop('title', 'Ver imágen en el mapa');
    }
  }else{
    var data = {imagen:nombre,rightP:rightP,action:action,idrecomendacion:idrecomendacion};
    $.ajax({
      type    : 'POST',
      url     : 'includes/controladores/controller.Images.php',
      dataType: 'json',
      data    : data,
      success : function(response) {
        $(elemento).html("<span class='glyphicon glyphicon-eye-close' aria-hidden='true'></span>");
        $(elemento).removeClass( "btn btn-info" ).addClass( "btn btn-secondary" );
        $(elemento).prop('title', 'Ocultar imágen del mapa');
        nombreAnt = nombre;
        triangleCoords = [];
        aux = [];
        response.forEach(function(item,index){
          aux[item.position] = item;
        });
        var bl = new google.maps.LatLng(aux["LL"].lat,aux["LL"].lon);
        var br = new google.maps.LatLng(aux["LR"].lat,aux["LR"].lon);
        var tr = new google.maps.LatLng(aux["UR"].lat,aux["UR"].lon);
        var tl = new google.maps.LatLng(aux["UL"].lat, aux["UL"].lon);
        var llq = new LatLngQuad(bl, br, tr, tl);
        var goex = new GroundOverlayEX('resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/'+response[0].nombre+'.jpg', null, { map: document.map,latlngQuad:llq,clickable: true });
        imgsMaps_agregados[nombre] = goex;
        addInfoWindow(goex,aux['Center']);
      },error : function(response){
        console.log(response.responseText);
      }
    });
  }
}

/*
* MUESTRA LA METADATA DE LA IMAGEN SOLICITADA
*/
function verMeta(nombre,rightP=false,idrecomendacion=-1){
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Images.php',
    dataType: 'json',
    data    : {imagen:nombre,action:"view_metadata",rightP:rightP,idrecomendacion:idrecomendacion},
    success : function(response) {
        $("#titleModData").html(response[0].nombre);
        content = "<table class='table table-striped'>  <thead><tr>><th>"+document.lngarr['data']+"</th><th>"+document.lngarr['value']+"</th></tr></thead><tbody>";
        content += "<tr><td>"+document.lngarr['datead']+": </td><td>"+response[0].date+"</td></tr>";
        content += "<tr><td>"+document.lngarr['catalog']+": </td><td>"+response[0].satelite+"</td></tr>";
        content += "<tr><td>"+document.lngarr['path']+" ("+document.lngarr['center']+"): </td><td>"+response[0].path+"</td></tr>";
        content += "<tr><td>"+document.lngarr['row']+" ("+document.lngarr['center']+"): </td><td>"+response[0].row+"</td></tr>";
        aux = [];
        response.forEach(function(item,index){
          aux[item.position] = item;
        });
        content += "<tr><td>"+document.lngarr['ul']+": </td><td>"+aux["UL"].lat+" , "+aux["UL"].lon+"</td></tr>";
        content += "<tr><td>"+document.lngarr['ur']+": </td><td>"+aux["UR"].lat+" , "+aux["UR"].lon+"</td></tr>";
        content += "<tr><td>"+document.lngarr['ll']+": </td><td>"+aux["LL"].lat+" , "+aux["LL"].lon+"</td></tr>";
        content += "<tr><td>"+document.lngarr['lr']+": </td><td>"+aux["LR"].lat+" , "+aux["LR"].lon+"</td></tr>";
        content += "<tr><td>"+document.lngarr['center']+": </td><td>"+aux["Center"].lat+" , "+aux["Center"].lon+"</td></tr>";
        content += "<tr><td>"+document.lngarr['projection']+": </td><td>"+response[0].projection+"</td></tr>";
        content += "<tr><td>"+document.lngarr['ellipsoid']+": </td><td>"+response[0].ellipsoid+"</td></tr>";
        content += "</tbody></table>"

        $("#bodymodalData").html(content);
        $('#modDataImg').modal('show');
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}


/*
* MUESTRA EL POLIGONO DE UNA IMAGEN EN EL MAPA
*/
function polygonToMap(elemento,nombre,action,rightP=false,idrecomendacion=-1){
  if(nombre in polys_agregados){
    if(polys_agregados[nombre]){
      polys_agregados[nombre].setMap(null);
      delete polys_agregados[nombre];
      $(elemento).html("<span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span> Ver polígono");
      $(elemento).removeClass( "btn btn-secondary" ).addClass( "btn btn-info" );
    }
  }else{
    var data = {imagen:nombre,rightP:rightP};
    if(arguments.length == 3){
      data.action = arguments[2];
    }else{
      data.action = "view_polygon";
    }
    data.idrecomendacion = idrecomendacion;
    console.log(data);
    $.ajax({
      type    : 'POST',
      url     : 'includes/controladores/controller.Images.php',
      dataType: 'json',
      data    : data,
      success : function(response) {
          $(elemento).html("<span class='glyphicon glyphicon-eye-close' aria-hidden='true'></span> Ocultar");
          $(elemento).removeClass( "btn btn-info" ).addClass( "btn btn-secondary" );
          nombreAnt = nombre;
          triangleCoords = [];
          aux = [];
          response.forEach(function(item,index){
            aux[item.position] = item;
          });
          triangleCoords.push({lat:parseFloat(aux["UL"].lat), lng:parseFloat(aux["UL"].lon)})
          triangleCoords.push({lat:parseFloat(aux["UR"].lat), lng:parseFloat(aux["UR"].lon)})
          triangleCoords.push({lat:parseFloat(aux["LR"].lat), lng:parseFloat(aux["LR"].lon)})
          triangleCoords.push({lat:parseFloat(aux["LL"].lat), lng:parseFloat(aux["LL"].lon)})

          // Construct the polygon.
          var polyfoto = new google.maps.Polygon({
            paths: triangleCoords,
            strokeColor: '#1A237E',
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: '#9FA8DA',
            fillOpacity: 0.35
          });
          polyfoto.setMap(document.map);
          console.log(aux);
          //var center = new google.maps.LatLng(aux["Center"].lat,aux["Center"].lon);
          polys_agregados[nombre] = polyfoto;
      }
    });
  }
}


/*
* OBTIENE LOS RESULTADOS DE UNA BUSQUEDA
*/
function getResults(page){
  var polysJson = toJSON(polys_agregados);
  var imgsJson = toJSON(imgsMaps_agregados);
  var satelites = getSats();
  var ischeck =  $('#chproductos').is(":checked");
  var clima = $("#chclima").is(":checked") ? 1 : 0;
  var showproducts = ischeck ? 1 : 0;
  var data;
  var filtro = $('input[name=radiosResultados]:checked').val();
  var startDate = $("#datetimepicker1").data('DateTimePicker').date();
  var endDate = $("#datetimepicker2").data('DateTimePicker').date();
  if(startDate != null){
    startDate = startDate.format("YYYY-MM-DD");
  }
  if(endDate != null){
    endDate = endDate.format("YYYY-MM-DD");
  }

  //GUARDA LAS COOKIES
  setCookie("satelites", satelites, 60);
  setCookie("shape", document.ant, 60);
  setCookie("startDate", startDate, 60);
  setCookie("endDate", endDate, 60);
  setCookie("onmap", $('#chOnMap').is(":checked"), 60);

  if(document.ant == "nombre"){
    //GUARDA LAS COOKIES
    setCookie("lat", this.place_coors['lat'],60);
    setCookie("lon", this.place_coors['lon'],60);
    setCookie("state",document.state,60);
    setCookie("country", document.country,60);
    setCookie("city", document.city,60);
    setCookie("place", document.place,60);

    data = {satelites:satelites,page:page,lat:this.place_coors['lat'],
            lon:this.place_coors['lon'],startDate:startDate,endDate:endDate,
            polis:polysJson,overlaps:imgsJson,height:document.height,
            state:document.state,country:document.country,city:document.city,
            shape:'lugar',filtro:FILTROS[filtro], clima:clima};
  }else{
    var coorsJson = getCoors();
    var radio = document.ant == "circulo" ? document.shape.getRadius() : 0;

    //GUARDA LAS COOKIES
    setCookie("poligono", coorsJson, 60);
    setCookie("radio", radio, 60);

    data = {coordenadas:coorsJson,satelites:satelites,shape:document.ant,
      radio:radio,startDate:startDate,endDate:endDate,page:page,polis:polysJson,
      overlaps:imgsJson,height:document.height,showproducts:showproducts,
      filtro:FILTROS[filtro], clima:clima};
  }

  if(document.band){
    data.month = document.month;
    data.year = document.year;
  }

  data.onlynames = 0;
  data.action = "get_images_in_shape";
  if($('#chOnMap').is(":checked") && $('#chlandsat').is(":checked") && !document.band){
    showAllOnMap(data);
  }else{
    if(!$('#chlandsat').is(":checked")){
      $("#dropyears").html("");
    }
    //var colors = ["red","blue","green","orange","purple"];
    if(clima){
      document.marcadoresClima.forEach(function(item,index){
        item.setMap(null);
      });
      var k = $("#txtKClust").val();
      data.k = k;
      console.log(k);
      var colors = {};
      for (var i = 0; i<k;i++) {
        colors[i] = Math.floor(Math.random()*16777215).toString(16)
         if(colors[i].length == 5){
          colors[i] += "0"
        }

        if(colors[i].length > 6){
          colors[i] = colors[i].substring(0,6)
        }
        //colors.push(Math.random());
      }
      console.log(colors);
      $.ajax({
          type    : 'POST',
          url     : 'includes/controladores/controller.Images.php',
          dataType: 'json',
          data    : data,
          beforeSend: function(){ $("#results2").html("<div style='width:100%; height:30px; color:blue'></div><img src='resources/imgs/loader.gif'></img>"); },
          success : function(response) {
            console.log(response);
            $("#results2").html("<div style='width:100%; height:30px; color:blue'></div>");
            //$("#results").html(response);
            clusters = response[0]['clusters'];
            regClus = {}
            for (var i = 0; i < k; i++) {
              regClus[i] = []
            }
            console.log(colors);
            response.forEach(function(item,index){
              clusters = item['clusters'];
              clusters.forEach(function(cluster){
                id = parseInt(cluster['id'])-1;
                //console.log(id);
                points = cluster['points'];
                points.forEach(function(p,i){
                  estcoors = {lat:parseFloat(p['latitude']),lng:parseFloat(p['longitude'])};
                  color = colors[id]
                  //console.log(color);
                var pinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + color,
                      new google.maps.Size(21, 34),
                      new google.maps.Point(0,0),
                      new google.maps.Point(10, 34));
                
                           var marker = new google.maps.Marker({
                            position: estcoors, 
                            map: document.map,
                            icon: pinImage
                        });

                 /*marker = new google.maps.Circle({
                          strokeColor: "#000",
                          strokeOpacity: 1,
                          strokeWeight: 2,
                          fillColor: color,
                          fillOpacity: 1,
                          map: document.map,
                          center: estcoors,
                          radius: 4000
                          });*/
                  regClus[id].push(p['station']);
                  document.marcadoresClima.push(marker);
                  var data = p['data'];
                  var perVar = data.length / 3;
                  var ii = 0;
                  var tmpMaxProm = 0, tmpMinProm = 0, precProm = 0;
                  for(ii = 0; ii < perVar; ii++){
                    tmpMaxProm += data[ii];
                    tmpMinProm += data[ii+perVar];
                    precProm += data[ii+perVar+perVar];
                  }
                  tmpMaxProm /= perVar;
                  tmpMinProm /= perVar;
                  precProm /= perVar;
                  var infowindow = new google.maps.InfoWindow({
                    content: "<div><div><strong>"+p['station']+"</strong></div><div>Latitud = "
                    +p['latitude']+
                    "<br><strong>Longitud</strong> = "+p['longitude']+"</div>"+
                    "<br><strong>Temperatura máxima promedio</strong> = "+tmpMaxProm.toFixed(2)+" °C"+
                    "<br><strong>Temperatura mínima promedio</strong> = "+tmpMinProm.toFixed(2)+" °C"+
                    "<br><strong>Precipitación promedio</strong> = "+precProm.toFixed(2)+" mmmm"+
                    "</div>"
                  });

                  marker.addListener('click', function() {
                    infowindow.open(document.map, marker);
                  });
                });
              });
            });

            //console.log(regClus[0]);
            getCorrelations(regClus, 0, parseInt(k), colors);
          },error: function(data){ //se lanza cuando ocurre un error
            console.log(data.responseText);
          }
        });
    }else{
      $.ajax({
          type    : 'POST',
          url     : 'includes/controladores/controller.Images.php',
          //dataType: 'json',
          data    : data,
          beforeSend: function(){ $("#results").html("<img src='resources/imgs/loader.gif'></img>"); },
          success : function(response) {
            $("#results").html(response).fadeIn('slow');
          },error: function(data){ //se lanza cuando ocurre un error
            console.log(data.responseText);
          }
        });
    }
  }
}

var names = ["Tmp Max", "Tmp Min", "Precipitation"];
function getCorrelations(stations, ii, k, colors){
  console.log("entrooooo");
  if(stations[ii] != null &&  stations[ii].length > 0){
    $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/getRegresions.php',
    dataType: 'json',
    data    : {stations:stations[ii]},
     success : function(response) {
        //console.log("Aaaa");
        console.log(response);
        var i = 0;
        $("#results2").append("<br><br><span class=\"dot\" style=\"background-color: #"+colors[ii]+"\"></span> <strong>Cluster " + ii+"</strong><br><hr>").fadeIn('slow');
        response.forEach(function(item){
          console.log(item);
          $("#results2").append("<a onclick=\"viewImage('http://adaptivez.org.mx/AEM-Eris/includes/controladores/"+item+"')\" >"+names[i]+"</a> ");
          i++;
         });
        //console.log(ii,k);
        if(ii < k){
          getCorrelations(stations, ii+1, k, colors);
        }
      },error: function(data){ //se lanza cuando ocurre un error
        if(ii < k){
          getCorrelations(stations, ii, k, colors);
        }
        //console.log(data.responseText);
      }
    });
  }else if(ii < k){
    getCorrelations(stations, ii+1, k, colors);
  }
  
}

function viewImage(imgSrc){
  $('#imagepreview').attr('src', imgSrc); // here asign the image to the modal when the user click the enlarge link
  $('#imagepreview').attr('data-big', imgSrc); // here asign the image to the modal when the user click the enlarge link
  //$('#imagepreview').attr('height','500px');
  $('#imagepreview').attr('width','600px');
  $('#imagemodal').modal('show'); // imagemodal is the id attribute assigned to the bootstrap modal, then i use the show function
}

/*
* convierte un arreglo a JSON
*/
function toJSON(arr){
  return JSON.stringify(Object.keys(arr));
}

/*
* regresa las coordenadas del poligono en el mapa en formato JSON
*/
function getCoors(){
  var arrJson = [];
  for (var key in coors) {
      if (coors.hasOwnProperty(key)){
        arrJson.push(coors[key]['decimal']);
      }
  }
  return JSON.stringify(arrJson);
}

/*
* regresa los satelites seleccionados en un arreglo
*/
function getSats(){
  var satelites = []
  $('.satelite:checked').each(
    function() {
        satelites.push($(this).val());
    }
  );
  return satelites;
}

/*
* ACTUALIZA LOS DATOS EN LA SESSION
*/
function updateCarSession(item,action){
  $.ajax({
    type    : 'POST',
    url     : 'includes/update_downloads.php',
    dataType: 'json',
    data    : {agregadas:item,action:action},
    success : function(response) {
      $("#lblNumberProducts").html(response);
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

/*
* DESCARGA LAS IMAGENES AGREGADAS A LA COLA DE DESCARGA
*/
function downloadImages(){
  $.ajax({
    type    : 'POST',
    url     : 'includes/download_images.php',
    data    : {descargar:"xxx"},
    beforeSend: function(){
      $('#modDownload').modal('show');
      $("#mensajedownload").html(document.lngarr['preparing']);
    },
    success : function(response) {
      if(response.length > 0){
        $("#mensajedownload").html('<a id="btnDownloadImages" download>'+document.lngarr['downloadimgs']+'</a>');
        $("#btnDownloadImages").attr("href", response);
      }else{
        $('#modDownload').modal('hide');
        notificarUsuario(document.lngarr['noaddimgs'],'danger');
      }
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

/*
* AGREGA UN ELEMENTO AL CARRITO DE DESCARGAS
*/
function addToCar(id,action){
  action = arguments[0][2];
  id = arguments[0][1];
  if(action == "add"){
    $("#chooseJPG").prop('checked', false);
    $("#chooseMeta").prop('checked', false);
    $("#spanImagen").html(id);
    $('#productsmodal').modal('hide');
    $("#modChoose").modal('show');
  }else{
    $("#btn"+id).html("<button title='Agregar a descargas' type='button'  onclick='checkSession(\"addToCar\",\""+id+"\",\"add\")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span></button>");
    updateCarSession(id,action);
  }
}

/*
* CAMBIA EL SATELITE SELECCIONADO
*/
function changeSatelite(satelite){
  $('.satelite:checked').each(
    function() {
      $('#ch'+$(this).val()).prop('checked', false);
    }
  );
  $('#ch'+satelite).prop('checked', true);
  toResults();
}

/**
* CAMBIA LA IMAGEN DEL PRODUCTO DERIVADO SELECCIONADO
*/
function changeImageProduct(index){
  $('#imgproduct').attr('src', 'resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/'+document.derivados[index]['descriptor']+'.jpg');
  $("#imgdescription").html(document.derivados[index]['description']);
}

/**
* MUESTRA LOS PRODUCTOS DERIVADOS DE UNA IMAGEN
*/
function verProducts(imagen,nombre){
  $("#titleModProducs").html(document.lngarr['derprods'] + nombre);
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Images.php',
    dataType: 'json',
    data    : {img:imagen,action:'get_derivados'},
    success : function(response) {
      document.derivados = response['derivados'];
      if(document.derivados.length > 0){
        $('#imgproduct').attr('src', 'resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/'+document.derivados[0]['descriptor']+'.jpg'); // here asign the image to the modal
        $("#imgdescription").html(document.derivados[0]['description']);
        tabla = "";
        document.it=0;
        document.derivados.forEach(function(item,index){
          tabla += "<tr><td><a href='javascript:;' onclick='changeImageProduct("+document.it+")'>"+item['descriptor']+"</a></td><td>"+item['short_description']+"</td><td><span id='btn"+item['descriptor']+"'><button title='"+document.lngarr['download']+"' type='button'  onclick='checkSession(\"addToCar\",\""+item['descriptor']+"\",\"add\")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span></button></span></td><td>";
          for(var i=1;i<=5;i++){
            if(i<=item['rating']){
              tabla += '<button id="btnStar'+item['idelemento']+i+'" onclick=\'checkSession(\"rate\",this,\"'+item['idelemento']+'\",\"'+i+'\")\' type="button" class="btn btn-default btn-xs"><span class="glyphicon glyphicon-star" aria-hidden="true"></span></button>';
            }else{
              tabla += '<button id="btnStar'+item['idelemento']+i+'" onclick=\'checkSession(\"rate\",this,\"'+item['idelemento']+'\",\"'+i+'\")\' type="button" class="btn btn-default btn-xs"><span class="glyphicon glyphicon-star-empty" aria-hidden="true"></span></button>';
            }
          }
          //url = 
          tabla += "</td><td>"
              + "<a href='#' data-trigger='focus' title='URL' data-toggle='popover' data-placement='left' data-content='"+
                    "<ul><li><a onclick=copyTextToClipboard(\""+response['url']+item['hash_name']+"\")>"+document.lngarr['desccopbtn']+"</a></li>"
                    + "<li><a href=\"element.php?elemento="+item['hash_name']+"\">"+document.lngarr['go']+"</a></li></ul>'><span class='glyphicon glyphicon-copy' aria-hidden='true'></span></a></td></tr>";
          document.it++;
        });
        $("#tblchilds").html(tabla);
        $('[data-toggle="popover"]').popover({
          animation: true,
          html: true
        });
        $('#productsmodal').modal('show');
      }else{
        notificarUsuario(document.lngarr['theimg'] + nombre + document.lngarr['donthave'],'danger');
      }
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

/*
* carga una busqueda previamente hecha
*/
function loadSearch(){
  idbusqueda = arguments[0][1];
  console.log("CARGANDO BUSQUEDA ..." + idbusqueda);
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Logs.php',
    dataType: 'json',
    data    : {busqueda:idbusqueda,action:"get_search"},
    success : function(response) {
      forma = response['busqueda'][0]['tipo'];
      filtro = response['busqueda'][0]['filtro'];
      startDate = response['busqueda'][0]['fecha_inicial'];
      endDate = response['busqueda'][0]['fecha_final'];
      setDate(startDate,endDate);
      response['satelites'].forEach(function(val,ind){
        $('#ch'+val[0]).prop('checked', true);
      });
      $("#chproductos").prop("checked", response['busqueda'][0]["derivados"]);

      for(var key in FILTROS) {
        if(FILTROS[key] === filtro) {
          filtro = key;
          break;
        }
      }
      $("#rd"+capitalizeFirstLetter(filtro)).prop("checked", true);
      switch (forma) {
        case 1: //poligono
          poligono = response['data'][0]['polygon'];
          poligono = poligono.replace(/"/g, "").replace(/'/g, "").replace(/\(|\)/g, "");
          coordenadas = poligono.split(",");
          for(i=0;i<coordenadas.length;i+=2){
            addCoorToPoli(coordenadas[i+1],coordenadas[i]);
          }
          document.ant = "poligono";
          //cleanMap();
          break;
        case 2: //circulo
          radio_cir = Number(response['data'][0]['radius']);
          lat_ctr = Number(response['data'][0]['center_lat']);
          lon_ctr = Number(response['data'][0]['center_lon']);
          addCircle(lat_ctr,lon_ctr,radio_cir);
          document.ant = "circulo";
          break;
        case 3: //rectangulo
          poligono = response['data'][0]['polygon'];
          poligono = poligono.replace(/"/g, "").replace(/'/g, "").replace(/\(|\)/g, "");
          coordenadas = poligono.split(",");
          var bounds = {
            north: Number(coordenadas[1]),
            south: Number(coordenadas[3]),
            east: Number(coordenadas[0]),
            west: Number(coordenadas[2])
          };
          document.ant = "rectangulo";
          drawRectangle(bounds);
          break;
        case 4: //point
          lat_p = Number(response['data'][0]['lat']);
          lon_p = Number(response['data'][0]['lon']);
          document.city = response['data'][0]['city'];
          document.state = response['data'][0]['state'];
          document.country = response['data'][0]['country'];
          document.place = document.city + "," + document.state + "," + document.country;
          addCoorToPoli(lat_p,lon_p);
          document.ant = "nombre";
          break;
        default:
      }
      toResults();

    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

/**
* CAMBIA EL FILTRO DE BUSQUEDA
*/
function mostrarImgs(filter){
  var $radios = $('input:radio[name=radiosResultados]');
  $radios.filter('[value='+filter+']').prop('checked', true);
  toResults();
}

/*
* MUESTRA UNA IMAGEN EN UN MODAL
*/
function showImage(item,rightP=false,idrecomendacion=-1){
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Images.php',
    dataType: 'json',
    data    : {action:'view_image',image:item,rightP:rightP,idrecomendacion:idrecomendacion},
    success : function(response) {
      console.log(response);
      $('#imagepreview').attr('src', 'resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/'+response[1]+'.jpg'); // here asign the image to the modal when the user click the enlarge link
      $('#imagepreview').attr('data-big', 'resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/'+response[1]+'.jpg'); // here asign the image to the modal when the user click the enlarge link
      $('#imagepreview').attr('height','500px');
      $('#imagemodal').modal('show'); // imagemodal is the id attribute assigned to the bootstrap modal, then i use the show function
      $("#txtWhereIs").html("<strong>Centro de la imágen en:</strong> ");
      $("#imagepreview").mlens({
          imgSrc: $("#imagepreview").attr("data-big"),   // path of the hi-res version of the image
          lensShape: "circle",                // shape of the lens (circle/square)
          lensSize: 180,                  // size of the lens (in px)
          borderSize: 4,                  // size of the lens border (in px)
          borderColor: "#fff",                // color of the lens border (#hex)
          borderRadius: 0,                // border radius (optional, only if the shape is square)
          zoomLevel: 3, 
          imgOverlay: $("#imagepreview").attr("data-overlay"), // path of the overlay image (optional)
      });
      if(response['city'] != null){
        $("#txtWhereIs").append(response['city']);
      }

      if(response['state'] != null){
        $("#txtWhereIs").append(", "+response['state']);
      }

      if(response['country'] != null){
        $("#txtWhereIs").append(", "+response['country']);
      }

    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

function getDataPolygon(year,month){
  var satelites = getSats();
  if(document.place.length > 0){
    console.log("entro1");
    data = {satelites:satelites,year:year,
            month:month,lat:place_coors['lat'],lon:place_coors['lon'],
            state:document.state,country:document.country,
            city:document.city,action:"get_images_date_point"};
  }else{
    console.log("entro");
    radio = document.ant == "circulo" ? document.shape.getRadius() : 0;
    coorsJson = getCoors();
    data = {satelites:satelites,
      year:year,month:month,
      result:coorsJson,shape:document.ant,
      radio:radio,action:"get_images_date_shape"};
  }
  return data;
}

/**
* MUESTRA TODAS LAS IMAGENES EN EL MAPA DE UN POLIGONO
*/
function polygonImagesToMap(elemento,year,month,tipo,satelite,rightP=false,idrecomendacion){
  var data = getDataPolygon(year,month);
  if(rightP){
    data.rightP = true;
    data.action = "get_images_date_shape"; 
    data.idrecomendacion = idrecomendacion;
  }
  data["clic"] = "view_image_on_map_poly";
  data.satelites = [satelite];
  
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Images.php',
    dataType: 'json',
    data    : data,
    success : function(response) {
      var i = 0;
      if(tipo == "poligono"){
        response.forEach(function(item,index){
          polygonToMap(elemento,item["hash_name"],"view_polygon_poly");
        });
      }else{
        response.forEach(function(item,index){
          imageToMap(elemento,item["hash_name"],"view_image_on_map_poly");
        });
      }
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}
/*
* MUESTRA LAS IMAGENES EN UN POLIGONO
*/
function showImagesPolygon(year,month,satelite,rightP=false,idrecomendacion=-1){

  var satelites = [satelite];
  data = {};
  if(document.place.length > 0){
    data = {satelites:satelites,year:year,month:month,lat:place_coors['lat'],lon:place_coors['lon'],state:document.state,country:document.country,city:document.city,action:"get_images_date_point"};
  }else{
    radio = document.ant == "circulo" ? document.shape.getRadius() : 0;
    data = {satelites:satelites,year:year,month:month,result:getCoors(),shape:document.ant,radio:radio,action:"get_images_date_shape"};
  }

  if(rightP){
    data.action = "get_images_date_shape";
    data.rightP = rightP;
    data.idrecomendacion = idrecomendacion;
  }
  data.clic = "gallery_poly";
  console.log(data);
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Images.php',
    dataType: 'json',
    data    :  data,
    success : function(response) {
      var i = 0;
      $("#divgaleria").html();
      response.forEach(function(item,index){
        if(i == 0){
          $("#divgaleria").html("<div class='item active'><center><img height='500px' src='resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/"+item['nombre']+".jpg' alt='item"+i+"'></center><div class='carousel-caption textonimage infoimage'><h3>"+item['nombre']+"</h3><h5>Path: "+item['path']+", Row: "+item['row']+".</h5>"+(i+1)+" de "+response.length+"</div></div>");
        }else{
          $("#divgaleria").append("<div class='item'><center><img height='500px' src='resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/"+item['nombre']+".jpg' alt='item"+i+"'></center><div class='carousel-caption textonimage infoimage'><h3>"+item['nombre']+"</h3><h5>Path: "+item['path']+", Row: "+item['row']+".</h5>"+(i+1)+" de "+response.length+"</div></div>");
        }
        i+=1;
      });
      $('#gallerymodal').modal('show');

    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

/*
* AGREGA LAS IMAGENES DE UN POLIGONO
*/
function addToCarPolygon(){
  console.log(arguments);
  satelite = arguments[0][4];
  action = arguments[0][3];
  year = arguments[0][1];
  month = arguments[0][2];
  rightP = arguments[0][5];
  idrecomendacion = arguments[0][6];
  console.log(rightP);
  idbutton = year+month+satelite;
  if(action == "remove"){
    updateCarSession(idbutton,action);
    $("#btn"+idbutton).html("<button title='Agregar a descargas' type='button'  onclick='checkSession(\"addToCarPolygon\",\""+year+"\",\""+month+"\",\"add\",\""+satelite+"\")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span>Agregar imágenes</button>");
  }else{
    var data = getDataPolygon(year,month);
    data.clic = "download_poly";
    if(rightP){
      data.action = "get_images_date_shape";
      data.rightP = true;
      data.idrecomendacion = idrecomendacion;
    }
    data.satelites = [satelite];
    console.log(data);
    $.ajax({
      type    : 'POST',
      url     : 'includes/controladores/controller.Images.php',
      dataType: 'json',
      data    : data,
      success : function(response) {
        aux = [];
        response.forEach(function(item,index){
          id = item['nombre']
          aux.push({id:id,opciones:['jpg','meta']});
        });
        aux = {imgs:aux,folder:"polygon_"+idbutton,isfolder:true,type:"polygon",month:month,year:year,id:idbutton};
        $("#btn"+idbutton).html("<button title='Agregar a descargas' type='button'  onclick='checkSession(\"addToCarPolygon\",\""+year+"\",\""+month+"\",\"remove\",\""+satelite+"\")' class='btn btn-danger btn-xs'>Eliminar</button>");
        updateCarSession(aux,action);
      },error: function(data){ //se lanza cuando ocurre un error
        console.log(data.responseText);
      }
    });
  }
}

/**
* AGREGA LAS IMAGENES DE UN SOLAPAMIENTO
*/
function addToCarOverleap(id,path,row,satelite,action){
  action = arguments[0][5];
  satelite = arguments[0][4];
  row = arguments[0][3];
  path = arguments[0][2];
  id = arguments[0][1];
  k = path+"_"+row+"_"+satelite;
  if(action == "remove"){
    updateCarSession(k,action);
    $("#btn"+k).html("<button title='Agregar a descargas' type='button'  onclick='checkSession(\"addToCarOverleap\",\""+id+"\",\""+path+"\",\""+row+"\",\""+satelite+"\",\"add\")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span>Agregar imágenes</button>");
  }else{
    $.ajax({
      type    : 'POST',
      url     : 'includes/controladores/controller.Images.php',
      dataType: 'json',
      data    : {satelite:satelite,path:path,row:row,action:"get_in_path_row",clic:"download_overlap"},
      success : function(response) {
        aux = [];
        response.forEach(function(item,index){
          id = item['nombre'];
          aux.push({id:id,opciones:['jpg','meta']});
        });
        aux = {imgs:aux,folder:"overlaps_"+k,isfolder:true,type:"overleap",path:path,row:row,id:k};
        updateCarSession(aux,action);
        $("#btn"+k).html("<button title='Agregar a descargas' type='button'  onclick='checkSession(\"addToCarOverleap\",\""+id+"\",\""+path+"\",\""+row+"\",\""+satelite+"\",\"remove\")' class='btn btn-danger btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span>Eliminar</button>");
      },error: function(data){ //se lanza cuando ocurre un error
        console.log(data.responseText);
      }
    });
  }
}

/*
* MUESTRA LAS IMAGENES DE UN SOLAPAMIENTO
*/
function showImagesGroup(path,row,satelite,rightP=0,idrecomendacion=-1){

  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Images.php',
    dataType: 'json',
    data    : {satelite:satelite,path:path,row:row,action:"get_in_path_row",idrecomendacion:idrecomendacion,clic:"gallery_overlap",rightP:rightP},
    success : function(response) {
      var i = 0;
      response.forEach(function(item,index){
        if(i == 0){
          $("#divgaleria").html("<div class='item active'><center><img height='500px' src='resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/"+item['nombre']+".jpg' alt='item"+i+"'></center><div class='carousel-caption textonimage infoimage'><h3>"+item['nombre']+"</h3><h5>"+item['date']+".</h5>"+(i+1)+" de "+response.length+"</div>            </div>");
        }else{
          $("#divgaleria").append("<div class='item'><center><img height='500px' src='resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/"+item['nombre']+".jpg' alt='item"+i+"'></center><div class='carousel-caption textonimage infoimage'><h3>"+item['nombre']+"</h3><h5>"+item['date']+".</h5>"+(i+1)+" de "+response.length+"</div>            </div>");
        }
        i+=1;
      });
      $('#gallerymodal').modal('show');
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
  //var height = $(document).height();
}

/**
* REMUEVE TODAS LAS IMAGENES DEL MAPA
*/
function removeImgs(){
  for (var key in imgsMaps_agregados) {
    imgsMaps_agregados[key].setMap(null);
    delete imgsMaps_agregados[key];
  }
}

/**
* MUESTRA TODAS LAS IMÁGENES DE UN AÑO
*/
function showImagesOfYear(year,month){
  removeImgs();
  document.year = year;
  document.month = month;
  document.band = true;
  getResults(0);


  var imgs = document.imagenes.filter(img => Number(img.yyyy) == year && Number(img.mmmm) == month);
  imgs.forEach(function(item,index){
    imageToMap(null,item['hash_name'],"view_image_on_map_poly");
  });
}

//Convierte la primer letra de un cadena a Mayusculas
function capitalizeFirstLetter(string) {
  if(typeof string == "string"){
    return string.charAt(0).toUpperCase() + string.slice(1);
  }
  return string;
}

/**
* AGREGA TODAS LAS IMAGENES DE UN MES Y AÑO A LA COLA DE 
* DESCARGAS
*/
function addAllMonthYear(action){
  year = document.year;
  month = document.month;
  var imgs = document.imagenes.filter(img => Number(img.yyyy) == year && Number(img.mmmm) == month);
  console.log(action);
  if(action == "add"){
    imgs.forEach(function(item,index){
      id = item['nombre'];
      var opciones = ["meta","jpg"];
      item = {id:id,opciones:opciones,isfolder:false,type:"single"};
      $("#btn"+id).html("<button title='Eliminar de las descargas' type='button'  onclick='checkSession(\"addToCar\",\""+id+"\",\"remove\")' class='btn btn-danger btn-xs'>Eliminar</button>");
      updateCarSession(item,"add");
    });
    $("#btnAddAll").html('<a title="Remover imágenes de la descarga" onclick="addAllMonthYear(\'remove\')" ><span class="glyphicon glyphicon-minus" aria-hidden="true"></span></a>');
  }else{
    imgs.forEach(function(item,index){
      id = item['nombre'];
      $("#btn"+id).html("<button title='Agregar a descargas' type='button'  onclick='checkSession(\"addToCar\",\""+id+"\",\"add\")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span></button>");
      //console.log(item);
      updateCarSession(id,"remove");
    });
    $("#btnAddAll").html('<a title="Agregar todas las imágenes a descarga" onclick="addAllMonthYear(\'add\')" ><span class="glyphicon glyphicon-plus" aria-hidden="true"></span></a>');
  }
}

/*
* MUESTRA TODAS LAS IMAGENES EN EL MAPA
*/
function showAllOnMap(data){
  data.onlynames = 1;
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Images.php',
    dataType: 'json',
    data    : data,
    success : function(response) {
      min_date = Number(response[0]['yyyy']);
      max_date = Number(response[response.length-1]['yyyy']);
      str = '<div  class="dropdown dropdown2"><a class=" dropdown-toggle" id="menu2" href="javascript:void(0);" type="button" data-toggle="dropdown"> <span class="glyphicon glyphicon-calendar" aria-hidden="true"></span></a> <ul  class="dropdown-menu" role="menu" aria-labelledby="menu2"></li><strong>&nbsp;&nbsp;&nbsp;Año del mosaico</strong> ';
      for(i=min_date;i<=max_date;i++){
        aux = response.filter(img => Number(img.yyyy) == i);
        if(aux.length > 0){
          //str += '<li role="presentation"><a role="menuitem" tabindex="-1" href="#" onclick="shonImagesOfYear('+i+')">'+i+'</a></li>';
          str += '<li class="dropdown-submenu"><a class="test" tabindex="-1" href="#">'+i+'<span class="caret"></span></a><ul class="dropdown-menu">';
          min_month = Number(aux[0]['mmmm']);
          max_month = Number(aux[aux.length-1]['mmmm']);
          for(j=min_month;j<=max_month;j++){
            aux2 = aux.filter(img => Number(img.mmmm) == j);
            if(aux2.length > 0){
              str += '<li><a tabindex="-1" onclick="showImagesOfYear('+i+','+j+')" href="#">'+MONTHS[j]+'</a></li>';
            }
          }
          str += '</ul></li>';
        }
      }
      str += ' </ul>  </div> <span id="btnAddAll"><a title="Agregar todas las imágenes a descarga" onclick="addAllMonthYear(\'add\')" ><span class="glyphicon glyphicon-plus" aria-hidden="true"></span></a><span>';
      $("#dropyears").html(str);
      document.imagenes = response;
      showImagesOfYear(min_date,response[0]['mmmm']);
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

// This function starts the timer
function startTimer(){
  clearInterval(document.timer);
  centesimas = 0;
  segundos = 0;
  minutos = 0;
  horas = 0;
  document.timer = setInterval(cronometro, 10);
}

function sesionExpirada(){
  $("#modExpirado").modal('show');
}

function cronometro () {
  if (centesimas < 99) {
    centesimas++;
  }
  if (centesimas == 99) {
    centesimas = -1;
  }
  if (centesimas == 0) {
    segundos ++;
  }
  if (segundos == 59) {
    segundos = -1;
  }
  if ( (centesimas == 0)&&(segundos == 0) ) {
    minutos++;
  }
  if (minutos == 59) {
    sesionExpirada();
  }
}

/*** DASHBOARD FUNCTIONS ****/

/*
CARGA LAS BÚSQUEDAS QUE HA REALIZADO UN USUARIO
*/
function cargarBusquedas(page){
  $.ajax({
    type    : 'POST',
    url     : 'includes/show_busquedas.php',
    data    : {page:page},
    success : function(response) {
      $("#divBusquedas").html(response);
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

/**
* MUESTRA EL CONTENIDO DEL DASHBOARD DEPENDIENDO EN QUE OPCIÓN SE DE CLIC
*/
function show(file){
  $.ajax({
    type    : 'POST',
    url     : 'includes/'+file+'.php',
    success : function(response) {
      $("#divcontenidodash").html(response);
      if(file == "preferences"){
        initMap();
        getUserUbication();
      }else if(file == "userloc"){
        initMap();
        getClusters();
      }else if(file == "stats"){
        loadCharts();
      }
      $("#dashoptions").find('li').each(function(){
        if($(this).hasClass("itemactive")){
          $(this).removeClass("itemactive")
        }
      });
      $("#li"+file).addClass("itemactive");
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}


/**
* OBTIENE LOS CLUSTERS GENERADOS CON EL ALGORITMO
*/
function getClusters(){
  var colors = ["red","blue","green","orange","purple"];
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Recomendations.php',
    dataType: 'json',
    data    : {action:'get_clusters'},
    success : function(response) {
      console.log(response);
      var coors,i=0;
      response.forEach(function(item,index){
        console.log("------------"+item['id']+"------------");
        item['elements'].forEach(function(element,ei){
          console.log(element['username']);
          console.log(element['ratings']);
          coors = {lat:element['ratings'][0],lng:element['ratings'][1]};
          var marker = new google.maps.Marker({
            position: coors,
            map: document.map,
            title: 'User '+element['username'],
            icon: 'http://maps.google.com/mapfiles/ms/icons/'+colors[i]+'-dot.png'
          });

          var infowindow = new google.maps.InfoWindow({
            content: "<div><div><strong>"+element['username']+"</strong></div><div>Latitud = "+element['ratings'][0]+"<br>Longitud = "+element['ratings'][1]+"</div></div>"
          });

          marker.addListener('click', function() {
            infowindow.open(document.map, marker);
          });

        });
        i++;
      });
      /*response.forEach(function(value,index){
        console.log(value);
        //coors = {lat:,lng:};
      }); */
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

/**
* OBTIENE LA UBICACIÓN DEL USUARIO CON LA QUE SE REALIZAN LAS RECOMENDACIONES
*/
function getUserUbication(){
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Session.php',
    dataType: 'json',
    data    : {action:'get_ubication'},
    success : function(response) {
      document.ant = "circulo";
      document.coorsRecomendations = response;
      document.coorsRecomendationsAnt = response;
      addCircle(Number(response['lat']),Number(response['lon']),Number(response['radio']));
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

function changeRecomendationCircle(location){
  if(location != null){
    deleteAllCoord();
    addCircle(location.coords.latitude,location.coords.longitude,300000);
    document.coorsRecomendations = {"lat":location.coords.latitude,
                                    "lon":location.coords.longitude,
                                    "definedbyuser":true,"radio":300000};
  }
}

/**
* REGRESA LA LOCALIZACIÓN A LA INICIAL
*/
function resetLocation(){
  deleteAllCoord();
  if(document.coorsRecomendationsAnt != null){
    addCircle(Number(document.coorsRecomendationsAnt['lat']),
              Number(document.coorsRecomendationsAnt['lon']),
              Number(document.coorsRecomendationsAnt['radio']));
    document.coorsRecomendations = document.coorsRecomendationsAnt;
  }else{
    addCircle(Number(document.coorsRecomendations['lat']),
              Number(document.coorsRecomendations['lon']),
              Number(document.coorsRecomendations['radio']));
  }
}

/**
* LLAMA A OBTENER LA UBICACION ACTUAL
*/
function useCurrentLocation(){
  getLocation("changeRecomendationCircle");
}

/**
* GUARDA LA LOCALIZACION ESTABLECIDA POR EL USUARIO
*/
function saveLocation(){
  if(document.shape != null && document.coorsRecomendations != null){
    document.coorsRecomendations.action = 'save_location';
    //document.coorsRecomendations.lat = 
    document.coorsRecomendations.radio = document.shape.getRadius();
    $.ajax({
      type    : 'POST',
      url     : 'includes/controladores/controller.Session.php',
      dataType: 'json',
      data    : document.coorsRecomendations,
      success : function(response) {
        if(response.codigo == 0){
          notificarUsuario(response.mensaje,"success");
        }else{
          notificarUsuario(response.mensaje,"danger");
        }
      },error: function(data){ //se lanza cuando ocurre un error
        console.log(data.responseText);
      }
    });
  }
}

/**
* CARGA LAS GRAFICAS DE ESTADISTICAS DE USUARIO
*/
function loadCharts(){
  loadSearchesChart();
  loadSearchesWayChart();
  recommendationsChart("get_recommendations_imgs","divGivenRecommendations","Recommended images");
  recommendationsChart("get_recommendations_polys","divGivenRecommendationsPolys","Recommended polygons");
  recommendationsChart("get_recommendations_overlaps","divGivenRecommendationsOverlaps","Recommended overlaps");
}

function loadSearchesChart(){
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Logs.php',
    dataType: 'json',
    data    : {action:"get_searches_stats"},
    success : function(response) {
      var ctx = document.getElementById("divSearchesStats").getContext('2d');
      var labels = [];
      var data = [];

      response.forEach(function(item,index){
        labels.push(item[1]);
        data.push(item[0]);
      });

      var myPieChart = new Chart(ctx,{
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
                label: '# of Searches',
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255,99,132,1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
            }]
        },options: {
          title: {
              display: true,
              text: 'Formas utilizadas para realizar las búsquedas'
          } 
        }
      });
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

function loadSearchesWayChart(){
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Logs.php',
    dataType: 'json',
    data    : {action:"get_searches_ways_stats"},
    success : function(response) {
      var ctx = document.getElementById("divSearchesWay").getContext('2d');
      var labels = [];
      var data = [];

      response.forEach(function(item,index){
        labels.push(item[1]);
        data.push(item[0]);
      });

      var myPieChart = new Chart(ctx,{
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
                label: '# of Searches',
                data: data,
                backgroundColor: [
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
            }]
        },options: {
          title: {
              display: true,
              text: 'Tipos de búsquedas realizadas'
          } 
        }
      });
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

function recommendationsChart(action,div,title){
  $.ajax({
    type    : 'POST',
    url     : 'includes/controladores/controller.Logs.php',
    dataType: 'json',
    data    : {action:action},
    success : function(response) {
      var ctx = document.getElementById(div).getContext('2d');
      var labels = ["Recommended images","Clicked images"];
      var data = [response[0][1],response[0][0]];
      showBarGraph(labels,data,title,ctx);
    },error: function(data){ //se lanza cuando ocurre un error
      console.log(data.responseText);
    }
  });
}

function showBarGraph(labels,data,label,ctx){
  new Chart(ctx,{
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
            label: label,
            data: data,
            backgroundColor: [
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)'
            ],
            borderColor: [
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)'
            ],
            "borderWidth":1
        }]
    },"options":{
        "scales":{
          "yAxes":[{
            "ticks":{
              "beginAtZero": true
            }
          }]
        }
      }
  });
}
