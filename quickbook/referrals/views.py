from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .services import (
    get_or_create_referral_node,
    build_tree_dict,
    find_root_node,
    get_team_stats,
)
from .serializers import UserSummarySerializer, ReferralStatsSerializer

from drf_spectacular.utils import extend_schema, OpenApiTypes

User = get_user_model()

class ReferralTreeView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Referrals"],
        summary="Get full binary referral tree structure for specified user ID",
        responses={200: OpenApiTypes.OBJECT}
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        node = get_or_create_referral_node(user)
        tree_data = build_tree_dict(node)
        return Response(tree_data, status=status.HTTP_200_OK)


class ReferralRootView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSummarySerializer

    @extend_schema(
        tags=["Referrals"],
        summary="Find top root ancestor node for specified user ID",
        responses={200: UserSummarySerializer}
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        node = get_or_create_referral_node(user)
        root_node = find_root_node(node)
        serializer = UserSummarySerializer(root_node.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReferralStatsView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ReferralStatsSerializer

    @extend_schema(
        tags=["Referrals"],
        summary="Get binary referral network team statistics (left/right count)",
        responses={200: ReferralStatsSerializer}
    )
    def get(self, request, user_id):
        user = get_object_or_404(User, pk=user_id)
        node = get_or_create_referral_node(user)
        stats_data = get_team_stats(node)
        serializer = ReferralStatsSerializer(stats_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
