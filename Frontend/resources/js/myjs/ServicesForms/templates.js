
a = {
        select_multiple_fromlist : `
        <div class="form-group row m-2">
                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Map type: </label>
                <div class="col-sm-8">
                        <select class="form-control" id="map_type" onchange="ChangeVisibileOptionsOfService(this)">
                                <option value="1"> heatmap </option>
                                <option value="2"> clustering map </option>
                        </select>
                </div>
        </div>
        `,
        select_multiple_fromcolumns : `
        <div class="form-group row m-2">
                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">columns: </label>
                <div class="col-sm-8">
                        <select class="form-control" id="columns" onclick=fillselect(this)></select>
                </div>
        </div>
        `,
        textbox_autocomplete : `                        
        <div class="form-group row m-2" servopt="EVAL" >
                <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Create or alter columns:</label>
                <div class="col-sm-8">
                        <input id="query_list" type="text" class="form-control autocomplete-column" placeholder="e.g. create a column C as: C  = A + B ">
                </div>
                <div class="container">
                        <span class="help-block">Multiple querys can be provided separated by ;</span>
                        <span class="help-block">Express columns with white spaces enclosed wiith {}. Do note use " </span>
                        <span class="help-block">Examples:</span>
                        <span class="help-block">E = (A + B) / (C + D)</span>
                        <span class="help-block">G = A + A.mean()</span>
                        <span class="help-block">G = 'OK'</span>
                        <span class="help-block">{Column A} = (A + A.mean()).round(1)</span>
                </div>
        </div>
        `
        ,

}