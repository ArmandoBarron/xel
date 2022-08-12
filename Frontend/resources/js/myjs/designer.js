var rootMoved = false;

var METADATA_SOLUTION = {}

// global variable. keeps all the instructions of the solution as: 
//      id: "root",
//      boxid: 0,
//      type: "root",
//      columns: {
//          default: [],
//          parent: []
//      },
//      name: "root",
//      root: true,
//      children: []
var dataObject = {};

// GLOBAL variable to enter into the pipeline functions
var canvasElementsCount;
// currentLayout saves the info about the on canvas positioned boxes, the order. 
var currentLayout = undefined;

var confighover = {    
    over: function(){ShowBoxParametersNav(this)}, // function = onMouseOver callback (REQUIRED)
    interval: 200, // number = milliseconds delay before trying to call over    
    timeout: 800, // number = milliseconds delay before onMouseOut    
    sensitivity:3,
    out: StandbyNav // function = onMouseOut callback (REQUIRED)    
};

$(document).ready(function () {



    flowey_createSections()
    // add dinamic parameters to services in ServiceArr
    flowey_ConfigServices()
    // data contains the static values for the 'services'
    demoflowy_createBoxes(ServicesArr.length, ServicesArr);

    $( ".blockdesc" ).hover(
        function() {
            $(this).toggleClass("text-truncate");
        }, function() {
            $(this).toggleClass("text-truncate");
        }
    );

    
    // init flowy
    flowy(document.getElementById("canvas"), demoflowy_drag, demoflowy_release,
        demoflowy_snapping, demoflowy_rearranging, demoflowy_onBlockChange, 30, 25);


    $('.modal.fade').on('shown.bs.modal', function (e) { //function que se ejecutan cuando el modal se abre
        ChangeVisibileOptionsOfService("",onlyhide=false) //este muestra los divs de la seccion seleccionada
        $(".courtain").show("slow") //se muestran todos los elementos de clase courtain (para hacerlo mas bonito)
        $(".compact-dt").DataTable().columns.adjust()//se ajustan las datatable
        $(".selectpicker").selectpicker("refresh")
        //Activate_Autcomplete() //se añade el evento para autocompletar
        
    })
    $('.modal.fade').on('hidden.bs.modal', function (e) { // funcion que se ejecuta cuando se cierra un modal
        $(".courtain").hide("slow")
        //$('#modal_inspect_body')
        
        if ($('.modal.show').length <= 0)
        {
            $('.modal-body-dynamic').html("") // se vacian todos los body
        }
      })

    var popoverShow = false;
    var tempblock2;
    canvasElementsCount = 0
    //$('#output').click((e) => {
    //    Exec_graph();
    //    // Add verification to enable when exec_graph() is done.
    //    $('#output').prop('disabled', true);
    //});
    // al clickear el boton #output se ejecuta la funcion

    
    $('#foutput').click((e) => {
        console.log(flowy.output());
    });
    // Modal buttons actions
    $('#btnSave').click(demoflowy_saveChanges);
    $('#btnClose').click((e) => {
        demoflowy_closeModal();
    })
    // Show/hide all popovers
    $('#gralInfo').click(function (event) {
        if (popoverShow) {
            $('[data-toggle="popover"]').popover('hide');
            $('[data-toggle="popover"]').popover('disable');
            popoverShow = false;
        } else {
            $('[data-toggle="popover"]').popover('enable');
            $('[data-toggle="popover"]').popover('show');
            popoverShow = true;
        }
    });
    // when modal is hidden, remove all input fields
    $('#modal_edition').on('hidden.bs.modal', (e) => {
        // remove params fields from modal
        $("#modal_edition .modal-body").empty();
    });
    // adding the dblclick event before elements are added, to avoid
    // using the observer
    var flowyoutputdata;
    $('#canvas').on('dblclick', '.blockelem', (e) => { //'.blockelem:not(#root)'
        demoflowy_showModalFromId(e.target.closest('.card').id, e.target.closest('.card').getAttribute("type"));
    });
    $('#btnImport').click((e) => {
        $('#inputImport').trigger('click');
    });
    $('#inputImport').change((e) => {
        name = document.getElementById('inputImport').files[0].name;

        var files = document.getElementById('inputImport').files;
        if(files.length <= 0) return false;

        var fr = new FileReader();
        fr.onload = (e) => {
            // FileReader result object. Containing the file text.
            var result = JSON.parse(e.target.result);
            // Update current data:
            // Change dataObject with the imported data.
            dataObject = result.dataobject;
            // Update the count of elements on canvas to keep adding more boxes.
            canvasElementsCount = result.lastBoxId;
            // Use Flowy import to add the boxes to the canvas.
            flowy.import(result.metadata.frontend);
            // load metadata into page
            Metadata_assign(result.metadata)
            
            currentLayout = [...flowy.output().blockarr]
            $(".block-hoverinfo").hoverIntent( confighover )
        }
        fr.readAsText(files.item(0));
    });
    // Export using the flowy output, which contains the data about
    // the position and html data of the boxes.
    // Add the dataObject and elementsCount to that flowy output object
    // To use it when importing the same file again.
    $('#btnExport').click((e) => {
        flowyOutput = {} //flowy.output();
        flowyOutput.dataobject = dataObject;
        flowyOutput.lastBoxId = canvasElementsCount;
        //save metadata
        flowyOutput.metadata = Metadata_collector()
        dag = []
        //transform_dag(dataObject,dag)
        //flowyOutput.DAG = dag
        //namefile
        if (flowyOutput.metadata.name==""){
            namefile = "flowy_output"
        }
        else{
            namefile = flowyOutput.metadata.name
        }

        exportTXTFile(flowyOutput, namefile);
    });

    function demoflowy_snapping(drag, first, parent) {

        drag.classList.remove("elementhover");

        var id = drag.getAttribute("id");
        var name = drag.getAttribute("name");
        var service_type = drag.getAttribute("type");
        //var idParent="root" // by default
        //var canvasId="root"
        canvasId= "c" + canvasElementsCount + "-" + id;

        console.log(service_type)
        if (first){
            if(service_type=="DATASOURCE"){
                idParent = canvasId // init data object
                ///dataObject = {id: "root", boxid: 0, type: id, service_type:service_type, columns: { default: [], parent: [] }, name: "root", root: true, children: []}
            }else{
                notificarUsuario("Select a datasource first.","warning")
                drag.innerHTML=""
                flowy.deleteBlocks()
                return false
            }
        }
        else{
            idParent = parent.getAttribute("id");
        }

        console.log("parent id:"+idParent )
        console.log("canvas id (in dataObject):"+canvasId )

        // Se configura el front end de la caja

        grab = drag.querySelector(".fb-grab");
        grab.parentNode.removeChild(grab);
        blockin = drag.querySelector(".fb-desc");
        blockin.parentNode.removeChild(blockin);
        blockin = drag.querySelector(".row-cols-2");
        blockin.parentNode.removeChild(blockin);

        drag.classList.add('position-absolute');
        drag.classList.remove('row');
        drag.classList.remove('container-fluid'); // ya no se usara row

        if (first){
            class_type_box = "root"
        }
        else{
            class_type_box = "task"
        }


        bcontent = `<div type="${id}" id="${canvasId}" class="card c-block container">
                        <div class="row card-header" style="background-color:#fff" >
                            <div class="col-12 text-left text-uppercase d-inline-block text-truncate" style="padding-left: 3px;padding-right: 3px;padding-bottom: 3px;">
                                <i style="margin-right:5px" class="fas fa-info-circle fa-lg block-hoverinfo" idcanvas="${canvasId}"></i> <em id="${canvasId}_alias" >${canvasId}</em>
                            </div>
                        </div>
                        <div class="row" style="padding:4px; overflow:auto">
                            <div class="service-options col-12 justify-content-center">
                                <div class= "serviceLoadingIcon-${class_type_box}" id="serviceLoadingIcon"></div>
                            </div>
                                <div class="col-2" style="padding:5px; text-align:center;" > <i class="fas fa-pen-square fa-xl elementhover" onclick="demoflowy_btnEditarClick(event)"></i></div>
                                <div class="col-2 InspectDataIcon-${class_type_box}" style="padding:5px; text-align:center;" id="${canvasId}_inspect"></div>
                                <div class="col-2 downloadDataIcon-${class_type_box}" style="padding:5px; text-align:center;" id="${canvasId}_downloadDataIcon"></div>
                                <div class="col-2 showOnMapIcon-${class_type_box}" style="padding:5px; text-align:center;" id="${canvasId}_showOnMapIcon"></div>
                        </div>
                    </div>
                `;
        //SE AÑADE EL CONTENIDO A LA CAJA
        drag.innerHTML += bcontent;
        drag.setAttribute("id", canvasId);
        //se modifican algunos estilos
        drag.style["padding-top"] = '3px';


        var box_template = flowey_GetTemplate_service(id)    
        box_template.id = canvasId
        box_template.alias = canvasId

        box_template.boxid= parseInt($(`#${canvasId} > .blockid`).val())
        canvasElementsCount++;

        // heredar la metadata del padre, salvo que sea la primera caja
        if (first){
            console.log("se inicializa el dataobject")
            dataObject= box_template
        }
        else{
            ParentBox = JSON.parse(JSON.stringify(demoflowy_lookForParent(idParent)))

            if(ParentBox.it_produced_data){ // si la caja padre ha producido datos entonces se heredan esos
                box_template.service_metadata.father = ParentBox.service_metadata.this
            }
            else{ // de lo contrario se heredan los del padre del padre
                box_template.service_metadata.father = ParentBox.service_metadata.father
            }
            demoflowy_lookForParent(idParent).children.push(box_template); //añadir caja al object
        }

        // hover for the info
        $(".block-hoverinfo").hoverIntent( confighover )
        return true;
    }


    function demoflowy_drag(block) {
        block.classList.add("blockdisabled");
        

        tempblock2 = block;
        all_arrows = $('.arrowblock');
        all_blocks = $('#c1-s-1');
    }

    function demoflowy_release() {
        console.log("release")
        all_arrows = $('.arrowblock');
        all_blocks = $('#c1-s-1');
        //tempblock2.classList.add("elementhover");
        if (tempblock2) tempblock2.classList.remove("blockdisabled");
    }

    function demoflowy_rearranging(block, parent) {
        demoflowy_removeChild(block.id);
        //canvasElementsCount = contar_servicios(dataObject.children)
        return false;
    }


    function demoflowy_onBlockChange(type) {

        console.log(type)
        if (type == 'add') {
            currentLayout = [...flowy.output().blockarr]
                .map(c => {
                    return {
                        id: c.id,
                        parent: c.parent
                    }
                })
                .sort((a, b) => a.id - b.id);
            //var left = parseInt($('#root')[0].style.left);
        } else if (type == 'reasign') {
            let changes = [...flowy.output().blockarr]
                .map(c => {
                    return {
                        id: c.id,
                        parent: c.parent
                    }
                })
                .sort((a, b) => a.id - b.id);

            // get only the elements that have changed.
            var realchanges = demoflowy_getRealChanges(changes, currentLayout);
            currentLayout = changes;

            if (realchanges.length < 1) {
            } else {
                realchanges.forEach(c => {
                    let newparent = demoflowy_lookForParentWithBoxId(c.parent);
                    // make a copy of the child, cuz it is removed after this
                    let chlidFound = demoflowy_lookForParentWithBoxId(c.id);
                    console.log(chlidFound)
                    let child = JSON.parse(JSON.stringify(chlidFound));

                    let deleted = demoflowy_removeChildWithBoxId(c.id);
                    if (deleted) {
                    } else {
                    }
                    newparent.children.push(child);
                });
            }
        }
        // hover for the info
        $(".block-hoverinfo").hoverIntent( confighover )

    }
});

