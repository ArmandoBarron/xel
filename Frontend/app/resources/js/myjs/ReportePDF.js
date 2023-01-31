var DATA_GRAPHS= new Object;

function validNull(value) {
    if (Number.isNaN(value)) {
        return "Null";
    }
    if (value == "NA" || value == -99 || value=="null" || value==null || value<-50 || value > 80) {
        return "Null";
    } else {
        return value
    }
}

function CalcularMediaYMediana(arrayData){
    media = "NA"
    mediana = "NA"
    if (arrayData.length != 0) {
        // console.log(temEmas)
        arrayData.sort((a, b) => a - b);
        var sumEmas = arrayData.reduce((previous, current) => current += previous);
        media = sumEmas / arrayData.length;

        if (arrayData.length % 2 == 0) {
            var pos1 = Math.round(arrayData.length / 2)
            var pos2 = Math.round(pos1 - 1)
            var elem1 = arrayData[pos1]
            var elem2 = arrayData[pos2]
            mediana = (elem1 + elem2) / 2
        } else {
            var pos_central = Math.round((arrayData.length - 1) / 2)
            mediana = arrayData[pos_central]
        }

    }
    if (media != "NA"){media=media.toFixed(4) }
    if (mediana != "NA"){mediana=mediana.toFixed(4) }

    return {"media":media,"mediana":mediana}
}

function CreatePDF(){
    notificarUsuario("Generando reporte", 'info')

    console.log("creating..")

    var HTML_Width = $("#tableReport").width();
    var HTML_Height = $("#tableReport").height();
    var top_left_margin = 40;
    var PDF_Width = HTML_Width + (top_left_margin * 2);
    var PDF_Height = (PDF_Width * 1.5) + (top_left_margin * 2);
    var canvas_image_width = HTML_Width;
    var canvas_image_height = HTML_Height;

    var totalPDFPages = Math.ceil(HTML_Height / PDF_Height) - 1;
    var pdf = new jsPDF('p', 'pt', [PDF_Width, PDF_Height]);
    pdf.setFont('Lato-Regular', 'normal');
    pdf.setFontSize(16);
    pdf.setFontStyle('bold');

    pdf.setTextColor(255, 0, 0);
    pdf.text(10, 20, 'Reporte Geoportal Meteo');
    pdf.setTextColor(0, 0, 0);
    pdf.setFontSize(10);

    html2canvas($("#tableReport")[0]).then(function (canvas) {
        var imgData = canvas.toDataURL("image/jpeg", 1.0);
        pdf.addImage(imgData, 'JPG', top_left_margin, top_left_margin, canvas_image_width, canvas_image_height);
        for (var i = 1; i <= totalPDFPages; i++) { 
            pdf.addPage(PDF_Width, PDF_Height);
            pdf.addImage(imgData, 'JPG', top_left_margin, -(PDF_Height*i)+(top_left_margin*4),canvas_image_width,canvas_image_height);
        }
        notificarUsuario("Reporte generado", 'success');
        namepdf= $("#box_cluster_historico").val()

        pdf.save("Reporte_"+namepdf+".pdf");
        //$(".html-content").hide();
    });
    
    
}


