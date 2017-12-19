# Created by colinwren at 19/04/16
Feature: Call Ambulance Notification
  As a Nurse
  In order to adhere to trust policy as I carry out NEWS Observations
  I want to have additional tasks generated for me to carry out based on the policy for the clinical risk of the patient

  Background:
    Given I am logged in as a Nurse
    And I submit a NEWS Observation for a patient with a medium clinical risk
    And I confirm the calculated clinical risk to be Medium

  Scenario: Call Ambulance Notification Form - Confirm
    Given I am shown the triggered tasks popup
    When I click the Call An Ambulance 2222/9999 notification item
    Then I can see the text "Call An Ambulance 2222/9999"
    And I can confirm the notification
    And I can cancel the notification
    And I should not see any triggered tasks when I confirm the notification

  Scenario: Call Ambulance Notification Form - Cancel
    Given I am shown the triggered tasks popup
    And I click the Call An Ambulance 2222/9999 notification item
    When I cancel the notification
    Then I am shown a list of cancellation reason
    And I should not see any triggered tasks when I cancel the notification