function reload_metadata_fromBox(id_box){

    box = demoflowy_lookForParent(id_box)
    FatherBox = demoflowy_lookForFather(id_box)
    console.log(id_box)
    console.log(`La caja padre de ${id_box} produjo datos?: ${FatherBox.it_produced_data}`)
    if(FatherBox.it_produced_data){ // si la caja padre ha producido datos entonces se heredan esos
        box.service_metadata.father = CloneJSON(FatherBox.service_metadata.this)
    }
    else{ // de lo contrario se heredan los del padre del padre
        box.service_metadata.father = CloneJSON(FatherBox.service_metadata.father)
    }

    const isEmpty = Object.keys(box.service_metadata.father).length === 0 //si es null no se hace nada
    if(isEmpty){return false}
    else{return true}
} 


function demoflowy_lookForFather(parentId) {
    var unknownBOX = arguments[1] ? arguments[1] : dataObject;
    var Father = null;
    parent = unknownBOX.children.find(child => child.id == parentId);
    if (parent === undefined) {
        for (let i = 0; i < unknownBOX.children.length; i++) {
            if (unknownBOX.children[i].children.length > 0) {
                Father = demoflowy_lookForFather(parentId, unknownBOX.children[i]);
                if (Father !== null && Father !== undefined) return Father;
            }
        }
    }
    else{ Father = unknownBOX}
    
    return Father;
}


