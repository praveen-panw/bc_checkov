resource "ibm_is_lb" "fail" {
  name    = "pud-load-balancer"
  subnets = [ibm_is_subnet.pud.id]
  profile = "network-fixed"
}