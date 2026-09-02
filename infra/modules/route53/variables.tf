variable "domain_name" {
  description = "Root domain name"
  type        = string
}

variable "record_name" {
  description = "Subdomain record name"
  type        = string
}

variable "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  type        = string
}

variable "alb_zone_id" {
  description = "Hosted zone ID of the Application Load Balancer"
  type        = string
}

variable "certificate_domain_validation_options" {
  description = "ACM certificate DNS validation options"
  type = list(object({
    domain_name           = string
    resource_record_name  = string
    resource_record_type  = string
    resource_record_value = string
  }))
}