function demoflowy_lookForParent(parentId) {
    var children = arguments[1] ? arguments[1] : dataObject.children;
    var parent = null;
    if (parentId == dataObject.id) parent = dataObject;
    else {
        parent = children.find(child => child.id == parentId);
        if (parent === undefined) {
            for (let i = 0; i < children.length; i++) {
                if (children[i].children.length > 0) {
                    parent = demoflowy_lookForParent(parentId, children[i].children);
                    if (parent !== null && parent !== undefined) return parent;
                }
            }
        }
    }
    return parent;
}


function demoflowy_lookForParentWithBoxId(id) {
    var children = arguments[1] ? arguments[1] : dataObject.children;
    var parent = null;
    if (id == dataObject.boxid) parent = dataObject;
    else {
        parent = children.find(child => child.boxid == id);
        if (parent === undefined) {
            for (let i = 0; i < children.length; i++) {
                if (children[i].children.length > 0) {
                    parent = demoflowy_lookForParentWithBoxId(id, children[i].children);
                    if (parent !== null && parent !== undefined) return parent;
                }
            }
        }
    }
    return parent;
}

function demoflowy_removeChildWithBoxId(id) {
    var children = arguments[1] ? arguments[1] : dataObject.children;
    var deleted = false;

    for (let i = 0; i < children.length; i++) {
        if (children[i].boxid == id) {
            children.splice(i, 1);
            deleted = true;
            break;
        } else if (children[i].children.length > 0) {
            deleted = demoflowy_removeChildWithBoxId(id, children[i].children);
        }
    }
    return deleted;
}
// Compare the new arranging of boxes to the previous arranging
// if there are changes, return which boxes where moved only, 
// to prevent reading all boxes which weren't changed.
function demoflowy_getRealChanges(changes, prevChanges) {
    var realChanges = [];

    for (let i = 0; i < changes.length; i++) {
        if (changes[i].parent !== prevChanges[i].parent) {
            // look for the changes and return those only
            realChanges.push(changes[i]);
        }
    }
    return realChanges;
}

