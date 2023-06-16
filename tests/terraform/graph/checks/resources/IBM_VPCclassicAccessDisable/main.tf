resource "ibm_is_vpc" "pass_1" {
  name = "pud-ibm-vpc"
  region = "us-east"
  classic_access = false
}

# Default classic_access is False
resource "ibm_is_vpc" "pass_2" {
  name = "pud-ibm-vpc"
  region = "us-east"
}

resource "ibm_is_vpc" "fail" {
  name = "pud-ibm-vpc"
  region = "us-east"
  classic_access = true
}
