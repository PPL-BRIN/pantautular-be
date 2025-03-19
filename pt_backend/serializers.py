from rest_framework import serializers

class CaseLocationSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    location__longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    location__latitude = serializers.DecimalField(max_digits=8, decimal_places=6)
    city = serializers.CharField(max_length=255)

class AgeDistributionSerializer(serializers.Serializer):
    under_12 = serializers.IntegerField()
    age_12_25 = serializers.IntegerField()
    age_26_45 = serializers.IntegerField()
    above_45 = serializers.IntegerField()