function demoflowy_closeModal() {
    $('#modal_edition').modal('hide');
}

// Remove child with id from dataObject
function demoflowy_removeChild(id) {
    if (rootMoved) return;
    var children = arguments[1] ? arguments[1] : dataObject.children;
    var deleted = false;

    for (let i = 0; i < children.length; i++) {
        if (children[i].id == id) {
            children.splice(i, 1);
            deleted = true;
            break;
        } else if (children[i].children.length > 0) {
            deleted = demoflowy_removeChild(id, children[i].children);
        }
    }
    return deleted;
}
function flowey_createSections(){
    i = 1
    CONFIG_SECTIONS.forEach(sec_info => {
        $("#faq").append(`\
        <div class="cardsec">\
            <div class="card-header" id="faqhead${i}">\
                <a href="#" class="btn btn-header-link collapsed" data-toggle="collapse" data-target="#faq${i}"\
                aria-expanded="false" aria-controls="faq1">${sec_info.name}</a>\
            </div>\
            <div id="faq${i}" class="collapse" aria-labelledby="faqhead${i}" data-parent="#faq">\
                <div class="card-body" id="${sec_info.id}"></div>\
            </div>\
        </div>`)
        i++
    });

}

function flowey_ConfigServices(){
    //serviceArr is a global variable with all the metadata for the services
    n = ServicesArr.length
    for (let i = 0; i < n; i++) {
        //create a new key for service metadata. columns, data, filenames, etc 
        ServicesArr[i].service_metadata={"father":{}, "this":{} }
        ServicesArr[i].it_produced_data=false
        ServicesArr[i].children=[]
        ServicesArr[i].alias=""
    }
}

