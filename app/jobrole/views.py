from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView

from app.jobrole.serializers import JobRoleSerializer
from app.langchain_utils.store import store_text
from app.langchain_utils.vectorstore import embedding_model
from app.utils import get_response_schema


# Create your views here.
class StoreJDOrResumeApiView(GenericAPIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "type": openapi.Schema(type=openapi.TYPE_STRING, enum=["job", "resume"], description="Document type"),
                "content": openapi.Schema(type=openapi.TYPE_STRING, description="JD or Resume text"),
                "metadata": openapi.Schema(type=openapi.TYPE_OBJECT,
                                           description="Metadata dict with job_id or candidate_id")
            },
            required=["type", "content", "metadata"]
        )
    )
    def post(self, request):
        doc_type = request.data.get("type")

        content = request.data.get("content")
        metadata = request.data.get("metadata")

        if not doc_type or not content or not metadata:
            return get_response_schema({}, "Missing fields", status.HTTP_400_BAD_REQUEST)

        metadata["type"] = doc_type
        store_text(content, metadata)

        job_role_data = {
            "title": metadata.get("title", "Untitled Role"),
            "description": content,
            "embedding_vector": embedding_model.embed_query(content)

        }

        serializer = JobRoleSerializer(data=job_role_data)

        if serializer.is_valid():
            serializer.save()
            return get_response_schema({"metadata": metadata}, f"{doc_type.capitalize()} stored and embedded",
                                       status.HTTP_201_CREATED)
        else:
            return get_response_schema({}, "Failed to store job role", status.HTTP_400_BAD_REQUEST)

