
/// SERVICOS DE VALIDACION
SECTION = "sec-validation"
ServicesArr.push(
    {
        id: "stats-serv",
        name: "statistics",
        process_tag:"statistics",

        valid_datatypes:{input:["CSV"],output:["TXT"]},
        section:SECTION,
        desc: `Statisticl analysis of  datasets. Correlation, covariance, etc.`,
        columns:{
            default: null,
            parent: [] 
        },
        params: {
            method: '',
            proccess: '',
            columns: '',
            SAVE_DATA:true
        },
        html: `
        <div class="form-check" style="text-align: right;">
            <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
            <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
        </div>
        <br>
                        <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm"> Process: </label>
                        <div class="col-sm-8">
                            <select class="form-control" id="proccess">
                                    <option value="correlation" selected>correlation</option>
                                    <option value="covariance" >covariance</option>
                                    <option value="stadistical"> statistical summary </option>

                            </select>
                        </div></div>

                        <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm">Columns: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="columns" data-actions-box="true" onclick=fillselect(this) >
                                </select>
                                </div>
                        </div>

                        <div class="form-group row m-2">
                        <label for="txttype" class="col-sm-4 col-form-label col-form-label-sm"> correlation method: </label>
                                <div class="col-sm-8">
                                <select class="form-control" id="method">
                                        <option value="kendall" selected>kendall</option>
                                        <option value="pearson" >Pearson</option>
                                        <option value="spearman"> Spearman </option>

                                </select>
                                </div>
                        </div>

                        `
    }
)