function flowey_GetTemplate_service(idservice){
    //serviceArr is a global variable with all the metadata for the services
    n = ServicesArr.length
    for (let i = 0; i < n; i++) {
        if (ServicesArr[i].id==idservice){
            return  JSON.parse(JSON.stringify(ServicesArr[i]))
        }
    }
    return null
}
function demoflowy_createBoxes(n, boxData) {
    for (let i = 0; i < n; i++) {

        let id = boxData[i].id;
        let name = boxData[i].name;
        let desc = boxData[i].desc;
        let type = boxData[i].service_type; //SERVICE OR DATASOURCE
        let IN_OUT = boxData[i].valid_datatypes; //{input:[], output:[]}

        Input_list =""
        Output_list =""

        IN_OUT.input.forEach(function(valid_file_format){
            Input_list += valid_file_format=="NA" ?  `<i class="fas fa-cloud" data-toggle="tooltip" data-placement="bottom" title="From repository"></i> `: ``;
            Input_list += valid_file_format=="CSV" ?  `<i class="fas fa-file-csv" data-toggle="tooltip" data-placement="bottom" title="CSV file"></i> `: ``;
            Input_list += valid_file_format=="ZIP" ?  `<i class="fas fa-file-archive"  data-toggle="tooltip" data-placement="bottom" title="ZIP file"></i> `: ``;
            Input_list += valid_file_format=="JPEG" ?  `<i class="fas fa-file-image  data-toggle="tooltip" data-placement="bottom" title="JPEG Image""></i> `: ``;
            Input_list += valid_file_format=="HTML" ?  `<i class="fab fa-html5" data-toggle="tooltip" data-placement="bottom" title="HTML file"></i>`: ``;
            Input_list += valid_file_format=="JSON" ||  valid_file_format=="TXT"  ?  `<i class="fas fa-file-alt"></i>  data-toggle="tooltip" data-placement="bottom" title="Plaintext file"`: ``;
        });
        IN_OUT.output.forEach(function(valid_file_format){
            Output_list += valid_file_format=="NA" ?  `<i class="fas fa-cloud" data-toggle="tooltip" data-placement="bottom" title="From repository"></i> `: ``;
            Output_list += valid_file_format=="CSV" ?  `<i class="fas fa-file-csv" data-toggle="tooltip" data-placement="bottom" title="CSV file"></i> `: ``;
            Output_list += valid_file_format=="ZIP" ?  `<i class="fas fa-file-archive"  data-toggle="tooltip" data-placement="bottom" title="ZIP file"></i> `: ``;
            Output_list += valid_file_format=="JPEG" ?  `<i class="fas fa-file-image  data-toggle="tooltip" data-placement="bottom" title="JPEG Image""></i> `: ``;
            Output_list += valid_file_format=="HTML" ?  `<i class="fab fa-html5" data-toggle="tooltip" data-placement="bottom" title="HTML file"></i>`: ``;
            Output_list += valid_file_format=="JSON" ||  valid_file_format=="TXT"  ?  `<i class="fas fa-file-alt"></i>  data-toggle="tooltip" data-placement="bottom" title="Plaintext file"`: ``;
        });



        if (type==undefined){type="SERVICE"}

        let section  = boxData[i].section;

        var box =
            `
            <div class="blockelem container-fluid create-flowy noselect elementhover" type="${type}" id="${id}" name="${name}">
                <div class="row" style="margin:0px">
                    <div class="col-1 fb-grab" >
                        <i class="fas fa-grip-vertical align-middle"></i>
                    </div>
                    <div class="col-10 fb-desc">
                        <div>
                            <p class="blocktitle">${name}</p>
                            <p class="blockdesc text-truncate">${desc}</p>
                        </div>
                    </div>
                </div>
                <div class="row row-cols-2" style="margin:0px">
                    <div class="col blocktag text-center"> Input: ${Input_list}</i> </div>
                    <div class="col blocktag text-center"> Output: ${Output_list} </div>
                </div>
            </div>
            `
        $('#'+section).append(box);
    }


}

function demoflowy_btnEditarClick(event) {
    closestCard = event.target.closest('.card');
    console.log(closestCard)
    canvastype = closestCard.getAttribute("type")
    canvasid = closestCard.id
    demoflowy_showModalFromId(canvasid,canvastype);
}

