module "vpc" {
  source = "./modules/vpc"

  name               = "threatlens"
  vpc_cidr           = "10.0.0.0/16"
  availability_zones = ["eu-west-2a", "eu-west-2b"]
}

module "ecr" {
  source = "./modules/ecr"

  repository_name = "threatlens"
}