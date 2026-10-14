# SmartMail AI — Terraform Automated Tests for Staging Safety Guardrails
# Uses Terraform native mock providers to run 100% locally with zero cloud connectivity.

mock_provider "aws" {}
mock_provider "random" {}

# Test 1: Staging environment MUST fail when allowed_account_id is empty
run "staging_fails_when_account_id_is_empty" {
  command = plan

  variables {
    environment        = "staging"
    allowed_account_id = ""
  }

  expect_failures = [
    var.allowed_account_id,
  ]
}

# Test 2: Staging environment MUST fail when allowed_account_id is not 12 digits
run "staging_fails_when_account_id_is_invalid" {
  command = plan

  variables {
    environment        = "staging"
    allowed_account_id = "12345" # Invalid length
  }

  expect_failures = [
    var.allowed_account_id,
  ]
}

# Test 3: Staging environment MUST succeed planning when allowed_account_id is a valid 12-digit ID
run "staging_succeeds_with_valid_12_digit_account_id" {
  command = plan

  variables {
    environment        = "staging"
    allowed_account_id = "123456789012"
  }
}

# Test 4: Production environment succeeds planning without blocking on staging guardrail
run "production_succeeds_with_default_account_id" {
  command = plan

  variables {
    environment        = "production"
    allowed_account_id = ""
  }
}