function demoflowy_showModalFromId(canvasId,canvasType) {
    let parent = demoflowy_lookForParent(canvasId); // se obtiene la metadata mediante el ID
    //modal que se abrira
    if (parent.service_type =="DATASOURCE"){modal2open = "modal_datasource"}
    else{modal2open = "modal_edition"}

    $(`#${modal2open}`).data("sourceId", canvasId);
    template = flowey_GetTemplate_service(canvasType)

    $(`#${modal2open} .modal-body`).html(template.html);
    $('.selectpicker').selectpicker('refresh') //carga los selectpicker en el modal

    $(`#${modal2open} .modal-body`).ready(function ($) {
        // first, add the current html to let the list, if there's any, as
        // it was the last time it was modified.
        for (let p in parent.params) {
            // then check the type of each param of the object, and assign its value to
            // its correspondent input on the modal form.
            
            let type = typeof (parent.params[p]);
            var input = $(`#${modal2open} .modal-body #${p}`);

            //console.log(type)
            if(input[0].tagName == 'SELECT') {
                
                $(`#${p}`).trigger('click'); //simulate click to load the options
                $(`#${p}`).selectpicker('val', parent.params[p]);

                var attr =  $(`#${p}`).attr('onchange'); //verify if has attr for handler
                if (typeof attr !== 'undefined' && attr !== false) {
                    $(`#${p}`).trigger("change");
                    //OptionsHandler(document.getElementById(p))
                }
            } 
            else if (input[0].tagName =="DIV"){ // esto quiere decir que es un from control personalizado
                type =  input.attr("type")
                if (type=="namefiles-tree"){
                    fill_namefiles() //se carga la info del arbol
                    nodes = []
                    parent.params[p].forEach(function(selected_file){
                        $("#"+p).jstree('select_node', selected_file);
                    });
                }
                if (type=="namefiles-list"){
                    list_selected_files =parent.params["list_files"]
                    id_destination = p

                    $("#"+id_destination).html("")
                    // div destino 
                    var id_tmp = 1
                    list_selected_files.forEach(function(path){
                            //create control
                            htmlstring =`
                                <div class="form-group row m-2"> 
                                    <label for="txttype" class="col-sm-12 col-form-label col-form-label-sm">Keys of ${path}</label>
                                    <div class="col-sm-12">
                                        <input id="file_${id_tmp}" type="text" class="form-control">
                                    </div>
                                </div>`
                            $("#"+id_destination).append(htmlstring)
                            //se le activa el autocomplete
                            AutocompleteByFileInfo("file_"+id_tmp, path,Modal_selector="#modal_edition")
                            id_tmp++

                    });
                
                    list_columns = parent.params[p].split(";")
                    list_selector = $(`#${p} > .form-group`)
                    list_selector.each(function(index,value){
                        $(this).children("div").children("input").val(list_columns[index]) 
                    })
                }
                if (type=="logical-rules"){
                    ID_rule=1
                    parent.params[p].forEach(function(rule,index){
                        Handler_Rules(`#${p}`)
                        i=index+1

                        var [column,process,operator,values] = rule.split("::")
                        console.log(column,process,operator,values)

                        $(`#rule_${i}_column`).trigger('click'); //simulate click to load the options
                        $(`#rule_${i}_column`).selectpicker('val',column);
                        $(`#rule_${i}_column`).selectpicker('refresh');

                        $(`#rule_${i}_process`).val(process)
                        $(`#rule_${i}_operator`).val(operator)
                        value_rule(i)

                        if (operator!="InRange" && operator!="OutRange"){ //no es un rango
                            $(`#rule_${i}_value1`).val(values)
                        }
                        else{//es un rango
                            console.log(values)
                            values = values.split("to")
                            $(`#rule_${i}_value1`).val(values[0])
                            $(`#rule_${i}_value2`).val(values[1])
                        }
                    });

                }
                if (type=="shopping-car-list"){
                    ID_CAR_ELEMENT = 1
                    parent.params[p].forEach(function(element,index){
                        console.log("se deberia estar añadiendo")
                        console.log(element)
                        console.log("#"+p)

                        ShoppingCar_add_element(element,element,"#"+p)
                    });
    
                }
    
            }
            else if (['string', 'number', 'boolean'].includes(type)) {
                if (type == 'boolean') $(`#${modal2open} .modal-body #${p}`)[0].checked = parent.params[p];
                else if (type == 'string'){ //string 
                    $(`#${modal2open} .modal-body #${p}`).val(parent.params[p]);

                    if_has_autocomplete= $(`#${modal2open} .modal-body #${p}`).hasClass("autocomplete-column")
                    if (if_has_autocomplete){
                        Activate_Autcomplete(`#${modal2open} .modal-body #${p}`,Modal_selector="#"+modal2open)
                        
                    }
                }
                else {  //number
                    $(`#${modal2open} .modal-body #${p}`).val(parent.params[p]);
                }
            } else {
                //for UL
                // remove list elements before adding the ones on the param array
                input.empty();
                parent.params[p].forEach(li => {
                    input.append(`<li id="${li}" class="list-group-item">${li}</li>`);
                });
                
            }
        }
        
        init_modal()
    });


    // from now on, modal always should be ready.
    //parent.isModalReady = true; //esta validacion ya no se ocupa
    init_modal()
    ChangeVisibileOptionsOfService("",onlyhide=true) // este esconde todos los divs que no se ocupan
    $('[opth]').hide() // todos los que tengan este atributo ser esconden. sirve para manejar las opciones en el modal

    // SHOW MODAL
    $(`#${modal2open}`).modal('show');
    //$(`#${modal2open} .modal-title`).text(parent.alias);
    $(`#${modal2open} .modal-title`).html(`<input type="text" class="invisible-input" id="alias_for_service" value="${parent.alias}" /> `);


}




