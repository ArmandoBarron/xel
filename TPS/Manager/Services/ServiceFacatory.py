import requests as api #for APIs request
import json
import logging #logger
from base64 import b64encode

class ServiceFactory(object):
    def Instance(self,name_service):
        if name_service == "describe": return describe()
        if name_service == "ANOVA": return ANOVA()     
        if name_service == "clustering": return clustering()     
        if name_service == "differential": return differential()  
        if name_service == "cleaningtools": return CleaningTools() 
        if name_service == "validateCluster": return ValidateCluster()  
        if name_service == "jaccard": return Jaccard()
        if name_service == "transform": return TransformationTools()
        if name_service == "graphics": return Graficas()

        return None

    def request(self,data,options,ip):
        """
        Create a request to the microservice
        data: is the input data in the format list[{json}].
            if its necessary another format, use format_data to define a transformation function
        options: additional options for the service in json format.
        ip: ip to access to the microservice. must be defined in config.ini file

        'RETURN' json
        """
        #return type mjust be always a json
        pass

    def format_data(self,data):
        return data


"""
HERE ARE DEFINED ALL THE SERVICES WITH THE NAME USED TO BE CALLED.
"""    
class describe(ServiceFactory):

    def request(self,data,options,ip):
        if 'columns' in options: 
            body = { 'data':  data, 'columns': options['columns']}
        else:
            body = { 'data':  data}
        url = 'http://'+ip+'/api/v1/describe'
        result = api.post(url, data=json.dumps(body))
        res = dict()
        res['result']= result.json()
        return res#json return

class ANOVA(ServiceFactory):

    def request(self,data,options,ip):
        warn = "Please send the following parameters"
        i_params = "list of variables to apply the ANOVA"
        i_method = "correlation method: pearson, kendall, spearman (pearson by default) "
        i_example = {"variables":"Temperatura,test","method":"pearson" }
        info = {'Warning':warn, 'variables':i_params,"method":i_method, 'example':i_example}

        if 'variables' in options: attribute = options['variables']
        if 'method' in options: Met = options['method']
        else: Met = "pearson"

        body = {'data':  data}
        params = {'columns': attribute, 'method': Met}
        url = 'http://'+ip+'/api/v1/correlation'
        result = api.post(url, data=json.dumps(body), params=params)
        if result.ok:
            res = dict()
            res['result']= result.json()
            return res#json return
        else:
            return json.dumps(info)

class clustering(ServiceFactory):

    def request(self,data,options,ip):
        warn = "Please send the following parameters"
        i_params = "list of variables to apply the clustering"
        i_k="number of groups"
        i_group = "variable to group data (optional)"
        i_alghoritm = "clustering alghorithm: kmeans, herarhical, silhouette (kmeans by default) "
        i_pca = "reduce dimencionality using pca (given a variance from 0 to 1) "
        i_example = {"K":"2","variables":"Humedad","group":"Codigo","alghoritm":"kmeans","pca":.95}
        info = {'Warning':warn, "k":i_k ,'variables':i_params,"group":i_group,"alghoritm":i_alghoritm, "pca":i_pca,'example':i_example}
        try:

            if 'alghoritm' not in options: algh = "kmeans"
            else: algh = options['alghoritm']

            Tosend = dict()
            Tosend['data']=data
            if 'group' in options: Tosend['index'] = options['group'] #data in groups (eg. date)
            if 'variables' in options: Tosend['columns'] = options['variables'] #variables (eg. temp)
            if 'method' in options: Tosend['method'] = options['method'] #data in groups (eg. date)
            if 'pca' in options: Tosend['pca'] = options['pca'] #data in groups (eg. date)
            if 'k' in options: Tosend['K'] = options['k'] #data in groups (eg. date)


            url = 'http://%s/clustering/%s' %(ip,algh)
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            result = api.post(url, data=json.dumps(Tosend),headers=headers)
            RES = result.json()
            if RES['status']=="OK":
                if algh=="silhouette":
                    response = api.get("http://%s%s" %(ip,RES['path']))
                    image_bin = b64encode(response.content)
                    RES = {"result":{"data":RES['result'],"image":image_bin.decode("utf-8"),"filename":"performance.png"},"TYPE":"binary"}

                return RES
            if RES['status']=="ERROR":
                raise KeyError('A very specific bad thing happened.')


        except (Exception,KeyError) as e:
            print(e)
            return json.dumps(info)

