import os
import tempfile

from PyPDF2 import PdfReader
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser

from app.global_constants import SuccessMessage, ErrorMessage
from app.jobrole.serializers import JobRoleSerializer
from app.jobrole.utils import parse_job_description_with_llm, parse_resume_with_llm, flatten_resume_dict
from app.langchain_utils.search import search_matching_documents_new_2
from app.langchain_utils.store import store_job_description
from app.langchain_utils.vectorstore import embedding_model, safe_vector_format
from app.utils import get_response_schema
from permissions import IsUser, IsSuperAdmin


# Create your views here.


class UploadJobDescriptionAPIView(GenericAPIView):
    permission_classes = [IsSuperAdmin]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="Job title"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, description="Full job description text"),
                "metadata": openapi.Schema(type=openapi.TYPE_OBJECT,
                                           description="Optional metadata (e.g., job_id, location)")
            },
            required=["title", "description"]
        )
    )
    def post(self, request):

        title = request.data.get("title")
        description = request.data.get("description")

        if not title or not description:
            return get_response_schema({}, ErrorMessage.MISSING_FIELDS.value, status.HTTP_400_BAD_REQUEST)

        structured_data = parse_job_description_with_llm(description)

        # Extract metadata fields from structured_data
        metadata = {}
        try:

            metadata['type'] = "job"
            metadata['title'] = structured_data.get("title")
            metadata['location'] = structured_data.get("location")
            metadata['department'] = structured_data.get("department")
        except Exception:
            metadata = {"type": "job"}

        # Store and embed in vector DB
        store_job_description(structured_data, metadata)

        # Embed for relational DB storage
        embedding_vector = safe_vector_format(embedding_model.embed_query(description))

        job_role_data = {
            "title": title,
            "description": structured_data,
            "embedding_vector": embedding_vector
        }

        serializer = JobRoleSerializer(data=job_role_data)

        if serializer.is_valid():
            serializer.save()
            return get_response_schema(serializer.data, SuccessMessage.RECORD_CREATED.value, status.HTTP_201_CREATED)

        return get_response_schema(serializer.errors, ErrorMessage.MISSING_FIELDS.value, status.HTTP_400_BAD_REQUEST)


class UploadResumeAPIView(GenericAPIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsUser]

    @swagger_auto_schema(
        operation_description='Upload a PDF file for ingestion. The file will be processed synchronously.',
        manual_parameters=[
            openapi.Parameter(name='resume', in_=openapi.IN_FORM, type=openapi.TYPE_FILE, required=True,
                              description='PDF resume to upload'),
        ]
    )
    def post(self, request):
        file = request.FILES.get("resume")
        if not file:
            return get_response_schema({}, "Resume file is required", status.HTTP_400_BAD_REQUEST)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            reader = PdfReader(tmp_path)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            structured_resume = parse_resume_with_llm(text)
        finally:
            os.remove(tmp_path)

        return get_response_schema(structured_resume, "Resume parsed successfully", status.HTTP_200_OK)


class MatchResumeToJobsAPIView(GenericAPIView):
    permission_classes = [IsUser]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "resume_data": openapi.Schema(type=openapi.TYPE_OBJECT, description="Resume data"),

            }
        )
    )
    def post(self, request):
        resume_data = request.data.get("resume_data")
        if not resume_data:
            return get_response_schema({}, ErrorMessage.MISSING_FIELDS.value, status.HTTP_400_BAD_REQUEST)

        resume_data = flatten_resume_dict(resume_data)
        results = search_matching_documents_new_2(query_text=resume_data, filter_type="job")
        return get_response_schema(results, SuccessMessage.RECORD_RETRIEVED.value, status.HTTP_200_OK)
