from rest_framework import serializers

from app.jobrole.models import JobRole


class JobRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRole
        fields = ('title', 'description', 'embedding_vector')