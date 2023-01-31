/* FUNCTIONES JS PARA EL MANEJO DEL CLIENTE Y LA COMUNICACIÓN CON EL SERVIDOR
/**/
//VARIABLES GLOBALES
var LOG_NOTIF = {}
var ID_NOTIF=1
var DATA_WORKFLOW_EXT = null; //file extension
var DATA_WORKFLOW_STATUS = false;
var DATA_WORKFLOW_DESC;
var REPORTE={}; 
var startTimeMS = 0; // EPOCH Time of event count started
var timerId; // Current timer handler
var timerStep = 5000; // Time beetwen calls
var polys_agregados = []; //POLIGONOS DE LAS IMAGENES MOSTRADOS EN EL MAPA
var imgsMaps_agregados = []; //IMAGENES MOSTRADAS EN EL MAPA
var markers = []; //MARCADORES AGREGDOS EN EL MAPA
var coors = []; //COORDENADAS AGREGADAS EN EL MAPA
var show_in_degrees = false; //MOSTRAR EN DECIMAL O GRADOS
var place = ""; //LUGAR BUSCADO (LOCALIZACION DE LUGAR)
var place_coors = []; //COORDENADAS DE UN LUGAR SELECCIONADO POR LA LOCALIZACION DE PUNTOS
var lang;
var filtro = "todas"; //GUARGA LO QUE SE VA  A MOSTRAR (todas,poligonos,solapamientos)
const FILTROS = { todas: 1, poligonos: 2, solapamientos: 3 };
var MONTHS = ["Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre"
]
var GlobalMarkers = new Object();
var GlobalColors = [];
var GlobalColorTopoformas = {}
var GlobalColorHidroregiones = {}

var GlobalImages = [];
var GlobalImagesSil = [];
var GlobalImagesDate = []
var Etiquetas_Colores = [];
var topoform_report = [];
var clima_report = [];

//temporizador
var centesimas = 0;
var segundos = 0;
var minutos = 0;
var horas = 0;
var htmlAnt;

var SERVER_URL = "http://localhost:8080";
//var METEO_IP = "http://148.247.201.211:5000"
//var METEO_IP = "http://localhost:8080" //para las imagenes
//var METEO_IP = "http://localhost:8080/AEM-Eris/meteo"

//Fecha maxima segun los datos
//1 mes para EMAS
//2 meses para MERRA

var fecha_max;
$('input[type=radio][name=font_study]').change(function() {
    numFuentes()
    var auxArray =  $('input[type=radio][name=font_study]:checked').val().split(",")
    var today = new Date();
    var dd = "01";
    var yyyy = 2019;
    var mm = 1;
    //opciones emas
    console.log(auxArray[0])
    if (auxArray[0] == "EMASMAX") {
        yyyy = today.getFullYear();
        mm = today.getMonth() + 1;

    }
    //opcione para los selecciones o merra
    if (auxArray[1] == "MERRA" || auxArray[0] == "MERRA") {
        if (today.getMonth() == 0) {
            //es enero
            yyyy = today.getFullYear() - 1;
            mm = 12;
        } else {
            console.log("merra")
            yyyy = today.getFullYear();
            mm = today.getMonth() - 1;
        }
    }
    if (mm < 10) {
        mm = '0' + mm;
    }
    if (auxArray.length != 0) {
        fecha_max = dd + '/' + mm + '/' + yyyy;
        console.log("fwehca - " + fecha_max);
        $("#datetimepicker1").data('DateTimePicker').date(null);
        $("#datetimepicker2").data('DateTimePicker').date(null);
        $("#datetimepicker2").data('DateTimePicker').maxDate(fecha_max);
    }


});


function Descargar_REPORTE(repo){
    for (x=0;x<repo.length;x++){
        reporte2download = repo[x]
        DataToSave = REPORTE[reporte2download]
        CSVheaders = Object.keys(DataToSave[0]);
        exportCSVFile(CSVheaders, DataToSave, "REPORTE_"+reporte2download);
    }
}

$(document).ready(function() {
    
    verifySession()

    document.dataAAS = {};
    document.polygons_states = [];
    document.polygons_reg = [];
    document.polygons_mun = [];
    document.polygons_eco = [];

    document.marcadoresClima = [];
    document.height = $(window).height(); //ALTURA MAXIMA DE LA VENTANA
    document.place = "";
    document.historico = []
    //checkSession();
    var gets = get_variables();
    window.busqueda = 0;

    /**
     * OBTIENE EL LENGUAJE DE LA URL O EL NAVEGADOR
     */
    lang = "es";
    if (gets.hasOwnProperty("lang")) {
        lang = gets['lang'];
        if (!(lang == "es" || lang == "en")) {
            lang = (navigator.language || navigator.userLanguage).substring(0, 2);
        }
    } else {
        lang = (navigator.language || navigator.userLanguage).substring(0, 2);
    }
    //console.log(lang);
    loadTexts(lang);

    //OBTIENE EL ID DE LA BUSQUEDA SI ES PASADO POR GET
    if (gets.hasOwnProperty('busqueda')) {
        if (Object.keys(gets).length == 1) {
            if (gets['busqueda'].length > 1) {
                window.busqueda = gets['busqueda'];
            }
        }
    }
    
    /// DROPDOWN
    $('.dropdown-submenu a.test').on("click", function(e) {
        $(this).next('ul').toggle();
        e.stopPropagation();
        e.preventDefault();
    });


    /// FIN DE LA INICIALIZACION DEL CONTROL DE FECHA
    if (window.location.href.indexOf("element.php") == -1 && window.location.href.indexOf("user.php") == -1) {
        getLocation("initMap"); //geolacalización del usuario
    }




    // HACE EL CAMBIO DE DECIMALES A GRADOS Y VICEVERSA
    $("#btnConvert :input").change(function() {
        if (this.value == "decimales") {
            mostrarEnDecimales();
            $('#btnAddNew').attr('data-target', '#modNewDec');
        } else {
            mostrarEnGrados();
            $('#btnAddNew').attr('data-target', '#modNewGrad');
        }
    });




    /* CHANGE LOG IN TO SIGN UP */
    $("#logindiv").on('change', '#btnchangelogin :input', function() {
        //console.log(this.value);
        if (this.value == "signup") {
            $("#frmlogin").addClass("invisible animation");
            $("#frmsignup").removeClass("invisible");
        } else {
            $("#frmlogin").removeClass("invisible animation");
            $("#frmsignup").addClass("invisible");
        }
    });


    $("#btnModalReloadPage").click(function(event) {
        event.preventDefault();
        logout();
    });

    // --------------------- LOG IN --------------------
  

    //LOG IN
    //$("#logindiv").on('submit', '#frmlogin', function(event) {
    //    event.preventDefault();
    //    //console.log("entro");
    //    var formData = new FormData($("#frmlogin")[0]);
    //    formData.append("action", "login");
    //    if (document.position != null) {
    //        formData.append("lat", document.position.coords.latitude);
    //        formData.append("lon", document.position.coords.longitude);
    //        formData.append("locationByIp", 0);
    //    }
    //    $.ajax({ //OBTIENE LA IP Y DATOS DE LOCALIZACION COMPLEMENTARIOS
    //        url: "http://ipinfo.io",
    //        dataType: "jsonp",
    //        success: function(response) {
    //            formData.append("ip", response.ip);
    //            if (document.position == null) {
    //                latlng = response.loc.split(",");
    //                formData.append("lat", latlng[0]);
    //                formData.append("lon", latlng[1]);
    //                formData.append("locationByIp", 1);
    //            }
    //            login(formData);
    //        },
    //        error: function(response) {
    //            formData.append("ip", "-");
    //            login(formData);
    //        }
    //    });
    //});

    //SIGN UP
    //$("#logindiv").on('submit', '#frmsignup', function(event) {
    //    event.preventDefault();
    //    var formData = new FormData($("#frmsignup")[0]);
    //    formData.append("action", "signup")
    //        //formData
    //    $.ajax({
    //        url: 'includes/controladores/controller.Session.php', //Server script to process data
    //        type: 'POST',
    //        data: formData,
    //        dataType: 'json',
    //        contentType: false,
    //        processData: false,
    //        beforeSend: function() {},
    //        success: function(data) { //muestra la respuesta
    //            if (data['codigo'] == 0) {
    //                $("#mensaje_signup").html('<div class="alert alert-success">' + data['mensaje'] + '</div>');
    //            } else {
    //                $("#mensaje_signup").html('<div class="alert alert-danger">' + data['mensaje'] + '</div>');
    //            }
    //        },
    //        error: function(data) { //se lanza cuando ocurre un error
    //            console.log(data.responseText);
    //        }
    //    });
    //});

    //MUESTRA EL MODAL DE LOGEO
    $("#divLogin").click(function() {
        $('#loginmodal').modal('show');
    });

    //MANDA A LLAMAR A CERRAR LA SESIONES
    $("#btnLogout").click(function() {
        deleteAllCookies();
        window.location = "includes/controladores/controller.Session.php";
    });

    //AGREGA UNA IMAGEN PARA DESCARGARLA
    $("#btnAddImageToDownload").click(function(e) {
        id = $("#spanImagen").html();
        var opciones = []
        $('.choose:checked').each(
            function() {
                opciones.push($(this).val());
            }
        );
        item = { id: id, opciones: opciones, isfolder: false, type: "single" };
        $("#btn" + id).html("<button title='Eliminar de las descargas'   type='button'  onclick='checkSession(\"addToCar\",\"" + id + "\",\"remove\")' class='btn btn-danger btn-xs'>Eliminar</button>");
        $("#modChoose").modal('hide');
        updateCarSession(item, "add");
    });

    document.place = "";

    //PARA QUE NO SE CIERRE EL MODAL HASTA QUE NO SE INICIE SESION
    $('#loginmodal').on('hidden.bs.modal', function() {
        checkSession();
    });

    $("#logindiv").on('click', '#btnResetPass', function(e) {
        e.preventDefault();
        htmlAnt = $("#logindiv").html();

        $("#logindiv").html("<h4>" + document.lngarr['passrecup'] + "</h4><div>" +
            "<p>" + document.lngarr['typeemail'] + "</p>" +
            "<form id='frmReset'><fieldset><input id='txtEmailRec' type='email' name='email' placeholder='" +
            document.lngarr['email'] + "' required/></fieldset><div id='divErrGetEm'></div><input type='submit' value='" + document.lngarr['search'] + "'/><a id='btnCancelRec' onclick='backLogin()'>" + document.lngarr['cancel'] + "</a></form><br></div>");
    });

    /*
     * VERIFICA SI EL EMAIL EXISTE PARA LA RECUPERACIÓN DE CONTRASEÑA
     */
    //$("#logindiv").on("submit", "#frmReset", function(e) {
    //    e.preventDefault();
    //    var email = $("#txtEmailRec").val();
    //    //console.log(username);
    //    $.ajax({
    //        url: 'includes/controladores/controller.Session.php', //Server script to process data
    //        type: 'POST',
    //        data: { email: email, action: "checkmail" },
    //        dataType: 'json',
    //        beforeSend: function() {},
    //        success: function(data) { //muestra la respuesta
    //            //console.log(data);
    //            if (data['codigo'] == 1) {
    //                $("#divErrGetEm").html('<div class="alert alert-success">' + document.lngarr['emailexists'] + '</div>');
    //                sendEmailPass(email, data['hash'], data['id']);
    //            } else {
    //                $("#divErrGetEm").html('<div class="alert alert-danger">' + document.lngarr['emailnotexists'] + '</div>');
    //            }
    //        },
    //        error: function(data) { //se lanza cuando ocurre un error
    //            console.log(data.responseText);
    //        }
    //    });
    //});

    $("#frmpasswordchange").submit(function(e) {
        e.preventDefault();
        var pass1 = $("#txtpass").val();
        var pass2 = $("#txtconfpass").val();
        var user = $("#txtUser").val();
        if (pass1 != pass2) {
            $("#diverror").html('<div class="alert alert-danger">' + document.lngarr["nopassmatch"] + '</div>');
        } else {
            $.ajax({
                url: 'includes/controladores/controller.Session.php', //Server script to process data
                type: 'POST',
                data: { password: pass1, action: "changepass", user: user },
                dataType: 'json',
                beforeSend: function() {},
                success: function(data) { //muestra la respuesta
                    if (data['keyuser'] != null) {
                        $("#diverror").html('<div class="alert alert-success">' + document.lngarr["passchanged"] + '</div>');
                    }
                },
                error: function(data) { //se lanza cuando ocurre un error
                    console.log(data.responseText);
                }
            });
        }
    });


});



function validate_date_selection(){
    selection = $('#slproductos').val();

    if (selection == "historico") {

        console.log("entro");
        $('#slDiv').show();
        $('#slDiv2').show();
        $("#divDates").hide();
        $("#options1").hide();
        $("#options2").show();
        $("#options_differential").hide();
        $("#options_cluster").hide();
        $("#options_cluster_historico").show();
        $("#options_filters").show();
        $("#results").show();
        $("#results2").show();
        $("#coordinates").show()
            //descarga de datos
        $("#addAll").show();
        $("#DropImages").hide();

        /// espaciales



        //$('#modClust').modal('show');
    } else if (selection == "actual") {

        $('#slDiv').hide();
        $('#slDiv2').show();
        $("#divDates").show();
        $("#options1").hide();
        $("#options2").show();
        $("#options_differential").show();
        $("#options_cluster").show();
        $("#options_cluster_historico").hide();
        $("#options_filters").show();
        $("#results").show();
        $("#results2").show();
        //descarga de datos
        $("#addAll").show();
        $("#DropImages").show();
        $("#coordinates").show()

    } else {
        $('#slDiv2').hide();
        //$('#slDiv').show();
        //$("#divDates").show();
        $("#options1").hide();
        $("#options2").show();

    }
}


function convertToCSV(objArray) {
    var array = typeof objArray != 'object' ? JSON.parse(objArray) : objArray;
    var str = '';

    for (var i = 0; i < array.length; i++) {
        var line = '';
        for (var index in array[i]) {
            if (line != '') line += ','

            line += array[i][index];
        }

        str += line + '\r\n';
    }

    return str;
}

