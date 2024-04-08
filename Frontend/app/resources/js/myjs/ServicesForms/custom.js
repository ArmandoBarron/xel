


/// SERVICOS DE fuentes de datos
SECTION = "sec-custom"

ServicesArr.push({
        id: "custom",
        process_tag:"single",
        valid_datatypes:{input:["NA"],output:["CSV"]},
        name: "Simple ",
        section:SECTION,
        desc: `custom desc`,
        columns:{
            default: null,
            parent: [] 
        },
        params: {
            actions:"REQUEST",
            SAVE_DATA:true,
        },
        html: `
        <div class="form-check" style="text-align: right;">
                <input type="checkbox" checked class="form-check-input" id="SAVE_DATA">
                <label class="form-check-label" for="SAVE_DATA">Index results (uncheck to improve the preformance)</label>
        </div>
        `
    }
)
