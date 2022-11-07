import json
import os

from behave import *

from cador.core.TagService import TagService


@given(u'An input payload "{input_path}"')
def step_impl(context, input_path):
    with open(os.path.join(os.getcwd(), 'resources', 'tag_service', input_path)) as file:
        context.inputs = json.loads(file.read())


@given(u'A geojson dictionary "{geojson_path}"')
def step_impl(context, geojson_path):
    with open(os.path.join(os.getcwd(), 'resources', 'tag_service', geojson_path)) as file:
        context.geojson = json.loads(file.read())


@when(u'The geojson is checked for tag transformation')
def step_impl(context):
    service = TagService()
    context.result = service.requires_tag_transformation(context.geojson)


@when(u'The tag transformation is applied')
def step_impl(context):
    service = TagService()
    context.result = service.create_tags(inputs=context.inputs, geojson=context.geojson)


@then(u'The result is "{expected}"')
def step_impl(context, expected: str):
    assert str(context.result).upper() == expected.upper()


@then(u'The result is same as "{expected_path}"')
def step_impl(context, expected_path):
    with open(os.path.join(os.getcwd(), 'resources', 'tag_service', expected_path)) as file:
        expected = json.loads(file.read())

        # ignore timestamp as it will be different each time
        expected['timestamp'] = context.result[0]['timestamp']

        result_json = json.dumps(context.result[0], sort_keys=True)
        expected_json = json.dumps(expected, sort_keys=True)

        assert result_json == expected_json
