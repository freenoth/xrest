from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse

from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import SomeFile
from .serializers import SomeFileSerializer, SomeFileMetaSerializer, SomeFileViewSerializer

from collections import OrderedDict
import mimetypes


# Create your views here.
def index(request):
    return render(request, 'api/content.html', {})


@csrf_exempt
@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser, ])
def files(request):
    if request.method == 'GET':
        sfiles = SomeFile.objects.all()
        serializer = SomeFileViewSerializer(sfiles, many=True)
        result = wrap_response('OK', status.HTTP_200_OK, serializer.data)
        return Response(data=result, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        serializer = SomeFileSerializer(data=request.data)
        if serializer.is_valid():
            # check for file exists
            if SomeFile.objects.filter(name=serializer.validated_data['file'].name):
                result = wrap_response('Error', status.HTTP_409_CONFLICT,
                                       {'file': ['File %s already exists' % serializer.validated_data['file'].name, ]})
                return Response(result, status=status.HTTP_409_CONFLICT)

            # save new file
            instance = serializer.save()
            view_serializer = SomeFileViewSerializer(instance)
            result = wrap_response('OK', status.HTTP_201_CREATED, view_serializer.data)
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            result = wrap_response('Error', status.HTTP_400_BAD_REQUEST, serializer.errors)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data=wrap_response('Error', status.HTTP_405_METHOD_NOT_ALLOWED, 'Method not allowed'),
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
@parser_classes([MultiPartParser, FormParser, ])
def file_detail(request, pk):
    sfiles = SomeFile.objects.filter(id=pk)
    if not sfiles:
        result = wrap_response('Error', status.HTTP_404_NOT_FOUND,
                               {'file': ['File not found', ]})
        return Response(result, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
            file = sfiles.first()
            with open(file.file.path, 'rb') as o_file:
                response = FileResponse(o_file, content_type=mimetypes.guess_type(file.file.path)[0])
                response['Content-Length'] = file.file.size
                response['Content-Disposition'] = 'attachment; filename=%s' % file.name
                return response

    elif request.method == 'PUT':
        serializer = SomeFileSerializer(sfiles.first(), data=request.data)
        if serializer.is_valid():
            # update file
            instance = serializer.save()
            view_serializer = SomeFileViewSerializer(instance)
            result = wrap_response('OK', status.HTTP_200_OK, view_serializer.data)
            return Response(result, status=status.HTTP_200_OK)
        else:
            result = wrap_response('Error', status.HTTP_400_BAD_REQUEST, serializer.errors)
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        model = sfiles.first()
        file = model.file
        file.delete()
        model.delete()

        result = wrap_response('OK', status.HTTP_200_OK,
                               {'result': ['File deleted', ]})
        return Response(result, status=status.HTTP_200_OK)

    else:
        return Response(data=wrap_response('Error', status.HTTP_405_METHOD_NOT_ALLOWED, 'Method not allowed'),
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(['GET'])
def file_meta(request, pk):
    sfiles = SomeFile.objects.filter(id=pk)
    if not sfiles:
        result = wrap_response('Error', status.HTTP_404_NOT_FOUND,
                               {'file': ['File not found', ]})
        return Response(result, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SomeFileMetaSerializer(sfiles.first())
        result = wrap_response('OK', status.HTTP_200_OK, serializer.data)
        return Response(data=result, status=status.HTTP_200_OK)

    else:
        return Response(data=wrap_response('Error', status.HTTP_405_METHOD_NOT_ALLOWED, 'Method not allowed'),
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)


def wrap_response(state, code, data):
    return OrderedDict([('status', state), ('code', code), ('data', data)])
