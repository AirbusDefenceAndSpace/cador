Feature: Store objects using many storage systems

  @storage_service
  Scenario Outline: Store object using storage config
    Given A storage configuration <storage>
    When The storage service try to save <data>
    Then The returned message is <expected_message>
    Examples:
      | storage | data   | expected_message |
      | S3      | bbbbbb | {}               |
      | GCS     | bbbbbb | {}               |
