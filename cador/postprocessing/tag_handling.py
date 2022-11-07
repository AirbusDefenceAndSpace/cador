import time

from cador.postprocessing.geometry import img_geometry_to_latlon_geometry


def produce_tagentry(service_description, request_order, service_output):
    """
    Produce the JSON tag entry from service description and service output
    :param service_description: result of service/about request
    :param request_order: request order in input of predict
    :param service_output: an output of service/predict request
    :return a list of tagentry
    """

    def create_tag_from_sources(service_description, request_order, service_output, algo_tag):
        """
        Use all the available sources to build the tag entry
        :param service description: result of about request on service
        :param request_order: request order ininout of predict
        :param service_output: an output of service predict request
        :param algo_tag: tag coming from algo in service output
        """
        tagentry = dict()
        tagentry['confidence'] = algo_tag['confidence']
        tagentry['inputs'] = list()
        tagentry['outputs'] = list()
        input_images = service_description['interface']['in']
        for elem in input_images:
            if elem['type']=='geoms.interface.Image':
                new_input = dict()
                # Type of the data source
                new_input['type'] = 'Not implemented' # TODO TO BE IMPLEMENTED
                # Role played by the source in the creation of the tagentry
                new_input['role'] = elem['description']
                # Universal identifier of the source entry
                new_input['id'] = [y['id'] for y in request_order['in'] if elem['name'] in y]
                # Timestamp (epoch-milliseconds) : date of the source entry creation
                if 'input_timestamp' in request_order['technicalMetadata']:
                    new_input['timestamp'] = request_order['technicalMetadata']['input_timestamp']
                else:
                    new_input['timestamp'] = -1 #If not available...
                # Array of properties for given input
                new_input['properties'] = dict() # TODO TO BE IMPLEMENTED, what type of properties? 'source' maybe?
                tagentry['inputs'].append(new_input)
        
        out_interface = service_description['interface']['out']
        new_output = dict()
        # Type of the output
        if 'linked_id' in algo_tag:
            for elem in service_description['interface']['out']:
                interface_type = [y['type'] for y in service_description['interface']['out'] if elem['name'] in y]
                if interface_type=='geoms.interface.ImageList' or interface_type=='geoms.interface.Image':
                    new_output['type'] = [y['description'] for y in service_description['interface']['out'] if elem['name'] in y]
                    # Role carried by generated output
                    new_output['role'] = [y['description'] for y in service_description['interface']['out'] if elem['name'] in y]
                    # Universal identifier of the generated output
                    new_output['id'] = algo_tag['linked_id']
                    # Timestamp (epoch-milliseconds) : date of the output creation
                    new_output['timestamp'] = algo_tag['timestamp']
                    tagentry['outputs'].append(new_output)
                    break

        tagentry['tag'] = dict()
        tagentry['tag']['area'] = algo_tag['area']
        tagentry['tag']['family'] = algo_tag['family']
        tagentry['tag']['name'] = algo_tag['name']
        tagentry['tag']['centroid'] = algo_tag['centroid']

        ## Geometry
        if 'referential' in request_order['technicalMetadata']:
            offset_lon = None
            offset_lat = None
            step_lon = None
            step_lat = None
            try:
                offset_lon = request_order['technicalMetadata']['referential']['upperLeft']['lon']
                offset_lat = request_order['technicalMetadata']['referential']['upperLeft']['lat']
                step_lon = request_order['technicalMetadata']['referential']['lonStep']
                step_lat = request_order['technicalMetadata']['referential']['latStep']
                tagentry['tag']['geometry'] = img_geometry_to_latlon_geometry(algo_tag['geometry'],offset_lat,offset_lon, step_lat,step_lon)
                tagentry['tag']['centroid']['coordinates'][1] = offset_lat + algo_tag['centroid']['coordinates'][0]*step_lat
                tagentry['tag']['centroid']['coordinates'][0] = offset_lon + algo_tag['centroid']['coordinates'][1]*step_lon
            except:
                tagentry['tag']['geometry'] = algo_tag['geometry']
        #existing_tag['tag']['tile'] = 'Not implemented' #TODO TO BE IMPLEMENTED
        #TODO to be implemented
        # if 'tag_properties'in algo_tag.keys():
        #     tagentry['tag']['properties'] = algo_tag['tag_properties']
        # if 'inputs_properties' in algo_tag.keys():
        #     tagentry['inputs']['properties'] = algo_tag['inputs_properties']
        # if 'outputs_properties' in algo_tag.keys():
        #     tagentry['outputs']['properties'] = algo_tag['outputs_properties']
        
        # Getting timestamp for validity of tag : latest timestamps of inputs
        latest = 0
        for elem in tagentry['inputs']:
            if elem['timestamp'] > latest:
                latest = elem['timestamp']
        tagentry['tag']['timestamp'] = latest
        tagentry['tagger'] = service_description['service']['organization'] + '.' + service_description['service']['processing'] + \
            '.' + service_description['service']['version']
        tagentry['timestamp'] = int(round(time.time()*1000))
        tagentry['tag']['value'] = algo_tag['linkedId']
        return tagentry

    tagentries = list()
    out_interface = service_description['interface']['out']
    for elem in out_interface:
        if elem['type'] == 'geoms.interface.TagList':
            for tag in service_output[elem['name']]:
                tagentries.append(create_tag_from_sources(service_description, request_order, service_output,tag))
        elif elem['type'] == 'geoms.interface.Tag':
            tagentries.append(create_tag_from_sources(service_description, request_order, service_output,service_output[elem['name']]))
    return tagentries