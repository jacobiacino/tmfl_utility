provider "aws" {
  region = "us-east-1"
}

resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_s3_bucket" "tmfl" {
  bucket        = "trace-mcsorely-fan-league"
  force_destroy = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "example" {
  bucket = aws_s3_bucket.tmfl.bucket

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "tmfl_lockdown" {
  bucket                  = aws_s3_bucket.tmfl.bucket
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_iam_role_policy_attachment" "attach" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "../get_adp_data.py"
  output_path = "../out/get_adp_data.zip"
}

resource "aws_lambda_function" "web_scraper" {
  filename      = data.archive_file.lambda_zip.output_path
  function_name = "scrape-adp-data"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "get_adp_data.lambda_handler"

  source_code_hash = filebase64sha256(data.archive_file.lambda_zip.output_path)

  runtime = "python3.9"

  layers = [
    "arn:aws:lambda:us-east-1:336392948345:layer:AWSDataWrangler-Python39:9"
  ]

  timeout = 30

  environment {
    variables = {
      s3_target = aws_s3_bucket.tmfl.bucket
    }
  }
}