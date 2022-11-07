Feature: Transform geojson output into tag

  @tag_service
  Scenario Outline: Check if a geojson must be converted to tag
    Given A geojson dictionary "<geojson_path>"
    When The geojson is checked for tag transformation
    Then The result is "<tag_transformation_required>"
    Examples:
      | geojson_path        | tag_transformation_required |
      | tag_geojson.json    | true                        |
      | no_tag_geojson.json | false                       |

  @tag_service
  Scenario Outline: Transform geojson in tag
    Given An input payload "<input_path>"
    Given A geojson dictionary "<geojson_path>"
    When The tag transformation is applied
    Then The result is same as "<expected_tag_path>"
    Examples:
      | input_path | geojson_path     | expected_tag_path  |
      | input.json | tag_geojson.json | generated_tag.json |
