variable "project_id" {
  type        = string
  description = "Google Cloud project ID."
}

variable "region" {
  type        = string
  description = "Google Cloud region."
  default     = "asia-southeast1"
}

variable "environment" {
  type        = string
  description = "Deployment environment."
  default     = "dev"
}

variable "state_bucket_name" {
  type        = string
  description = "GCS Terraform state bucket."
}

variable "namespace" {
  type        = string
  description = "Kubernetes namespace for Philobiblus."
  default     = "philobiblus"
}

variable "backend_image" {
  type        = string
  description = "Immutable backend image reference."

  validation {
    condition     = can(regex("@sha256:[0-9a-f]{64}$", var.backend_image))
    error_message = "backend_image must use an immutable sha256 digest."
  }
}

variable "recommendation_image" {
  type        = string
  description = "Immutable recommendation image reference."

  validation {
    condition     = can(regex("@sha256:[0-9a-f]{64}$", var.recommendation_image))
    error_message = "recommendation_image must use an immutable sha256 digest."
  }
}

variable "model_fetcher_image" {
  type        = string
  description = "Immutable model-fetcher image reference used by the recommender initContainer."

  validation {
    condition     = can(regex("@sha256:[0-9a-f]{64}$", var.model_fetcher_image))
    error_message = "model_fetcher_image must use an immutable sha256 digest."
  }
}

variable "frontend_origin" {
  type        = string
  description = "Allowed GitHub Pages origin without a trailing path."

  validation {
    condition     = can(regex("^https://[^/]+$", var.frontend_origin))
    error_message = "frontend_origin must be an HTTPS origin without a path."
  }
}

variable "recommendations_enabled" {
  description = "Emergency operator override for backend requests to the optional recommendation service."
  type        = bool
  default     = true
}

variable "recommendation_load_shedding_enabled" {
  description = "Whether high aggregate recommendation traffic opens a shared circuit."
  type        = bool
  default     = true
}

variable "recommendation_load_shedding_max_requests" {
  description = "Maximum aggregate recommendation requests allowed during one load-shedding window."
  type        = number
  default     = 12

  validation {
    condition     = var.recommendation_load_shedding_max_requests >= 1
    error_message = "recommendation_load_shedding_max_requests must be at least one."
  }
}

variable "recommendation_load_shedding_window_seconds" {
  description = "Length of the aggregate recommendation request window in seconds."
  type        = number
  default     = 10

  validation {
    condition     = var.recommendation_load_shedding_window_seconds >= 1
    error_message = "recommendation_load_shedding_window_seconds must be at least one."
  }
}

variable "recommendation_load_shedding_cooldown_seconds" {
  description = "How long the recommendation circuit remains open after a load-shedding event."
  type        = number
  default     = 30

  validation {
    condition     = var.recommendation_load_shedding_cooldown_seconds >= 1
    error_message = "recommendation_load_shedding_cooldown_seconds must be at least one."
  }
}

variable "gateway_host" {
  type        = string
  description = "Optional DNS hostname for the Gateway. Empty exposes an HTTP IP only."
  default     = ""
}

variable "gateway_https_enabled" {
  type        = bool
  description = "Enable HTTPS on the GKE Gateway using Certificate Manager."
  default     = false
}

variable "gateway_certificate_map_name" {
  type        = string
  description = "Certificate Manager certificate map name to attach to Gateway. If empty, reads from platform remote state."
  default     = ""
}

variable "gateway_http_to_https_redirect" {
  type        = bool
  description = "Enable HTTP to HTTPS redirect route on the Gateway."
  default     = false
}

variable "include_imgbb_secret" {
  type        = bool
  description = "Sync the ImgBB secret after it has an enabled Secret Manager version."
  default     = false
}