function demoflowy_saveChanges() {
    Modal_selector = ".modal.fade.show" // sirve para los modal activos (debe estar activo primero)

    var id = $(Modal_selector).data('sourceId');
    var parent = demoflowy_lookForParent(id);
    var fulltext = '';

    // primero se guarda metadata externa a los parametros 
    parent.alias= $(`${Modal_selector} .modal-title #alias_for_service`).val()
    $(`#${id}_alias`).text(parent.alias)

    for (let p in parent.params) {
        //console.log(p)
        let input = $(`#${p}`)[0];
        let tagname = input.tagName;

        fulltext += `<strong>${p}:</strong> `;

        // TODO: ADD SAVES AND LOADS FOR TYPE SELECT AND SELECT MULTIPLE
        //console.log(tagname)

        if (tagname == 'UL') {
            // emtpy the array before adding the new list order
            parent.params[p] = [];
            let children = Array.from(input.childNodes)
                .filter(c => c.nodeType == Node.ELEMENT_NODE);

            fulltext += `<ul class="list-group my-2">`;
            children.forEach(el => {
                let id = el.id;
                let text = el.innerHTML;
                iconToRemove =  ` <a href="#" onclick="remove_list_element(this)" data-toggle="tooltip" title="remove this"><span class="glyphicon glyphicon-minus" aria-hidden="true"></span></a>`
                text = text.replace(iconToRemove,"")
                text=text.replace(/\s/g, "");
                fulltext += `<li id="${id}" class="list-group-item">${text}</li>`;

                // parent.params[p].push({id: id, text: text});
                //parent.params[p].push({id: id, text: text});
                parent.params[p].push(text);
            });
            fulltext += `</ul>`;
        } 
        else if (tagname=="DIV"){ // esto quiere decir que es un from control personalizado
            type =  $(`#${p}`).attr("type")

            if (type=="namefiles-tree"){
                list_selected_files = $("#"+p).jstree().get_checked(["full"]) // se obtienen los nodos seleccionados
                tmp_list = []
                list_selected_files.forEach(function(obj){
                    if (obj.type=="file"){
                        tmp_list.push(obj.original.path)
                    }
                });
                parent.params[p] = tmp_list
                console.log("se guardaron los datos del files tree")
            }
            if (type=="namefiles-list"){
                list_selector = $("#list_columns > .form-group")
                list_columns = ""
                list_selector.each(function(){
                    list_columns += $(this).children("div").children("input").val() + ";"
                })
                parent.params[p] = list_columns.slice(0, -1);
            }
            if (type=="shopping-car-list"){
                parent.params[p] = ShoppingCar_get_list("#"+p)

            }
            if (type=="logical-rules"){
                lista_reglas = []
                for (i=1;i<ID_rule;i++){
                    column = $(`#rule_${i}_column`).val()
                    process = $(`#rule_${i}_process`).val()
                    operator = $(`#rule_${i}_operator`).val()
                    val1 = $(`#rule_${i}_value1`).val()
                    val2 = $(`#rule_${i}_value2`).val()

                    if (column!==undefined){
                        if (operator!="InRange" && operator!="OutRange"){ //no es un rango
                            rule = `${column}::${process}::${operator}::${val1}`
                        }
                        else{//es un rango
                            rule = `${column}::${process}::${operator}::${val1}to${val2}`
                        }
                        lista_reglas.push(rule)
                    }
                    else{
                        console.log(`la regla ${i} no existe`)
                    }

                }
                parent.params[p] = lista_reglas
                console.log(lista_reglas)
            }

        }
        else {
            let value = $(`#${p}`).val()
            let type = input.type;
            if (type == 'checkbox'){
                parent.params[p] = input.checked;
                fulltext += `<label class="text-danger">${parent.params[p]}</label><br>`;
            }
            else if (value === "" || value === null) {
                parent.params[p] = "";
                fulltext += `<label class="text-danger">${parent.params[p]}</label><br>`;
            }
            else if (!isNaN(value)) {
                parent.params[p] = Number(value);
                fulltext += `<label class="text-danger">${parent.params[p]}</label><br>`;
            }
            else if(type == 'select-multiple') {
                parent.params[p] = value;
                fulltext += `<ul>`;                
                value.forEach(v => {
                    fulltext += `<li>${v}</li>`;
                })
                fulltext += `</ul>`;
            }
            else {
                parent.params[p] = value;
                fulltext += `<label class="text-danger">${parent.params[p]}</label><br>`;

            }
        }
    }

    $(`#${id}`).find('div.card-text').html(fulltext);
    demoflowy_closeModal();
}

