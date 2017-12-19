# Created by colinwren at 19/04/16
Feature: Shift Coordinator Notification
  As a Nurse
  In order to adhere to trust policy as I carry out NEWS Observations
  I want to have additional tasks generated for me to carry out based on the policy for the clinical risk of the patient

  Background:
    Given I am logged in as a Nurse
    And I submit a NEWS Observation for a patient with a medium clinical risk
    And I confirm the calculated clinical risk to be Medium

  Scenario: Shift Coordinator Notification Form
    Given I am shown the triggered tasks popup
    When I click the Inform Shift Coordinator notification item
    Then I can see the text "Inform Shift Coordinator"
    And I can confirm the notification
    And I should not see any triggered tasks when I confirm the notification