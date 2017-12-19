# Created by colinwren at 19/04/16
Feature: NEWS Observation - Medium Clinical Risk
  As a HCA/Nurse
  In order to adhere to trust policy as I carry out NEWS Observations
  I want to have additional tasks generated for me to carry out based on the policy for the clinical risk of the patient

  Scenario: Triggered tasks shown to Nurse user after submitting observation
    Given I am logged in as a Nurse
    And I submit a NEWS Observation for a patient with a medium clinical risk
    And I confirm the calculated clinical risk to be Medium
    When I am shown the triggered tasks popup
    Then I should see these triggered tasks:
      | tasks                            |
      | Inform Shift Coordinator         |
      | Urgently Inform Medical Team     |
      | Call An Ambulance 2222/9999      |

  Scenario: Triggered tasks shown to HCA user after submitting observation
    Given I am logged in as a HCA
    And I submit a NEWS Observation for a patient with a medium clinical risk
    And I confirm the calculated clinical risk to be Medium
    When I am shown the triggered tasks popup
    Then I should see these triggered tasks:
      | tasks                      |
      | Inform Nurse About Patient |

  Scenario Outline: Triggered tasks shown in task list for Nurse
    Given I am logged in as a Nurse
    And I submit a NEWS Observation for a patient with a medium clinical risk who has been in hospital for <stay duration> days
    And I confirm the calculated clinical risk to be Medium
    When I go to the task list
    Then I should see the following new notifications for the patient
      | tasks                            |
      | Inform Shift Coordinator         |
      | Urgently Inform Medical Team     |
      | Call An Ambulance 2222/9999      |
    And the next NEWS observation task for the patient is in <time to next NEWS> hours

    Examples:
      | stay duration | time to next NEWS |
      | 1-2           | 1                 |
      | 3+            | 1                 |


  Scenario Outline: Triggered tasks shown in task list for HCA
    Given I am logged in as a HCA
    And I submit a NEWS Observation for a patient with a medium clinical risk who has been in hospital for <stay duration> days
    And I confirm the calculated clinical risk to be Medium
    When I go to the task list
    Then I should see the following new notifications for the patient
      | tasks                      |
      | Inform Nurse About Patient |
    And the next NEWS observation task for the patient is in <time to next NEWS> hours

    Examples:
      | stay duration | time to next NEWS |
      | 1-2           | 1                 |
      | 3+            | 1                 |