from django.contrib.auth.models import User
from django.db import models


class Test(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    arms = models.IntegerField()
    proportional_metric = models.BooleanField()
    description = models.TextField(blank=True, null=True)
    hypothesis = models.TextField(blank=True, null=True)
    primary_metric = models.CharField(max_length=255, blank=True, null=True)
    business_target = models.CharField(max_length=255, blank=True, null=True)

    confidence_level = models.FloatField(blank=True, null=True)
    power = models.FloatField(blank=True, null=True)
    baseline_conversion_rate = models.FloatField(blank=True, null=True)
    baseline_kpi = models.FloatField(blank=True, null=True)
    kpi_sd = models.FloatField(blank=True, null=True)
    mde = models.FloatField(blank=True, null=True)
    daily_interactions = models.IntegerField(blank=True, null=True)
    absolute = models.BooleanField(blank=True, null=True)
    equal_allocation = models.BooleanField(blank=True, null=True)
    two_tailed_test = models.BooleanField(blank=True, null=True)
    expected_uplift = models.FloatField(blank=True, null=True)
    revenue_per_conversion = models.FloatField(blank=True, null=True)
    allocations = models.JSONField(default=list())
    # OUTPUT
    total_sample_size = models.IntegerField(blank=True, null=True)
    sample_size_per_arm = models.IntegerField(blank=True, null=True)
    days_required = models.IntegerField(blank=True, null=True)
    weeks_required = models.IntegerField(blank=True, null=True)
    control_revenue = models.FloatField(blank=True, null=True)
    test_revenue = models.FloatField(blank=True, null=True)

    visitors_conversions_input = models.JSONField(default=[])
    p_values = models.JSONField(default=[])
    relative_uplift_values = models.JSONField(default=[])
    max_uplift = models.FloatField(blank=True, null=True)
    test_statistic = models.FloatField(blank=True, null=True)
    ci_lower_bound = models.FloatField(blank=True, null=True)
    ci_upper_bound = models.FloatField(blank=True, null=True)
    disclaimer_note = models.TextField(blank=True, null=True)
    statistically_significant = models.BooleanField(blank=True, null=True)

    status = models.CharField(max_length=15, blank=True, null=True, default="APPR")
    integrity = models.CharField(max_length=15, blank=True, null=True)
    modified_date = models.DateField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