function exportCSVFile(headers, items, fileTitle) {
    if (headers) {
        items.unshift(headers);
    }

    // Convert Object to JSON
    var jsonObject = JSON.stringify(items);

    var csv = this.convertToCSV(jsonObject);

    var exportedFilenmae = fileTitle + '.csv' || 'export.csv';

    var blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    if (navigator.msSaveBlob) { // IE 10+
        navigator.msSaveBlob(blob, exportedFilenmae);
    } else {
        var link = document.createElement("a");
        if (link.download !== undefined) { // feature detection
            // Browsers that support HTML5 download attribute
            var url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", exportedFilenmae);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
}

function exportTXTFile(items, fileTitle) {

    // Convert Object to JSON
    var jsonObject = JSON.stringify(items, null, 4);

    var exportedFilenmae = fileTitle + '.json' || 'export.txt';

    var blob = new Blob([jsonObject], { type: 'text/ json;charset=utf-8;' });
    if (navigator.msSaveBlob) { // IE 10+
        navigator.msSaveBlob(blob, exportedFilenmae);
    } else {
        var link = document.createElement("a");
        if (link.download !== undefined) { // feature detection
            // Browsers that support HTML5 download attribute
            var url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", exportedFilenmae);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
}

function exportBINFile(b64Data, fileTitle,preprocessing=true,sliceSize=512) {
    byteArrays = [];
    if (preprocessing){
        const byteCharacters = atob(b64Data);

      
        for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
          const slice = byteCharacters.slice(offset, offset + sliceSize);
      
          const byteNumbers = new Array(slice.length);
          for (let i = 0; i < slice.length; i++) {
            byteNumbers[i] = slice.charCodeAt(i);
          }
      
          const byteArray = new Uint8Array(byteNumbers);
          byteArrays.push(byteArray);
        }
    }
    else{
        byteArrays = [b64Data]
    }

    var exportedFilenmae = fileTitle ;

    var blob = new Blob(byteArrays, { type: 'octet/stream' });
    if (navigator.msSaveBlob) { // IE 10+
        navigator.msSaveBlob(blob, exportedFilenmae);
    } else {
        var link = document.createElement("a");
        if (link.download !== undefined) { // feature detection
            // Browsers that support HTML5 download attribute
            var url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", exportedFilenmae);
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }
}

function getNotificaciones() {
    $.ajax({
        url: 'includes/controladores/controller.Element.php', //Server script to process data
        type: 'POST',
        data: { action: "get_news_elem" },
        dataType: 'json',
        beforeSend: function() {},
        success: function(data) { //muestra la respuesta
            console.log(data);
            $("#lblNumberNews").html(data.length);
            for (var i = 0; i < data.length; i++) {
                item = data[i];
                $("#bodynots").append("<div><strong>New file</strong><br>" + item["namefile"] + "<br>" + item["created_at"] + "<hr style='border-top: 1px solid #8c8b8b'></div>")
            }
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}


/*
 * ENVIA EL EMAIL DE RECUPERACIÓN DE CONTRASEÑA
 */
function sendEmailPass(email, hash, id) {
    $.ajax({
        url: 'includes/controladores/controller.Session.php', //Server script to process data
        type: 'POST',
        data: { email: email, action: "sendmailpass", hash: hash, id: id },
        dataType: 'json',
        beforeSend: function() {},
        success: function(data) { //muestra la respuesta
            console.log(data);
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

function backLogin() {
    $("#logindiv").html(htmlAnt);
}

/**
 * VALIDA LAS FECHAS
 */
function validarFecha(picker, e) {
    /**
    * VALIDA LAS FECHAS

    if (picker == 1) {
        $("#datetimepicker2").data('DateTimePicker').minDate(e.date);
    } else if (picker == 2) {
        $("#datetimepicker1").data('DateTimePicker').maxDate(e.date);
    }
 */
}

/**
 * MUESTRA EL MODAL DEL INICIO DE SESION
 */
function showLoginModal() {
    $('#loginmodal').modal('show');
}

/**
 * INICIA LA SESION
 */
function login(data) {
    $.ajax({
        url: 'includes/controladores/controller.Session.php', //Server script to process data
        type: 'POST',
        data: data,
        dataType: 'json',
        contentType: false,
        processData: false,
        beforeSend: function() {},
        success: function(data) { //muestra la respuesta
            if (data['codigo'] == 0) {
                $("#mensaje_login").html('<div class="alert alert-success">' + data['mensaje'] + '</div>');
                location.href = "index.php?lang=" + lang;
            } else {
                $("#mensaje_login").html('<div class="alert alert-danger">' + data['mensaje'] + '</div>');
            }
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

/**
 * CIERRA LA SESION
 */
function logout() {
    console.log("LOGOUT");
    clearTimeout(timerId); // clear timer
    deleteAllCookies();
    window.location = "includes/controladores/controller.Session.php";
}

/**
 * MUESTRA LOS LUGARES EN BASE A LA BUSQUEDA REALIZADA
 */
function mostrarLugares() {
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({ 'address': $("#txtSearchText").val() }, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            this.lugares_obtenidos = results;
            content = "<table class='table table-striped'>  <thead><tr><th>#</th><th>Lugar</th><th>Latitud</th><th>Longitud</th></tr></thead><tbody>";
            for (var i = 0; i < results.length; i++) {
                content += "<tr><td>" + (i + 1) + "</td><td><a class='lugar' onclick='addPlaceToSearch(\"" + results[i].geometry.location.lat() + "\",\"" + results[i].geometry.location.lng() + "\",\"" + results[i].formatted_address + "\"," + i + ")'>" + results[i].formatted_address + "</a></td><td>" + results[i].geometry.location.lat().toFixed(5) + "</td><td>" + results[i].geometry.location.lng().toFixed(5) + "</td></tr>";
            }
            content += "</tbody></table>"
            $("#lugaresEncontrados").html(content);
        } else {
            console.log("Something got wrong " + status);
        }
    });
}

function addAllSearch() {
    var polysJson = toJSON(polys_agregados);
    var imgsJson = toJSON(imgsMaps_agregados);
    var satelites = getSats();
    var ischeck = $('#chproductos').is(":checked");
    var clima = $("#slproductos").val();
    console.log("xxx " + clima);
    var showproducts = ischeck ? 1 : 0;
    var data;
    var filtro = $('input[name=radiosResultados]:checked').val();
    var startDate = $("#datetimepicker1").data('DateTimePicker').date();
    var endDate = $("#datetimepicker2").data('DateTimePicker').date();


}

/**
 * CAMBIA A LA PESTAÑA DE RESULTADOS
 */
function toDesign() {
    $('#mytabs a[href="#xel-tab"]').tab('show');
    $('#tabs_show a[href="#designer"]').tab('show');
    return false;
}


/**
 * CAMBIA A LA PESTAÑA DE RESULTADOS
 */
function toResults() {
    cleanMap();
    console.log(Object.keys(this.coors).length);
    console.log(Object.keys(this.coors).length > 2);

    var clima = $("#slproductos").val();
    var esp = $("#slShape2").val();
    if (((clima == "historico" || clima == "actual") && Object.keys(this.coors).length > 2) || (esp == "regiones") || (esp == "estados")) {
        document.band = false;
        checkSession("getResults");
        if (filtro == "todas") {
            mostrar = $('input:radio[name=radiosResultados]:checked').val();
        }
        $('#mytabs a[href="#results-tab"]').tab('show');
        return true;
    }
    return false;
}

/*
 * establece las fechas en el selector
 */
function setDate(date1, date2) {
    if (moment(date1, "YYYY-MM-DD", true).isValid() && moment(date2, "YYYY-MM-DD", true).isValid()) {
        $("#datetimepicker1").data('DateTimePicker').date(moment(date1));
        $("#datetimepicker2").data('DateTimePicker').date(moment(date2));
    }
}

/**
 * VERIFICA SI UN SATELITE ESTA SELECCIONADO
 */
function isSatSelected() {
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
function get_variables() {
    var $_GET = {};
    document.location.search.replace(/\??(?:([^=]+)=([^&]*)&?)/g, function() {
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
function getLocation(strfunction) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(window[strfunction], function(error) {
            showError(error, strfunction);
        });
    } else {
        console.log("Geolocation is not supported by this browser.");
    }
}

/**
 * MANEJO DE ERRORES EN LA GEOLOCALIZACIÓN
 */
function showError(error, strfunction) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            notificarUsuario("No ha sido posible obtener la ubicación. El denego la solicitud.", "danger");
            console.log("User denied the request for Geolocation.");
            break;
        case error.POSITION_UNAVAILABLE:
            notificarUsuario("No ha sido posible obtener la ubicación.", "danger");
            console.log("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            notificarUsuario("Tiempo de solicitud de localización excedido.", "danger");
            console.log("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            notificarUsuario("Error desconocido. NO es posible obtener la ubicación.", "danger");
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
    if (mapDiv != null) {
        //INSTANCIA UN NUEVO OBJETO DE MAPA
        document.map = new google.maps.Map(mapDiv, {
            zoom: 5,
            minZoom: 6,
            center: { lat: 23.948089, lng: -102.514651 },
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
        if (position) { //CAMBIA LA POSICION DEL MAPA
            document.map.setCenter({ lat: position.coords.latitude, lng: position.coords.longitude });
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
    //if (window.location.href.indexOf("element.php") == -1 && window.location.href.indexOf("user.php") == -1) {
    //    if (window.busqueda == 0) {
    //        checkSession("cargar_cookies");
    //    } else if (window.busqueda.length > 0) {
    //        checkSession("loadSearch", busqueda);
    //    }
    //}
}

/**
 * FUNCION QUE CARGA EL ARCHIVO DE LENGUAJE
 */
function loadTexts(lang) {
    $.getJSON("resources/langs.json", function(json) {
        //console.log(json[lang]);
        document.lngarr = json[lang];
        MONTHS = document.lngarr['months'];
    });
}

/**
 * AGREGA UNA FORMA AL MAPA CUANDO SE HACE CLIC EN EL
 */
function agregar_forma(event) {
    switch (document.ant) {
        case "rectangulo":
            deleteAllCoord();
            var lat = event.latLng.lat();
            var lon = event.latLng.lng();
            var bounds = {
                north: lat + .5,
                south: lat,
                east: lon + .5,
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
            if (document.coorsRecomendations != null) {
                document.coorsRecomendations = {
                    definedbyuser: true,
                    lat: event.latLng.lat(),
                    lon: event.latLng.lng()
                };
            }

            addCircle(event.latLng.lat(), event.latLng.lng(), 0);
            break;
    }
}

/**
 * MUESTRA EL LUGAR SELECCIONADO EN EL MAPA
 */
function addPlaceToSearch(lat, lng, address, i) {
    document.country = this.lugares_obtenidos[i]['address_components'].filter(place => place.types.indexOf("country") > -1);
    document.country = (document.country.length > 0) ? document.country[0]["long_name"] : "";
    document.state = this.lugares_obtenidos[i]['address_components'].filter(place => place.types.indexOf("administrative_area_level_1") > -1);
    document.state = (document.state.length > 0) ? document.state[0]["long_name"] : "";
    document.city = this.lugares_obtenidos[i]['address_components'].filter(place => place.types.indexOf("locality") > -1);
    document.city = (document.city.length > 0) ? document.city[0]["long_name"] : "";
    var latlng = new google.maps.LatLng(lat, lng);
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
function addCircle(c_lat, c_lon, radius) {
    var center = { lat: c_lat, lng: c_lon };
    //CALCULA EL RADIO EN FUNCION DEL ZOOM DEL MAPA CUANDO ESTE ES CERO
    if (radius <= 0) {
        radius = Math.pow(2, (21 - document.map.getZoom()));
        document.radius = radius * 1128.497220 * 0.0027;
    } else {
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
function addRectangleToMap(bounds) {
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
    showCoorsInDiv(new google.maps.LatLng(
        document.shape.getBounds().getNorthEast().lat(),
        document.shape.getBounds().getSouthWest().lng()));
    showCoorsInDiv(new google.maps.LatLng(
        document.shape.getBounds().getSouthWest().lat(),
        document.shape.getBounds().getNorthEast().lng()));
}


/**
 * AGREGA UNA NUEVA COORDENADA AL POLIGONO
 */
function addCoorToPoli() {
    var latLng;
    if (arguments.length == 2) {
        latLng = new google.maps.LatLng(arguments[0], arguments[1]);
    } else if (arguments.length == 1) {
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
function mostrarEnDecimales() {
    show_in_degrees = false;
    if (path != null) {
        var childs = document.getElementById("coordinates").childNodes;
        for (i = 0; i < childs.length; i++) {
            document.getElementById("ch" + childs[i].id).innerHTML = coors[childs[i].id]['decimal']['lat'] + "," + coors[childs[i].id]['decimal']['lon'];
        }
    }
}

/**
 * MUESTRA LAS COORDENADAS EN GRADOS
 */
function mostrarEnGrados() {
    show_in_degrees = true;
    if (path != null) {
        var childs = document.getElementById("coordinates").childNodes;
        for (i = 0; i < childs.length; i++) {
            document.getElementById("ch" + childs[i].id).innerHTML = coors[childs[i].id]['grados']['lat'] + "," + coors[childs[i].id]['grados']['lon'];
        }
    }
}

/**
 * MUESTRA LAS COORDENADAS AGREGADAS EN UN DIV
 */
function showCoorsInDiv(latLng) {
    var n = Object.keys(this.coors).length;
    var key = "div" + n; //CLAVE PARA LOS ARREGLOS
    var aux = n + 1; //NUMERO DE OBJETOS EN EL ARRAY
    // Add a new marker at the new plotted point on the polyline.
    //GUARDA EL MARCADOR EN UN ARREGLO
    this.markers[key] = new google.maps.Marker({
        position: latLng,
        map: document.map
    });
    //GUARDA LAS COORDENADAS EN UN OBJETO
    coors[key] = { decimal: { lat: latLng.lat().toFixed(5), lon: latLng.lng().toFixed(5) }, grados: { lat: toDegrees(latLng.lat().toFixed(5), true), lon: toDegrees(latLng.lng().toFixed(5), false) } };

    //MUESTRA LAS COORDENADAS
    if (show_in_degrees) {
        if (aux == 1) {
            $("#coordinates").html("<div class='coords1' id='div" + n + "'><div class='divcoordenadas' id='chdiv" + n + "'>" + coors[key]['grados']['lat'] + " , " + coors[key]['grados']['lon'] + "</div> <div class='btndelete'><button type='button' class='btn btn-default btn-xs pull-right'  onclick=\"deleteCoord(" + n + ")\"><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button></div> </div>");
        } else if (aux % 2 == 0) {
            $("#coordinates").append("<div class='coords2' id='div" + n + "'><div class='divcoordenadas' id='chdiv" + n + "'>" + coors[key]['grados']['lat'] + " , " + coors[key]['grados']['lon'] + "</div> <div class='btndelete'><button type='button' class='btn btn-default btn-xs pull-right'  onclick=\"deleteCoord(" + n + ")\"><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button></div> </div>");
        } else {
            $("#coordinates").append("<div class='coords1' id='div" + n + "'><div class='divcoordenadas' id='chdiv" + n + "'>" + coors[key]['grados']['lat'] + " , " + coors[key]['grados']['lon'] + "</div> <div class='btndelete'><button type='button' class='btn btn-default btn-xs pull-right'  onclick=\"deleteCoord(" + n + ")\"><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button></div> </div>");
        }
    } else {
        if (aux == 1) {
            $("#coordinates").html("<div class='coords1' id='div" + n + "'><div class='divcoordenadas' id='chdiv" + n + "'>" + coors[key]['decimal']['lat'] + " , " + coors[key]['decimal']['lon'] + "</div> <div class='btndelete'><button type='button' class='btn btn-default btn-xs pull-right'  onclick=\"deleteCoord(" + n + ")\"><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button></div> </div>");
        } else if (aux % 2 == 0) {
            $("#coordinates").append("<div class='coords2' id='div" + n + "'><div class='divcoordenadas' id='chdiv" + n + "'>" + coors[key]['decimal']['lat'] + "," + coors[key]['decimal']['lon'] + "</div> <div class='btndelete'><button type='button' class='btn btn-default btn-xs pull-right'  onclick=\"deleteCoord(" + n + ")\"><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button></div> </div>");
        } else {
            $("#coordinates").append("<div class='coords1' id='div" + n + "'><div class='divcoordenadas' id='chdiv" + n + "'>" + coors[key]['decimal']['lat'] + "," + coors[key]['decimal']['lon'] + "</div> <div class='btndelete'><button type='button' class='btn btn-default btn-xs pull-right'  onclick=\"deleteCoord(" + n + ")\"><span class='glyphicon glyphicon-remove' aria-hidden='true'></span></button></div> </div>");
        }
    }
}

/**
 * ELIMINA UNA COORDENADA AGREGADA
 */
function deleteCoord(marker) {

    if (document.ant == "poligono") {
        markers["div" + marker].setMap(null);
        var i = 0;
        var childs = document.getElementById("coordinates").childNodes;
        for (i = 0; i < childs.length; i++) {
            if (childs[i].id == "div" + marker) {
                break;
            }
        }
        path.removeAt(i);
        delete this.coors["div" + marker];
        $("#div" + marker).remove();
        if (path.length == 0) {
            $("#coordinates").html('<div class="coords1">No se han agregado coordenadas.</div>');
        }
    } else {
        deleteAllCoord();
    }

}

//convierte las coordenadas a decimales
function toDecimal(grad, mins, segs, orien) {
    sign = (orien == "N" || orien == "E") ? 1 : -1;
    return (sign * (parseInt(grad) + parseInt(mins) / 60 + parseInt(segs) / 3600)).toFixed(5);
}

//convierte las coordenadas a grados
function toDegrees(decimal, lat) {
    ent = parseInt(decimal);

    sign = (lat) ? "N" : "E";
    if (ent < 0) {
        if (!lat) {
            sign = "W";
        } else {
            sign = "S";
        }
        ent *= -1;
        decimal *= -1;
    }
    dec = decimal - ent;
    seg = dec * 60;
    dec = seg - parseInt(seg);
    seg = parseInt(seg);

    return ent + "° " + seg + "\' " + (dec * 60).toFixed(3) + "\'\' " + sign;
}

//LIMPIA EL MAPA REMOVIENDO LOS POLIGONOS E IMAGENES QUE AGREGO EL USUARIO
function cleanMap() {
    //console.log(polys_agregados);
    for (var key in polys_agregados) {
        console.log(key);
        polygonToMap(null, key);
    }
    for (var key in this.imgsMaps_agregados) {
        imageToMap(null, key);
    }
    if (document.marcadoresClima.length > 0) {
        document.marcadoresClima.forEach(function(item, index) {
            item.setMap(null);
        });
    }
}

//ELIMINA TODAS LAS COORDENADAS AGREGADAS
function deleteAllCoord(shape_null = true) {
    for (var key in this.markers) {
        this.markers[key].setMap(null);
    }

    if (shape_null) {
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
    controlText.innerHTML = "CLEAN"; //document.lngarr['clean'];
    controlUI.appendChild(controlText);

    // Setup the click event listeners: simply set the map to Chicago.
    controlUI.addEventListener('click', function() {
        initMap();
        deleteAllCoord();
        Object.keys(GlobalMarkers).forEach(function(gk) {
            GlobalMarkers[gk]["marker"].setMap(null)
        });

        $('#results').html("");
        $('#results2').html("");

    });
}

//NOTIFICA UN ERROR
function notificarUsuario(msj, tipo) {
    $.notify({
        message: msj
    }, {
        type: tipo,
        delay: 6000,
        z_index: 5000
    });
    LOG_NOTIF[`m_${ID_NOTIF}`]={"tipo":tipo,"mensaje":msj}
    ID_NOTIF +=1
}

/**
 * MUESTRA EL POLIGONO DE UN PATH ROW
 */
function showPathRowsCoors(path, row) {
    data = { path: path, row: row, action: "get_pathrow_poly" };
    $.ajax({
        url: 'includes/controladores/controller.Images.php', //Server script to process data
        type: 'POST',
        data: data,
        dataType: 'json',
        success: function(data) { //muestra la respuesta
            lat = data[0]['ul_lat'];
            lon = data[0]['ul_lon'];
            var latlng = new google.maps.LatLng(lat, lon);
            addCoorToPoli(latlng);
            lat = data[0]['ur_lat'];
            lon = data[0]['ur_lon'];
            latlng = new google.maps.LatLng(lat, lon);
            addCoorToPoli(latlng);
            lat = data[0]['lr_lat'];
            lon = data[0]['lr_lon'];
            latlng = new google.maps.LatLng(lat, lon);
            addCoorToPoli(latlng);
            lat = data[0]['ll_lat'];
            lon = data[0]['ll_lon'];
            latlng = new google.maps.LatLng(lat, lon);
            addCoorToPoli(latlng);
            document.map.setCenter(new google.maps.LatLng(data[0]['ctr_lat'], data[0]['ctr_lon']));
            $("#txtPath").val("");
            $("#txtRow").val("");
            $('#modPathRow').modal('hide');
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log("error " + data.responseText);
        }
    });
}


///////// MANEJO DE COOKIES
//agrega una nueva cookie
function setCookie(cname, cvalue, minutes) {
    var d = new Date();
    d.setTime(d.getTime() + (minutes * 60 * 1000));
    var expires = "expires=" + d.toGMTString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

//elimina todas las cookies
function deleteAllCookies() {
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');

    for (var i = 0; i < ca.length; i++) {
        var c = ca[i].trim().split("=", 2);
        setCookie(c[0], "", -1);
    }
}

//regresa el valor de una cookie
function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');

    for (var i = 0; i < ca.length; i++) {
        var c = ca[i].trim().split("=", 2);
        if (c[0] == cname.trim()) {
            return c[1];
        }
    }
    return "";
}

//CARGA LAS COOKIES GUARDADAS
function cargar_cookies() {
    console.log("CARGANDO COOKIES");
    cook_shape = getCookie("shape");
    cook_onmap = getCookie("onmap");
    cook_onmap = cook_onmap == "true"
    $('#chOnMap').prop('checked', cook_onmap);
    if (cook_shape != null) {
        cook_sats = getCookie("satelites").split(',');
        startDate = getCookie("startDate");
        endDate = getCookie("endDate");

        if (cook_shape == "poligono") {
            cook = jQuery.parseJSON(getCookie("poligono"));
            cook.forEach(function(val, ind) {
                addCoorToPoli(val['lat'], val['lon']);
            });
        } else if (cook_shape == "rectangulo") {
            cook = jQuery.parseJSON(getCookie("poligono"));
            var bounds = {
                north: Number(cook[0]['lat']),
                south: Number(cook[1]['lat']),
                east: Number(cook[0]['lon']),
                west: Number(cook[1]['lon'])
            };
            addRectangleToMap(bounds);
        } else if (cook_shape == "circulo") {
            cook = jQuery.parseJSON(getCookie("poligono"));
            radio_cook = Number(getCookie("radio"));
            addCircle(Number(cook[0]['lat']), Number(cook[0]['lon']), radio_cook);
        } else if (cook_shape == "nombre") {
            place_coors['lat'] = getCookie("lat");
            place_coors['lon'] = getCookie("lon");
            document.state = getCookie("state");
            document.country = getCookie("country");
            document.city = getCookie("city");
            document.place = getCookie("place");
            addCoorToPoli(place_coors['lat'], place_coors['lon']);
        }

        setDate(startDate, endDate);

        document.ant = cook_shape;
        cook_sats.forEach(function(val, ind) {
            $('#ch' + val).prop('checked', true);
        });
        toResults();
    }
}

/*
 * CHECA SI LA SESIÓN ESTA ACTIVA
 */
function checkSession() {
    strfunction = arguments[0];
    function_arguments = arguments;
    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Session.php',
        dataType: 'json',
        data: { action: "check" },
        success: function(response) {
            if (response) {
                if (timerId != null) {
                    clearTimeout(timerId); // clear timer
                }
                startTimer();
                if (strfunction != null && strfunction.length > 0) {
                    if (strfunction != "sesionExpirada") {
                        if (function_arguments.length > 1) {
                            window[strfunction](function_arguments);
                        } else {
                            window[strfunction]();
                        }
                    }
                }
            } else {
                if (strfunction == "sesionExpirada") {
                    window[strfunction]();
                } else {
                    $('#loginmodal').modal('show');
                }
            }
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

/*
 * CAMBIA LA PUNTUACIÓN DE UNA IMAGEN EN LA BASE DE DATOS
 */
function rate() {
    element = arguments[0][1];
    id = arguments[0][2];
    rating = arguments[0][3];
    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Session.php',
        data: { img: id, rating: rating, action: "rate" },
        success: function(response) {
            for (i = 1; i <= 5; i++) {
                if (i <= rating) {
                    $("#btnStar" + id + i).html('<span class="glyphicon glyphicon-star" aria-hidden="true"></span>');
                } else {
                    $("#btnStar" + id + i).html('<span class="glyphicon glyphicon-star-empty" aria-hidden="true"></span>');
                }
            }
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}


/*
 * MODIFICA LA BASE DE DATOS CON LOS VALORES DE LA RECCIOÓN DEL USUARIO (LIKE OR DISLIKE)
 */
function modifyreactiondb(imagen, rating) {
    $.ajax({
        type: 'POST',
        url: 'includes/reactions.php',
        dataType: 'json',
        data: { img: imagen, rating: rating },
        success: function(response) {
            $("#btnLike" + imagen + " span").text("" + response[0].likes);
            $("#btnDislike" + imagen + " span").text("" + response[0].dislikes);
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

/*
 * AGREGA UNA VENTANA DE INFORMACIÓN AL ELEMENTO ESPECIFICADO
 */
function addInfoWindow(element, data) {
    var contentString = '<h5>' + data['nombre'] + '</h5><br>';
    if (data['city'] != null) {
        contentString += data['city'];
    }

    if (data['state'] != null) {
        contentString += ", " + data['state'];
    }

    if (data['country'] != null) {
        contentString += ", " + data['country'];
    }
    contentString += '<br><strong>Path</strong>:' + data['path'] + '<br><strong>Row</strong>:' + data['row'] + '<br>';
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
function imageToMap(elemento, nombre, action, rightP = false, idrecomendacion = -1) {
    if (nombre in imgsMaps_agregados) {
        if (imgsMaps_agregados[nombre]) {
            imgsMaps_agregados[nombre].setMap(null);
            delete imgsMaps_agregados[nombre];
            $(elemento).html("<span class='glyphicon glyphicon-picture' aria-hidden='true'></span>");
            $(elemento).removeClass("btn btn-secondary").addClass("btn btn-info");
            $(elemento).prop('title', 'Ver imágen en el mapa');
        }
    } else {
        var data = { imagen: nombre, rightP: rightP, action: action, idrecomendacion: idrecomendacion };
        $.ajax({
            type: 'POST',
            url: 'includes/controladores/controller.Images.php',
            dataType: 'json',
            data: data,
            success: function(response) {
                $(elemento).html("<span class='glyphicon glyphicon-eye-close' aria-hidden='true'></span>");
                $(elemento).removeClass("btn btn-info").addClass("btn btn-secondary");
                $(elemento).prop('title', 'Ocultar imágen del mapa');
                nombreAnt = nombre;
                triangleCoords = [];
                aux = [];
                response.forEach(function(item, index) {
                    aux[item.position] = item;
                });
                var bl = new google.maps.LatLng(aux["LL"].lat, aux["LL"].lon);
                var br = new google.maps.LatLng(aux["LR"].lat, aux["LR"].lon);
                var tr = new google.maps.LatLng(aux["UR"].lat, aux["UR"].lon);
                var tl = new google.maps.LatLng(aux["UL"].lat, aux["UL"].lon);
                var llq = new LatLngQuad(bl, br, tr, tl);
                var goex = new GroundOverlayEX('resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/' + response[0].nombre + '.jpg', null, { map: document.map, latlngQuad: llq, clickable: true });
                imgsMaps_agregados[nombre] = goex;
                addInfoWindow(goex, aux['Center']);
            },
            error: function(response) {
                console.log(response.responseText);
            }
        });
    }
}

/*
 * MUESTRA LA METADATA DE LA IMAGEN SOLICITADA
 */
function verMeta(nombre, rightP = false, idrecomendacion = -1) {
    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Images.php',
        dataType: 'json',
        data: { imagen: nombre, action: "view_metadata", rightP: rightP, idrecomendacion: idrecomendacion },
        success: function(response) {

            $("#titleModData").html(response[0].nombre);
            content = "<table class='table table-striped'>  <thead><tr>><th>" + document.lngarr['data'] + "</th><th>" + document.lngarr['value'] + "</th></tr></thead><tbody>";
            content += "<tr><td>" + document.lngarr['datead'] + ": </td><td>" + response[0].date + "</td></tr>";
            content += "<tr><td>" + document.lngarr['catalog'] + ": </td><td>" + response[0].satelite + "</td></tr>";
            content += "<tr><td>" + document.lngarr['path'] + " (" + document.lngarr['center'] + "): </td><td>" + response[0].path + "</td></tr>";
            content += "<tr><td>" + document.lngarr['row'] + " (" + document.lngarr['center'] + "): </td><td>" + response[0].row + "</td></tr>";
            aux = [];
            response.forEach(function(item, index) {
                //console.log(item);
                aux[item.position] = item;
            });
            //console.log(aux);
            content += "<tr><td>" + document.lngarr['ul'] + ": </td><td>" + aux["UL"].lat + " , " + aux["UL"].lon + "</td></tr>";
            content += "<tr><td>" + document.lngarr['ur'] + ": </td><td>" + aux["UR"].lat + " , " + aux["UR"].lon + "</td></tr>";
            content += "<tr><td>" + document.lngarr['ll'] + ": </td><td>" + aux["LL"].lat + " , " + aux["LL"].lon + "</td></tr>";
            content += "<tr><td>" + document.lngarr['lr'] + ": </td><td>" + aux["LR"].lat + " , " + aux["LR"].lon + "</td></tr>";
            content += "<tr><td>" + document.lngarr['center'] + ": </td><td>" + aux["CENTER"].lat + " , " + aux["CENTER"].lon + "</td></tr>";
            content += "<tr><td>" + document.lngarr['projection'] + ": </td><td>" + response[0].projection + "</td></tr>";
            content += "<tr><td>" + document.lngarr['ellipsoid'] + ": </td><td>" + response[0].ellipsoid + "</td></tr>";
            content += "</tbody></table>"

            $("#bodymodalData").html(content);
            $('#modDataImg').modal('show');
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}


/*
 * MUESTRA EL POLIGONO DE UNA IMAGEN EN EL MAPA
 */
function polygonToMap(elemento, nombre, action, rightP = false, idrecomendacion = -1) {
    //console.log(nombre);
    //console.log(polys_agregados);
    if (nombre in polys_agregados) {
        if (polys_agregados[nombre]) {
            polys_agregados[nombre].setMap(null);
            delete polys_agregados[nombre];
            $(elemento).html("<span class='glyphicon glyphicon-eye-open' aria-hidden='true'></span> Ver polígono");
            $(elemento).removeClass("btn btn-secondary").addClass("btn btn-info");
        }
    } else {
        var data = { imagen: nombre, rightP: rightP };
        if (arguments.length == 3) {
            data.action = arguments[2];
        } else {
            data.action = "view_polygon";
        }
        data.idrecomendacion = idrecomendacion;
        //console.log(data);
        $.ajax({
            type: 'POST',
            url: 'includes/controladores/controller.Images.php',
            dataType: 'json',
            data: data,
            success: function(response) {
                $(elemento).html("<span class='glyphicon glyphicon-eye-close' aria-hidden='true'></span> Ocultar");
                $(elemento).removeClass("btn btn-info").addClass("btn btn-secondary");
                nombreAnt = nombre;
                triangleCoords = [];
                aux = [];
                response.forEach(function(item, index) {
                    aux[item.position] = item;
                });
                triangleCoords.push({ lat: parseFloat(aux["UL"].lat), lng: parseFloat(aux["UL"].lon) })
                triangleCoords.push({ lat: parseFloat(aux["UR"].lat), lng: parseFloat(aux["UR"].lon) })
                triangleCoords.push({ lat: parseFloat(aux["LR"].lat), lng: parseFloat(aux["LR"].lon) })
                triangleCoords.push({ lat: parseFloat(aux["LL"].lat), lng: parseFloat(aux["LL"].lon) })

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
                //console.log(aux);
                //var center = new google.maps.LatLng(aux["Center"].lat,aux["Center"].lon);
                polys_agregados[nombre] = polyfoto;
            }
        });
    }
}

/**
 * Convierte un objeto HTML5 FormData a un JSON
 */
function formData2json(formData) {
    var object = {};
    console.log(formData);
    formData.forEach(function(value, key) {
        object[key] = value;
    });
    var json = JSON.stringify(object);
    return json;
}
/// --------------------- CAMBIA LA INFO DE LA ANTENA ----------------------------///
function onChangeDiferential(combo, estacion, it) {
    date = combo.value;
    Fuentes = $('input[type=radio][name=font_study]:checked').val().split(",")
    var opt_diferencial = $('#Diferencial').is(':checked');

    var dataStation = document.diferenciales[estacion];
    dataStation.forEach(function(item, index) {
        if (date == item['Fecha'] && Fuentes.length == 2) {
            temp = ""
            if (opt_diferencial) {
                temp = "<hr> <strong>Diferencial temperatura máxima: </strong>  " + item['Differential_max'] + "<br>" +
                    "<strong>Diferencial temperatura mínima: </strong>  " + item['Differential_min'] + "<br>" +
                    "<strong>Hidroregion </strong>  " + item['Hidroregion'] + "<br>" +
                    "<strong>Topoforma </strong>  " + item['Topoforma'].replace(/[^a-zA-Z ]/g, "") + "<br>" +
                    "<hr>";
            }
            $("#div" + it).html(temp +
                "<strong>Temperatura máxima EMAS: </strong>  " + item['Temp_max_emas'] + "<br>" +
                "<strong>Temperatura mínima EMAS: </strong>  " + item['Temp_min_emas'] + "<br>" +
                "<strong>Temperatura media EMAS: </strong>  " + item['Temp_mean_emas'] + "<br>" +
                "<strong>Temperatura máxima MERRA: </strong>  " + item['Temp_max_merra'] + "<br>" +
                "<strong>Temperatura mínima MERRA: </strong>  " + item['Temp_min_merra'] + "<br>" +
                "<strong>Temperatura media MERRA: </strong>  " + item['Temp_mean_merra'] + "<br>" +
                "<hr>" +
                "<strong>Humedad: </strong>  " + item['Humedad'] + "<br>" +
                "<strong>Presion barometrica: </strong>  " + item['Presion_barometrica'] + "<br>" +
                "<strong>Precipitacion: </strong>  " + item['Precipitacion'] + "<br>" +
                "<strong>Radiacion solar: </strong>  " + item['Radiacion_solar'] + "<br>"

            );
        } else if (date == item['Fecha'] && Fuentes[0] == "EMASMAX") {
            $("#div" + it).html(
                "<hr><<strong>Temperatura máxima  </strong>  " + item['Temp_max'] + "<br>" +
                "<strong>Temperatura mínima  </strong>  " + item['Temp_min'] + "<br>" +
                "<strong>Temperatura media   </strong>  " + item['Temp_mean'] + "<br>" +
                "<strong>Humedad: </strong>  " + item['Humedad'] + "<br>" +
                "<strong>Presion barometrica: </strong>  " + item['Presion_barometrica'] + "<br>" +
                "<strong>Precipitacion: </strong>  " + item['Precipitacion'] + "<br>" +
                "<strong>Radiacion solar: </strong>  " + item['Radiacion_solar'] + "<br>"
            );
        } else if (date == item['Fecha'] && Fuentes[0] == "MERRA") {
            $("#div" + it).html(
                "<hr><<strong>Temperatura máxima  </strong>  " + item['Temp_max'] + "<br>" +
                "<strong>Temperatura mínima  </strong>  " + item['Temp_min'] + "<br>" +
                "<strong>Temperatura media   </strong>  " + item['Temp_mean'] + "<br>"
            );
        }



    });

    // mostrar link de imagen
    var val = true;
    GlobalColors.forEach(function(arr, index) {
        GlobalImages.forEach(function(im, ix) {
            // Mostrar zip Imagenes Estaciones        
            if (Object.keys(im) == arr[0][2]) {
                if (val == true) {
                    folder = im[arr[0][2]].split("/")
                    folder = folder[2]
                    $("#imgStat").attr("href", "static/Zips/ImagesStations_" + folder + ".tar");
                    val = false
                }
                $("#div" + arr[0][2]).html("<hr><a onclick=\"viewImage('" + im[arr[0][2]] + "')\"><strong>Imagen</strong></a>");
            }
        });
    });



}

/*
 * OBTIENE LOS RESULTADOS DE UNA BUSQUEDA
 */
function zeros(dimensions) {
    var array = [];

    for (var i = 0; i < dimensions[0]; ++i) {
        array.push(dimensions.length == 1 ? 0 : zeros(dimensions.slice(1)));
    }

    return array;
}

function Filtter_stations(checkboxvalue,station_source) {
    value = $('#'+checkboxvalue).is(":checked")
    console.log(value)
    Object.keys(GlobalMarkers).forEach(function(gk) {
        if (value){ //encender
            if(GlobalMarkers[gk]['source']==station_source){
                v=true
                GlobalMarkers[gk]['filtros']['ST'] = v
                Object.keys(GlobalMarkers[gk]['filtros']).forEach(function(it) {
                    //console.log(GlobalMarkers[gk]['filtros'][it])
                    if (!GlobalMarkers[gk]['filtros'][it]){v =false}
                });
                GlobalMarkers[gk]['marker'].setVisible(v)

            }
        }
        else{
            if(GlobalMarkers[gk]['source']==station_source){
                GlobalMarkers[gk]['marker'].setVisible(false)
                GlobalMarkers[gk]['filtros']['ST'] = false
            }
        }



    });
}

function CrearGraficaRegresion(DIV_ID,obj_pares_datos,title="",yaxis="",xaxis="",xaxisname=""){
    //{"raw":{"var1":[]},"predict":{"var1":[]}}
    var data=[]


    Object.keys(obj_pares_datos.raw).forEach(function(key,index) {
            // al ser muchos puntos, solo se 10% se muestran
        datauntil = obj_pares_datos.raw[key]["x"].length*.1
        var trace_points = {
            x: obj_pares_datos.raw[key]["x"].slice(0,datauntil) ,
            y: obj_pares_datos.raw[key]["y"].slice(0,datauntil),
            name: key,
            type: 'scatter',
            mode: 'markers',
            marker: {
                size: 4,
                opacity: 0.6
            }
            };

        var trace_line = {
            x: obj_pares_datos.predict[key]["x"] ,
            y: obj_pares_datos.predict[key]["y"],
            name: key+"_trend",
            type: 'scatter',
            mode: 'lines',
            line: {
                width: 6
              }
            };

        data.push(trace_line)
        data.push(trace_points)
    })
    
    var layout = {
        margin: {l: 80,r: 20,b: 100,t: 100},
        showlegend: true,
        legend: { "orientation": "h"},
        title: title,
        xaxis: {
            title: {text: xaxis,font: {family: 'Courier New, monospace',size: 18,color: '#7f7f7f'}},
        },
        yaxis: {
            title: {text: yaxis,font: {family: 'Courier New, monospace',size: 18,color: '#7f7f7f'}}
        }
      };
      config_plot = { 
        showSendToCloud: true,
        showLink: true,
        displaylogo: false,
        responsive: true,
        plotlyServerURL: "https://chart-studio.plotly.com",
        toImageButtonOptions: {
            format: 'svg', // one of png, svg, jpeg, webp
            filename: 'Plot',
            height: 500,
            width: 700,
            scale: 1 // Multiply title/legend/axis/canvas sizes by this factor
        } 
    }
      Plotly.newPlot(DIV_ID, data, layout,config_plot);

}


function CrearGrafica2Axis(DIV_ID,obj_pares_datos,xdata,title="",yaxis1name="",yaxis2name="",  xaxisname=""){
    //{"kmeans":{ch:[],dv:[]}
    var data=[]
    var colors = ['blue','orange','grey','red','green','black']
    Object.keys(obj_pares_datos).forEach(function(key,index) {
        var trace1 = {
            x: xdata,
            y: obj_pares_datos[key]['ch'],
            name: key,
            type: 'scatter',
            marker:{color:colors[index]},
            legendgroup: key,
            };

        var trace2 = {
            x: xdata,
            y: obj_pares_datos[key]['db'],
            name: key+"_DB",
            yaxis: 'y2',
            showlegend:false,
            opacity:0.5,
            type: 'scatter',
            legendgroup: key,
            marker:{color:colors[index]},
            line: {
                dash: 'dot',
                width: 2
              }
            };
        data.push(trace1)
        data.push(trace2)
    })
      
      var layout = {
        margin: {l: 70,r: 70,b: 25,t: 35},
        showlegend: true,
        legend: { "orientation": "h"},
        title: title,
        yaxis: {title: yaxis1name},
        yaxis2: {
          title: yaxis2name,
          titlefont: {color: 'rgb(148, 103, 189)'},
          tickfont: {color: 'rgb(148, 103, 189)'},
          overlaying: 'y',
          side: 'right'
        }
      };
      config_plot = { 
        showSendToCloud: true,
        editable: true,
        showLink: true,
        displaylogo: false,
        responsive: true,
        plotlyServerURL: "https://chart-studio.plotly.com",
        toImageButtonOptions: {
            format: 'svg', // one of png, svg, jpeg, webp
            filename: 'Plot',
            height: 500,
            width: 700,
            scale: 1 // Multiply title/legend/axis/canvas sizes by this factor
        } 
    }
      Plotly.newPlot(DIV_ID, data, layout,config_plot);
      
}

function ChangeClusteringHistorico(combo) {
    
    clust = combo.value
    var Variables = $('#variable').val()
    var fuentes = $('input[type=radio][name=font_study]:checked').val().split(",")

    //mostrar info de scores
    $("#H-clustInfo").html("")
    $("#H-clustInfo").append(`<p class="font-weight-bold">${clust} </p>`)
    Object.keys(document.diferenciales.scores[clust]).forEach(function(name_score,index_score){
        $("#H-clustInfo").append(`<p class="text-center" >${name_score}: ${document.diferenciales.scores[clust][name_score]} </p>`)
    })
    

    if (fuentes.length == 2) { CasoFuente = "D" } else if (fuentes[0] == "EMASMAX") { CasoFuente = "E" } else if (fuentes[0] == "MERRA") { CasoFuente = "M" }

    document.diferenciales.data.forEach(function(row,index){
        Etiqueta_clase = document.diferenciales.clusters[clust][index] 
        if (Etiqueta_clase!="-"){
            if (Number(Etiqueta_clase)<0){
                Etiqueta_clase = 14-Number(Etiqueta_clase)
            }
            marker_color = Etiquetas_Colores[Etiqueta_clase]

        }
        else{marker_color="#fff"}

        antena = document.diferenciales.stations[index]

            var pinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + marker_color,
            new google.maps.Size(21, 34),
            new google.maps.Point(0, 0),
            new google.maps.Point(10, 34));

            

            GlobalMarkers[antena]["marker"].setIcon(pinImage)


    })

    function onlyUnique(value, index, self) {
        return self.indexOf(value) === index;
    }
    var etiquetas_clases  = document.diferenciales.clusters[clust].filter(onlyUnique);
    console.log(etiquetas_clases)

    //generar graficas por cluster historico

        dataCluster = []; markerSize=10

        if (Variables.length>=3) {xlabel = Variables[0]; ylabel=Variables[1]; zlabel=Variables[2]; markerSize=2.5}
        else if (Variables.length==2) {xlabel = Variables[0]; ylabel=Variables[1]; zlabel=Variables[1]}
        else {xlabel = Variables[0]; ylabel=Variables[0]; zlabel=Variables[0]}
        
        etiquetas_clases.forEach(function(cluster) {
            if(cluster!="-"){
                idclust = parseInt(cluster);
                x = []; y = []; z=[]

                document.diferenciales.clusters[clust].forEach(function(item,index) {
                    if (item == cluster) {
                        x.push( document.diferenciales.data[index][xlabel]);
                        y.push( document.diferenciales.data[index][ylabel])
                        if(Variables.length>=3){z.push( document.diferenciales.data[index][zlabel])}

                    }
                });
                if (idclust<0){
                    idclust = 14-idclust
                }
                color_etiqueta=Etiquetas_Colores[idclust]

                trace = {
                    x: x,
                    y: y,
                    mode: 'markers',
                    name: 'Cluster ' + cluster,
                    marker: {
                        color: '#' + color_etiqueta,
                        size: markerSize,
                        opacity: 0.8
                    }
                }
                if(Variables.length>=3){
                    trace.z = z
                    trace.type= 'scatter3d'
                }

                dataCluster.push(trace)
            }
        });
        var layoutClust = {
            margin: {l: 30,r: 30,b: 40,t: 40},
            showlegend: true,
            legend: { x: 1,   y: 1,   xanchor: 'right', 'itemsizing': 'constant'},
            title: {text: 'Clusters',font: {family: 'Courier New, monospace',size: 24},xref: ' ',x: 0.05,},
            xaxis: {
                title: {text: xlabel,font: {family: 'Courier New, monospace',size: 18,color: '#7f7f7f'}},
            },
            yaxis: {
                title: {text: ylabel,font: {family: 'Courier New, monospace',size: 18,color: '#7f7f7f'}}
            }
        };

        if(Variables.length>=3){
            layoutClust['scene'] = {xaxis:{title: xlabel},yaxis:{title: ylabel},zaxis:{title: zlabel},}
        }

        config_plot = { 
            showSendToCloud: true,
            editable: true,
            showLink: true,
            displaylogo: false,
            responsive: true,
            plotlyServerURL: "https://chart-studio.plotly.com",
            toImageButtonOptions: {
                format: 'svg', // one of png, svg, jpeg, webp
                filename: 'Plot',
                height: 500,
                width: 700,
                scale: 1 // Multiply title/legend/axis/canvas sizes by this factor
            } 
        }

        Plotly.newPlot('H-Gclust', dataCluster, layoutClust, config_plot );
        DATA_GRAPHS['H-Gclust'] = {"data":dataCluster,"layout":layoutClust}

        // =============== GENERAR GRAFICA DE REGRESION ===============
            document.diferenciales.clusters[clust].forEach(function(item,index) {
                    x.push( document.diferenciales.data[index]['Differential_max']);
                    y.push( document.diferenciales.data[index]['Differential_min'])
            });

        //if (CasoFuente == "D") {
        //    //ARRAYS PARA LA GRAFICA DE DISPERSION
        //    dataCluster=[]
        //    etiquetas_clases.forEach(function(cluster) {
        //        if(cluster!="-"){
        //            idclust = parseInt(cluster);
        //            x = [];
        //            y = []
        //            document.diferenciales.clusters[clust].forEach(function(item,index) {
        //                if (item == cluster) {
        //                    x.push( document.diferenciales.data[index]['Differential_max']);
        //                    y.push( document.diferenciales.data[index]['Differential_min'])
        //                }
        //            });
        //            if (idclust<0){
        //                idclust = 14-idclust
        //            }
        //            color_etiqueta=Etiquetas_Colores[idclust]
        //            trace = {
        //                x: x,
        //                y: y,
        //                mode: 'markers',
        //                name: 'Cluster ' + cluster,
        //                marker: {
        //                    color: '#' + color_etiqueta,
        //                    size: 10
        //                }
        //            }
        //            dataCluster.push(trace)
        //        }
        //    });
        //    var layoutClust = {
        //        title: {
        //            text: 'Differential MERRA-EMAS',
        //            font: {
        //                family: 'Courier New, monospace',
        //                size: 24
        //            },
        //            xref: ' ',
        //            x: 0.05,
        //        },
        //        xaxis: {
        //            title: {
        //                text: 'Differential MAX (C°)',
        //                font: {
        //                    family: 'Courier New, monospace',
        //                    size: 18,
        //                    color: '#7f7f7f'
        //                }
        //            },
        //        },
        //        yaxis: {
        //            title: {
        //                text: 'Differential MIN(C°)',
        //                font: {
        //                    family: 'Courier New, monospace',
        //                    size: 18,
        //                    color: '#7f7f7f'
        //                }
        //            }
        //        }
        //    };
        //    Plotly.newPlot('H-Dispersion', dataCluster, layoutClust, { showSendToCloud: true });
        //    DATA_GRAPHS['H-Dispersion'] = {"data":dataCluster,"layout":layoutClust}
        //    dataCluster=null
        //    layoutClust=null
        //}
}


// --------------------------- COMBOBOX DATES -----------------------------------
function ChangeClustering(combo, k, GroupByDate = "None") {
    $("#ScatPlot").html("");
    $("#ClustPlot").html("");
    $("#GeneralPlot").html("");

    console.log("CAMBIANDO CLUSTERING...")
    var dataStation = document.diferenciales;
    var summ = new Object()
    var opt_clustering = $('#clustering').is(':checked');
    var auxArray = $('input[type=radio][name=font_study]:checked').val().split(",")
    lbvariables = $('#variable').val()
    if (Array.isArray(auxArray) && auxArray.length < 2) { //format variables when its just one source
        lbvariables.forEach(function(v, ix) {
            if (lbvariables[ix] == "Temp_max_emas" || lbvariables[ix] == "Temp_max_merra") { lbvariables[ix] = "Temp_max" }
            if (lbvariables[ix] == "Temp_min_emas" || lbvariables[ix] == "Temp_min_merra") { lbvariables[ix] = "Temp_min" }
        })
    }

    for (var i = 0; i < k; i++) {
        summ[i.toString()] = new Object()
        var temp_var = lbvariables.slice()
        if (auxArray.length == 2) { //mas de dos fuentes
            if (!temp_var.includes('Differential_max')){
                temp_var.push("Differential_max");temp_var.push("Differential_min") //differencial
            }
        }
        temp_var.forEach(function(v, ix) {
            summ[i.toString()][temp_var[ix]] = 0
            summ[i.toString()][temp_var[ix]+"counter"] = 0
        })

    }
    
    Object.keys(dataStation).forEach(function(key) {
        marker_color = "#fff"
        dataStation[key].forEach(function(estacion, idx) {
            class_lablel = estacion['Etiqueta_clase']
            if (opt_clustering) {
                estacion[lbvariables[0]] = parseFloat(estacion[lbvariables[0]])
                estacion[lbvariables[1]] = parseFloat(estacion[lbvariables[1]])

                if ((combo.value == estacion['Fecha'] && !isNaN(estacion[lbvariables[0]]) && !isNaN(estacion[lbvariables[1]])) ||
                    (combo.value == estacion['Fecha'] && (Array.isArray(lbvariables) && lbvariables.length <= 1 && !isNaN(estacion[lbvariables[0]])))) {
                    marker_color = Etiquetas_Colores[estacion['Etiqueta_clase']]
                    var temp_var = lbvariables.slice()
                    if (auxArray.length == 2) { //mas de dos fuentes
                        if (!temp_var.includes('Differential_max')){
                            temp_var.push("Differential_max");temp_var.push("Differential_min") //differencial
                        }
                    }

                    temp_var.forEach(function(v, ix) {
                        value_var = parseFloat(estacion[temp_var[ix]])
                        if (!isNaN(value_var) && value_var != -99){
                            summ[class_lablel][temp_var[ix]] += parseFloat(value_var)
                            summ[class_lablel][temp_var[ix]+'counter'] += 1

                        }
                    })

                } else { //just 1 cluster
                    if ((GroupByDate == "GROUP" && !isNaN(estacion[lbvariables[0]]) && !isNaN(estacion[lbvariables[1]])) ||
                        (GroupByDate == "GROUP" && (Array.isArray(lbvariables) && lbvariables.length <= 1 && !isNaN(estacion[lbvariables[0]])))) {
                        marker_color = Etiquetas_Colores[estacion['Etiqueta_clase']]
                        var temp_var = lbvariables.slice()
                        if (auxArray.length == 2) { //mas de dos fuentes
                            if (!temp_var.includes('Differential_max')){
                                temp_var.push("Differential_max");temp_var.push("Differential_min") //differencial
                            }
                        }
                        temp_var.forEach(function(v, ix) {
                            value_var = parseFloat(estacion[temp_var[ix]])
                            if (!isNaN(value_var) && value_var != -99){
                                summ[class_lablel][temp_var[ix]] += parseFloat(value_var)
                                summ[class_lablel][temp_var[ix]+'counter'] += 1
                            }
                        })
                        
                    }
                }
            }
            var pinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + marker_color,
                new google.maps.Size(21, 34),
                new google.maps.Point(0, 0),
                new google.maps.Point(10, 34));
            GlobalMarkers[key]["marker"].setIcon(pinImage)
        })
    })
    console.log(lbvariables)
    console.log("COLORES RESTABLECIDOS...")

    //-------------------------------------INFO DE CLUSTERS ------------------------------
    if (opt_clustering) {
        var temp_var = lbvariables.slice()
        REPORTE.CLUSTERINFO = []
        if (auxArray.length == 2) { //mas de dos fuentes
            temp_var.push("Differential_max");temp_var.push("Differential_min") //differencial
        }
        $("#Clusters_res").html("")
        for (var i = 0; i < k; i++) {
            $("#Clusters_res").append("<br><br><span class=\"dot\" style=\"background-color:#" + Etiquetas_Colores[i] + "\"></span> <strong>Cluster " + (i + 1) + "</strong><br><hr>").fadeIn('slow');
            temp_var.forEach(function(v, ix) {
                if (summ[i][temp_var[ix]+'counter'] != 0){
                    $("#Clusters_res").append("Average " + temp_var[ix] + ": " + (summ[i][temp_var[ix]] / summ[i][temp_var[ix]+'counter']) + "</br>");
                    REPORTE.CLUSTERINFO.push({"class":i,"variable":temp_var[ix],"mean": (summ[i][temp_var[ix]] / summ[i][temp_var[ix]+'counter'])})
                }
            })

        }
        //here add button to download Descargar_REPORTE
        $("#Clusters_res").append(`<button onclick="Descargar_REPORTE(['CLUSTERINFO'])" class="btn btn-warning btn-sm btn-block"><span class="glyphicon glyphicon-save" aria-hidden="true"></span></button>`)
    }
    console.log("INFO CLUSTERING...")

    //------------------------------------IMAGENES DE SILUETA---------------------------
    if ($('#Silhouette_auto').is(':checked')) {
        if (GroupByDate == "GROUP") {
            $("#DetailsQuery").html("<img src =/AEM-Eris/meteo" + GlobalImagesSil['path'] + " onclick=\"viewImage('/AEM-Eris/meteo" + GlobalImagesSil['path'] + "')\" width='300px' height='230px' >")
        } else {
            GlobalImagesSil.forEach(function(item, index) {
                fecha = item['date']
                if (fecha == combo.value) {
                    $("#DetailsQuery").html("<img src =/AEM-Eris/meteo" + item['path'] + " onclick=\"viewImage('/AEM-Eris/meteo" + item['path'] + "')\" width='300px' height='230px' >")
                }

            });
        }

    }
    //------------------------------------IMAGENES DE FECHAS---------------------------
    if ($('#IMG_dates').is(':checked') && auxArray.length == 2) {
        i = 1;
        val = true;
        $("#img_res").html("");
        $("#img_res").html("<br><h2>Results</h2>")
        GlobalImagesDate.forEach(function(item, index) {
            folder = item[i].split("/")
            fecha = folder[3]
            folder = folder[2]
            fecha = fecha.split("_")[0];
            fecha = fecha.split("-");
            fecha = fecha[2] + "/" + fecha[1] + "/" + fecha[0]

            if (val == true) {
                $("#imgDate").attr("href", "static/Zips/ImagesDates_" + folder + ".tar");
                val = false
            }
            if (fecha == combo.value) {

                $("#img_res").append("<div style='width:100%; height:130px; color:blue'> \
      <img src =" + item[i] + " onclick=\"viewImage('" + item[i] + "')\" width='100%' height='100%' >  \
        </div> <br>");
            }
            i++
        });
    }
    // ------------------------------------- GRAFICAS (DISPERCION) ----------------------------

    data = [];
    datadiff = []
    dataGen = []
    dataGenRep = []
    hoverlable_DGR = []
    xGen = [];
    yGen = [];
    for (var i = 0; i < k; i++) { //POR CADA GRUPO
        x = [];
        xd = [];
        y = [];
        yd = []


        Object.keys(dataStation).forEach(function(key) {
            counter = 0;
            xrepres = 0;
            yrepres = 0;
            classrepres = NaN
            dataStation[key].forEach(function(estacion, idx) { // all records from a same station
                estacion[lbvariables[0]] = parseFloat(estacion[lbvariables[0]])
                estacion[lbvariables[1]] = parseFloat(estacion[lbvariables[1]])


                if (!isNaN(estacion[lbvariables[0]]) && !isNaN(estacion[lbvariables[1]]) || (Array.isArray(lbvariables) && lbvariables.length <= 1)) {
                    if (combo.value == estacion['Fecha'] && estacion['Etiqueta_clase'] == i || estacion['Etiqueta_clase'] == i && GroupByDate == "GROUP") { // si es la fecha correcta
                        if (auxArray.length == 2) { //grafica de dispersion por dia
                            x.push(estacion['Temp_mean_emas'])
                            y.push(estacion['Temp_mean_merra'])
                        }
                        if (opt_clustering) { //grafica de clustering
                            if (lbvariables.length >= 2 && Array.isArray(lbvariables)) { //2 or more data sources
                                xd.push(estacion[lbvariables[0]])
                                yd.push(estacion[lbvariables[1]])
                                xdlabel = lbvariables[0]
                                ydlabel = lbvariables[1]
                                dtitle = "Clustering (records)"
                            } else { //one data source
                                xd.push(estacion['Etiqueta_clase'])
                                yd.push(estacion[lbvariables[0]])
                                xdlabel = "Clase"
                                ydlabel = lbvariables[0]
                                dtitle = "Clustering (records) "
                            }
                        }
                    }
                    if (estacion['Etiqueta_clase'] == i && GroupByDate == "None") { //general graph
                        if (lbvariables.length >= 2 && Array.isArray(lbvariables)) { //2 or more data sources
                            xGen.push(estacion[lbvariables[0]])
                            yGen.push(estacion[lbvariables[1]])
                            xglabel = lbvariables[0]
                            yglabel = lbvariables[1]
                            gtitle = "General"
                        } else { // one data source
                            xGen.push(estacion['Antena'])
                            yGen.push(estacion[lbvariables[0]])
                            xglabel = "Class"
                            yglabel = lbvariables[0]
                            gtitle = "General"
                        }
                    } else { //general graph but with representative data
                        if (estacion['Etiqueta_clase'] == i) {
                            if (lbvariables.length >= 2 && Array.isArray(lbvariables)) { //2 or more data sources
                                if (!isNaN(estacion[lbvariables[0]]) && !isNaN(estacion[lbvariables[1]])) {
                                    xrepres += estacion[lbvariables[0]]
                                    yrepres += estacion[lbvariables[1]]
                                    classrepres = i
                                    counter += 1
                                }
                                xglabel = lbvariables[0]
                                yglabel = lbvariables[1]
                                gtitle = "Clustering (stations)"
                            } else { // one data source
                                xrepres = estacion['Antena']
                                    //console.log((Array.isArray(lbvariables) && lbvariables.length <= 1 && !isNaN(estacion[lbvariables[0]])))
                                if ((!isNaN(estacion[lbvariables[0]]) && !isNaN(estacion[lbvariables[1]])) ||
                                    (Array.isArray(lbvariables) && lbvariables.length <= 1 && !isNaN(estacion[lbvariables[0]]))) {
                                    yrepres += estacion[lbvariables[0]]
                                    counter += 1
                                    classrepres = i
                                }
                                xglabel = "Class"
                                yglabel = lbvariables[0]
                                gtitle = "Clustering (stations)"
                            }
                        }
                    }
                } //if is nan

            }); //for por cada fecha
            if (GroupByDate == "GROUP" && classrepres == i) {
                if (lbvariables.length >= 2 && Array.isArray(lbvariables)) { //2 or more data sources
                    xGen.push(xrepres / counter)
                    yGen.push(yrepres / counter)

                } else {
                    xGen.push(xrepres)
                    yGen.push(yrepres / counter)
                }
                hoverlable_DGR.push(key)
                classrepres = NaN


            }
        })
        traceScat = {
            x: x,
            y: y,
            mode: 'markers',
            name: 'Cluster ' + i,
            marker: {
                color: '#' + Etiquetas_Colores[i],
                size: 10
            }

        }
        traceClust = {
            x: xd,
            y: yd,
            mode: 'markers',
            name: 'Cluster ' + i,
            marker: {
                color: '#' + Etiquetas_Colores[i],
                size: 10
            }
        }
        if (GroupByDate == "GROUP") {
            traceGeneralCluster = {
                x: xGen,
                y: yGen,
                mode: 'markers',
                name: 'Cluster ' + i,
                text: hoverlable_DGR,

                marker: {
                    color: '#' + Etiquetas_Colores[i],
                    size: 10
                }

            }
            dataGenRep.push(traceGeneralCluster)
            xGen = []
            yGen = []
            hoverlable_DGR = []
        }

        data.push(traceScat)
        datadiff.push(traceClust)
    } //end for clusters
    traceGeneral = {
        x: xGen,
        y: yGen,
        mode: 'markers',
        name: 'All ',
        marker: {
            color: '#' + Etiquetas_Colores[6],
            size: 10
        }

    }
    line = {
        x: [0, 50],
        y: [0, 50],
        mode: 'lines',
        name: 'División'
    }
    data.push(line)
    dataGen.push(traceGeneral)

    var layoutScatt = {
        title: {
            text: 'Dispersión',
            font: {
                family: 'Courier New, monospace',
                size: 20
            },
            xref: 'paper',
            x: 0.05,
        },
        xaxis: {
            title: {
                text: 'Temp MEAN EMAS (C°)',
                font: {
                    family: 'Courier New, monospace',
                    size: 18,
                    color: '#7f7f7f'
                }
            },
        },
        yaxis: {
            title: {
                text: 'Temp MEAN MERRA (C°)',
                font: {
                    family: 'Courier New, monospace',
                    size: 18,
                    color: '#7f7f7f'
                }
            }
        }
    };

    if (opt_clustering) {
        var layoutClust = {
            title: {
                text: dtitle,
                font: {
                    family: 'Courier New, monospace',
                    size: 20
                },
                xref: 'paper',
                x: 0.05,
            },
            xaxis: {
                title: {
                    text: xdlabel,
                    font: {
                        family: 'Courier New, monospace',
                        size: 18,
                        color: '#7f7f7f'
                    }
                },
            },
            yaxis: {
                title: {
                    text: ydlabel,
                    font: {
                        family: 'Courier New, monospace',
                        size: 18,
                        color: '#7f7f7f'
                    }
                }
            }
        };
    }
    var layoutGeneral = {
        title: {
            text: gtitle,
            font: {
                family: 'Courier New, monospace',
                size: 20
            },
            xref: 'paper',
            x: 0.05,
        },
        xaxis: {
            title: {
                text: xglabel,
                font: {
                    family: 'Courier New, monospace',
                    size: 18,
                    color: '#7f7f7f'
                }
            },
        },
        yaxis: {
            title: {
                text: yglabel,
                font: {
                    family: 'Courier New, monospace',
                    size: 18,
                    color: '#7f7f7f'
                }
            }
        }
    };
    console.log("GENERANDO GRAFICAS CLUSTERING...")

    if (auxArray.length == 2) {
        Plotly.newPlot('ScatPlot', data, layoutScatt, { showSendToCloud: true });
    }
    if (opt_clustering) {
        Plotly.newPlot('ClustPlot', datadiff, layoutClust, { showSendToCloud: true });
    }
    //if (GroupByDate == "GROUP") {
    //    Plotly.newPlot('GeneralPlot', dataGenRep, layoutGeneral, { showSendToCloud: true });
    //} else {
    //    Plotly.newPlot('GeneralPlot', dataGen, layoutGeneral, { showSendToCloud: true });
    //}



}
function Filtter_clima(checkboxvalue,clima_source){
    value = $('#'+checkboxvalue).is(":checked")
    Object.keys(GlobalMarkers).forEach(function(gk) {
        clima_label = GlobalMarkers[gk]['clima']['nombre']
        if (value){ //encender
            if(clima_label==clima_source){
                v=true
                GlobalMarkers[gk]['filtros']['C'] = v
                Object.keys(GlobalMarkers[gk]['filtros']).forEach(function(it) {
                    if (!GlobalMarkers[gk]['filtros'][it])
                    {
                        v =false
                    }
                });
                GlobalMarkers[gk]['marker'].setVisible(v)
            }
        }
        else{
            if(clima_label==clima_source){
                GlobalMarkers[gk]['marker'].setVisible(false)
                GlobalMarkers[gk]['filtros']['C'] = false
            }
        }
    });
}


function Filtter_hidroregions(checkboxvalue,hidroform_source){
    value = $('#'+checkboxvalue).is(":checked")
    Object.keys(GlobalMarkers).forEach(function(gk) {
        HR = GlobalMarkers[gk]['hidroregion']
        if (value){ //encender
            if(HR==hidroform_source){
                v=true
                GlobalMarkers[gk]['filtros']['HR'] = v
                Object.keys(GlobalMarkers[gk]['filtros']).forEach(function(it) {
                    if (!GlobalMarkers[gk]['filtros'][it])
                    {
                        v =false
                    }
                });
                GlobalMarkers[gk]['marker'].setVisible(v)
            }
        }
        else{
            if(HR==hidroform_source){
                GlobalMarkers[gk]['marker'].setVisible(false)
                GlobalMarkers[gk]['filtros']['HR'] = false
            }
        }
    });
}

function Filtter_topoforms(checkbox,topoform_source){

    value = $('#'+checkboxvalue).is(":checked")

    Object.keys(GlobalMarkers).forEach(function(gk) {
        TF = GlobalMarkers[gk]['topoforma']
        if (value){ //encender
            if(TF==topoform_source){
                v=true
                GlobalMarkers[gk]['filtros']['TF'] = v
                Object.keys(GlobalMarkers[gk]['filtros']).forEach(function(it) {
                    if (!GlobalMarkers[gk]['filtros'][it])
                    {
                        v =false
                    }
                });
                GlobalMarkers[gk]['marker'].setVisible(v)
            }
        }
        else{
            if(TF==topoform_source){
                GlobalMarkers[gk]['marker'].setVisible(false)
                GlobalMarkers[gk]['filtros']['TF'] = false
            }
        }



    });
}

function onlyUnique(value, index, self) {
    return self.indexOf(value) === index;
}


function Clustering_results(datos, Fuentes, opt_summary, group_by_date, opt_clustering, k) {
    CasoClust="D"
    notificarUsuario("Clustering info fully loaded", 'success');
    GlobalImagesSil = datos['images']
    REPORTE.SEE = []
    datos = datos['results']
    Object.keys(GlobalMarkers).forEach(function(gk) {
        GlobalMarkers[gk]['marker'].setMap(null)
    });


    //CASOS DE CLUSTERING
    if (Fuentes.length == 2) { CasoClust = "D" }
    if (Fuentes.length === 1 && Fuentes[0] == "EMASMAX") { CasoClust = "E"}
    if (Fuentes.length === 1 && Fuentes[0] == "MERRA") { CasoClust = "M"}

    if (opt_summary && CasoClust == "D") {
        $('#SSE').append('<br><br><br><hr><h2>SSE</h2><table style="width:100%">') //CREAR TABLA SSE
        $('#SSE').append('<tr><th>Station</th><th>  SSE MAX  </th><th>  SSE MIN  </th>/tr>')
    }
    $("#clust_box").html("")
    GlobalColors = [];
    GlobalMarkers = new Object();
    fechas = []

    var places = {};
    datos.forEach(function(item, index) {
        index = index + 1;
        if (item[index] === undefined){
            item = item
        }
        else{
            item = item[index];
        }
        if (!(item['Antena'] in places)) {
            places[item['Antena']] = [];
        }
        places[item['Antena']].push(item);
    });
    document.diferenciales = places;

    var it = 5;


    Object.keys(places).forEach(key => {
        let value = places[key];
        estcoors = { lat: parseFloat(value[0]['Latitud']), lng: parseFloat(value[0]['Longitud']) };
        color = "#FF212";
        var pinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + color,
            new google.maps.Size(21, 34),
            new google.maps.Point(0, 0),
            new google.maps.Point(10, 34));

        var marker = new google.maps.Marker({
            position: estcoors,
            map: document.map,
            icon: pinImage
        });
        //console.log(value)
        var dates = "";
        var colores = [];
        dates = "<option value='1'>---</option>"
        SSEMAX = 0;
        SSEMIN = 0;
        Cant_fechas = 0;
        station_source = "EMASMAX";
        topoform = ""
        Hidroregion = ""
        value.forEach(function(item, index) {
            if ("Topoforma" in item) { topoform = item['Topoforma']}
            if ("Hidroregion" in item){ Hidroregion = item['Hidroregion']}

            dates += "<option value='" + item['Fecha'] + "'>" + item['Fecha'] + "</option>";
            if (CasoClust == "D") {
                colores.push([item['Etiqueta_clase'], item['Fecha'], item['Codigo'], item['Differential_max'], item['Differential_min']])
            } else {
                colores.push([item['Etiqueta_clase'], item['Fecha'], item['Codigo'], item['Temp_max'], item['Temp_min']])
            }

            fechas.push(item['Fecha'])

            // CALCULO DE SSE
            if (CasoClust == "D" && opt_summary && item['Temp_max_emas'] != -99 && item['Temp_min_emas'] != -99) {
                SSEMAX += Math.pow(item['Temp_max_emas'] - item['Temp_max_merra'], 2)
                SSEMIN += Math.pow(item['Temp_min_emas'] - item['Temp_min_merra'], 2)
                Cant_fechas += 1
            }
            if(item['Temp_max_emas'] == -99){station_source="MERRA"}
        });
        if (CasoClust == "D" && opt_summary) {
            SSEMAX /= (Cant_fechas - 1);
            SSEMAX = Math.sqrt(SSEMAX);
            SSEMIN /= (Cant_fechas - 1);
            SSEMIN = Math.sqrt(SSEMIN);
        }
        //console.log(colores)
        var infowindow = new google.maps.InfoWindow({
            content: "<div><div><strong>" + key + "</strong></div><div>Latitud = " +
                value[0]['Latitud'] +
                "<br><strong>Longitud</strong> = " + value[0]['Longitud'] + "</div>" +
                "<div id='div" + value[0]['Codigo'] + "'></div>" +
                "<br><select class='form-control idfechas' onchange=\"onChangeDiferential(this,'" + key + "','" + it + "')\">" + dates + "</select>" +
                "<div id='div" + it + "'></div>" +
                "<div id='Emasdiv" + it + "'></div>" +
                "</div>"
        });

        marker.addListener('click', function() {
            infowindow.open(document.map, marker);
        });
        google.maps.event.addListenerOnce(infowindow, 'domready', function() {
            ShowRegression();
        });

        // INSERTAR SEE en tabla
        if (CasoClust == "D" && opt_summary) {
            REPORTE.SEE.push({"Estacion":key,"SEEMAX":SSEMAX,"SSEMIN":SSEMIN})
            $('#SSE').append('<tr><th>' + key + '</th><th>' + SSEMAX.toFixed(2) + '</th><th>' + SSEMIN.toFixed(2) + '</th></tr>')
        }
        it += 1;
        GlobalMarkers[key] = { "marker": marker,"source":station_source, "hidroregion":Hidroregion.replace(/[^a-zA-Z ]/g, "").replace(/\s+/g, '_'),"topoforma":topoform.replace(/[^a-zA-Z ]/g, "").replace(/\s+/g, '_'),filtros:{"ST":true,"TF":true,"HR":true}}
        GlobalColors.push(colores)
    });
    if (CasoClust == "D" && opt_summary) {
        $("#SSE").append(`<button onclick="Descargar_REPORTE(['SEE'])" class="btn btn-warning btn-sm btn-block"><span class="glyphicon glyphicon-save" aria-hidden="true"></span></button>`)
       }
    fechas = fechas.filter(onlyUnique);
    //cambiar los colores de todos los marcadores
    if (!group_by_date) { // si solo es un clustering no se imprime el combobox de fechas
        dates = "<option value='1'>Elegir fecha</option>"
        fechas.forEach(function(item, index) {
            dates += "<option value='" + item + "'>" + item + "</option>";
        });
        if (opt_clustering) {
            $("#clust_box").append("<hr><h3>" + document.lngarr['select_date'] + " </h3><select class='form-control idfechas' width='80%' onchange=\"ChangeClustering(this,'" + k + "')\">" + dates + "</select><hr>\
                        <div id='clustinfo' style='width:100%; color:blue'; height:100%>");
        }
    } else {
        ChangeClustering({ 'value': 'None' }, k, GroupByDate = "GROUP")
    }


    HabilitarFiltros()

}

function HabilitarFiltros(Emas=false){
    $("#results2").append("<div  id='map_filtters' style='width: 100%; height: 45%; overflow-y: auto; resize: vertical'> </div>")
    console.log("se entra a la funcion de filtros")
    $("#map_filtters").html("<h2>FILTERS</h2>")
    var Fuentes = $('input[type=radio][name=font_study]:checked').val().split(",")

    $("#map_filtters").append("<h4> Sources </h4><hr>")
    Object.keys(Fuentes).forEach(function(gk) {
        src =  Fuentes[gk]
        if(Emas & src=="EMASMAX"){src = "EMAS"}
        $("#map_filtters").append(`<div class="inputGroup col-sm-6">
            <input type="checkbox" id="FIL_${src}" name="FIL_${src}" onchange="Filtter_stations('FIL_${src}','${src}')" checked> 
            <label style="font-size:11px" for="FIL_${src}"> ${src} </label>
        </div>`)
    });


    // si la opcion de las topoformas esta activa
    var filtrar_por_topoformas = $("#filt_topo").is(":checked");
    if (filtrar_por_topoformas){ $("#map_filtters").append("<h4> TOPOFORMS </h4><hr>")}
    
        var topoforms_used = []
        Object.keys(GlobalMarkers).forEach(function(gk) { //iterate all stations
            TF = GlobalMarkers[gk]['topoforma']
            if (!(TF in GlobalColorTopoformas)){
                GlobalColorTopoformas[TF]= Math.floor(Math.random() * 16777215).toString(16)
            }
            if (!(topoforms_used.includes(TF))){
                if (filtrar_por_topoformas){
                    $("#map_filtters").append(`<div class="inputGroup col-sm-6">
                    <input type="checkbox" id="FIL_TF_${TF}" name="FIL_TF_${TF}" onchange="Filtter_topoforms('FIL_TF_${TF}','${TF}')" checked> 
                    <label style="font-size:11px" for="FIL_TF_${TF}"> ${TF} </label>
                    </div>`)
                }
                topoforms_used.push(TF)
            }

        });
        $("#map_filtters").append("<br>")
        topoform_report = topoforms_used //guardar lista de topoformas usadas


    

    if ($("#filt_hidro").is(":checked")){
        $("#map_filtters").append("<h4> HIDROREGIONS </h4><hr>")
        var hydroregions_used = []
        Object.keys(GlobalMarkers).forEach(function(gk) { //iterate all stations
            HR = GlobalMarkers[gk]['hidroregion']
            if (!(HR in GlobalColorHidroregiones)){
                GlobalColorHidroregiones[HR]= Math.floor(Math.random() * 16777215).toString(16)
            }
            if (!(hydroregions_used.includes(HR))){
                $("#map_filtters").append(`<div class="inputGroup col-sm-6" >
                <input type="checkbox" id="FIL_HR_${HR}" name="FIL_HR_${HR}" onchange="Filtter_hidroregions('FIL_HR_${HR}','${HR}')" checked> 
                <label style="font-size:11px" for="FIL_HR_${HR}"> ${HR} </label>
                </div>`)
                hydroregions_used.push(HR)

            }
        });
    }

    if ($("#filt_clima").is(":checked")){
        $("#map_filtters").append("<h4> Clima </h4><hr>")
        var clima_labels_used = []
        Object.keys(GlobalMarkers).forEach(function(gk) { //iterate all stations
            clima_label = GlobalMarkers[gk]['clima']['nombre']
            clima_desc = GlobalMarkers[gk]['clima']['desc']

            if (!(clima_labels_used.includes(clima_label))){
                $("#map_filtters").append(`<div class="inputGroup col-sm-6" >
                <input type="checkbox" id="FIL_C_${clima_label}" name="FIL_C_${clima_label}" onchange="Filtter_clima('FIL_C_${clima_label}','${clima_label}')" checked> 
                <label style="font-size:11px" for="FIL_C_${clima_label}"> ${clima_label}(${clima_desc}) </label>
                </div>`)
                clima_labels_used.push(clima_label)

            }
        });
        clima_report = clima_labels_used
    }

}
function GenerarEtiquetas(k=30){
    if (k == 0) { k = 30 } // IF K =====0
    for (var i = 0; i <= k; i++) {
        Etiquetas_Colores[i] = Math.floor(Math.random() * 16777215).toString(16)
        if (Etiquetas_Colores[i].length <6) {
            Etiquetas_Colores[i] += "000000"
        }

        if (Etiquetas_Colores[i].length > 6) {
            Etiquetas_Colores[i] = Etiquetas_Colores[i].substring(0, 6)
        }
    }
}

function getResults(page) {

    var weather_selection = $('#slproductos').val();
    var espacial_selection = $('#slShape2').val();

    //  ----------------------------------- DIFERENCIAL---------------------------------------------------------
    if (weather_selection == "actual" && (espacial_selection == "poligono" || espacial_selection == "regiones" || espacial_selection == "estados" || espacial_selection == "municipios" || espacial_selection == "ecoregion")) {

        if (espacial_selection == "poligono") {
            var coorsJson = getCoors();
        } else if (espacial_selection == "regiones" || espacial_selection == "estados" || espacial_selection == "municipios" || espacial_selection == "ecoregion") { var coorsJson = JSON.stringify(coors) }

        var startDate = $("#datetimepicker1").data('DateTimePicker').date();
        var endDate = $("#datetimepicker2").data('DateTimePicker').date();
        var k = $("#txtKClust").val();
        var algh = $("#Clust_alg").val();
        var SIL = $('#Silhouette_auto').is(':checked');
        var GrStat = $('#IMG_stat').is(':checked');
        var GrDate = $('#IMG_dates').is(':checked');
        var Fill = $('#Extra').is(':checked').toString();
        var Fuentes = $('input[type=radio][name=font_study]:checked').val().split(",")
        var Variables = $('#variable').val()
        var opt_summary = $('#Summay').is(':checked');
        var opt_clustering = $('#clustering').is(':checked');
        var group_by_date = $('#group').is(':checked');
        

        $("#variables").val('Temp_max_emas');
        if (opt_clustering && PIPELINE==false) {
            if (Variables.length == 0) {
                notificarUsuario("You have forgot to select the variables", 'Warning');
                return 0;
            }
        } else {
            if (Variables.length == 0) {
                Variables = ["Temp_max_emas","Temp_max_merra"]
            }
        }


        if (SIL) {
            k = 0
            algh = 0
        }

        if (startDate != null) {
            startDate = startDate.format("YYYY-MM-DD");
        }
        if (endDate != null) {
            endDate = endDate.format("YYYY-MM-DD");
        }
        //DIVS PARA RESULTADOS
        $("#results2").html("")
        $("#results2").append("<div id='clust_box' style='width:100%; color:blue'></div>");
        $("#results2").append("<div id='ScatPlot' style='width:100%; color:blue'></div>");
        $("#results2").append("<div id='GeneralPlot' style='width:100%; color:blue'></div>");
        $("#results2").append("<div id='ClustPlot' style='width:100%; color:blue'></div>");
        $("#results2").append("<div id='DetailsQuery' style='width:100%; color:blue'></div>");
        $("#results2").append("<div id='clust_res' style='width:100%; color:blue'></div>");
        $("#clust_res").append("<div id='Clusters_res' style='width:100%; color:blue'></div>")
        $("#results2").append("<div id='img_res' style='width:100%; color:blue'></div>");
        $("#results2").append("<div id='summary_res' style='width:100%; color:blue'></div>")
        $("#results2").append("<div id='SSE' style='width:100%; color:blue'></div>")

        // console.log("Coord");
        // console.log(coorsJson);

        data = { coordenadas: coorsJson, shape: document.ant, startDate: startDate, endDate: endDate, K: k, type: algh, fillblank: Fill };
        data.action = "get_images_in_shape";
        data.fuentes = Fuentes.toString();
        data.variables = Variables.toString();
        //si se necesita agrupar por fecha

        var dataSend = []; //creamos un variable paa guardar el json
        dataSend = data; //igualamos a la variable general

        if (!group_by_date) {
            data.group = "1" // 1 es el valor de la fecha
            dataSend.group = "1"
        } else {
            dataSend.group = "0"
        }
        console.log(dataSend.group);
        var id_shape;
        if (espacial_selection == "regiones") {
            id_shape = $("#higroRegiones").val();
        } else if (espacial_selection == "estados") {
            id_shape = $("#states").val();
        } else if (espacial_selection == "municipios") {
            id_shape = $("#municipios").val();
        }

        var dataRet = [];

        if (espacial_selection == "regiones" || espacial_selection == "estados" || espacial_selection == "municipios" || espacial_selection == "ecoregion") {
            //Funcion de resultados guardados.
            var xhr = new XMLHttpRequest();
            var url = "includes/verificar_results.php";
            xhr.open("POST", url, false); //False significa que es sincrona la consulta
            xhr.setRequestHeader("Content-Type", "application/json");
            dataSend.idShape = id_shape; //guardamos el identificador del shape

            var dataSend_proc = { "DATA": dataSend }; //la guardamos en una general 
            var send = JSON.stringify(dataSend_proc); //lo convertimos en una cadena
            xhr.send(send); //se envia el json
            if (xhr.status == 200) {
                dataRet = JSON.parse(xhr.responseText);
                console.log(xhr.responseText);
            }
        } else {
            dataRet.Respuesta = "No";
        }


        if (!$('#chlandsat').is(":checked")) {
            $("#dropyears").html("");
        }
        document.marcadoresClima.forEach(function(item, index) {
            item.setMap(null);
        });
        data.clima = weather_selection;
        //ETIQUTAS DE COLORES
        GenerarEtiquetas();
        // ------------------------------------------------ PIPELINE -----------------------------------
        if(PIPELINE == true){
            DATA_WORKFLOW = {'data':pipe_getdata(dataSend),'type':'csv'}
            //send request to describe data
            Describe_dataset(DATA_WORKFLOW.data)
            //pipe_dag(data_for_workflow)
            $(".serviceLoadingIcon-raw").html("")
            $(".showOnMapIcon-raw").html(`<button onclick="Show_data_on_map(0,0,raw=true)" class="btn btn-primary btn-sm btn-block"><span class="glyphicon glyphicon-map-marker" aria-hidden="true"></span></button>`)
            $(".downloadDataIcon-raw").html(`<button onclick="download_data_pipe(0,'rawdata',raw=true)" class="btn btn-warning btn-sm btn-block"><span class="glyphicon glyphicon-save" aria-hidden="true"></span></button>`)
        
            return 0
        }

        // ------------------------------------------------IMAGENES DE Silhouette -----------------------------------
        if (false) {
            $.ajax({
                type: "POST", // la variable type guarda el tipo de la peticion GET,POST,..
                url: 'includes/imagenes_silhouette.php', //url guarda la ruta hacia donde se hace la peticion
                data: data, // data recive un objeto con la informacion que se enviara al servidor
                success: function(datos) { //success es una funcion que se utiliza si el servidor retorna informacion
                    GlobalImagesSil = datos
                    notificarUsuario("Graphics per Silhouette fully loaded", 'success');

                },
                error: function(data) { //se lanza cuando ocurre un error
                    console.log(data);
                },
                dataType: 'json' // El tipo de datos esperados del servidor. Valor predeterminado: Intelligent Guess (xml, json, script, text, html).
            });
        }
        // ------------------------------------------------ REGRESIONES -----------------------------------
        if (GrStat && Fuentes[0] == "EMASMAX") {
            $.ajax({
                type: "POST", // la variable type guarda el tipo de la peticion GET,POST,..
                url: 'includes/imagenes_estaciones.php', //url guarda la ruta hacia donde se hace la peticion
                data: data, // data recive un objeto con la informacion que se enviara al servidor
                success: function(datos) { //success es una funcion que se utiliza si el servidor retorna informacion
                    GlobalImages = datos
                    notificarUsuario("Graphics per station fully loaded", 'success');

                },
                error: function(data) { //se lanza cuando ocurre un error
                    console.log(data);
                },
                dataType: 'json' // El tipo de datos esperados del servidor. Valor predeterminado: Intelligent Guess (xml, json, script, text, html).
            });
        }

        // ------------------------------------------------IMAGENES POR FECHA (COMPARATIVAS) -----------------------------------
        if (GrDate && Fuentes.length == 2) {
            $.ajax({
                type: "POST", // la variable type guarda el tipo de la peticion GET,POST,..
                url: 'includes/imagenes_fechas.php', //url guarda la ruta hacia donde se hace la peticion
                data: data, // data recive un objeto con la informacion que se enviara al servidor
                beforeSend: function() {
                    $("#img_res").html("<div style='width:100%; height:20px; color:blue'></div><img src='resources/imgs/loader.gif'></img>");
                },
                success: function(datos) { //success es una funcion que se utiliza si el servidor retorna informacion
                    notificarUsuario("Graphics per date fully loaded", 'success');
                    $("#img_res").html("");
                    GlobalImagesDate = datos
                },
                error: function(data) { //se lanza cuando ocurre un error
                    console.log(data);
                },
                dataType: 'json' // El tipo de datos esperados del servidor. Valor predeterminado: Intelligent Guess (xml, json, script, text, html).
            });
        }

        // ------------------------------------------------CLUSTERING -- -----------------------------------

        // En caso de que regrese un 'No' es que no hay un resultado guardao
        if (dataRet['Respuesta'] == "No") {

            $.ajax({
                type: "POST", // la variable type guarda el tipo de la peticion GET,POST,..
                url: 'includes/differential.php', //url guarda la ruta hacia donde se hace la peticion
                data: data, // data recive un objeto con la informacion que se enviara al servidor

                beforeSend: function() {
                    $("#clust_box").html("<div style='width:100%; height:10px; color:blue'></div><img src='resources/imgs/loader.gif'></img>");
                },
                success: function(datos) { //success es una funcion que se utiliza si el servidor retorna informacion

                    Clustering_results(datos, Fuentes, opt_summary, group_by_date, opt_clustering, k);
                    //guardar datos
                    var xhr = new XMLHttpRequest();
                    url = "includes/save_results.php";
                    xhr.open("POST", url, true); //True significa que es asincrona la consulta
                    xhr.setRequestHeader("Content-Type", "application/json");

                    dataSend.Results = datos;
                    dataSend_proc = { "DATA": dataSend };
                    send = JSON.stringify(dataSend_proc);
                    xhr.send(send); //se envia el json
                    if (xhr.status == 200) {
                        dataRet = JSON.parse(xhr.responseText);

                    }
                },
                error: function(data) { //se lanza cuando ocurre un erro
                    console.log(data);
                    notificarUsuario("ERROR: Something went wrong, try again refreshing the page", 'danger');

                },
                dataType: 'json' // El tipo de datos esperados del servidor. Valor predeterminado: Intelligent Guess (xml, json, script, text, html).
            });
        } else {
            Clustering_results(dataRet['Respuesta'], Fuentes, opt_summary, group_by_date, opt_clustering, k);
        }


        // ------------------------------------------------SUMMARY -- -----------------------------------
        if (opt_summary && Fuentes.length == 2) {
            $.ajax({
                type: "POST", // la variable type guarda el tipo de la peticion GET,POST,..
                url: 'includes/summary.php', //url guarda la ruta hacia donde se hace la peticion
                data: data, // data recive un objeto con la informacion que se enviara al servidor
                beforeSend: function() {
                    console.log('entra a summary')
                },
                success: function(datos) { //success es una funcion que se utiliza si el servidor retorna informacion
                    console.log(datos)
                    notificarUsuario("Summary info fully loaded", 'success');
                    summary = JSON.parse(datos);
                    REPORTE.summary = []
                    REPORTE.summary.push({column:"EMAS",
                                        varianceMAX: summary.MAX.correlation.variance.maximaEmas,
                                        varianceMIN: summary.MIN.correlation.variance.minimaEmas,
                                        covarianceMAX: summary.MAX.correlation.covariance,
                                        covarianceMIN: summary.MIN.correlation.covariance,
                                        correlationMAX:summary.MAX.correlation.correlation,
                                        correlationMIN: summary.MIN.correlation.correlation
                                                    })
                    REPORTE.summary.push({column:"MERRA",
                                        varianceMAX: summary.MAX.correlation.variance.temp_maxMerra,
                                        varianceMIN: summary.MIN.correlation.variance.temp_minMerra,
                                        covarianceMAX: summary.MAX.correlation.covariance,
                                        covarianceMIN: summary.MIN.correlation.covariance,
                                        correlationMAX:summary.MAX.correlation.correlation,
                                        correlationMIN:summary.MIN.correlation.correlation
                    })
                    table = `<br><br><br><hr><h2>Summary</h2><table style="width:100%"><tr>
                            <th>Varianza MAX EMAS</th><th>${summary.MAX.correlation.variance.maximaEmas}</th></tr>
                            <th>Varianza MIN EMAS</th><th>${summary.MIN.correlation.variance.minimaEmas}</th></tr>

                            <tr><th>Varianza MAX MERRA</th><th>${summary.MAX.correlation.variance.temp_maxMerra}</th></tr>
                            <tr><th>Varianza MIN MERRA</th><th>${summary.MIN.correlation.variance.temp_minMerra}</th></tr>

                            <tr><th>Covarianza MAXIMAS</th><th>${summary.MAX.correlation.covariance}</th></tr>
                            <tr><th>Covarianza MINIMAS</th><th>${summary.MIN.correlation.covariance}</th></tr>

                            <tr><th>Correlacion Pearson MAXIMAS</th><th>${summary.MAX.correlation.correlation}</th></tr>
                            <tr><th>Correlacion Pearson MINIMAS</th><th>${summary.MIN.correlation.correlation}</th></tr></table>`


                    $("#summary_res").html(table);
                    $("#summary_res").append(`<button onclick="Descargar_REPORTE(['summary'])" class="btn btn-warning btn-sm btn-block"><span class="glyphicon glyphicon-save" aria-hidden="true"></span></button>`)

                },
                error: function(data) { //se lanza cuando ocurre un error
                    console.log(data);
                    notificarUsuario("ERROR: Something went wrong, try again refreshing the page", 'danger');

                },
                dataType: 'json' // El tipo de datos esperados del servidor. Valor predeterminado: Intelligent Guess (xml, json, script, text, html).
            });
        }
    } else if (weather_selection == "historico") {

        //GUARDA LAS COOKIES
        //setCookie("satelites", satelites, 60);
        //setCookie("shape", document.ant, 60); document.ant
        
        $("#results2").html("")
        var fuentes = $('input[type=radio][name=font_study]:checked').val().split(",")
        var opt_clustering = $('#clustering').is(':checked');
        var opt_summary = $('#Summay').is(':checked');
        var Fuentes = $('input[type=radio][name=font_study]:checked').val().split(",")
        var Variables = $('#variable').val()
        var algorithms = $('#algorithms-hist').val() //['kmeans','dbscan']
        var k = $("#txtKClust-hist").val();
        var epshist = Number($("#eps-hist").val());
        var min_samples = Number($("#min_samples-hist").val());
        var auto_process = $("#Silhouette_auto_hist").is(':checked');

        //variables para agglomerative
        var linkage_agg = $('#agg-linkage-hist').val() //['kmeans','dbscan']
        dbscan_params = JSON.stringify({'dbscan':{"eps":epshist,"min_samples":min_samples},'agglomerative':{"linkage":linkage_agg}})
        var period = $('#hist_periodo').val()
        if (period=="year"){specific_period=""}
        if (period=="month"){specific_period=$('#opt_periodo_historico_month').val()}
        if (period=="season"){specific_period=$('#opt_periodo_historico_season').val()}
        query_data ={'period':period,'specific_period':specific_period}

        Object.keys(GlobalMarkers).forEach(function(gk) {
            GlobalMarkers[gk]['marker'].setMap(null)
        });
        

        document.historico = []
        if (fuentes.length == 2) { CasoFuente = "D" } else if (fuentes[0] == "EMASMAX") { CasoFuente = "E" } else if (fuentes[0] == "MERRA") { CasoFuente = "M" }

        if (espacial_selection == "poligono") {
            var coorsJson = getCoors();
        } else if (espacial_selection == "regiones" || espacial_selection == "estados" || espacial_selection == "municipios" || espacial_selection == "ecoregion") {
            var coorsJson = JSON.stringify(coors);
            document.ant = "poligono"
        }


        ToSend = { coordenadas: coorsJson, fuentes: Fuentes,columns:Variables,algorithms,K: k,clustering_params:dbscan_params,query:query_data};
        
        if (auto_process){ToSend.sil = true}

        //vaciar marcadores
        document.marcadoresClima.forEach(function(item, index) {
            item.setMap(null);
        });

        GenerarEtiquetas()

        $("#results2").html("")
        $("#results2").append("<div id='H-Cluster' class='row'></div>");
        //$("#results2").append("<div id='H-Dispersion' class='row'></div>");
        $("#results2").append("<div id='H-regression' class='row'></div>");

        $("#results2").append("<div id='H-clustInfo' class='row'></div>");
        $("#results2").append("<div id='H-Gclust' class='row'></div>");
        $("#results2").append("<div id='H-clustInfo_graph' class='row'></div>");
        $("#results2").append("<div id='H-variance' class='row'></div>");
        $("#results2").append("<div id='H-Summary' class='row'></div>");

        //$("#H-variance").html("<br><br><br><hr><h2>Summary</h2><table style='width:100%'>");

        $.ajax({
            type: 'POST',
            url: 'includes/get_historico.php',
            dataType: 'json',
            data: ToSend,
            beforeSend: function() {
                $("#results").html("<div style='width:100%; height:30px; color:blue'></div><img src='resources/imgs/loading.gif'></img>");

            },
            success: function(response) {
                response.data.forEach(function(registro,index){ //limpiar topoformas e hidroregiones
                    if (response.data[index]['topoforma'] == null){response.data[index]['topoforma'] = ""}
                    if (response.data[index]['hidroregion'] == null){response.data[index]['hidroregion'] = ""}
                    response.data[index]['topoforma'] = registro['topoforma'].replace(/[^a-zA-Z ]/g, "").replace(/\s+/g, '_')
                    response.data[index]['hidroregion'] = registro['hidroregion'].replace(/[^a-zA-Z ]/g, "").replace(/\s+/g, '_')
                })

                console.log(response)
                res_stations = response.stations
                res_data = response.data
                res_clusters = response.clusters
                document.diferenciales = response //esta variable global guarda toda la respuesta

                response=null
                GlobalMarkers = new Object()

                $("#results").html("<div class='row'></div>");
                notificarUsuario("Historic data fully loaded", 'success');

                
                var colores = [];
                clustering_result_list = "<option value='1'>---</option>"
                Object.keys(res_clusters).forEach(function(index,idx){
                    clustering_result_list+= "<option value='"+index+"'>"+index+"</option>"
                });
                $("#H-Cluster").append("<select id='box_cluster_historico' class='form-control' onchange=\"ChangeClusteringHistorico(this)\">" + clustering_result_list + "</select><hr>")

                res_data.forEach(function(registro,index){
                    topoform = ""
                    Hidroregion = ""
                    Clima=""
                    Clima_desc=""
                        //limpiar de outliers
                    //res_data[index]['Temp_max_emas']= validNull(registro['Temp_max_emas'])
                    //res_data[index]['Temp_min_emas']= validNull(registro['Temp_min_emas'])

                        // validar fuente. si le hace falta un datos de ambas fuentes se clasifica como una opcion adicional
                    if(registro.Differential_max== null || registro.Differential_min== null){
                        registro.fuente = "UNKNOWN"
                        res_data[index].fuente = "UNKNOWN"
                    }

                    estcoors = { lat: parseFloat(registro['latitud']), lng: parseFloat(registro['longitud']) };
                    color = "#FF212";
                    var pinImage = new google.maps.MarkerImage("http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|" + color,
                        new google.maps.Size(21, 34),
                        new google.maps.Point(0, 0),
                        new google.maps.Point(10, 34));
            
                    var marker = new google.maps.Marker({
                        position: estcoors,
                        map: document.map,
                        icon: pinImage
                    });

                    datainfo = ""
                    di_emas = "<br><strong>Temperatura máxima promedio (EMAS)</strong> = " + registro.Temp_max_emas + " °C" +
                        "<br><strong>Temperatura mínima promedio (EMAS)</strong> = " + registro.Temp_min_emas + " °C"

                    di_merra = "<br><strong>Temperatura máxima promedio (MERRA)</strong> = " + registro.Temp_max_merra + " °C" +
                        "<br><strong>Temperatura minima promedio (MERRA)</strong> = " + registro.Temp_min_merra+ " °C" +
                        "<br><strong>Temperatura media promedio (MERRA)</strong> = " + registro.Temp_mean_merra + " °C";
                    di_dif = "<br><strong>DIFERENCIAL máxima promedio (MERRA-EMAS)</strong> = " + registro.Differential_max + " °C" +
                        "<br><strong>DIFERENCIAL mínima promedio (MERRA-EMAS)</strong> = " + registro.Differential_min + " °C"
                    if (CasoFuente == "D") {
                        datainfo += "<hr>" + di_emas + "<hr>" + di_merra + "<hr>" + di_dif + "</div>"
                    }
                    if (CasoFuente == "E") {
                        datainfo += "<hr>" + di_emas + "</div>"
                    }
                    if (CasoFuente == "M") {
                        datainfo += "<hr>" + di_merra + "</div>"
                    }

                    //Se añade info de etiquettas de clima, topoforma, etc
                    descriptive_info = ""
                    if ("topoforma" in registro) { 
                        topoform = registro['topoforma']
                        descriptive_info+="<br><strong>Topoforma: "+registro['topoforma']+"</strong>"
                    }
                    if ("hidroregion" in registro){ 
                        Hidroregion = registro['hidroregion']
                        descriptive_info+="<br><strong>Hidroregion: "+registro['hidroregion']+"</strong>"
                    }
                    if ("clima_label" in registro){ 
                        Clima = registro['clima_label']
                        Clima_desc = registro['clima_desc']
                        descriptive_info+="<br><strong>Clima : "+registro['clima_desc']+"</strong>"
                    }

                    var infowindow = new google.maps.InfoWindow({
                        content: "<div><div><strong>" + registro['antena'] + "</strong></div>\
                            <strong>Latitud </strong>="+ registro['latitud'] +
                            "<br><strong>Longitud</strong> = " + registro['longitud'] +
                            "<br><strong>Longitud</strong> = " + registro['altitud'] +
                            "<div id='div'>"+descriptive_info+"</div>" +
                            "<div id='div'>"+datainfo+"</div>" +
                            "</div>"
                    });
            
                    marker.addListener('click', function() {
                        infowindow.open(document.map, marker);
                    });


                    GlobalMarkers[res_stations[index]] = { "marker": marker,filtros:{"source":true},"source":registro.fuente}

                    var SeFiltraTopoforma = $("#filt_topo").is(":checked");
                    var SeFiltraHidroregion = $("#filt_hidro").is(":checked")
                    var SeFiltraClima = $("#filt_clima").is(":checked")

                    lista_filtros = {}
                    lista_filtros['source']=true
                    if (SeFiltraTopoforma){
                        lista_filtros['topoform']=true
                        GlobalMarkers[res_stations[index]]["topoform"] = topoform
                        GlobalMarkers[res_stations[index]].filtros["topoform"]= true
                    }
                    if (SeFiltraHidroregion){
                        lista_filtros['hidroregion']=true
                        GlobalMarkers[res_stations[index]]["hidroregion"] = Hidroregion
                        GlobalMarkers[res_stations[index]].filtros["hidroregion"]= true
                    }
                    if (SeFiltraClima){
                        lista_filtros['weather']=true
                        GlobalMarkers[res_stations[index]]["weather"] = Clima
                        GlobalMarkers[res_stations[index]].filtros["weather"]= true
                    }

                    document.dataAAS = GlobalMarkers // la funcion de filtros usa dataAAS para funcionar

                });
                // ====================== Grafica de regresion ===========================
                    //se crearan 3 imagenes, max min y mean
                    $("#modal-gallery-carrusel-items").html("")//se vacía el modal
                    DT = document.diferenciales.regression
                    list_graph_pairs = [["Mean_merra","Mean_emas"],
                                        ['Temp_max_merra','Temp_max_emas'],
                                        ['Temp_min_merra','Temp_min_emas']]
                    titles_list = ["Mean temperatures trend","MAX temperatures trend", "MIN temperatures trend"]

                    class_active="active"
                    list_graph_pairs.forEach(function(v,index){
                        temp = {"raw":{"merra":DT.raw[v[0]],"emas":DT.raw[v[1]]}
                        ,"predict":{"merra":DT.predict[v[0]],"emas":DT.predict[v[1]]}}

                        $("#modal-gallery-carrusel-items").append(`<div class="carousel-item ${class_active}"> <div class="d-block w-100" id="mgci-${index}"></div> </div>`)
                        class_active=""
                        CrearGraficaRegresion(`mgci-${index}`,temp,titles_list[index],"Temperature","year")
                    })

                    $("#H-regression").html(`<button type="submit" id="btnReg" 
                        class="btn btn-outline-primary btn-block" data-toggle="modal" 
                        data-target="#modal-gallery">Regression</button>`)


                // ====================== Grafica de scores ===========================
                if(auto_process){
                    res_scores = document.diferenciales.scores
                    //reorganizar scores
                    org_res_scores = {}
                    Object.keys(res_scores).forEach(function(name_clust){ //se crea el dict
                        name_clust=name_clust.split("_")
                        console.log(name_clust)
                        k_clust = name_clust[1];variant_clust =name_clust[2];name_clust=name_clust[0]

                        if (!Object.keys(org_res_scores).includes(name_clust)){org_res_scores[name_clust+"_"+variant_clust]={"ch":[],"db":[]}}

                    });
                    Object.keys(org_res_scores).forEach(function(name_clust){ //se rellena el dict en orden
                        name_clust=name_clust.split("_")
                        variant_clust =name_clust[1];name_clust=name_clust[0]
                        for(i=2;i<=parseInt(k);i++){
                            org_res_scores[name_clust+"_"+variant_clust]['ch'].push(res_scores[name_clust+"_"+i+"_"+variant_clust]["calinski_harabasz"])
                            org_res_scores[name_clust+"_"+variant_clust]['db'].push(res_scores[name_clust+"_"+i+"_"+variant_clust]["davies_bouldin"])
                        }
                    })
                    const range = (min, max) => [...Array(max - min + 1).keys()].map(i => i + min);
                    console.log("validation index")
                    CrearGrafica2Axis("H-clustInfo_graph",org_res_scores,range(2, parseInt(k)),"Validation scores","calinski_harabasz score", "davies_bouldin score","value of k" )
                }
                // ==================== filtros para las antenas =======================
                $("#results2").append("<div  id='map_filtters' class='row'> </div>")
                lista_global_filtros = {} // se requiere vaciar la lista de filtros
                Object.keys(lista_filtros).forEach(function(flt){
                    HabiltarFiltroDinamico("#map_filtters",flt,encabezado=true)
                });
                //Actualizar_Filtro_datos()

                //HabilitarFiltros(Emas=true)

                // estadisticos harcodeados
                        params1 = { columns: 'Temp_max_emas,Temp_max_merra' }
                        params2 = { columns: 'Temp_min_emas,Temp_min_merra' }

                        djson = { datos: JSON.stringify(res_data), params: params1 }
                        //djson2 = { datos: res_data, params: params2 }

                        if (opt_summary) {
                            $.ajax({
                                type: 'POST',
                                url: 'includes/summaryAAS.php',
                                dataType: 'json',
                                data: djson,
                                success: function(response) {
                                    //console.log(response)
                                    notificarUsuario("Summary info fully loaded", 'success');
                                    summary = JSON.parse(response);
                                    table = `
                                        <tr><th>Varianza MAX EMAS</th><th>${summary.correlation.variance.Temp_max_emas}</th></tr>      
                                        <tr><th>Varianza MAX MERRA</th><th>${summary.correlation.variance.Temp_max_merra}</th></tr>
                                        <tr><th>Covarianza MAXIMAS</th><th>${summary.correlation.covariance}</th></tr>
                                        <tr><th>Correlacion Pearson MAXIMAS</th><th>${summary.correlation.correlation}</th></tr>`


                                    $("#H-variance").append(table);
                                },
                                error: function(data) { //se lanza cuando ocurre un error
                                    console.log(data);
                                    console.log(data.responseText);
                                    notificarUsuario("ERROR: Something went wrong, please try again ", 'danger');
                                }
                            });

                            djson.params=params2

                            $.ajax({
                                type: 'POST',
                                url: 'includes/summaryAAS.php',
                                dataType: 'json',
                                data: djson,
                                success: function(response) {
                                    //console.log(response)
                                    notificarUsuario("Summary info fully loaded", 'success');
                                    summary = JSON.parse(response);
                                    table = `
                                            <tr><th>Varianza MIN EMAS</th><th>${summary.correlation.variance.Temp_min_emas}</th></tr>      
                                            <tr><th>Varianza MIN MERRA</th><th>${summary.correlation.variance.Temp_min_merra}</th></tr>
                                            <tr><th>Covarianza MINIMAS</th><th>${summary.correlation.covariance}</th></tr>
                                            <tr><th>Correlacion Pearson MINIMAS</th><th>${summary.correlation.correlation}</th></tr>`


                                    $("#H-variance").append(table);
                                },
                                error: function(data) { //se lanza cuando ocurre un error
                                    console.log(data);
                                    console.log(data.responseText);
                                    notificarUsuario("ERROR: Something went wrong, please try again ", 'danger');
                                }
                            });
                            djson = null //vaciar variable para liberar memoria
                        }

                        //SE COMIENZA A CONSTRUIR LAS GRAFICAS
                        


//
            },
            error: function(data) { //se lanza cuando ocurre un error
                console.log(data);
                console.log(data.responseText);
                notificarUsuario("ERROR: Something went wrong, please try again ", 'danger');
           }
       });



    } 
}

function clean_region() {
    if (document.polygons_reg.length > 0) {
        document.polygons_reg.forEach(function(item, index) {
            item.setMap(null)
        });
        coors = [];
    }
}

function clean_state() {
    if (document.polygons_states.length > 0) {
        document.polygons_states.forEach(function(item, index) {
            item.setMap(null)
        });
        coors = [];
    }
}

function clean_mun() {
    if (document.polygons_mun.length > 0) {
        document.polygons_mun.forEach(function(item, index) {
            item.setMap(null)
        });
        coors = [];
    }
}

function clean_eco() {
    if (document.polygons_eco.length > 0) {
        document.polygons_eco.forEach(function(item, index) {
            item.setMap(null)
        });
        coors = [];
    }
}

function draw_ecoregion() {
    clean_eco();
    url = 'includes/get_eco_by_id.php?id=' + $("#ecoregion").val()
    console.log(url);
    $.getJSON(url,
        function(data) {
            var color = "ff5733"
            var coordinates = data[0]['coordinates'];
            var n = coordinates.length;

            var m;
            var auvCoor = []
            for (var i = 0; i < n; i++) {
                // var coordinatesGoogle = [];
                m = coordinates[i].length;
                coordinatesArr = m != 1 ? coordinates[i] : coordinates[i][0];
                m = coordinatesArr.length;
                // console.log(m);
                for (var j = 0; j < m; j++) {
                    var coordinatesGoogle = [];
                    var numCoord = coordinatesArr[j][0].length;
                    auvCoor = coordinatesArr[j][0];
                    for (let k = 0; k < numCoord; k++) {
                        // console.log(auvCoor[k]);
                        coordinatesGoogle.push({ lat: auvCoor[k][1], lng: auvCoor[k][0] })
                        coors.push({ lat: auvCoor[k][1], lon: auvCoor[k][0] })
                    }
                    //console.log(color);
                    var polygon = new google.maps.Polygon({
                        paths: coordinatesGoogle,
                        strokeColor: "#" + color,
                        strokeWeight: 2,
                        fillColor: "#" + color,
                        fillOpacity: 1
                    });
                    polygon.setMap(document.map);
                    document.polygons_eco.push(polygon);

                }


            }
        });
}


function draw_mun() {
    clean_mun();

    console.log(url);
    var id_states = "municipios";
    $("#munDiv").html("<h3> " + document.lngarr['states'] + "</h3>");
    $("#munDiv").append("<select id=" + id_states + " onchange=\"draw_mun_id()\" data-live-search=\"true\">");
    $("#municipios").append("<option disabled selected> " + document.lngarr["select_region"] + "</option>");


    url = 'includes/get_mun_by_state.php?id=' + $("#states").val()

    $.getJSON(url, function(data) {

        for (var i = 0; i < data.length; i++) {
            $("#municipios").append("<option id=" + data[i]['id'] + " value= " + data[i]['id'] + "> " + data[i]['nombre'] + "</option>");
        }
        $("#munDiv").append("</select>");
        $("#municipios").addClass("form-control");
        $("#municipios").addClass("selectpicker");
        $(".selectpicker").selectpicker('refresh');
    });

}

// $("#higroRegiones").change(
function draw_region() {

    clean_region();
    console.log("entro a una region");
    url = 'includes/get_region_by_id.php?id=' + $("#higroRegiones").val()
    console.log(url);
    $.getJSON(url, function(data) {
        tipo_coor= "topoformas"
        var coordinates = data[0][tipo_coor];
        var n = coordinates.length;
        var m;
        console.log(coordinates.length) //cantidad de topoformas por region

        coordinates_shape= data[0]['coordinates'] //coordenadas de la hidroregion (para la cosulta)
        for (var i = 0; i < coordinates_shape.length; i++) {
            m = coordinates_shape[i].length;
            coordinate_hr = m != 1 ? coordinates_shape[i] : coordinates_shape[i][0];
            m = coordinate_hr.length;

            //console.log(m);
            for (var j = 0; j < m; j++) {
                if (j < 1) {
                    console.log(coordinate_hr[j].length);
                }
                coors.push({ lat: coordinate_hr[j][1], lon: coordinate_hr[j][0] })
            }
        }


        if (tipo_coor=="topoformas")
        {
            for (var t = 0; t < coordinates.length; t++) { // por cada topoforma 
                topoforma = coordinates[t]['coordinates']
                nombre_topoforma = coordinates[t]['nombre'].replace(/[^a-zA-Z ]/g, "").replace(/\s+/g, '_')
                if (!(nombre_topoforma in GlobalColorTopoformas)){
                    GlobalColorTopoformas[nombre_topoforma]= Math.floor(Math.random() * 16777215).toString(16)
                }
                color = GlobalColorTopoformas[nombre_topoforma]
                
                var n = topoforma.length;
                for (var i = 0; i < n; i++) {
                    m = topoforma[i].length; // cantidad posible de array de poligonos o coordenadas
                    if (topoforma[i][0].length ==2){ //es de coordenadas
                        var coordinatesGoogle = [];
                        coordinatesArr = topoforma[i]
                        cant_coord = m
                        //console.log(m);
                        for (var j = 0; j < cant_coord; j++) {
                            if (j < 1) {
                                    console.log(coordinatesArr[j].length);
                            }
                            coordinatesGoogle.push({ lat: coordinatesArr[j][1], lng: coordinatesArr[j][0] })
                        }
            
                        //console.log(color);
                        var polygon = new google.maps.Polygon({
                            paths: coordinatesGoogle,
                            coordiantes_arr:coordinatesGoogle,
                            strokeColor: "#" + color,
                            strokeWeight: 2,
                            fillColor: "#" + color,
                            fillOpacity: 1,
                            content: nombre_topoforma,
                            clickable:true
                        });
                        polygon.setMap(document.map);

                        var infowindow = new google.maps.InfoWindow({pixelOffset: new google.maps.Size(0, -10),
                            disableAutoPan: true});
                        infowindow.opened = false;

                        function mousefn(evt) {
                            var bounds = new google.maps.LatLngBounds();
                            for (var q = 0; q < this.coordiantes_arr.length; q++) {
                              bounds.extend(this.coordiantes_arr[q]);
                            }  
                            infowindow.setContent(this.content);
                            infowindow.setPosition(this.coordiantes_arr[1]);
                            infowindow.open(document.map);
                        }
                        google.maps.event.addListener(polygon, 'mouseover', mousefn);
                        // google.maps.event.addListener(mrpdPolygon, 'mousemove', mousefn);
                        google.maps.event.addListener(polygon, 'mouseout', function(evt) {
                          infowindow.close();
                          infowindow.opened = false;
                        });
                        document.polygons_reg.push(polygon);


                    }
                    else{ //son poligonos
                        cant_poly =m
                        for (var p = 0; p < cant_poly; p++) {
                            var coordinatesGoogle = [];
                            coordinatesArr = topoforma[i][p]
                            cant_coord = coordinatesArr.length
                            //console.log(m);
                            for (var j = 0; j < cant_coord; j++) {
                                if (j < 1) {
                                        console.log(coordinatesArr[j].length);
                                }
                                coordinatesGoogle.push({ lat: coordinatesArr[j][1], lng: coordinatesArr[j][0] })
                            }
                
                            var polygon = new google.maps.Polygon({
                                paths: coordinatesGoogle,
                                coordiantes_arr:coordinatesGoogle,
                                strokeColor: "#" + color,
                                strokeWeight: 2,
                                fillColor: "#" + color,
                                fillOpacity: 1,
                                content: nombre_topoforma,
                                clickable:true
                            });
                            polygon.setMap(document.map);

                            var infowindow = new google.maps.InfoWindow({pixelOffset: new google.maps.Size(0, -10),
                                disableAutoPan: true});
                            infowindow.setOptions({disableAutoPan:false})
                            infowindow.opened = false;
                        
                            function mousefn(evt) {
                                var bounds = new google.maps.LatLngBounds();
                                for (var q = 0; q < this.coordiantes_arr.length; q++) {
                                  bounds.extend(this.coordiantes_arr[q]);
                                }  
                                infowindow.setContent(this.content);
                                infowindow.setPosition(this.coordiantes_arr[1]);
                                infowindow.open(document.map);
                            }
                            google.maps.event.addListener(polygon, 'mouseover', mousefn);
                            // google.maps.event.addListener(mrpdPolygon, 'mousemove', mousefn);
                            google.maps.event.addListener(polygon, 'mouseout', function(evt) {
                              infowindow.close();
                              infowindow.opened = false;
                            });
                            document.polygons_reg.push(polygon);
    
                        }
                    }

                }
            }
        }

    });
}


function draw_mun_id() {
    clean_mun();
    url = 'includes/get_mun_by_id.php?id=' + $("#municipios").val()
    console.log(url);
    $.getJSON(url, function(data) {
        console.log(data[0]['coordinates']);
        var color = "ff5733";
        var coordinates = data[0]['coordinates'];
        var n = coordinates.length;
        var m;
        for (var i = 0; i < n; i++) {
            var coordinatesGoogle = [];
            m = coordinates[i].length;
            coordinatesArr = m != 1 ? coordinates[i] : coordinates[i][0];
            m = coordinatesArr.length;
            //console.log(m);
            for (var j = 0; j < m; j++) {
                //console.log(coordinatesArr[j]);
                coordinatesGoogle.push({ lat: coordinatesArr[j][1], lng: coordinatesArr[j][0] })
                coors.push({ lat: coordinatesArr[j][1], lon: coordinatesArr[j][0] })
            }

            //console.log(color);
            var polygon = new google.maps.Polygon({
                paths: coordinatesGoogle,
                strokeColor: "#" + color,
                strokeWeight: 2,
                fillColor: "#" + color,
                fillOpacity: 1
            });
            polygon.setMap(document.map);
            document.polygons_mun.push(polygon);
        }
    });
}

// $("#states").change(
function draw_state() {
    clean_state();
    url = 'includes/get_shapeby_id.php?id=' + $("#states").val()
    console.log(url);
    $.getJSON(url, function(data) {
        var color = "ff5733"
        var coordinates = data[0]['coordinates'];
        var n = coordinates.length;
        var m;
        for (var i = 0; i < n; i++) {
            var coordinatesGoogle = [];
            m = coordinates[i].length;
            coordinatesArr = m != 1 ? coordinates[i] : coordinates[i][0];
            m = coordinatesArr.length;
            //console.log(m);
            for (var j = 0; j < m; j++) {
                // console.log(coordinatesArr[j]);
                coordinatesGoogle.push({ lat: coordinatesArr[j][1], lng: coordinatesArr[j][0] })
                coors.push({ lat: coordinatesArr[j][1], lon: coordinatesArr[j][0] })
            }

            //console.log(color);
            var polygon = new google.maps.Polygon({
                paths: coordinatesGoogle,
                strokeColor: "#" + color,
                strokeWeight: 2,
                fillColor: "#" + color,
                fillOpacity: 1
            });
            polygon.setMap(document.map);
            document.polygons_states.push(polygon);
        }
    });
}
// );

function show_clustering_values(values, colors, k) {
    console.log(values);
    $("#results2").html("");
    for (var i = 0; i < k; i++) {
        console.log(values[i]);
        $("#results2").append("<br><br><span class=\"dot\" style=\"background-color: #" + colors[i] + "\"></span> <strong>Cluster " + i + "</strong><br><hr>").fadeIn('slow');
        $("#results2").append("Temperatura: " + values[i]['mean_temperature'] + "C</br>");
        $("#results2").append("Humedad: " + values[i]['humedad'] + "</br>");
        $("#results2").append("Velocidad rafaga: " + values[i]['vel_rafaga'] + "</br>");
        $("#results2").append("Velocidad del viento: " + values[i]['vel_viento'] + "</br>");
        $("#results2").append("Presion baromérica: " + values[i]['presion_barometrica'] + "</br>");
        $("#results2").append("Radiación solar: " + values[i]['radiacion_solar'] + "</br>");
        $("#results2").append("Precipitacion: " + values[i]['precipitacion'] + "</br>");
    }
}

function show_shape(code, color, map) {
    console.log("entro");
    $.ajax({
        url: 'includes/get_shape.php?state=' + code,
        dataType: 'json',
        success: function(data) {
            //console.log(color);
            var coordinates = data['geometry']['coordinates'];
            var n = coordinates.length;
            var coordinatesGoogle = [];
            var m = 0;
            //var color = colors[cluster];
            //console.log(color);
            //console.log(cluster);
            //console.log(coordinates.length);
            for (var i = 0; i < n; i++) {
                var coordinatesGoogle = [];
                m = coordinates[i].length;
                coordinatesArr = m != 1 ? coordinates[i] : coordinates[i][0];
                m = coordinatesArr.length;
                //console.log(m);
                for (var j = 0; j < m; j++) {
                    //console.log(coordinatesArr[j]);
                    coordinatesGoogle.push({ lat: coordinatesArr[j][1], lng: coordinatesArr[j][0] })
                }

                //console.log(color);
                var polygon = new google.maps.Polygon({
                    paths: coordinatesGoogle,
                    strokeColor: "#" + color,
                    strokeWeight: 2,
                    fillColor: "#" + color,
                    fillOpacity: 1
                });
                polygon.setMap(map);
                document.polygons_states.push(polygon);
            }
        }
    });
    /*$.getJSON('includes/get_shape.php?state=' + code, {
  }, function(data) {
console.log(data);
      //console.log(color);
      var coordinates = data['geometry']['coordinates'];
      var n = coordinates.length;
      var coordinatesGoogle = [];
      var m = 0;
      //var color = colors[cluster];
      //console.log(color);
      //console.log(cluster);
      //console.log(coordinates.length);
      for (var i = 0; i < n; i++) {
        var coordinatesGoogle = [];
        m = coordinates[i].length;
        coordinatesArr = m != 1 ? coordinates[i] : coordinates[i][0];
        m = coordinatesArr.length;
        //console.log(m);
        for(var j = 0; j < m; j++){
            //console.log(coordinatesArr[j]);
            coordinatesGoogle.push({lat:coordinatesArr[j][1], lng:coordinatesArr[j][0]})
        }
        
        //console.log(color);
        var polygon = new google.maps.Polygon({
            paths: coordinatesGoogle,
            strokeColor: "#" +  color,
            strokeWeight: 2,
            fillColor: "#" +  color,
            fillOpacity: 1
        });
        polygon.setMap(map);
        document.polygons_states.push(polygon);
      }
  });*/
}

var names = ["Tmp Max", "Tmp Min", "Precipitation"];

function getCorrelations(stations, ii, k, colors) {

    if (stations[ii].length > 0) {
        $.ajax({
            type: 'POST',
            url: 'includes/controladores/getRegresions.php',
            dataType: 'json',
            data: { stations: stations[ii] },
            success: function(response) {
                console.log(response);
                var i = 0;
                $("#results2").append("<br><br><span class=\"dot\" style=\"background-color: #" + colors[ii] + "\"></span> <strong>Cluster " + ii + "</strong><br><hr>").fadeIn('slow');
                response.forEach(function(item) {
                    console.log(SERVER_URL + "includes/controladores/" + item);
                    $("#results2").append("<a onclick=\"viewImage('" + SERVER_URL + "/includes/controladores/" + item + "')\" >" + names[i] + "</a> ");
                    i++;
                });
                //console.log(ii,k);
                if (ii < k) {
                    getCorrelations(stations, ii + 1, k, colors);
                }
            },
            error: function(data) { //se lanza cuando ocurre un error
                if (ii < k) {
                    getCorrelations(stations, ii, k, colors);
                }
                console.log(data.responseText);
            }
        });
    } else if (ii < k) {
        getCorrelations(stations, ii + 1, k, colors);
    }

}

function viewImage(imgSrc) {
    $(".modal-footer").html("<span id='txtWhereIs' class='form-control-static pull-left'></span> \
        <button type='button' class='btn btn-default' data-dismiss='modal'>Cerrar</button>\
        <a type='button' class='btn btn-default' href='" + imgSrc + "' download='' target='_blank' >Descargar</a>")

    $('#imagepreview').attr('src', imgSrc); // here asign the image to the modal when the user click the enlarge link
    $('#imagepreview').attr('data-big', imgSrc); // here asign the image to the modal when the user click the enlarge link
    //$('#imagepreview').attr('height','500px');
    $('#imagepreview').attr('width', '500px');
    $('#imagemodal').modal('show'); // imagemodal is the id attribute assigned to the bootstrap modal, then i use the show function
}

/*
 * convierte un arreglo a JSON
 */
function toJSON(arr) {
    return JSON.stringify(Object.keys(arr));
}

/*
 * regresa las coordenadas del poligono en el mapa en formato JSON
 */
function getCoors() {
    var arrJson = [];
    for (var key in coors) {
        if (coors.hasOwnProperty(key)) {
            arrJson.push(coors[key]['decimal']);
        }
    }
    return JSON.stringify(arrJson);
}

/*
 * regresa los satelites seleccionados en un arreglo
 */
function getSats() {
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
function updateCarSession(item, action) {
    $.ajax({
        type: 'POST',
        url: 'includes/update_downloads.php',
        dataType: 'json',
        data: { agregadas: item, action: action },
        success: function(response) {
            $("#lblNumberProducts").html(response);
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

/*
 * DESCARGA LAS IMAGENES AGREGADAS A LA COLA DE DESCARGA
 */
function downloadImages() {
    console.log("entro");
    $.ajax({
        type: 'POST',
        url: 'includes/download_images.php',
        data: { descargar: "xxx" },
        beforeSend: function() {
            $('#modDownload').modal('show');
            notificarUsuario(document.lngarr['preparing'], 'info');
            $("#mensajedownload").html(document.lngarr['preparing']);
        },
        success: function(response) {
            if (response.length > 0) {
                notificarUsuario('File ready', 'info');
                $('#modDownload').modal('show');
                $("#mensajedownload").html('<a id="btnDownloadImages" download>' + document.lngarr['downloadimgs'] + '</a>');
                $("#btnDownloadImages").attr("href", response);
                urlAnt = document.lngarr['downloadimgs'];
            } else {
                $('#modDownload').modal('hide');
                notificarUsuario(document.lngarr['noaddimgs'], 'danger');
            }
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

/*
 * AGREGA UN ELEMENTO AL CARRITO DE DESCARGAS
 */
function addToCar(id, action) {
    action = arguments[0][2];
    id = arguments[0][1];
    //console.log(id);
    if (action == "add") {
        $("#chooseJPG").prop('checked', false);
        $("#chooseMeta").prop('checked', false);
        $("#spanImagen").html(id);
        $('#productsmodal').modal('hide');
        $("#modChoose").modal('show');
    } else {
        $("#btn" + id).html("<button title='Agregar a descargas' type='button'  onclick='checkSession(\"addToCar\",\"" + id + "\",\"add\")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span></button>");
        updateCarSession(id, action);
    }
}

/*
 * CAMBIA EL SATELITE SELECCIONADO
 */
function changeSatelite(satelite) {
    $('.satelite:checked').each(
        function() {
            $('#ch' + $(this).val()).prop('checked', false);
        }
    );
    $('#ch' + satelite).prop('checked', true);
    toResults();
}

/**
 * CAMBIA LA IMAGEN DEL PRODUCTO DERIVADO SELECCIONADO
 */
function changeImageProduct(index) {
    $('#imgproduct').attr('src', 'resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/' + document.derivados[index]['descriptor'] + '.jpg');
    $("#imgdescription").html(document.derivados[index]['description']);
}

/**
 * MUESTRA LOS PRODUCTOS DERIVADOS DE UNA IMAGEN
 */
function verProducts(imagen, nombre) {
    $("#titleModProducs").html(document.lngarr['derprods'] + nombre);
    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Images.php',
        dataType: 'json',
        data: { img: imagen, action: 'get_derivados' },
        success: function(response) {
            document.derivados = response['derivados'];
            if (document.derivados.length > 0) {
                $('#imgproduct').attr('src', 'resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/' + document.derivados[0]['descriptor'] + '.jpg'); // here asign the image to the modal
                $("#imgdescription").html(document.derivados[0]['description']);
                tabla = "";
                document.it = 0;
                document.derivados.forEach(function(item, index) {
                    tabla += "<tr><td><a href='javascript:;' onclick='changeImageProduct(" + document.it + ")'>" + item['descriptor'] + "</a></td><td>" + item['short_description'] + "</td><td><span id='btn" + item['descriptor'] + "'><button title='" + document.lngarr['download'] + "' type='button'  onclick='checkSession(\"addToCar\",\"" + item['descriptor'] + "\",\"add\")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span></button></span></td><td>";
                    for (var i = 1; i <= 5; i++) {
                        if (i <= item['rating']) {
                            tabla += '<button id="btnStar' + item['idelemento'] + i + '" onclick=\'checkSession(\"rate\",this,\"' + item['idelemento'] + '\",\"' + i + '\")\' type="button" class="btn btn-default btn-xs"><span class="glyphicon glyphicon-star" aria-hidden="true"></span></button>';
                        } else {
                            tabla += '<button id="btnStar' + item['idelemento'] + i + '" onclick=\'checkSession(\"rate\",this,\"' + item['idelemento'] + '\",\"' + i + '\")\' type="button" class="btn btn-default btn-xs"><span class="glyphicon glyphicon-star-empty" aria-hidden="true"></span></button>';
                        }
                    }
                    //url = 
                    tabla += "</td><td>" +
                        "<a href='#' data-trigger='focus' title='URL' data-toggle='popover' data-placement='left' data-content='" +
                        "<ul><li><a onclick=copyTextToClipboard(\"" + response['url'] + item['hash_name'] + "\")>" + document.lngarr['desccopbtn'] + "</a></li>" +
                        "<li><a href=\"element.php?elemento=" + item['hash_name'] + "\">" + document.lngarr['go'] + "</a></li></ul>'><span class='glyphicon glyphicon-copy' aria-hidden='true'></span></a></td></tr>";
                    document.it++;
                });
                $("#tblchilds").html(tabla);
                $('[data-toggle="popover"]').popover({
                    animation: true,
                    html: true
                });
                $('#productsmodal').modal('show');
            } else {
                notificarUsuario(document.lngarr['theimg'] + nombre + document.lngarr['donthave'], 'danger');
            }
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

/*
 * carga una busqueda previamente hecha
 */
function loadSearch() {
    idbusqueda = arguments[0][1];
    console.log("CARGANDO BUSQUEDA ..." + idbusqueda);
    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Logs.php',
        dataType: 'json',
        data: { busqueda: idbusqueda, action: "get_search" },
        success: function(response) {
            forma = response['busqueda'][0]['tipo'];
            filtro = response['busqueda'][0]['filtro'];
            startDate = response['busqueda'][0]['fecha_inicial'];
            endDate = response['busqueda'][0]['fecha_final'];
            setDate(startDate, endDate);
            response['satelites'].forEach(function(val, ind) {
                $('#ch' + val[0]).prop('checked', true);
            });
            $("#chproductos").prop("checked", response['busqueda'][0]["derivados"]);

            for (var key in FILTROS) {
                if (FILTROS[key] === filtro) {
                    filtro = key;
                    break;
                }
            }
            $("#rd" + capitalizeFirstLetter(filtro)).prop("checked", true);
            switch (forma) {
                case 1: //poligono
                    poligono = response['data'][0]['polygon'];
                    poligono = poligono.replace(/"/g, "").replace(/'/g, "").replace(/\(|\)/g, "");
                    coordenadas = poligono.split(",");
                    for (i = 0; i < coordenadas.length; i += 2) {
                        addCoorToPoli(coordenadas[i + 1], coordenadas[i]);
                    }
                    document.ant = "poligono";
                    //cleanMap();
                    break;
                case 2: //circulo
                    radio_cir = Number(response['data'][0]['radius']);
                    lat_ctr = Number(response['data'][0]['center_lat']);
                    lon_ctr = Number(response['data'][0]['center_lon']);
                    addCircle(lat_ctr, lon_ctr, radio_cir);
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
                    addCoorToPoli(lat_p, lon_p);
                    document.ant = "nombre";
                    break;
                default:
            }
            console.log("heyyyyy")
            toResults();

        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

/**
 * CAMBIA EL FILTRO DE BUSQUEDA
 */
function mostrarImgs(filter) {
    var $radios = $('input:radio[name=radiosResultados]');
    $radios.filter('[value=' + filter + ']').prop('checked', true);
    toResults();
}

/*
 * MUESTRA UNA IMAGEN EN UN MODAL
 */
function showImage(item, rightP = false, idrecomendacion = -1) {
    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Images.php',
        dataType: 'json',
        data: { action: 'view_image', image: item, rightP: rightP, idrecomendacion: idrecomendacion },
        success: function(response) {
            //console.log(response);
            $('#imagepreview').attr('src', 'resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/' + response[1] + '.jpg'); // here asign the image to the modal when the user click the enlarge link
            $('#imagepreview').attr('data-big', 'resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/' + response[1] + '.jpg'); // here asign the image to the modal when the user click the enlarge link
            $('#imagepreview').attr('height', '500px');
            $('#imagemodal').modal('show'); // imagemodal is the id attribute assigned to the bootstrap modal, then i use the show function
            $("#txtWhereIs").html("<strong>Centro de la imágen en:</strong> ");
            $("#imagepreview").mlens({
                imgSrc: $("#imagepreview").attr("data-big"), // path of the hi-res version of the image
                lensShape: "circle", // shape of the lens (circle/square)
                lensSize: 180, // size of the lens (in px)
                borderSize: 4, // size of the lens border (in px)
                borderColor: "#fff", // color of the lens border (#hex)
                borderRadius: 0, // border radius (optional, only if the shape is square)
                zoomLevel: 3,
                imgOverlay: $("#imagepreview").attr("data-overlay"), // path of the overlay image (optional)
            });
            if (response['city'] != null) {
                $("#txtWhereIs").append(response['city']);
            }

            if (response['state'] != null) {
                $("#txtWhereIs").append(", " + response['state']);
            }

            if (response['country'] != null) {
                $("#txtWhereIs").append(", " + response['country']);
            }

        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

function getDataPolygon(year, month) {
    var satelites = getSats();
    if (document.place.length > 0) {
        //console.log("entro1");
        data = {
            satelites: satelites,
            year: year,
            month: month,
            lat: place_coors['lat'],
            lon: place_coors['lon'],
            state: document.state,
            country: document.country,
            city: document.city,
            action: "get_images_date_point"
        };
    } else {
        //console.log("entro");
        radio = document.ant == "circulo" ? document.shape.getRadius() : 0;
        coorsJson = getCoors();
        data = {
            satelites: satelites,
            year: year,
            month: month,
            result: coorsJson,
            shape: document.ant,
            radio: radio,
            action: "get_images_date_shape"
        };
    }
    return data;
}

/**
 * MUESTRA TODAS LAS IMAGENES EN EL MAPA DE UN POLIGONO
 */
function polygonImagesToMap(elemento, year, month, tipo, satelite, rightP = false, idrecomendacion) {
    var data = getDataPolygon(year, month);
    if (rightP) {
        data.rightP = true;
        data.action = "get_images_date_shape";
        data.idrecomendacion = idrecomendacion;
    }
    data["clic"] = "view_image_on_map_poly";
    data.satelites = [satelite];

    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Images.php',
        dataType: 'json',
        data: data,
        success: function(response) {
            var i = 0;
            if (tipo == "poligono") {
                response.forEach(function(item, index) {
                    polygonToMap(elemento, item["hash_name"], "view_polygon_poly");
                });
            } else {
                response.forEach(function(item, index) {
                    imageToMap(elemento, item["hash_name"], "view_image_on_map_poly");
                });
            }
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}
/*
 * MUESTRA LAS IMAGENES EN UN POLIGONO
 */
function showImagesPolygon(year, month, satelite, rightP = false, idrecomendacion = -1) {

    var satelites = [satelite];
    data = {};
    if (document.place.length > 0) {
        data = { satelites: satelites, year: year, month: month, lat: place_coors['lat'], lon: place_coors['lon'], state: document.state, country: document.country, city: document.city, action: "get_images_date_point" };
    } else {
        radio = document.ant == "circulo" ? document.shape.getRadius() : 0;
        data = { satelites: satelites, year: year, month: month, result: getCoors(), shape: document.ant, radio: radio, action: "get_images_date_shape" };
    }

    if (rightP) {
        data.action = "get_images_date_shape";
        data.rightP = rightP;
        data.idrecomendacion = idrecomendacion;
    }
    data.clic = "gallery_poly";
    //console.log(data);
    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Images.php',
        dataType: 'json',
        data: data,
        success: function(response) {
            var i = 0;
            $("#divgaleria").html();
            response.forEach(function(item, index) {
                if (i == 0) {
                    $("#divgaleria").html("<div class='item active'><center><img height='500px' src='resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/" + item['nombre'] + ".jpg' alt='item" + i + "'></center><div class='carousel-caption textonimage infoimage'><h3>" + item['nombre'] + "</h3><h5>Path: " + item['path'] + ", Row: " + item['row'] + ".</h5>" + (i + 1) + " de " + response.length + "</div></div>");
                } else {
                    $("#divgaleria").append("<div class='item'><center><img height='500px' src='resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/" + item['nombre'] + ".jpg' alt='item" + i + "'></center><div class='carousel-caption textonimage infoimage'><h3>" + item['nombre'] + "</h3><h5>Path: " + item['path'] + ", Row: " + item['row'] + ".</h5>" + (i + 1) + " de " + response.length + "</div></div>");
                }
                i += 1;
            });
            $('#gallerymodal').modal('show');

        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

/*
 * AGREGA LAS IMAGENES DE UN POLIGONO
 */
function addToCarPolygon() {
    //console.log(arguments);
    satelite = arguments[0][4];
    action = arguments[0][3];
    year = arguments[0][1];
    month = arguments[0][2];
    rightP = arguments[0][5];
    idrecomendacion = arguments[0][6];
    //console.log(rightP);
    idbutton = year + month + satelite;
    if (action == "remove") {
        updateCarSession(idbutton, action);
        $("#btn" + idbutton).html("<button title='Add to donwloads' type'button' \
                              onclick='checkSession(\"addToCarPolygon\", \
                              \"" + year + "\",\
                              \"" + month + "\",\
                              \"add\",\
                              \"" + satelite + "\",\
                              \"" + rightP + "\",\
                              \"" + idrecomendacion + "\")' \
                              class='btn btn-default btn-xs'><span \
                              class='glyphicon glyphicon-plus'> \
                              </span>Add to donwloads</button>");
    } else {
        var data = getDataPolygon(year, month);
        data.clic = "download_poly";
        if (rightP) {
            data.action = "get_images_date_shape";
            data.rightP = true;
            data.idrecomendacion = idrecomendacion;
        }
        data.satelites = [satelite];
        console.log(data);
        $.ajax({
            type: 'POST',
            url: 'includes/controladores/controller.Images.php',
            dataType: 'json',
            data: data,
            success: function(response) {
                aux = [];
                response.forEach(function(item, index) {
                    id = item['nombre']
                    aux.push({ id: id, opciones: ['jpg', 'meta'] });
                });
                aux = { imgs: aux, folder: "polygon_" + idbutton, isfolder: true, type: "polygon", month: month, year: year, id: idbutton };
                $("#btn" + idbutton).html("<button title='Agregar a descargas' type='button' \
         onclick='checkSession(\"addToCarPolygon\",\"" + year + "\",\"" + month +
                    "\",\"remove\",\"" + satelite + "\", \"" + rightP + "\", \"" + idrecomendacion + "\")' \
         class='btn btn-danger btn-xs'>Eliminar</button>");
                updateCarSession(aux, action);
            },
            error: function(data) { //se lanza cuando ocurre un error
                console.log(data.responseText);
            }
        });
    }
}

/**
 * AGREGA LAS IMAGENES DE UN SOLAPAMIENTO
 */
function addToCarOverleap(id, path, row, satelite, action) {
    action = arguments[0][5];
    satelite = arguments[0][4];
    row = arguments[0][3];
    path = arguments[0][2];
    id = arguments[0][1];
    k = path + "_" + row + "_" + satelite;
    if (action == "remove") {
        updateCarSession(k, action);
        $("#btn" + k).html("<button title='Agregar a descargas' type='button'  onclick='checkSession(\"addToCarOverleap\",\"" + id + "\",\"" + path + "\",\"" + row + "\",\"" + satelite + "\",\"add\")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span>Agregar imágenes</button>");
    } else {
        $.ajax({
            type: 'POST',
            url: 'includes/controladores/controller.Images.php',
            dataType: 'json',
            data: { satelite: satelite, path: path, row: row, action: "get_in_path_row", clic: "download_overlap" },
            success: function(response) {
                aux = [];
                response.forEach(function(item, index) {
                    id = item['nombre'];
                    aux.push({ id: id, opciones: ['jpg', 'meta'] });
                });
                aux = { imgs: aux, folder: "overlaps_" + k, isfolder: true, type: "overleap", path: path, row: row, id: k };
                updateCarSession(aux, action);
                $("#btn" + k).html("<button title='Agregar a descargas' type='button'  onclick='checkSession(\"addToCarOverleap\",\"" + id + "\",\"" + path + "\",\"" + row + "\",\"" + satelite + "\",\"remove\")' class='btn btn-danger btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span>Eliminar</button>");
            },
            error: function(data) { //se lanza cuando ocurre un error
                console.log(data.responseText);
            }
        });
    }
}

/*
 * MUESTRA LAS IMAGENES DE UN SOLAPAMIENTO
 */
function showImagesGroup(path, row, satelite, rightP = 0, idrecomendacion = -1) {

    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Images.php',
        dataType: 'json',
        data: { satelite: satelite, path: path, row: row, action: "get_in_path_row", idrecomendacion: idrecomendacion, clic: "gallery_overlap", rightP: rightP },
        success: function(response) {
            var i = 0;
            response.forEach(function(item, index) {
                if (i == 0) {
                    $("#divgaleria").html("<div class='item active'><center><img height='500px' src='resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/" + item['nombre'] + ".jpg' alt='item" + i + "'></center><div class='carousel-caption textonimage infoimage'><h3>" + item['nombre'] + "</h3><h5>" + item['date'] + ".</h5>" + (i + 1) + " de " + response.length + "</div>            </div>");
                } else {
                    $("#divgaleria").append("<div class='item'><center><img height='500px' src='resources/kxHot9kVSXqFe7p8Yts9dUUZ8Nq92WjdFKljz1gQfSu1RFrre6FhtTRKuaKBuASxn/Q0SEUUh7qhc0X7dvtD90K2yZd7euodNvAdE2GwdDUyEMBkuXfxkdNJyu9AQplmDoU/" + item['nombre'] + ".jpg' alt='item" + i + "'></center><div class='carousel-caption textonimage infoimage'><h3>" + item['nombre'] + "</h3><h5>" + item['date'] + ".</h5>" + (i + 1) + " de " + response.length + "</div>            </div>");
                }
                i += 1;
            });
            $('#gallerymodal').modal('show');
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
    //var height = $(document).height();
}

/**
 * REMUEVE TODAS LAS IMAGENES DEL MAPA
 */
function removeImgs() {
    for (var key in imgsMaps_agregados) {
        imgsMaps_agregados[key].setMap(null);
        delete imgsMaps_agregados[key];
    }
}

/**
 * MUESTRA TODAS LAS IMÁGENES DE UN AÑO
 */
function showImagesOfYear(year, month) {
    removeImgs();
    document.year = year;
    document.month = month;
    document.band = true;
    getResults(0);


    var imgs = document.imagenes.filter(img => Number(img.yyyy) == year && Number(img.mmmm) == month);
    imgs.forEach(function(item, index) {
        imageToMap(null, item['hash_name'], "view_image_on_map_poly");
    });
}

//Convierte la primer letra de un cadena a Mayusculas
function capitalizeFirstLetter(string) {
    if (typeof string == "string") {
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    return string;
}

/**
 * AGREGA TODAS LAS IMAGENES DE UN MES Y AÑO A LA COLA DE 
 * DESCARGAS
 */
function addAllMonthYear(action) {
    year = document.year;
    month = document.month;
    var imgs = document.imagenes.filter(img => Number(img.yyyy) == year && Number(img.mmmm) == month);
    //console.log(action);
    if (action == "add") {
        imgs.forEach(function(item, index) {
            id = item['nombre'];
            var opciones = ["meta", "jpg"];
            item = { id: id, opciones: opciones, isfolder: false, type: "single" };
            $("#btn" + id).html("<button title='Eliminar de las descargas' type='button'  onclick='checkSession(\"addToCar\",\"" + id + "\",\"remove\")' class='btn btn-danger btn-xs'>Eliminar</button>");
            updateCarSession(item, "add");
        });
        $("#btnAddAll").html('<a title="Remover imágenes de la descarga" onclick="addAllMonthYear(\'remove\')" ><span class="glyphicon glyphicon-minus" aria-hidden="true"></span></a>');
    } else {
        imgs.forEach(function(item, index) {
            id = item['nombre'];
            $("#btn" + id).html("<button title='Agregar a descargas' type='button'  onclick='checkSession(\"addToCar\",\"" + id + "\",\"add\")' class='btn btn-default btn-xs'><span class='glyphicon glyphicon-plus' aria-hidden='true'></span></button>");
            //console.log(item);
            updateCarSession(id, "remove");
        });
        $("#btnAddAll").html('<a title="Agregar todas las imágenes a descarga" onclick="addAllMonthYear(\'add\')" ><span class="glyphicon glyphicon-plus" aria-hidden="true"></span></a>');
    }
}

/*
 * MUESTRA TODAS LAS IMAGENES EN EL MAPA
 */
function showAllOnMap(data) {
    data.onlynames = 1;
    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Images.php',
        dataType: 'json',
        data: data,
        success: function(response) {
            min_date = Number(response[0]['yyyy']);
            max_date = Number(response[response.length - 1]['yyyy']);
            str = '<div  class="dropdown dropdown2"><a class=" dropdown-toggle" id="menu2" href="javascript:void(0);" type="button" data-toggle="dropdown"> <span class="glyphicon glyphicon-calendar" aria-hidden="true"></span></a> <ul  class="dropdown-menu" role="menu" aria-labelledby="menu2"></li><strong>&nbsp;&nbsp;&nbsp;Año del mosaico</strong> ';
            for (i = min_date; i <= max_date; i++) {
                aux = response.filter(img => Number(img.yyyy) == i);
                if (aux.length > 0) {
                    //str += '<li role="presentation"><a role="menuitem" tabindex="-1" href="#" onclick="shonImagesOfYear('+i+')">'+i+'</a></li>';
                    str += '<li class="dropdown-submenu"><a class="test" tabindex="-1" href="#">' + i + '<span class="caret"></span></a><ul class="dropdown-menu">';
                    min_month = Number(aux[0]['mmmm']);
                    max_month = Number(aux[aux.length - 1]['mmmm']);
                    for (j = min_month; j <= max_month; j++) {
                        aux2 = aux.filter(img => Number(img.mmmm) == j);
                        if (aux2.length > 0) {
                            str += '<li><a tabindex="-1" onclick="showImagesOfYear(' + i + ',' + j + ')" href="#">' + MONTHS[j] + '</a></li>';
                        }
                    }
                    str += '</ul></li>';
                }
            }
            str += ' </ul>  </div> <span id="btnAddAll"><a title="Agregar todas las imágenes a descarga" onclick="addAllMonthYear(\'add\')" ><span class="glyphicon glyphicon-plus" aria-hidden="true"></span></a><span>';
            $("#dropyears").html(str);
            document.imagenes = response;
            showImagesOfYear(min_date, response[0]['mmmm']);
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

// This function starts the timer
function startTimer() {
    clearInterval(document.timer);
    centesimas = 0;
    segundos = 0;
    minutos = 0;
    horas = 0;
    document.timer = setInterval(cronometro, 10);
}

function sesionExpirada() {
    $("#modExpirado").modal('show');

}

function cronometro() {
    if (centesimas < 99) {
        centesimas++;
    }
    if (centesimas == 99) {
        centesimas = -1;
    }
    if (centesimas == 0) {
        segundos++;
    }
    if (segundos == 59) {
        segundos = -1;
    }
    if ((centesimas == 0) && (segundos == 0)) {
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
function cargarBusquedas(page) {
    $.ajax({
        type: 'POST',
        url: 'includes/show_busquedas.php',
        data: { page: page },
        success: function(response) {
            $("#divBusquedas").html(response);
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

/**
 * MUESTRA EL CONTENIDO DEL DASHBOARD DEPENDIENDO EN QUE OPCIÓN SE DE CLIC
 */
function show(file) {
    $.ajax({
        type: 'POST',
        url: 'includes/' + file + '.php',
        success: function(response) {
            $("#divcontenidodash").html(response);
            if (file == "preferences") {
                initMap();
                getUserUbication();
            } else if (file == "userloc") {
                initMap();
                getClusters();
            } else if (file == "stats") {
                loadCharts();
            }
            $("#dashoptions").find('li').each(function() {
                if ($(this).hasClass("itemactive")) {
                    $(this).removeClass("itemactive")
                }
            });
            $("#li" + file).addClass("itemactive");
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}


/**
 * OBTIENE LOS CLUSTERS GENERADOS CON EL ALGORITMO
 */
function getClusters() {
    var colors = ["red", "blue", "green", "orange", "purple"];
    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Recomendations.php',
        dataType: 'json',
        data: { action: 'get_clusters' },
        success: function(response) {
            console.log(response);
            var coors, i = 0;
            response.forEach(function(item, index) {
                //console.log("------------"+item['id']+"------------");
                item['elements'].forEach(function(element, ei) {
                    //console.log(element['username']);
                    //console.log(element['ratings']);
                    if (element['ratings'] != null) {
                        coors = { lat: element['ratings'][0], lng: element['ratings'][1] };
                        var marker = new google.maps.Marker({
                            position: coors,
                            map: document.map,
                            title: 'User ' + element['username'],
                            icon: 'http://maps.google.com/mapfiles/ms/icons/' + colors[i] + '-dot.png'
                        });

                        var infowindow = new google.maps.InfoWindow({
                            content: "<div><div><strong>" + element['username'] + "</strong></div><div>Latitud = " + element['ratings'][0] + "<br>Longitud = " + element['ratings'][1] + "</div></div>"
                        });

                        marker.addListener('click', function() {
                            infowindow.open(document.map, marker);
                        });
                    }
                });
                i++;
            });
            /*response.forEach(function(value,index){
              console.log(value);
              //coors = {lat:,lng:};
            }); */
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

/**
 * OBTIENE LA UBICACIÓN DEL USUARIO CON LA QUE SE REALIZAN LAS RECOMENDACIONES
 */
function getUserUbication() {
    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Session.php',
        dataType: 'json',
        data: { action: 'get_ubication' },
        success: function(response) {
            document.ant = "circulo";
            document.coorsRecomendations = response;
            document.coorsRecomendationsAnt = response;
            addCircle(Number(response['lat']), Number(response['lon']), Number(response['radio']));
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

function changeRecomendationCircle(location) {
    if (location != null) {
        deleteAllCoord();
        addCircle(location.coords.latitude, location.coords.longitude, 300000);
        document.coorsRecomendations = {
            "lat": location.coords.latitude,
            "lon": location.coords.longitude,
            "definedbyuser": true,
            "radio": 300000
        };
    }
}

/**
 * REGRESA LA LOCALIZACIÓN A LA INICIAL
 */
function resetLocation() {
    deleteAllCoord();
    if (document.coorsRecomendationsAnt != null) {
        addCircle(Number(document.coorsRecomendationsAnt['lat']),
            Number(document.coorsRecomendationsAnt['lon']),
            Number(document.coorsRecomendationsAnt['radio']));
        document.coorsRecomendations = document.coorsRecomendationsAnt;
    } else {
        addCircle(Number(document.coorsRecomendations['lat']),
            Number(document.coorsRecomendations['lon']),
            Number(document.coorsRecomendations['radio']));
    }
}

/**
 * LLAMA A OBTENER LA UBICACION ACTUAL
 */
function useCurrentLocation() {
    getLocation("changeRecomendationCircle");
}

/**
 * GUARDA LA LOCALIZACION ESTABLECIDA POR EL USUARIO
 */
function saveLocation() {
    if (document.shape != null && document.coorsRecomendations != null) {
        document.coorsRecomendations.action = 'save_location';
        //document.coorsRecomendations.lat = 
        document.coorsRecomendations.radio = document.shape.getRadius();
        $.ajax({
            type: 'POST',
            url: 'includes/controladores/controller.Session.php',
            dataType: 'json',
            data: document.coorsRecomendations,
            success: function(response) {
                if (response.codigo == 0) {
                    notificarUsuario(response.mensaje, "success");
                } else {
                    notificarUsuario(response.mensaje, "danger");
                }
            },
            error: function(data) { //se lanza cuando ocurre un error
                console.log(data.responseText);
            }
        });
    }
}

/**
 * CARGA LAS GRAFICAS DE ESTADISTICAS DE USUARIO
 */
function loadCharts() {
    loadSearchesChart();
    loadSearchesWayChart();
    recommendationsChart("get_recommendations_imgs", "divGivenRecommendations", "Recommended images");
    recommendationsChart("get_recommendations_polys", "divGivenRecommendationsPolys", "Recommended polygons");
    recommendationsChart("get_recommendations_overlaps", "divGivenRecommendationsOverlaps", "Recommended overlaps");
}

function loadSearchesChart() {
    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Logs.php',
        dataType: 'json',
        data: { action: "get_searches_stats" },
        success: function(response) {
            var ctx = document.getElementById("divSearchesStats").getContext('2d');
            var labels = [];
            var data = [];

            response.forEach(function(item, index) {
                labels.push(item[1]);
                data.push(item[0]);
            });

            var myPieChart = new Chart(ctx, {
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
                },
                options: {
                    title: {
                        display: true,
                        text: 'Formas utilizadas para realizar las búsquedas'
                    }
                }
            });
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

function loadSearchesWayChart() {
    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Logs.php',
        dataType: 'json',
        data: { action: "get_searches_ways_stats" },
        success: function(response) {
            var ctx = document.getElementById("divSearchesWay").getContext('2d');
            var labels = [];
            var data = [];

            response.forEach(function(item, index) {
                labels.push(item[1]);
                data.push(item[0]);
            });

            var myPieChart = new Chart(ctx, {
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
                },
                options: {
                    title: {
                        display: true,
                        text: 'Tipos de búsquedas realizadas'
                    }
                }
            });
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

function recommendationsChart(action, div, title) {
    $.ajax({
        type: 'POST',
        url: 'includes/controladores/controller.Logs.php',
        dataType: 'json',
        data: { action: action },
        success: function(response) {
            var ctx = document.getElementById(div).getContext('2d');
            var labels = ["Recommended images", "Clicked images"];
            var data = [response[0][1], response[0][0]];
            showBarGraph(labels, data, title, ctx);
        },
        error: function(data) { //se lanza cuando ocurre un error
            console.log(data.responseText);
        }
    });
}

function showBarGraph(labels, data, label, ctx) {
    new Chart(ctx, {
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
                "borderWidth": 1
            }]
        },
        "options": {
            "scales": {
                "yAxes": [{
                    "ticks": {
                        "beginAtZero": true
                    }
                }]
            }
        }
    });
}

$('#tutorial').on("click", function(e) {
    console.log("tutorial")
    introJs().start();
});

function clusDesactivate(aux) {
    $("#Silhouette_auto").prop('disabled', aux);
    $("#txtKClust").prop('disabled', aux);
    $("#Clust_alg").prop('disabled', aux);
    $("#variable").prop('disabled', aux);
    $("#sec-clust").collapse("hide")
}



$("#clustering").on('change', function(e) {
    if ($("#clustering").prop('checked') == true) {
        clusDesactivate(false);
    } else {
        clusDesactivate(true);
        $("#Silhouette_auto").prop('checked', false);
    }

});


$("#Silhouette_auto").on('change', function(e) {
    if ($("#Silhouette_auto").prop('checked') == true) {
        $("#txtKClust").prop('disabled', true);
        $("#Clust_alg").prop('disabled', true);
    } else {
        $("#txtKClust").prop('disabled', false);
        $("#Clust_alg").prop('disabled', false);
    }
});

function quitarTodo() {
    clusDesactivate(true);
    var temporal = $("#slproductos").val();
    if (temporal == "actual") {
        $("#IMG_stat").prop('disabled', true);
        $("#IMG_dates").prop('disabled', true);
        $("#Diferencial").prop('disabled', true);
        $("#Extra").prop('disabled', true);
        $("#Summay").prop('disabled', true);
        $("#Basic_stad").prop('disabled', false);
        //quitar marcado a todo
        $("#Silhouette_auto").prop('checked', false);
        $("#IMG_stat").prop('checked', false);
        $("#IMG_dates").prop('checked', false);
        $("#Diferencial").prop('checked', false);
        $("#Extra").prop('checked', false);
        $("#Summay").prop('checked', false);
        $("#Basic_stad").prop('checked', false);
    }

    console.log("temporal - " + temporal);
    if (temporal == "historico") {
        //quito marcado a todo
        $("#Silhouette_auto").prop('checked', false);
        $("#IMG_stat").prop('checked', false);
        $("#IMG_dates").prop('checked', false);
        $("#Diferencial").prop('checked', false);
        $("#Extra").prop('checked', false);
        $("#Summay").prop('checked', false);
        $("#Basic_stad").prop('checked', false);
        //escondo silueta
        $("#options_differential").hide();
    }



}
var POPOVER_sil = false;
$('#sil_info').click(function (event) {
    console.log(POPOVER_sil)
    if (POPOVER_sil) {
        $('[data-toggle="info_sil"]').popover('hide');
        $('[data-toggle="info_sil"]').popover('disable');
        POPOVER_sil = false;
    } else {
        $('[data-toggle="info_sil"]').popover('enable');
        $('[data-toggle="info_sil"]').popover('show');
        POPOVER_sil = true;
    }
});


//Funciones de habilitacion de filtros segun la fuentes seleccionadas. y las fechas
function numFuentes() {
    var auxArray= $('input[type=radio][name=font_study]:checked').val().split(",")
    $("#clustering").prop( "checked", false );

    var fuentes = auxArray.toString()
    $("#listOfDatasources").html(fuentes)
    selection = $('#slproductos').val();
    console.log(selection)

    if (auxArray.length == 0) {
        //Disbale para todos los componentes debido a que ninguna fuente esta seleccionada
        $("#clustering").hide()
        quitarTodo();

        var classe = "form-control selectpicker";
        var id = "variable";
        var multiple = "multiple";

        $("#selectVariable").html("<select required data-actions-box='true' class=" + classe + " id=" + id + ">");
        $("#selectVariable").append("</select>");
    }
    if (auxArray.length == 1) { // una fuente
        //Disbale para todos los componentes debido a que ninguna fuente esta seleccionada
        $("#clustering").show()
        clusDesactivate(false);

        $("#div_IMG_stat").hide()
        $("#div_IMG_dates").hide()
        $("#div_Diferencial").hide()
        $("#div_Extra").hide()
        $("#div_Summay").hide()
        $("#Basic_stad").hide()
        $("#variable").show()
        var id = "variable";
        $("#selectVariable").html("<select required data-actions-box='true' id='" + id + "' multiple>");
        validate_date_selection();

        //opciones emas
        if (auxArray == "EMASMAX") {
            $("#variable").append('<option value="Temp_max_emas">' + document.lngarr['tem_max_emas'] + ' </option>');
            $("#variable").append('<option value="Temp_min_emas">' + document.lngarr['tem_min_emas'] + ' </option>');
            if (selection == "actual") { $("#div_IMG_stat").show()}
            if (selection == "actual") { $("#div_IMG_dates").show()}
            if (selection == "actual"){
                $("#variable").append('<option value="Humedad">' + document.lngarr['humedad_emas'] + ' </option>');
                $("#variable").append('<option value="Precipitacion">' + document.lngarr['precipitacion_emas'] + ' </option>');
                $("#variable").append('<option value="Presion_barometrica"> ' + document.lngarr['presion'] + '  </option>');
                $("#variable").append('<option value="Radiacion_solar">' + document.lngarr['radiacion_solar'] + '</option>');
            }

        }
        //opciones de merra
        if (auxArray == "MERRA") {
            $("#variable").append('<option value="Temp_max_merra"> ' + document.lngarr['tem_max_merra'] + ' </option>');
            $("#variable").append('<option value="Temp_min_merra"> ' + document.lngarr['tem_min_merra'] + ' </option>');
        }

        $("#selectVariable").append('</select>');
        $("#variable").addClass("form-control");
        $("#variable").addClass("selectpicker");
        $(".selectpicker").selectpicker('refresh');


    }
    if (auxArray.length >= 2) {
        //Disbale para todos los componentes debido a que ninguna fuente esta seleccionada
        if (selection == "actual") {     
            $("#clustering").show()
            clusDesactivate(false);
            $("#div_IMG_stat").show()
            $("#div_IMG_dates").show()
            $("#div_Diferencial").show()
            $("#div_Extra").show()
            $("#div_Summay").show()
            $("#Basic_stad").show()
        }
        if (selection == "historico") {     
            $("#clustering").show()
            clusDesactivate(false);
            $("#div_IMG_stat").hide()
            $("#div_IMG_dates").hide()
            $("#div_Diferencial").hide()
            $("#div_Extra").hide()
            $("#div_Summay").show()
            $("#Basic_stad").hide()
        }

        validate_date_selection()


        var id = "variable";
        $("#selectVariable").html("<select required data-actions-box='true' id='" + id + "' multiple>");
        //opciones emas
        if (auxArray[0] == "EMASMAX") {
            $("#variable").append('<option value="Temp_max_emas">' + document.lngarr['tem_max_emas'] + ' </option>');
            $("#variable").append('<option value="Temp_min_emas">' + document.lngarr['tem_min_emas'] + ' </option>');
            if (selection == "actual") { 
                $("#variable").append('<option value="Humedad">' + document.lngarr['humedad_emas'] + ' </option>');
                $("#variable").append('<option value="Precipitacion">' + document.lngarr['precipitacion_emas'] + ' </option>');
                $("#variable").append('<option value="Presion_barometrica"> ' + document.lngarr['presion'] + '  </option>');
                $("#variable").append('<option value="Radiacion_solar">' + document.lngarr['radiacion_solar'] + '</option>');
            }
        }

        //opciones de merra
        if (auxArray[0] == "MERRA") {
            $("#variable").html('<option value="Temp_max_merra"> ' + document.lngarr['tem_max_merra'] + ' </option>');
            $("#variable").append('<option value="Temp_min_merra"> ' + document.lngarr['tem_min_merra'] + ' </option>');
        }
        if (auxArray[1] == "MERRA") {
            $("#variable").append('<option value="Temp_max_merra"> ' + document.lngarr['tem_max_merra'] + ' </option>');
            $("#variable").append('<option value="Temp_min_merra"> ' + document.lngarr['tem_min_merra'] + ' </option>');
        }
        $("#variable").append("<option value='Differential_max'> " + document.lngarr['dif_max'] + " </option>");
        $("#variable").append("<option value='Differential_min'> " + document.lngarr['dif_min'] + "</option>");
        $("#variable").append("<option value='temp_max'>  Max temperature fill by merra </option>");
        $("#variable").append("<option value='temp_min'>  Min temperature fill by merra </option>");
        $("#variable").append("<option value='temp_max_fusion'>  Max temperature fusioned</option>");
        $("#variable").append("<option value='temp_min_fusion'>  Min temperature fusioned </option>");

        //variables solo de historico
        if (selection == "historico") { 
            
            $("#variable").append("<option value='latitud'>  Lat </option>");
            $("#variable").append("<option value='longitud'>  Lon </option>");
            $("#variable").append("<option value='altitud'>  Alt </option>");
            $("#variable").append("<option value='evaporacion'>  evaporacion </option>");

            $("#variable").append("<option value='r2_max'>  R2 score (max temperature)</option>");
            $("#variable").append("<option value='r2_min'>  R2 score  (min temperature)</option>");
            $("#variable").append("<option value='max_rmse'>  RMSE score (max temperature) </option>");
            $("#variable").append("<option value='min_rmse'>  RMSE score (min temperature)</option>");
            $("#variable").append("<option value='max_pbias'>  Bias Percentage (max temperature) </option>");
            $("#variable").append("<option value='min_pbias'>  Bias Percentage (min temperature)</option>");
        }

        $("#selectVariable").append('</select>');
        $("#variable").addClass("form-control");
        $("#variable").addClass("selectpicker");
        //$("#variable").selectpicker(); //con la nueva version de selectpicker
        $(".selectpicker").selectpicker('refresh');

    }

}

function ShowRegression() {
    console.log("entroRegression")
        // mostrar link de imagen
    var val = true;
    GlobalColors.forEach(function(arr, index) {
        GlobalImages.forEach(function(im, ix) {
            // Mostrar zip Imagenes Estaciones        
            if (Object.keys(im) == arr[0][2]) {
                if (val == true) {
                    folder = im[arr[0][2]].split("/")
                    folder = folder[2]
                    $("#imgStat").attr("href", "static/Zips/ImagesStations_" + folder + ".tar");
                    val = false
                }
                $("#div" + arr[0][2]).html("<hr><a onclick=\"viewImage('" + im[arr[0][2]] + "')\"><h4>Imagen</h4></a>");
            }
        });
    });
}


function ConvertKeysToLowerCase(obj) {
    var output = {};
    for(var i in obj){
        output[i.toLowerCase()] = obj[i]; 
    }
    return output;
};

function DibujarEstado_AAS(dataset,columns) {
    //dataset es orientado a columnas

    //obtener coordenads de cada estado y pintarlo (1-32)
    clean_state();
    GenerarEtiquetas(k=34) // genera etiquetas en la variable Etiquetas_Colores[]

    $("#results2").html("")
    $("#results2").append("<div id='clust_res' style='width:100%; color:blue'></div>");
    $("#clust_res").append("<div id='color_scale' style='width:100%; color:blue'></div><br>");
    $("#clust_res").append("<div id='Clusters_res' style='width:100%; color:blue'></div>")


    array_entidades= ConvertKeysToLowerCase(dataset) //array de entidades en minusculas
    array_entidades = array_entidades['entidad'].map(name => name.toLowerCase());


    //calcular resumenes por cluster
    var lista_clusters = dataset['class'].filter(onlyUnique);
    lista_colores = chroma.scale(["#feffa0", "#e50000"]).mode('lch').colors(lista_clusters.length)
    
    lista_clusters= lista_clusters.sort() //ordenada
    console.log(lista_clusters)

    resumenes = {}
    cantidades_para_escala = []

    //inicializar json de resumenes
    lista_clusters.forEach(function(cl, index) {
        resumenes[cl]={}
        columns.forEach(function(col, ix) {
            resumenes[cl][col]= {"cantidad":0,"valor":0}
        });
    })

    //recorrer datos para generar medias de las columnas seleccionadas por el usuario
    dataset['class'].forEach(function(etiqueta, index) {
        columns.forEach(function(col, ix) {
            if (etiqueta!="-"){
            resumenes[etiqueta][col]["valor"]+= dataset[col][index]
            resumenes[etiqueta][col]["cantidad"]+= 1
            }
        });
    });

    //calcular cantidades para la escala
    lista_clusters.forEach(function(label_grupo, index) {
        suma=0
        columns.forEach(function(v, ix) {
                suma+=resumenes[label_grupo][v]["valor"] /resumenes[label_grupo][v]["cantidad"] 
        })
        cantidades_para_escala.push(suma)
    });

   //ordenar cantidadesw
   cantidades_para_escala_ordenados = [...cantidades_para_escala]
   cantidades_para_escala_ordenados = cantidades_para_escala_ordenados.sort(function(a, b) {return a - b;});
   cantidades_para_escala_ordenados_values = [...cantidades_para_escala_ordenados]


   //ordenar lista de clusters segun las cantidades
   lista_clusters_ordenados = [...[lista_clusters]]
   cantidades_para_escala.forEach(function(cantidad_grupo, index) { //buscar donde quedo cada clase
       ubicacion = cantidades_para_escala_ordenados.findIndex((element) => element == cantidad_grupo);
       lista_clusters_ordenados[ubicacion]=index
   })

    //imprimir en pantalla
    lista_clusters_ordenados.forEach(function(label_grupo, index) {
        if (label_grupo!="-"){color = lista_colores[index]}
        else{color = "#FFFFFF"}
        $("#Clusters_res").append("<br><br><span class=\"dot\" style=\"background-color:" + color + "\"></span> <strong>Cluster " + label_grupo + "</strong><br><hr>").fadeIn('slow');
        columns.forEach(function(v, ix) {
                $("#Clusters_res").append("Average " + v + ": " + (resumenes[label_grupo][v]["valor"] /resumenes[label_grupo][v]["cantidad"] ) + "</br>");
        })
    });

 
    renderPalette('color_scale', lista_colores,cantidades_para_escala_ordenados_values);

    for (var state_id = 1; state_id <= 32; state_id++) { //recorrer los 32 estados
        url = 'includes/get_shapeby_id.php?id=' + state_id.toString()
        $.getJSON(url, function(data)
            {
                data = data[0]
                // caso especial con el df
                if (data['nombre'].toLowerCase()=="distrito federal"){data['nombre'] = "ciudad de méxico"} 

                //buscar si hay algun registro en los datos con este estado
                index_w_registro_de_la_entidad = array_entidades.findIndex((element) => element == data['nombre'].toLowerCase());

                if(index_w_registro_de_la_entidad >=0){ //si no hay, se devuelve un -1

                    label_grupo = dataset['class'][index_w_registro_de_la_entidad]//Obtener etiqueta de clase del registro
                    color = "#FFFFFF"
                    lista_clusters_ordenados.forEach(function(label_lista, index) {
                        if (label_grupo==label_lista){color = lista_colores[index]}

                    });

                    var bounds = new google.maps.LatLngBounds(); //obtiene las dimensiones del poligono
                    var coordinates = data['coordinates'];
                    var n = coordinates.length;
                    var m;
                    for (var i = 0; i < n; i++) {
                        var coordinatesGoogle = [];
                        m = coordinates[i].length;
                        coordinatesArr = m != 1 ? coordinates[i] : coordinates[i][0];
                        m = coordinatesArr.length;
                        for (var j = 0; j < m; j++) {
                            coordinatesGoogle.push({ lat: coordinatesArr[j][1], lng: coordinatesArr[j][0] })
                            bounds.extend( new google.maps.LatLng(coordinatesArr[j][1], coordinatesArr[j][0]));
                        }
                        //console.log(color);
                        var polygon = new google.maps.Polygon({
                            paths: coordinatesGoogle,
                            strokeColor: "#080200",
                            strokeWeight: 2,
                            fillColor: color,
                            fillOpacity: 1
                        });
                        polygon.setMap(document.map);
                    
                        content_window = "<h4>"+data['nombre']+"</h4> "
                        content_window += "<h5>cluster "+dataset['class'][index_w_registro_de_la_entidad]+"</h5> "
                        content_window += "<p><b>coords</b>:" + bounds.getCenter().toUrlValue(6) + "</p>"
                        columns.forEach(function(columna_datos, index) {
                            content_window+= "<p><b>"+columna_datos+"</b>: "+dataset[columna_datos][index_w_registro_de_la_entidad] + "</p>"
                        });

                        var infowindow = new google.maps.InfoWindow({
                            content: content_window,
                            position:bounds.getCenter()
                        });
                        infowindow.opened = false;
                    
                        polygon.addListener('mouseover', function(evt) {
                            infowindow.open(document.map);
                            infowindow.opened = false;
                          });

                        polygon.addListener('mouseout', function(evt) {
                          infowindow.close();
                          infowindow.opened = false;
                        });

                        document.polygons_states.push(polygon); //Guardar poligono en un conjunto lleno de poligonos

                        }
                }
                else{
                    console.log(index_w_registro_de_la_entidad)
                    console.log(data['nombre'].toLowerCase())
                }

            });
    }
}





function DibujarMunicipio_AAS(dataset,columns,lista_clusters_ordenados,lista_filtros=['class','Entidad'], variable_clase = "class",variable_entidad ="entidad",variable_municipio ="municipio",variable_temporal="Anio",combo_fechas=false) {
       

    $("#clust_res").html("");
    $("#clust_res").append("<div id='cluster-plot-container' style='width:100%;'></div><br>");
    $("#clust_res").append("<div id='color_scale' style='width:100%'></div><br>");
    $("#clust_res").append("<div id='boxplot-plot-container' style='width:100%;'></div><br>");


    $("#clust_res").append("<div id='Clusters_res' style='width:100%;'></div>")

    lista_colores = chroma.scale(["#feffa0", "#e50000"]).mode('lch').colors(lista_clusters.length)
    resumenes = {}
    cantidades_para_escala = []



    //inicializar json de resumenes
    lista_clusters_ordenados.forEach(function(cl, index) {
        resumenes[cl]={}
        columns.forEach(function(col, ix) {
            resumenes[cl][col]= {"cantidad":0,"valor":0}
        });
    })

    //recorrer datos para generar medias de las columnas seleccionadas por el usuario
    dataset[variable_clase].forEach(function(etiqueta, index) {
        columns.forEach(function(col, ix) {
            resumenes[etiqueta][col]["valor"]+= dataset[col][index]
            resumenes[etiqueta][col]["cantidad"]+= 1
        });
    });

    //calcular cantidades para la escala
    lista_clusters_ordenados.forEach(function(label_grupo, index) {
        suma=0
        columns.forEach(function(v, ix) {
                suma+=resumenes[label_grupo][v]["valor"] /resumenes[label_grupo][v]["cantidad"] 
        })
        if (Number.isNaN(suma)){suma=0}
        cantidades_para_escala.push(suma)
    });

    //imprimir en pantalla
    //lista_colores_ordenados = [...lista_clusters_ordenados]
    lista_clusters_ordenados.forEach(function(label_grupo, index) {
        if (label_grupo!="-"){color = lista_colores[index]}
        else{color = "#FFFFFF"}
        //lista_colores_ordenados[label_grupo]=color
        $("#Clusters_res").append("<br><br><span class=\"dot\" style=\"background-color:" + color + "\"></span> <strong>Cluster " + label_grupo + " summary (Average)</strong><br><hr>").fadeIn('slow');
        columns.forEach(function(v, ix) {
                $("#Clusters_res").append("<p style='font-size: 16px;'><b>" + v + ":</b> " + (resumenes[label_grupo][v]["valor"] /resumenes[label_grupo][v]["cantidad"] ).toFixed(0) + "</p>");
        })
    });


     //GRAFICAS
     if (columns.length>=2){ CreatePlotCluster(dataset[columns[0]],dataset[columns[1]],dataset[variable_clase],lista_clusters_ordenados,xlabel = columns[0], ylabel=columns[1],color_list=lista_colores,div_container="cluster-plot-container")}
     else { CreatePlotCluster(dataset[columns[0]],dataset[columns[0]],dataset[variable_clase],lista_clusters_ordenados,xlabel = columns[0], ylabel=columns[0],color_list=lista_colores,div_container="cluster-plot-container")}
 
    CreatePlotHistogram(dataset,columns,div_container="boxplot-plot-container")

    renderPalette('color_scale', lista_colores,cantidades_para_escala);


    conteo_faltantes=0
    url = 'includes/get_mun_centroids.php'
    $.getJSON(url, function(data){

        encabezados= ConvertKeysToLowerCase(dataset) //array de entidades en minusculas
        array_entidades = encabezados[variable_entidad].map(name => name.toLowerCase());
        array_municipios = encabezados[variable_municipio].map(name => name.toLowerCase());

        var array_ent_mun = array_entidades.map(function (num, idx) { //concatenar ambos array de manera paralela
            if (num=="Distrito federal"){num= "ciudad de méxico"} 
            return num +"-"+ array_municipios[idx];
        }); 

        //console.log(array_ent_mun)
        var lista_estados;
        url = 'includes/get_shape.php' //consultar lista de estados 
        $.getJSON(url, function(temp){ 
            lista_estados = temp
            if(!combo_fechas){clean_AAS();}//si no es un cambio por el combo se borran los marcadores
            else{decolorar_AAS()} 
            
            data.forEach(function(municipio, municipio_id) { //lista de municipios de la BD
                    lista_estados.forEach(function(registro_estado,id_registro){
                        if (registro_estado['nombre']=="Distrito federal"){
                            registro_estado['nombre']= "ciudad de méxico"
                        } 
                        if(parseInt(registro_estado["id"])== municipio['state']) {
                            municipio['estado'] = registro_estado['nombre'].toLowerCase()
                        }
                    })

                    //buscar si hay algun registro de este estado con los datos de este municipio
                    index_w_registro_de_la_entidad = array_ent_mun.findIndex((element) => element == municipio['estado']+"-"+municipio['nombre'].toLowerCase());

                    if(index_w_registro_de_la_entidad >=0){ //si no hay, se devuelve un -1
                        id_marcador = municipio['estado']+"-"+municipio['nombre']
                        
                        label_grupo = dataset[variable_clase][index_w_registro_de_la_entidad]//Obtener etiqueta de clase del registro
                        color = "#000000"
                        lista_clusters_ordenados.forEach(function(label_lista, index) {
                            if (label_grupo==label_lista){color = lista_colores[index]}

                        });

                        var pinImage = new google.maps.MarkerImage('http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|'+color.substring(1),
                        new google.maps.Size(21, 34),
                        new google.maps.Point(0, 0),
                        new google.maps.Point(10, 34));
                        
                        //contenido de la ventana
                        content_window = "<h4>"+municipio['nombre']+"</h4> "
                        content_window += "<h4>cluster "+dataset[variable_clase][index_w_registro_de_la_entidad]+"</h4> "
                        content_window += "<h4>temporal "+dataset[variable_temporal][index_w_registro_de_la_entidad]+"</h4> " /// <- HARDOCDEADO

                        sum = 0
                        columns.forEach(function(columna_datos, index) {
                            sum+=dataset[columna_datos][index_w_registro_de_la_entidad]
                            content_window+= "<p style='font-size: 16px;' ><b>"+columna_datos+"</b>: "+dataset[columna_datos][index_w_registro_de_la_entidad] + "</p>"
                        });
                        content_window+= "<p style='font-size: 18px;' ><b>TOTAL</b>: "+sum+ "</p>"
                        //---------------------------


                        if(combo_fechas && document.dataAAS[id_marcador] ){//solo se cambia el color del pin y la info dentro del infowindow
                            //document.dataAAS[id_marcador].marker.addListener('click', function() {
                            //    infowindow.open(document.map, document.dataAAS[id_marcador].marker);
                            //});
                            document.dataAAS[id_marcador].infowindow.setContent(content_window)
                            document.dataAAS[id_marcador].marker.setIcon(pinImage)
                            //actualizar valor de los filtros
                            lista_filtros.forEach(function(flt){
                                 temp = String(dataset[flt][index_w_registro_de_la_entidad]).toLowerCase()
                                 document.dataAAS[id_marcador][flt] = temp 
                             })

                        } else{ //se crea nueov marcador, si no, se cambia unicamente el color
                            var infowindow = new google.maps.InfoWindow({
                                content: content_window
                            });
                            infowindow.opened = false;
                            coors = { lat: municipio['centroid'][1], lng: municipio['centroid'][0] };
                            var marker = new google.maps.Marker({
                                position: coors,
                                map: document.map,
                                icon: pinImage
                            });
                            marker.addListener('click', function() {
                                infowindow.open(document.map, marker);
                            });
                            obj_marcador = {"marker": marker,"infowindow":infowindow,filtros:{}}
                        
                            //crar datos de filtros segun la lista otorgada
                            lista_filtros.forEach(function(flt){
                               //caso especial
                                temp = String(dataset[flt][index_w_registro_de_la_entidad]).toLowerCase()
                                obj_marcador[flt] = temp
                                obj_marcador["filtros"][flt]=true
                                //if(combo_fechas){Filtro_datos('FIL_'+flt+"_"+temp,temp,flt)} //es nuevo marcador, hay que actualiza rel}

                            })
                            document.dataAAS[id_marcador]= obj_marcador; //Guardar poligono en un conjunto lleno de poligonos
                        }

                            
                    }
                    else{
                        conteo_faltantes+=1
                        //console.log(municipio['estado']+"-"+municipio['nombre'])
                    }

                });
                //console.log(conteo_faltantes)
                //console.log(data.length)

                // filtros dinamicos
                    lista_filtros.forEach(function(flt){
                        HabiltarFiltroDinamico("#filtros-dinamicos",flt,encabezado=!combo_fechas)
                    });
                    Actualizar_Filtro_datos()
                
            });//end GET
    }); //end GET

}

function clean_AAS() {
    if(document.dataAAS!=undefined){
        Object.keys(document.dataAAS).forEach(function(gk) {
            if(document.dataAAS[gk]['marker']!=undefined){
                document.dataAAS[gk]['marker'].setMap(null)
            }
        });
        coors = [];    
    }
    document.dataAAS = {}
}
function decolorar_AAS() {
    color ="#000000"
    var pinImage = new google.maps.MarkerImage('http://chart.apis.google.com/chart?chst=d_map_pin_letter&chld=%E2%80%A2|'+color.substring(1),
    new google.maps.Size(21, 34),
    new google.maps.Point(0, 0),
    new google.maps.Point(10, 34));
    Object.keys(document.dataAAS).forEach(function(gk) {
        document.dataAAS[gk]['marker'].setIcon(pinImage)
    });
    coors = [];        
}


function getAllIndexes(arr, val) {
    var indexes = [], i;
    for(i = 0; i < arr.length; i++)
        if (arr[i] === val)
            indexes.push(i);
    return indexes;
}


function renderPalette(hook, colorCodes,values) {
  var hook = document.getElementById(hook);
 
  var palette = document.createElement('div');
  palette.className = 'palette';
  
  colorCodes.forEach(function(colorCode,idx) {
    var item = document.createElement('div');
    item.className = 'palette__item';
    item.style.backgroundColor = colorCode;    

    item.appendChild(document.createTextNode(values[idx].toFixed(0)));
    //if(values[idx]!=0){
    //    item.appendChild(document.createTextNode(values[idx].toFixed(0)));
    //}
    //else{
    //    item.appendChild(document.createTextNode("SIN VALORES"));
    //}
    
    palette.appendChild(item);
  });
  
  // remove all child elements
  while (hook.firstChild) {
    hook.removeChild(hook.firstChild);
  }
  // append the palette
  hook.appendChild(palette);
}


function CreatePlotHistogram(dataset,columnas,div_container="H-Gclust"){
    var data = [];
    columnas.forEach(function(col){
        x = dataset[col]
        var trace = {
            y: x,
            name: col,
            type: "box",
            opacity: 0.5,
            boxpoints: false
          };
          data.push(trace)
    })

    var layout = {barmode:"overlay",width: 350,height: 420,
    xaxis: {
        autorange: true,
        autotick: true,
        ticks: '',
        showticklabels: false
      },
      legend: {
        x: 0,
        xanchor: 'left',
        y: -.2
      }};
    Plotly.newPlot(div_container, data, layout);

}

function CreatePlotCluster(arr_x,arr_y,arr_labels,lista_clusters_ordenados,xlabel = "x", ylabel="y",lista_colores=Etiquetas_Colores,div_container="H-Gclust")
{
    GenerarEtiquetas()
    dataCluster = []
    //var etiquetas_clases  = arr_labels.filter(onlyUnique);

    if (lista_clusters_ordenados == null){
        trace = {
            x: arr_x,
            y: arr_y,
            mode: 'markers',
            name: 'data',
            marker: {
                color: "#fff000",
                size: 8
            }
        }
        dataCluster.push(trace)
    }
    else{
        lista_clusters_ordenados.forEach(function(cluster,idx) {
            if(cluster!="-"){
                idclust = parseInt(cluster);
                x = [];
                y = []
                arr_labels.forEach(function(item,index) {
                    if (item == cluster) {
                        x.push(arr_x[index]);
                        y.push(arr_y[index])
                    }
                });
                if (idclust<0){
                    idclust = 14-idclust
                    lista_colores=Etiquetas_Colores
                }
                    color_etiqueta=lista_colores[idx]
    
                if (color_etiqueta.charAt(0)=="#"){color_etiqueta=color_etiqueta.substring(1);}    // Returns "H"
    
    
                trace = {
                    x: x,
                    y: y,
                    mode: 'markers',
                    name: 'Cluster ' + cluster,
                    marker: {
                        color: "#"+color_etiqueta,
                        size: 8
                    }
                }
                dataCluster.push(trace)
            }
        });
    }




    var layoutClust = {
        autosize: false,
        width: 350,
        height: 400,
        title: {
            text: 'Clusters',
            font: {
                family: 'Courier New, monospace',
                size: 16
            },
            xref: ' ',
            x: 0.03,
        },
        xaxis: {
            title: {
                text: xlabel,
                font: {
                    family: 'Courier New, monospace',
                    size: 12,
                    color: '#7f7f7f'
                }
            },
        },
        yaxis: {
            title: {
                text: ylabel,
                font: {
                    family: 'Courier New, monospace',
                    size: 12,
                    color: '#7f7f7f'
                }
            }
        }
    };

    Plotly.newPlot(div_container, dataCluster, layoutClust, { showSendToCloud: true });
    //DATA_GRAPHS['H-Gclust'] = {"data":dataCluster,"layout":layoutClust}
}



function Filtro_datos(checkbox_reference,valor_filtro,nombre_filtro){
    value = $("#"+checkbox_reference).is(":checked")

    Object.keys(document.dataAAS).forEach(function(gk) {
        valor_registro = document.dataAAS[gk][nombre_filtro]
        if (value){ //encender
            if(valor_registro==valor_filtro){
                v=true
                document.dataAAS[gk]['filtros'][nombre_filtro] = v
                Object.keys(document.dataAAS[gk]['filtros']).forEach(function(it) {
                    if (!document.dataAAS[gk]['filtros'][it])
                    {
                        v =false
                    }
                });
                document.dataAAS[gk]['marker'].setVisible(v)
            }
        }
        else{
            if(valor_registro==valor_filtro){
                document.dataAAS[gk]['marker'].setVisible(false)
                document.dataAAS[gk]['filtros'][nombre_filtro] = false
            }
        }

    });
}

function Actualizar_Filtro_datos(){
    Object.keys(lista_global_filtros).forEach(function(gk) { //iterate all stations
        Filtro_datos(lista_global_filtros[gk][0],lista_global_filtros[gk][1],lista_global_filtros[gk][2])
    });
}

function Trigger_FiltrosPorSeccion(seccion,accion=true){
    Object.keys(lista_global_filtros).forEach(function(gk) { //iterate all stations
        nombre_filtro = gk.split("_")[1]
        if(nombre_filtro==seccion){
            $("#"+gk).prop("checked", accion);
        } 
    });
    Actualizar_Filtro_datos()
}

function HabiltarFiltroDinamico(div_container,nombre_filtro,encabezado=true){

    div_filtro = 'sec-filt-'+nombre_filtro
    if(encabezado){
        $(div_container).append('<button aria-expanded="false" style="    margin-top: 5px; margin-bottom: 5px; padding: 6px;" type="button" class="btn btn-info col-sm-12" data-toggle="collapse" data-target="#'+div_filtro+'_div">\
        '+nombre_filtro.toUpperCase()+' <i class="glyphicon glyphicon-chevron-down" aria-hidden="true"></i> <i class="glyphicon glyphicon-chevron-right" aria-hidden="true"></i > </button>\
        <div class="collapse" id="'+div_filtro+'_div"> <div class="row" id="'+div_filtro+'">  </div> </div>')
        
        //se añaden 2 botones para desactivar y activar todos los filtros
        $("#"+div_filtro).append(`<div class="col-sm-6"> <button onclick="Trigger_FiltrosPorSeccion('${nombre_filtro}',accion=true)" class="btn btn-info btn-block">SELECT ALL</button></div>`)
        $("#"+div_filtro).append(`<div class="col-sm-6"> <button onclick="Trigger_FiltrosPorSeccion('${nombre_filtro}',accion=false)"class="btn btn-info btn-block">DESELECT ALL</button></div>`)
    
    }

    var elementos_usados = []
    conteo_pares=0
    Object.keys(document.dataAAS).forEach(function(gk) { //iterate all stations
        valor_filtro_marcador = document.dataAAS[gk][nombre_filtro]
        valor_formateado = valor_filtro_marcador.replace(/\s/g, '-')
        //console.log(valor_filtro_marcador,valor_formateado)


        if (!(elementos_usados.includes(valor_filtro_marcador))){
            conteo_pares+=1
            if(!(Object.keys(lista_global_filtros).includes(`FIL_${nombre_filtro}_${valor_formateado}`))){ //si no existe aun en la lista global
                $("#"+div_filtro).append(`<div class="inputGroup col-6" id="DIV_${nombre_filtro}_${valor_formateado}">
                <input type="checkbox" id="FIL_${nombre_filtro}_${valor_formateado}" name="FIL_${nombre_filtro}_${valor_formateado}" onchange="Filtro_datos('FIL_${nombre_filtro}_${valor_formateado}','${valor_filtro_marcador}','${nombre_filtro}')" checked> 
                <label style="font-size:13px" for="FIL_${nombre_filtro}_${valor_formateado}"> ${valor_filtro_marcador.toUpperCase()} </label>
                </div>`)
            elementos_usados.push(valor_filtro_marcador)
            lastname = `DIV_${nombre_filtro}_${valor_formateado}`
            lista_global_filtros[`FIL_${nombre_filtro}_${valor_formateado}`]=[`FIL_${nombre_filtro}_${valor_formateado}`,valor_filtro_marcador,nombre_filtro]
            }
        }
    });
    if (conteo_pares%2==0) { console.log("pares")}
    else{  $("#"+lastname).attr("class","inputGroup col-12")}

    //$(div_container).append("<hr>")
}

function CalcularRegresionLinear(xArray,yArray){
    // Calculate Sums
    var xSum=0, ySum=0, xxSum=0, xySum=0;
    var count = xArray.length;
    for (var i = 0, len = count; i < count; i++) {
    xSum += xArray[i];
    ySum += yArray[i];
    xxSum += xArray[i] * xArray[i];
    xySum += xArray[i] * yArray[i];
    }

    // Calculate slope and intercept
    var slope = (count * xySum - xSum * ySum) / (count * xxSum - xSum * xSum);
    var intercept = (ySum / count) - (slope * xSum) / count;

    // Generate values
    var xValues = [];
    var yValues = [];
    for (var x = 50; x <= 150; x += 1) {
    xValues.push(x);
    yValues.push(x * slope + intercept);
    }

    return {"x":xValues,"y":yValues}

}

/* FUNCIONES DE MEJORA VISUAL - HOVER Y NAVBAR */

function openNav() {
    document.getElementById("mySidenav").style.width = "380px";
    console.log("opening")
  }
  
/* Set the width of the side navigation to 0 */
function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
}

function StandbyNav(){
    //this function does nothing... but we need it, belive me
    console.log("times up")
}