class CleaningTools(ServiceFactory):

    def request(self,data,options,ip):
        
        warn = "Please send the following parameters"
        i_columns = "list columns names to work with (all by default)"
        i_RWN = "list of values to replace with a Na value []"
        i_DropNa="options to drop a record with Na values.\n check pandas dropna options. must be a dict()"
        i_NaReaplace = "Option to replace all the NA values with a value (e.g. mean, mode, -99, 'Not know')"
        i_DataTypes = "List of json records. Parse datatypes for specific columns"
        i_example = {"columns":['humedity',"temperature"],"ReplaceWithNa":['None',-99,'NaN'],"DropNa":None,"NaReaplace":"mode","DataTypes":[{'column':'last_name','type':'str'}]}
        info = {'Warning':warn, "columns": i_columns ,"ReplaceWithNa":i_RWN ,'DropNa':i_DropNa,"NaReaplace":i_NaReaplace,"DataTypes":i_DataTypes, 'example':i_example}
        try:

            Tosend = options
            Tosend['data']=data
            url = 'http://%s/cleaning/basic' %(ip)
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            result = api.post(url, data=json.dumps(Tosend),headers=headers)
            RES = result.json()
            if RES['status']=="OK":
                return RES

        except (Exception,KeyError) as e:
            print(e)
            return json.dumps(info)

class TransformationTools(ServiceFactory):

    def request(self,data,options,ip):
        if options['process']=="melt":
            warn = "Please send the following parameters"
            i_id_vars = ""
            i_var_name=""
            i_value_name= ""
            i_example ={}
            info = {'Warning':warn, 'example':i_example}
            try:

                Tosend = {"id_vars":options['id_vars'],"value_name":options['value_name'],"var_name":options['var_name']}
                Tosend['data']=data
                url = 'http://%s/transform/melt' %(ip)
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                result = api.post(url, data=json.dumps(Tosend),headers=headers)
                RES = result.json()
                if RES['status']=="OK":
                    return RES
            except (Exception,KeyError) as e:
                print(e)
                return json.dumps(info)
        elif options['process']=="group":
            warn = "Please send the following parameters"
            i_id_vars = ""
            i_var_name=""
            i_value_name= ""
            i_example ={}
            info = {'Warning':warn, 'example':i_example}
            try:

                Tosend = {"group":options['group'],"variable":options['variable'],"group_by":options['group_by']}
                Tosend['data']=data
                url = 'http://%s/transform/group' %(ip)
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                result = api.post(url, data=json.dumps(Tosend),headers=headers)
                RES = result.json()
                if RES['status']=="OK":
                    return RES
            except (Exception,KeyError) as e:
                print(e)
                return json.dumps(info)
        else: return json.dumps(info)

class differential(ServiceFactory):

    def request(self,data,options,ip):

        warn = "Differential between 2 numeric attributtes (A-B)"
        i_A = "Attribute A"
        i_B= "Attribute B"
        i_example = {"A":"A+Temperature","B":"E+Temperature"}
        info = {'Warning':warn, "A":i_A ,'B':i_B, 'example':i_example}
        #services are not neccesary a web service

        try:
            A = options['A']
            B = options['B']
            for row in data:
                avail_keys = row.keys()
                row['differential']  = float(row[A]) - float(row[B])
            res = dict()
            res['result']= data
            return res#json return
        except KeyError as ke:
            info['available_keys'] = list(avail_keys)
            return info


