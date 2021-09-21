output "load_balancer_hostname" {
  value = aws_alb.main.dns_name
}
