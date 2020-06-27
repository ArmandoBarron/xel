library('plumber')
api <- plumb('api.R')
api$run(host='0.0.0.0', port=80)