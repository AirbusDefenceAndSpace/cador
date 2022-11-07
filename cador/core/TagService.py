import time

from shapely.geometry import shape, mapping

from cador.config import log
from cador.postprocessing.geometry import img_geometry_to_latlon_geometry


class TagService:

    def extract_tags(self, inputs, referential: dict, timestamp, job_results, result_key):
        tags = []
        if self._requires_tag_transformation(job_results[result_key]):
            log.info('geojson : {}'.format(result_key))
            self.patch_geometry(referential, job_results[result_key])
            tags = [self._create_tag(i, x, timestamp) for i, x in enumerate(job_results[result_key]['features'])]

        return [self._format_tag(inputs, tag) for tag in tags]

    @staticmethod
    def _requires_tag_transformation(geojson_collection: [dict]):
        try:
            confidence = geojson_collection['features'][0]['properties']['confidence']
            return isinstance(confidence, float)
        except:
            return False

    @staticmethod
    def patch_geometry(referential: dict, data: dict):
        if referential is not None:
            try:
                features = data['features']
                for feature in features:
                    offset_lon = referential['upperLeft']['lon']
                    offset_lat = referential['upperLeft']['lat']
                    step_lon = referential['lonStep']
                    step_lat = referential['latStep']
                    img_geometry_to_latlon_geometry(feature['geometry'], offset_lat, offset_lon, step_lat, step_lon)
                log.info('geometry coordinates patched !')
            except:
                log.warn('could not patch geometry coordinates !')

    @staticmethod
    def _create_tag(linked_id: int, geojson: dict, timestamp):
        try:
            confidence = geojson['properties']['confidence']
            name = geojson['properties'].get('name')
            value = geojson['properties'].get('value')
            geometry = geojson['geometry']
            return {
                'linkedId': linked_id,
                'family': 'detection',
                'geometry': geometry,
                'value': value,
                'name': name,
                'confidence': confidence,
                'timestamp': timestamp
            }
        except Exception as e:
            log.error('could not create tag : {}'.format(geojson))
            raise e

    @staticmethod
    def _format_tag(inputs: [], tag: dict) -> dict:
        try:
            geom = shape(tag['geometry'])
            tag['area'] = geom.area
            tag['centroid'] = mapping(geom.centroid)

            confidence = 1.0
            if 'confidence' in tag:
                confidence = tag.pop('confidence')

            return {
                'inputs': inputs,
                'outputs': [
                    # TODO : define how to build the outputs field
                ],
                'confidence': confidence,
                'tag': tag,
                'timestamp': int(round(time.time()*1000)),
                'tagger': 'airbus.algo_name.version'
            }
        except Exception as e:
            log.error('could not format tag : {}'.format(tag))
            raise e
