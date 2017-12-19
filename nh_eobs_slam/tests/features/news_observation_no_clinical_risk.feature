# Created by colinwren at 19/04/16
Feature: NEWS Observation - No Clinical Risk
  As a HCA/Nurse
  In order to adhere to trust policy as I carry out NEWS Observations
  I want to have additional tasks generated for me to carry out based on the policy for the clinical risk of the patient

  Scenario Outline: Triggered tasks shown to user after submitting observation
    Given I am logged in as a <user>
    And I submit a NEWS Observation for a patient with no clinical risk
    And I confirm the calculated clinical risk to be None
    When I am shown the triggered tasks popup
    Then I should see no triggered tasks

    Examples:
      | user  |
      | Nurse |
      | HCA   |

  Scenario Outline: Triggered tasks shown in task list
    Given I am logged in as a <user>
    And I submit a NEWS Observation for a patient with no clinical risk who has been in hospital for <stay duration> days
    And I confirm the calculated clinical risk to be None
    When I go to the task list
    Then I should see no new notifications for the patient
    And the next NEWS observation task for the patient is in <time to next NEWS> hours

    Examples:
      | user  | stay duration | time to next NEWS |
      | Nurse | 1-2           | 12                |
      | HCA   | 1-2           | 12                |
      | Nurse | 3+            | 24                |
      | HCA   | 3+            | 24                |