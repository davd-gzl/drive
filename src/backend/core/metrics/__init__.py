"""
Prometheus metrics of the application, as served on /metrics.

Enabled by PROMETHEUS_METRICS_ENABLED and protected by
`core.middleware.PrometheusAuthMiddleware`, see
docs/self-hosting/configuration/monitoring.md. Only imported when the metrics
are enabled.
"""
