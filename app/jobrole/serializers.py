from rest_framework import serializers

from app.jobrole.models import JobRole


class JobRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRole
        fields = ('title', 'description', 'embedding_vector')

        extra_kwargs = {
            'embedding_vector': {'write_only': True}
        }

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_description(self, value):
        if len(value.strip()) < 100:
            raise serializers.ValidationError("Description must be at least 100 characters.")
        return value