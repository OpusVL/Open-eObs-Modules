# Created by colinwren at 19/04/16
Feature: Review Frequency Notification
  As a Nurse
  In order to adhere to trust policy as I carry out NEWS Observations
  I want to have additional tasks generated for me to carry out based on the policy for the clinical risk of the patient

  Background:
    Given I am logged in as a Nurse
    And I submit a NEWS Observation for a patient with a low clinical risk
    And I confirm the calculated clinical risk to be Low
    And I confirm the Assess Patient notification

  Scenario: Assess Patient Notification Form
    Given I am shown the triggered tasks popup
    When I click the Review Frequency notification item
    Then I can see the text "Review Frequency"
    And I can see a list of frequencies
      | frequency        |
      | Every 15 Minutes |
      | Every 30 Minutes |
      | Every Hour       |
      | Every 2 Hours    |
      | Every 4 Hours    |
      | Every 6 Hours    |
    And I can confirm the notification

  Scenario: Post Assess Patient Triggered Actions
    When I confirm the Review Frequency notification
    Then I see a popup with the following notifications:
      | tasks                    |
      | Inform Medical Team      |