function ShowBoxParametersNav(el){
    id = el.getAttribute('idcanvas')
    console.log(id)
    var box = demoflowy_lookForParent(id);
    
    i = 1
    content = `<div class='row col-12'><h1>${box.alias}</h1></div>`
    content+=`<table class="table">
                <thead class="thead-dark">
                <tr>
                    <th scope="col">#</th>
                    <th scope="col">Params</th>
                    <th scope="col">value</th>
                </tr>
                </thead> <tbody>
                `
    for (let p in box.params) {
        console.log(p)
        content+= `<tr>
                    <th scope="row">${i}</th> <td>${p}</td><td>${box.params[p]}</td>
                   </tr>`
        i++
    }

    content+="</tbody> </table>"

    $("#sidebar-content").hide().html(content).slideDown(500);
    openNav()
}

function Metadata_collector(){
    obj_metadata= {}
    token = $("#modal_save-solutions-form-tokensolution").val()
    name = $("#modal_save-solutions-form-name").val()
    desc= $("#modal_save-solutions-form-desc").val()
    tags= $("#modal_save-solutions-form-tags").val().split(",")
    obj_metadata.name= name
    obj_metadata.desc= desc
    obj_metadata.tags= tags
    obj_metadata.token= token
    obj_metadata.frontend = flowy.output();
    obj_metadata.source_type = dataObject.source_type //type of the root box
    obj_metadata.datasource = DATA_WORKFLOW.data //dataset
    obj_metadata.datasource_type = DATA_WORKFLOW.type //kind of dataset
    obj_metadata.canvasElementsCount = canvasElementsCount //kind of dataset
    return obj_metadata

}

function Metadata_assign(meta){
    $("#modal_save-solutions-form-name").val(meta.name)
    $("#modal_save-solutions-form-desc").val(meta.desc)
    $("#modal_save-solutions-form-tags").val(meta.tags)
    // load token
    Set_Tokensolution(meta.token)
    //import dataset info
    Set_DatasourceMap(meta.datasource,meta.datasource_type)
}

function Set_Tokensolution(token){
    TOKEN_SOLUTION = token
    $("#modal_save-solutions-form-tokensolution").val(token)
}
function Set_DatasourceMap(datasource_Obj,type_dataset)
{
    DATA_WORKFLOW = {'data':datasource_Obj,'type':type_dataset};
}


function contar_servicios(DAG){
    contador = DAG.length
    for (let i = 0; i < DAG.length; i++) {
        contador= contador + contar_servicios(DAG[i].children)
    }
    return contador
}

function Listar_tareas(lista_tareas, objeto_padre){

    objeto_padre.forEach(function(task){ 
        lista_tareas.push(task.id)
        // se recorren los hijos de esa tarea
        lista_tareas = Listar_tareas(lista_tareas,task.children) 
    });
    return lista_tareas
}



function CloneJSON(js){
    return copiedjson = JSON.parse(JSON.stringify(js));
}

function arrayRemove(arr, value) { 
    return arr.filter(function(ele){ 
        return ele != value; 
    });
}

function Toggle_Modal(action="show",Modal_selector=".modal.fade.show"){ //por defecto cierra el modal que se esta mostrando
    $(Modal_selector).modal(action);
}

function Toggle_Loader(action="show",text="Loading... Please wait."){
    console.log(action)
    if (action=="show"){
        $(".overlay_loader").show()
        $(".spanner_loader").show()
        $("#text_loader").html(text)
    }
    if (action=="message"){
        $("#text_loader").html(text)
    }
    if (action=="hide"){
        $(".overlay_loader").hide()
        $(".spanner_loader").hide()
    }
    
}