function get_topoformas() {

    var fil_tf = [];
    var fil_clima = [];

    //topoform_report.forEach(TF => {
    //    if ($('#FIL_TF_' + TF).is(":checked")) {
    //        fil_tf.push(TF);
    //    }
    //});
    Lista_Filtros = Object.keys(lista_global_filtros)

    dict_secciones = {} //objecto  con filtros divididos por secciones
    // por clima
    Lista_Filtros.forEach(filtro => {
        var arrfiltro = filtro.split("_");
        seccion_filtro = arrfiltro[1]; valor_filtro = arrfiltro[2]
        if ($('#FIL_'+seccion_filtro+'_' + valor_filtro).is(":checked"))  { // se añade solo si esta sleeccionada

            if (!Object.keys(dict_secciones).includes(seccion_filtro)){dict_secciones[seccion_filtro]=[] } //si no existe se crea
            dict_secciones[seccion_filtro].push(valor_filtro) // se agrega al objeto
        }
    });

    // var send_Antenas = { "results": antenas["results"], "selected": fil_tf };
    var send_Antenas = document.diferenciales;
    console.log(send_Antenas)
    var content = "";
    $("#tableReport").html("");
    $("#mapEMAS").html("");
    $("#mapMERRA").html("");

    //mapboxgl.accessToken = 'pk.eyJ1Ijoiam9zZW1vcmluOTg0MiIsImEiOiJja2pybTc5MmEwYjVjMnpqeG1yM3lkbTR1In0.2wBB7QTlDu1evrGZk4I4Iw';
    $("#tableReport").append("<br>");
    // añadir graficas y estadisticos generales
    //$("#tableReport").append("<div class='row'><div class='col-sm-12' id='reporte_grafica1'> </div> <div id='reporte_grafica2' class='col-sm-12'> </div> </div>");

    //Plotly.newPlot('reporte_grafica1', DATA_GRAPHS['H-Dispersion']['data'], DATA_GRAPHS['H-Dispersion']['layout']);
    //Plotly.newPlot('reporte_grafica2', DATA_GRAPHS['H-Gclust']['data'], DATA_GRAPHS['H-Gclust']['layout'],);

    $("#tableReport").append("<div class='row container' id='reporte_varianza'></div>");
    $("#reporte_varianza").html($("#H-variance").html());

    console.log(dict_secciones)

    // CREAR TABLAS
    Object.keys(dict_secciones).forEach(sec => {
        if (sec=="source") {CrearTablaSimple(dict_secciones[sec],sec,sec)}
        else{CrearTablasReporte(dict_secciones[sec],sec,sec)}
    });
}

function CrearTablaSimple(list_elements,title,identifier){

}

