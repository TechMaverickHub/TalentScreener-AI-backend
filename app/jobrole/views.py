import os
import tempfile

from PyPDF2 import PdfReader
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import MultiPartParser, FormParser

from app.jobrole.serializers import JobRoleSerializer
from app.jobrole.utils import extract_relevant_sections_with_llm, extract_job_keywords_from_resume, \
    parse_job_description_with_llm, parse_resume_with_llm, flatten_resume_dict
from app.langchain_utils.search import search_matching_documents, search_matching_documents_new, \
    search_matching_documents_new_2
from app.langchain_utils.store import store_job_description
from app.langchain_utils.vectorstore import embedding_model, safe_vector_format
from app.utils import get_response_schema


# Create your views here.
class StoreJobRoleApiView(GenericAPIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="Job title"),
                "description": openapi.Schema(type=openapi.TYPE_STRING, description="Full job description text"),
                "metadata": openapi.Schema(type=openapi.TYPE_OBJECT, description="Optional metadata (e.g., job_id, location)")
            },
            required=["title", "description"]
        )
    )
    def post(self, request):
        title = request.data.get("title")
        description = request.data.get("description")
        metadata = request.data.get("metadata", {})

        if not title or not description:
            return get_response_schema({}, "Title and description are required", status.HTTP_400_BAD_REQUEST)

        metadata["type"] = "job"
        metadata["title"] = title

        # Store and embed in vector DB
        store_job_description(description, metadata)

        # Embed for relational DB storage
        embedding_vector = safe_vector_format(embedding_model.embed_query(description))

        job_role_data = {
            "title": title,
            "description": description,
            "embedding_vector": embedding_vector
        }

        serializer = JobRoleSerializer(data=job_role_data)

        if serializer.is_valid():
            serializer.save()
            return get_response_schema(serializer.data, "JobRole stored successfully", status.HTTP_201_CREATED)

        return get_response_schema(serializer.errors, "Validation failed", status.HTTP_400_BAD_REQUEST)

class HybridSearchApiView(GenericAPIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "query": openapi.Schema(type=openapi.TYPE_STRING, description="Search query text"),
                "target": openapi.Schema(type=openapi.TYPE_STRING, enum=["resume", "job"],
                                         description="Search target type"),
                "top_k": openapi.Schema(type=openapi.TYPE_INTEGER, default=5)
            },
            required=["query", "target"]
        )
    )
    def post(self, request):
        query = request.data.get("query")
        target = request.data.get("target")
        top_k = int(request.data.get("top_k", 5))

        if not query or target not in ["resume", "job"]:
            return get_response_schema({}, "Invalid or missing parameters", status.HTTP_400_BAD_REQUEST)

        results = search_matching_documents(query_text=query, top_k=top_k, filter_type=target)
        return get_response_schema(results, f"Top {top_k} matches retrieved", status.HTTP_200_OK)


class CandidateSearchFromResumeTextApiView(GenericAPIView):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "resume_text": openapi.Schema(type=openapi.TYPE_STRING,
                                              description="Candidate resume content to search relevant job roles"),
                "top_k": openapi.Schema(type=openapi.TYPE_INTEGER, default=5)
            },
            required=["resume_text"]
        )
    )
    def post(self, request):
        resume_text = request.data.get("resume_text")
        top_k = int(request.data.get("top_k", 5))

        if not resume_text:
            return get_response_schema({}, "Resume text is required", status.HTTP_400_BAD_REQUEST)

        filtered_resume = extract_relevant_sections_with_llm(resume_text)

        included_titles = extract_job_keywords_from_resume(filtered_resume)

        results = search_matching_documents_new_2(query_text=filtered_resume, filter_type="job")
        return get_response_schema(results, f"Top {top_k} matching job roles retrieved", status.HTTP_200_OK)



class UploadJobDescriptionAPIView(GenericAPIView):

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
            return get_response_schema({}, "Title and description are required", status.HTTP_400_BAD_REQUEST)

        structured_data = parse_job_description_with_llm(description)

        # Extract metadata fields from structured_data
        metadata = {}
        try:
            metadata = {
                "type": "job",
                "title": structured_data.get("title"),
                "location": structured_data.get("location"),
                "department": structured_data.get("department")
            }
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
            return get_response_schema(serializer.data, "JobRole stored successfully", status.HTTP_201_CREATED)

        return get_response_schema(serializer.errors, "Validation failed", status.HTTP_400_BAD_REQUEST)

class UploadResumeAPIView(GenericAPIView):
    parser_classes = (MultiPartParser, FormParser)

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
            return get_response_schema({}, "Resume data is required", status.HTTP_400_BAD_REQUEST)

        resume_data = flatten_resume_dict(resume_data)
        results = search_matching_documents_new_2(query_text=resume_data, filter_type="job")
        return get_response_schema(results, "Matching job roles retrieved", status.HTTP_200_OK)
