# Created by colinwren at 19/04/16
Feature: NEWS Observation - Low Clinical Risk
  As a HCA/Nurse
  In order to adhere to trust policy as I carry out NEWS Observations
  I want to have additional tasks generated for me to carry out based on the policy for the clinical risk of the patient

  Scenario Outline: Triggered tasks shown to user after submitting observation
    Given I am logged in as a <user>
    And I submit a NEWS Observation for a patient with a low clinical risk
    And I confirm the calculated clinical risk to be Low
    When I am shown the triggered tasks popup
    Then I should see these triggered tasks:
      | tasks                |
      | <user specific task> |

    Examples:
      | user  | user specific task         |
      | Nurse | Assess Patient             |
      | HCA   | Inform Nurse About Patient |

  Scenario Outline: Triggered tasks shown in task list
    Given I am logged in as a <user>
    And I submit a NEWS Observation for a patient with a low clinical risk who has been in hospital for <stay duration> days
    And I confirm the calculated clinical risk to be Low
    When I go to the task list
    Then I should see the following new notifications for the patient
      | tasks                |
      | <user specific task> |
    And the next NEWS observation task for the patient is in <time to next NEWS> hours

    Examples:
      | user  | user specific task         | stay duration | time to next NEWS |
      | Nurse | Assess Patient             | 1-2           | 6                 |
      | HCA   | Inform Nurse About Patient | 1-2           | 6                 |
      | Nurse | Assess Patient             | 3+            | 6                 |
      | HCA   | Inform Nurse About Patient | 3+            | 6                 |