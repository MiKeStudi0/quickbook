from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    referred_by_code = serializers.CharField(source='referred_by.referral_code', read_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'is_staff',
            'is_vendor',
            'referral_code',
            'referred_by',
            'referred_by_code',
            'created_at',
        )
        read_only_fields = ('id', 'is_staff', 'referral_code', 'referred_by', 'created_at')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    referral_code = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_vendor', 'referral_code')

    def validate_referral_code(self, value):
        if value:
            if not User.objects.filter(referral_code=value).exists():
                raise serializers.ValidationError("Invalid referral code.")
        return value

    def create(self, validated_data):
        referral_code_input = validated_data.pop('referral_code', None)
        password = validated_data.pop('password')
        
        referrer = None
        if referral_code_input:
            referrer = User.objects.filter(referral_code=referral_code_input).first()

        user = User.objects.create_user(
            password=password,
            referred_by=referrer,
            **validated_data
        )

        from referrals.services import place_user_in_referral_tree
        place_user_in_referral_tree(user, referrer)

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                # Fallback check if user passed email instead of username
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request=self.context.get('request'), username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass

            if not user:
                raise serializers.ValidationError({"detail": "Unable to log in with provided credentials."})
            if not user.is_active:
                raise serializers.ValidationError({"detail": "User account is disabled."})
        else:
            raise serializers.ValidationError({"detail": "Must include 'username' and 'password'."})

        attrs['user'] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except Exception as e:
            raise serializers.ValidationError({"detail": "Invalid or expired token."})
