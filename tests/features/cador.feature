Feature: Cador handle requests sent to kafka topic

  @cador
  Scenario: Cador handle requests sent to kafka topic
    Given The web-service is running
    When The test folder is defined
    Then Check each test is passing