function CrearTablasReporte(list_elements,title,identifier){
    var Temporalidad = $('#slproductos').val();
    var divid=0
    $("#tableReport").append("<h2>"+title+"</h2>")

    $("#tableReport").append("<div class='row container' id='summary_"+identifier+"' ></div>")


    // se debe parsear el identifier a la key del json que tiene los datos, ya que no es la misma
    key_data =""
    if (identifier=="weather"){key_data="clima_label"} 
    if (identifier=="topoform"){key_data="topoforma"} 

    obj_summary = {}

    list_elements.forEach(element => {
        var total = 0;
        var clustersCont = new Object()
        total = 0;
        divid+=1
        TF = element
        if (TF == "Lomer?o") {TF = "Lomero";}
        if (TF == "Caon") {TF = "Cañon";}
        if (TF == "Cuerpo_de_agua") {TF = "Cuerpo de agua";}
        if (TF == "Depresin") {TF = "Depresión";}
        if (TF == "Playa_o_Barra") {TF = "Playa o Barra";}
        if (TF == "Campo_de_dunas") {TF = "Campo de dunas"}

        content = "";
        div_contenedor ="#tableReport"
        if(divid % 2 == 0) {
            div_contenedor="#"+(divid-1)+"_row_"+ identifier
        }
        else{
            $(div_contenedor).append("<div id='"+divid+"_row_"+identifier+"' class='row'></div>");
            div_contenedor="#"+divid+"_row_"+identifier
        }
        $(div_contenedor).append("<div id='"+divid+"_div_"+identifier+"' class='container col-sm-6'></div>");
        $("#"+divid+"_div_"+identifier).append("<h3>" + TF + "</h3>");

        // contar antenas por cada fuente 
        cont1 = 0;
        cont = 0
        Object.keys(GlobalMarkers).forEach(function(gk) {
            if (GlobalMarkers[gk]['source'] == 'EMASMAX' || GlobalMarkers[gk]['source'] == 'EMAS') {
                if (GlobalMarkers[gk][identifier] == element) {cont1++;}
            }
            if (GlobalMarkers[gk]['source'] == 'MERRA' || GlobalMarkers[gk]['source'] == 'UNKNOWN') {
                if (GlobalMarkers[gk][identifier] == element) {cont++;}
            }
        });


        // PORCENTAJE DE ANTENAS POR FUENTE DE DATOS
        $("#"+divid+"_div_"+identifier).append("<h5> Stations in EMAS: " + cont1 + " (" + ((cont1 / (cont + cont1)) * 100).toFixed(2) + "%)" + "</h5>");
        $("#"+divid+"_div_"+identifier).append("<h5> Stations only in MERRA: " + cont + " (" + ((cont / (cont + cont1)) * 100).toFixed(2) + "%)" + "</h5>");
        $("#"+divid+"_div_"+identifier).append("<h5> Stations in MERRA but also in EMAS: " + (cont+cont1) + "</h5>");


        temMerra = []
        temEmas = []
        diffMAX = []
        diffMIN = []
        diffPerClass = new Object()

        if (Temporalidad=="actual"){

            Object.keys(document.diferenciales).forEach(key => {
                let value = places[key];
                value.forEach(function(item, index) {
                    if (item["Topoforma"] == element || item['clima_label'] == element ) {
                        //Conteo de registros por cluster
                        if (clustersCont[item["Etiqueta_clase"]]==undefined ){
                            console.log(clustersCont[item["Etiqueta_clase"]] )
                            clustersCont[item["Etiqueta_clase"]]=0
                            diffPerClass[item["Etiqueta_clase"]]= new Object()
                            diffPerClass[item["Etiqueta_clase"]]['max'] = []
                            diffPerClass[item["Etiqueta_clase"]]['min'] = []

                        }
                        clustersCont[item["Etiqueta_clase"]] += 1;
                        total += 1;
        
    
                        // maximas
                        txt_null_MAX_E = validNull(item["Temp_max_emas"]);
                        txt_null_MAX_M = validNull(item["Temp_max_merra"]);
                        // minimas
                        txt_null_MIN_E = validNull(item["Temp_min_emas"]);
                        txt_null_MIN_M = validNull(item["Temp_min_merra"]);

                        Diferencia_max = -99
                        Diferencia_min = -99

                        if (txt_null_MAX_E != "Null" && txt_null_MAX_M != "Null") {
                            Diferencia_max = txt_null_MAX_M- txt_null_MAX_E
                            diffMAX.push(Diferencia_max)
                            diffPerClass[item["Etiqueta_clase"]]['max'].push(Diferencia_max)


                        }
                        if (txt_null_MIN_E != "Null" && txt_null_MIN_M != "Null") {
                            Diferencia_min = txt_null_MIN_M- txt_null_MIN_E
                            diffMIN.push(Diferencia_min)
                            diffPerClass[item["Etiqueta_clase"]]['min'].push(Diferencia_min)

                        }

                    }
    
                });
    
            });

        } // fin if temporalidad actual
        if (Temporalidad=="historico"){
            document.diferenciales.data.forEach(function(item,index){

                if (item[key_data] == element) { //where thefiltter (identifier) matches with the filter (element) iterated in the list
                    clust= $("#box_cluster_historico").val()
                    Etiqueta_clase = document.diferenciales.clusters[clust][index] 
    
                    if (clustersCont[Etiqueta_clase]==undefined){
                        clustersCont[Etiqueta_clase]={"EMAS":0,"MERRA":0}
                        diffPerClass[Etiqueta_clase]= new Object()
                        diffPerClass[Etiqueta_clase]['max'] = []
                        diffPerClass[Etiqueta_clase]['min'] = []
                    }

                    //clustersCont[Etiqueta_clase] += 1;
                    total += 1;
                    if(item['fuente']=="EMAS" ){clustersCont[Etiqueta_clase]["EMAS"] += 1;}
                    if(item['fuente']=="MERRA" || item['fuente']=="UNKWNON"){clustersCont[Etiqueta_clase]["MERRA"] += 1;}

                    // maximas
                    txt_null_MAX_E = validNull(item["Temp_max_emas"]);
                    txt_null_MAX_M = validNull(item["Temp_max_merra"]);
                    // minimas
                    txt_null_MIN_E = validNull(item["Temp_min_emas"]);
                    txt_null_MIN_M = validNull(item["Temp_min_merra"]);

                    Diferencia_max = -99
                    Diferencia_min = -99

                    if (txt_null_MAX_E != "Null" && txt_null_MAX_M != "Null") {
                        Diferencia_max = txt_null_MAX_M- txt_null_MAX_E
                        diffMAX.push(Diferencia_max)
                        diffPerClass[Etiqueta_clase]['max'].push(Diferencia_max)

                    }
                    if (txt_null_MIN_E != "Null" && txt_null_MIN_M != "Null") {
                        Diferencia_min = txt_null_MIN_M- txt_null_MIN_E
                        diffMIN.push(Diferencia_min)
                        diffPerClass[Etiqueta_clase]['min'].push(Diferencia_min)
                    }

                }
            });
        }// fin if temporalidad historico



        diffmax_stats= CalcularMediaYMediana(diffMAX)
        diffmin_stats= CalcularMediaYMediana(diffMIN)
        $("#"+divid+"_div_"+identifier).append("<h5> Calculo de diferenciales (EMAS-MERRA) </h5>");
        $("#"+divid+"_div_"+identifier).append("<h5> Diferencial MAX (mean): " + diffmax_stats['media'] + "</h5>");
        $("#"+divid+"_div_"+identifier).append("<h5> Diferencial MAX (median): " + diffmax_stats['mediana'] + "</h5>");
        $("#"+divid+"_div_"+identifier).append("<h5> Diferencial MIN (mean): " + diffmin_stats['media'] + "</h5>");
        $("#"+divid+"_div_"+identifier).append("<h5> Diferencial MIN (median): " + diffmin_stats['mediana'] + "</h5>");

        obj_summary[element] = {}

        content = "<table id=\"clusterTable_" + element + "\" class=\"table table-striped\">";
        content += "<tr class=\"info\">" +
            "<th>Cluster</th>" +
            "<th>Diff MAX</th>" +
            "<th>Diff MIN</th>" +
            "<th>stations(EMAS and MERRA)</th>" +
            "<th>EMAS</th>" +
            "<th>MERRA</th>" +
            "<th>Percentage</th></tr>";
            Object.keys(clustersCont).forEach(idCluster => {
                percentage_stations = (((clustersCont[idCluster]["EMAS"] +clustersCont[idCluster]["MERRA"])  / total) * 100).toFixed(2)
                if(idCluster=="-"){textoCluster="- Sin etiqueta "}else{textoCluster="Cluster "}
                content += "<tr>";
                content += "<td>"+ textoCluster + idCluster + "</td>";
                content += "<td>"+ CalcularMediaYMediana(diffPerClass[idCluster]['max'])['media'] + "</td>";
                content += "<td>"+ CalcularMediaYMediana(diffPerClass[idCluster]['min'])['media'] + "</td>";
                content += "<td>"+ diffPerClass[idCluster]['min'].length + "</td>";
                content += "<td>" + clustersCont[idCluster]["EMAS"] + "</td>";
                content += "<td>" + clustersCont[idCluster]["MERRA"] + "</td>";
                content += "<td>" + percentage_stations + "%</td></tr>";

                obj_summary[element][idCluster] = percentage_stations
            });
            content += "</table><hr><br>"
        $("#"+divid+"_div_"+identifier).append(content);

    });

    //los datos de la tabla summary se escriben aqui
    n_clusters= $("#txtKClust-hist").val() //para el caso de historico

    content = "<h4>precentage of stations by cluster label</h4><table id=\"tabla_summary_report_" + identifier + "\" class=\"table table-striped\">";
    content += "<tr class=\"info\">"
    content += "<th>"+identifier+"</th>";
    for (i=0;i<n_clusters;i++){
        content += "<th> Cluster "+i+"</th>";
    }
    content += "</tr>"

    Object.keys(obj_summary).forEach(element => {
        content += "<tr> <td>"+element+"</td>"
        max_value=[]
        for (i=0;i<n_clusters;i++){
            temp= obj_summary[element][i]//percentage of stations
            if (temp== undefined){temp=0}
            max_value.push(temp)//percentage of stations
        }
        console.log(max_value)

        max_value = Math.max.apply(Math, max_value);

        for (i=0;i<n_clusters;i++){
            temp= obj_summary[element][i]//percentage of stations
            if (temp== undefined){temp=0}
            if (temp == max_value){ content+= "<td style='color:red'>"+temp+"%</td>";}
            else{ content+= "<td>"+temp+"%</td>";}

        }
        content += "</tr>"
    });
    content += "</table><hr><br>"

    $("#summary_"+identifier).append(content);
    
}

