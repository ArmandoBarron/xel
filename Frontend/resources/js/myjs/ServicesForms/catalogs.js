


/// SERVICOS DE CATALOGO
SECTION = "sec-catalogs"
ServicesArr.push({
        id: "data-catalogs",
        name: "catalogs",
        section:SECTION,
        valid_datatypes:{input:["CSV"],output:["CSV"]},
        desc: `data catalogs with geographical data.`,
        columns:{
            default: null,
            parent: [] 
        },
        params: {
            actions:"",
            cve_ent:"",
            cve_mun:"",
            mode:1,
            lat:"",
            lon:"",
            SAVE_DATA:true
        },
        html: `
        <div class="form-check" style="text-align: right;">
            <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
            <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
        </div>
        <br>

                <div class="form-group row m-2">
                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">catalog </label>
                        <div class="col-sm-8">
                        <select class="form-control" id="actions" onchange="OptionsHandler(this)">
                                <option value=""> </option>
                                <option value="MUNICIPIOS"> By 'clave entidad' </option>
                                <option value="MUN_POR_LATLON"> By lat-lon </option>
                        </select>
                        </div>
                </div>

                <div opth opt-actions="MUNICIPIOS">
                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">catalog </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="mode" onchange="OptionsHandler(this)">
                                        <option value="1"> Clave entidad y clave municipio </option>
                                        <option value="2"> Clave Entidad-municipio </option>
                                        <option value="3"> Nombre municipio </option>
                                </select>
                                </div>
                        </div>

                        <div opth opt-mode="1 2" class="form-group row m-2">
                                <label for="txttype" class="col-sm-6 col-form-label col-form-label-sm">Column with the key of "entidad" </label>
                                <div class="col-sm-6">
                                        <select class="form-control" id="cve_ent" data-actions-box="true" onclick=fillselect(this,mult=false)></select>
                                </div>
                        </div>

                        <div opth opt-mode="1 3" class="form-group row m-2">
                                <label for="txttype" class="col-sm-6 col-form-label col-form-label-sm">Column with the key of "municipio" </label>
                                <div class="col-sm-6">
                                        <select class="form-control" id="cve_mun" data-actions-box="true" onclick=fillselect(this,mult=false)></select>
                                </div>
                        </div>

                </div>
                
                <div opth opt-actions="MUN_POR_LATLON">

                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-6 col-form-label col-form-label-sm">Latitud </label>
                                <div class="col-sm-6">
                                        <select class="form-control" id="lat" data-actions-box="true" onclick=fillselect(this,mult=false)></select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                                <label for="txttype" class="col-sm-6 col-form-label col-form-label-sm">Longitud</label>
                                <div class="col-sm-6">
                                        <select class="form-control" id="lon" data-actions-box="true" onclick=fillselect(this,mult=false)></select>
                                </div>
                        </div>

                </div>




`
    }
)