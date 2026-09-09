from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'referral_code', 'is_vendor', 'is_staff', 'created_at')


class ReferralStatsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    left_team_count = serializers.IntegerField()
    right_team_count = serializers.IntegerField()
    total_team_count = serializers.IntegerField()