class ValidateCluster(ServiceFactory):

    def request(self,data,options,ip):
        warn = "calculates various internal clustering validation or quality criteria"
        i_indexes = "list of containing the names of the indices to compute separated by comma. Available indexes:\n Ball_Hall,\
            Banfeld_Raftery,C_index,Calinski_Harabasz,Davies_Bouldin,Det_Ratio,Dunn8 intCriteria,Gamma,G_plus,\
                GDI11,GDI12,GDI13,GDI21,GDI22,GDI23,GDI31,GDI32,GDI33,GDI41,GDI42,GDI43,GDI51,GDI52,GDI53,Ksq_DetW,\
                Log_Det_Ratio,Log_SS_Ratio,McClain_Rao,PBM,Point_Biserial,Ray_Turi,Ratkowsky_Lance,Scott_Symons,\
                SD_Scat,SD_Dis,S_Dbw,Silhouette,Tau,Trace_W,Trace_WiB,Wemmert_Gancarski,Xie_Beni"
        i_column = "column name of the cluster labels (the last column by default) "
        i_ignore = "list of columns ignored in clustering (nothing by default)"
        i_cluster_cols = "list of columns used in clustering (all by default)"

        i_example = {"indexes":"Silhouette,Tau,Trace_W","column":"group","ignore_columns":"FECHA"}
        info = {'Warning':warn, 'indexes':i_indexes,"column":i_column , "ignore_columns":i_ignore, "cluster_columns":i_cluster_cols,'example':i_example}

        if 'indexes' in options: indexes = options['indexes']
        else: indexes = "all"
        if 'column' in options: column = options['column']
        else: column = "last"
        if 'ignore_columns' in options: ignore = options['ignore_columns']
        else: ignore = ""
        if 'cluster_columns' in options: cluster_cols = options['cluster_columns']
        else: cluster_cols = ""


        body = {'data':  data}
        params = {'column': column, 'indexes': indexes,'cluster_columns':cluster_cols,'ignore':ignore}
        url = 'http://'+ip+'/api/v1/validation'
        result = api.post(url, data=json.dumps(body), params=params)
        if result.ok:
            return result.json()
        else:
            return json.dumps(info)

class Jaccard(ServiceFactory):

    def request(self,data,options,ip):
        warn = "calculates various internal clustering validation or quality criteria"
        i_columns = "list of columns with group labels. separated by comma. MAX 2 (last 2 columns by default)"

        i_example = {"columns":"kmeans_clust,herarhical_clust"}
        info = {'Warning':warn, "columns":i_columns,'example':i_example}

        if 'columns' in options: columns = options['columns'] 
        else: columns = "last"

        body = {'data':  data}
        params = {'columns': columns}
        url = 'http://'+ip+'/api/v1/jaccard'
        result = api.post(url, data=json.dumps(body), params=params)
        if result.ok:
            return result.json()
        else:
            return json.dumps(info)

class Graficas(ServiceFactory):

    def request(self,data,options,ip):
        warn = "data columns grafication"
        i_columns = "list of columns to graph. (max 3 columns)"
        i_graph= "kind of graph (scatter,bar,line)"
        i_labels = "Column of labels or groups."
        i_example = {"kind":"scatter","columns":['temp','presure']}
        info = {'Warning':warn,"kind":i_graph ,"variables":i_columns,'example':i_example}

        if 'kind' in options: kind = options['kind'] 
        else: return json.dumps(info)
        toSend= dict()
        if 'variables' in options: toSend['variables'] = options['variables'] 
        if 'labels' in options: toSend['labels']=options['labels'] 
        if 'bins' in options: toSend['bins']=options['bins'] 
        if 'alpha' in options: toSend['alpha']=options['alpha'] 
        if 'point_label' in options: toSend['point_label']=options['point_label']

        toSend['data']=data


        url = 'http://%s/%s' %(ip,kind)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        result = api.post(url, data=json.dumps(toSend),headers=headers)
        RES = result.json()
        #here is retrived the url to get the image.
        if RES['status']=="ok":
            #now its necesary to get the byte of the image
            response = api.get("http://%s/%s" %(ip,RES['file']))
            image_bin = b64encode(response.content)
            return {"result":image_bin.decode("utf-8"),"TYPE":"binary","filename":RES['file']+".png"}
        if RES['status']=="ERROR":
            raise KeyError('A very specific bad thing happened.')