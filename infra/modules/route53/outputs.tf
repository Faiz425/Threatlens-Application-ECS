output "record_name" {
  description = "Route 53 application record"
  value       = aws_route53_record.app.fqdn
}

output "zone_id" {
  description = "Route 53 hosted zone ID"
  value       = data.aws_route53_zone.this.zone_id
}